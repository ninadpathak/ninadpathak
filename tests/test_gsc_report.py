"""Deterministic tests for the Search Console report logic.

Everything worth testing in tools/gsc_report.py is pure: the fan-out heuristic, the
window arithmetic, the delta maths, the cluster mapping, and the decay filter. None of
it touches the network, so all of it is pinned here.

The fan-out cases are built from the real 28-day query set to 2026-08-14, where 26 of
the 46 queries in positions 4-30 were permutations of one token core carrying 145
impressions and zero clicks. That is the failure this heuristic exists to prevent, so
the tests assert against the actual shape of it rather than invented strings.
"""

from __future__ import annotations

import datetime as dt
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import gsc_report as gr  # noqa: E402


# The real fan-out, trimmed to the variants that carried impressions. The variety
# matters: some members drop "official", some drop "bm25", and one reorders the head.
# A fixture where every member shares the same tokens would make the shared core look
# far more specific than it is and would not exercise straggler absorption.
FANOUT = [
    "anthropic contextual retrieval bm25 embeddings reranking official",
    "anthropic contextual retrieval official contextual embeddings bm25 reranking",
    "anthropic contextual retrieval official blog bm25 embeddings reranking",
    "anthropic contextual retrieval contextual embeddings bm25 reranking official",
    "anthropic contextual retrieval official blog contextual embeddings bm25 reranking",
    "anthropic contextual retrieval bm25 embeddings reranking official 2024",
    "anthropic contextual retrieval official bm25 embeddings reranking",
    "anthropic contextual retrieval bm25 reranking official",
    "anthropic contextual retrieval bm25 embeddings official",
    "anthropic contextual retrieval contextual embeddings bm25 official",
    "anthropic contextual retrieval bm25 embeddings reranking 2024",
    "contextual retrieval anthropic official 2024",
]
HUMAN = [
    "how do you handle errors when ai agents make mistakes in production?",
    "how do companies debug ai agents that fail in production?",
    "ai agent memory vs fine-tuning for domain-specific knowledge retention",
    "long context windows",
    "top k rag",
]


def row(key: str, clicks: float, impressions: float, position: float) -> dict:
    return {"keys": [key], "clicks": clicks, "impressions": impressions,
            "position": position}


class TestTokenising(unittest.TestCase):
    def test_content_tokens_drop_stopwords(self):
        self.assertEqual(gr.content_tokens("how do you handle errors in production"),
                         {"handle", "errors", "production"})

    def test_content_tokens_are_order_blind(self):
        a = "anthropic contextual retrieval bm25 embeddings reranking official"
        b = "official reranking embeddings bm25 retrieval contextual anthropic"
        self.assertEqual(gr.content_tokens(a), gr.content_tokens(b))

    def test_stopword_ratio(self):
        self.assertEqual(gr.stopword_ratio("anthropic contextual retrieval bm25"), 0.0)
        self.assertGreater(gr.stopword_ratio(
            "why do i have to keep re-explaining my codebase to my ai agent"), 0.5)

    def test_stopword_ratio_empty_query_does_not_divide_by_zero(self):
        self.assertEqual(gr.stopword_ratio(""), 0.0)

    def test_jaccard(self):
        self.assertEqual(gr.jaccard(set(), set()), 0.0)
        self.assertEqual(gr.jaccard({"a"}, {"a"}), 1.0)
        self.assertAlmostEqual(gr.jaccard({"a", "b"}, {"b", "c"}), 1 / 3)


class TestBlobFilter(unittest.TestCase):
    def test_long_pasted_passage_is_a_blob(self):
        pasted = ("how does hnsw improve vector retrieval? it allows for lexical search "
                  "by identifying keywords across a very long pasted passage that keeps "
                  "going well past any real query length")
        self.assertTrue(gr.is_blob(pasted))

    def test_object_replacement_character_is_a_blob(self):
        self.assertTrue(gr.is_blob("how does hnsw improve retrieval? ￼ it allows"))

    def test_ordinary_queries_are_not_blobs(self):
        for q in HUMAN + FANOUT:
            self.assertFalse(gr.is_blob(q), q)

    def test_boundary_at_max_words(self):
        self.assertFalse(gr.is_blob(" ".join(["w"] * gr.MAX_QUERY_WORDS)))
        self.assertTrue(gr.is_blob(" ".join(["w"] * (gr.MAX_QUERY_WORDS + 1))))


class TestFamilies(unittest.TestCase):
    def test_permutation_fan_out_collapses_to_one_family(self):
        families = gr.find_families(FANOUT + HUMAN)
        self.assertEqual(len(families), 1)
        self.assertEqual(len(families[0]), len(FANOUT))

    def test_human_queries_are_not_absorbed(self):
        families = gr.find_families(FANOUT + HUMAN)
        claimed = {q for fam in families for q in fam}
        for q in HUMAN:
            self.assertNotIn(q, claimed, q)

    def test_shared_core_is_the_topic(self):
        families = gr.find_families(FANOUT)
        self.assertEqual(gr.family_core(families[0]),
                         {"anthropic", "contextual", "retrieval"})

    def test_core_containment_absorbs_decorated_stragglers(self):
        """These two fall under the Jaccard threshold but are the same fan-out."""
        stragglers = ["anthropic contextual retrieval official engineering blog",
                      "anthropic contextual retrieval 49% 67% failed retrievals"]
        families = gr.find_families(FANOUT + stragglers)
        claimed = {q for fam in families for q in fam}
        for q in stragglers:
            self.assertIn(q, claimed, q)

    def test_bare_core_query_is_never_absorbed(self):
        """The undecorated head term is a real query and must survive."""
        families = gr.find_families(FANOUT + ["anthropic contextual retrieval"])
        claimed = {q for fam in families for q in fam}
        self.assertNotIn("anthropic contextual retrieval", claimed)

    def test_below_minimum_family_size_is_not_a_family(self):
        self.assertEqual(gr.find_families(FANOUT[:gr.MIN_FAMILY_SIZE - 1]), [])

    def test_unrelated_queries_form_no_family(self):
        self.assertEqual(gr.find_families(HUMAN), [])


class TestClassifyClose(unittest.TestCase):
    def build(self):
        rows = [row(q, 0, 10, 9.0) for q in FANOUT]
        rows += [row("how do you handle errors when ai agents make mistakes in production?",
                     0, 11, 10.6),
                 row("ai agent memory vs fine-tuning for domain-specific knowledge retention",
                     0, 15, 6.7),
                 row("navin pathak", 0, 8, 22.5),            # brand-adjacent
                 row("top k rag", 0, 1, 11.0),               # below impression floor
                 row("technical documentation", 4, 90, 2.1)]  # outside 4-30
        return rows

    def test_fan_out_is_kept_out_of_the_human_list(self):
        result = gr.classify_close(self.build())
        humans = {h["query"] for h in result["human"]}
        for q in FANOUT:
            self.assertNotIn(q, humans)

    def test_human_queries_survive_and_are_ordered_by_impressions(self):
        result = gr.classify_close(self.build())
        self.assertEqual([h["query"] for h in result["human"]],
                         ["ai agent memory vs fine-tuning for domain-specific knowledge retention",
                          "how do you handle errors when ai agents make mistakes in production?"])

    def test_brand_query_is_excluded_and_counted(self):
        result = gr.classify_close(self.build())
        self.assertNotIn("navin pathak", {h["query"] for h in result["human"]})
        self.assertEqual(result["excluded"]["brand"], 1)

    def test_impression_floor_excludes_and_counts(self):
        result = gr.classify_close(self.build())
        self.assertEqual(result["excluded"]["below_impression_floor"], 1)

    def test_out_of_range_position_is_not_considered(self):
        result = gr.classify_close(self.build())
        self.assertNotIn("technical documentation", {h["query"] for h in result["human"]})

    def test_family_impressions_are_reported_not_lost(self):
        result = gr.classify_close(self.build())
        self.assertEqual(len(result["families"]), 1)
        self.assertEqual(result["families"][0]["impressions"], 10 * len(FANOUT))
        self.assertEqual(result["families"][0]["clicks"], 0)

    def test_every_in_range_query_is_accounted_for(self):
        """Nothing may vanish: human + families + exclusions must equal the input."""
        result = gr.classify_close(self.build())
        counted = (len(result["human"]) + result["excluded"]["fan_out"]
                   + result["excluded"]["brand"] + result["excluded"]["blob"]
                   + result["excluded"]["below_impression_floor"])
        self.assertEqual(counted, result["in_range"])


class TestWindows(unittest.TestCase):
    def test_windows_end_three_days_back_and_do_not_overlap(self):
        start, end, pstart, pend = gr.windows(dt.date(2026, 8, 17))
        self.assertEqual(end, dt.date(2026, 8, 14))
        self.assertEqual(start, dt.date(2026, 7, 18))
        self.assertEqual(pend, dt.date(2026, 7, 17))
        self.assertEqual(pstart, dt.date(2026, 6, 20))

    def test_both_windows_are_the_same_length(self):
        start, end, pstart, pend = gr.windows(dt.date(2026, 8, 17))
        self.assertEqual((end - start).days, (pend - pstart).days)
        self.assertEqual((end - start).days + 1, gr.WINDOW_DAYS)


class TestDeltas(unittest.TestCase):
    def test_position_delta_is_positive_when_rank_improves(self):
        cur = gr.index_rows([row("/a/", 5, 100, 6.0)])
        pre = gr.index_rows([row("/a/", 3, 90, 11.0)])
        d = gr.deltas(cur, pre)[0]
        self.assertEqual(d["position_delta"], 5.0)
        self.assertEqual(d["clicks_delta"], 2)
        self.assertEqual(d["impressions_delta"], 10)

    def test_position_delta_is_negative_when_rank_worsens(self):
        cur = gr.index_rows([row("/a/", 0, 50, 20.0)])
        pre = gr.index_rows([row("/a/", 0, 90, 12.0)])
        self.assertEqual(gr.deltas(cur, pre)[0]["position_delta"], -8.0)

    def test_thin_prior_window_is_not_comparable(self):
        cur = gr.index_rows([row("/a/", 0, 40, 8.0)])
        pre = gr.index_rows([row("/a/", 0, 1, 30.0)])
        d = gr.deltas(cur, pre)[0]
        self.assertFalse(d["comparable"])
        self.assertIsNone(d["position_delta"])

    def test_new_and_gone_are_labelled(self):
        cur = gr.index_rows([row("/new/", 0, 10, 9.0)])
        pre = gr.index_rows([row("/gone/", 0, 10, 9.0)])
        got = {d["key"]: d["status"] for d in gr.deltas(cur, pre)}
        self.assertEqual(got, {"/new/": "new", "/gone/": "gone"})

    def test_flagged_moves_uses_a_strict_threshold(self):
        cur = gr.index_rows([row("/a/", 0, 50, 5.0), row("/b/", 0, 50, 8.0)])
        pre = gr.index_rows([row("/a/", 0, 50, 9.0), row("/b/", 0, 50, 11.0)])
        moved = {m["key"] for m in gr.flagged_moves(cur and gr.deltas(cur, pre))}
        self.assertEqual(moved, {"/a/"})  # 4.0 flagged, exactly 3.0 not


class TestDecay(unittest.TestCase):
    def test_impression_loss_is_decay(self):
        cur = gr.index_rows([row("/a/", 0, 20, 9.0)])
        pre = gr.index_rows([row("/a/", 0, 80, 9.0)])
        self.assertEqual(len(gr.decaying(gr.deltas(cur, pre))), 1)

    def test_position_loss_alone_is_decay(self):
        cur = gr.index_rows([row("/a/", 0, 80, 18.0)])
        pre = gr.index_rows([row("/a/", 0, 80, 9.0)])
        self.assertEqual(len(gr.decaying(gr.deltas(cur, pre))), 1)

    def test_growth_is_not_decay(self):
        cur = gr.index_rows([row("/a/", 2, 120, 6.0)])
        pre = gr.index_rows([row("/a/", 0, 80, 9.0)])
        self.assertEqual(gr.decaying(gr.deltas(cur, pre)), [])

    def test_noise_below_the_prior_floor_is_ignored(self):
        cur = gr.index_rows([row("/a/", 0, 0, 30.0)])
        pre = gr.index_rows([row("/a/", 0, 2, 9.0)])
        self.assertEqual(gr.decaying(gr.deltas(cur, pre)), [])


class TestClusterMapping(unittest.TestCase):
    SLUGS = {"the-taxonomy-of-ai-agents": "ai-engineering",
             "api-documentation-template": "technical-documentation"}

    def test_post_maps_through_frontmatter_category(self):
        self.assertEqual(
            gr.page_cluster("https://ninadpathak.com/articles/the-taxonomy-of-ai-agents/",
                            self.SLUGS), "ai-engineering")

    def test_owner_page_maps_to_its_own_cluster(self):
        self.assertEqual(
            gr.page_cluster("https://ninadpathak.com/articles/reddit-marketing/", self.SLUGS),
            "reddit-marketing")

    def test_shipped_tools_belong_to_cluster_four(self):
        for path in ("/linter/", "/llms-txt-generator/"):
            self.assertEqual(
                gr.page_cluster(f"https://ninadpathak.com{path}", self.SLUGS),
                "ai-search-optimization")

    def test_missing_trailing_slash_still_matches(self):
        self.assertEqual(
            gr.page_cluster("https://ninadpathak.com/articles/reddit-marketing", self.SLUGS),
            "reddit-marketing")

    def test_pages_outside_any_cluster_return_none(self):
        for url in ("https://ninadpathak.com/",
                    "https://ninadpathak.com/about/",
                    "https://ninadpathak.com/articles/unknown-slug/",
                    "https://ninadpathak.com/work/kiwisizing/",
                    "https://ninadpathak.com/glossary/late-chunking/"):
            self.assertIsNone(gr.page_cluster(url, self.SLUGS))

    def test_legacy_blog_path_maps_to_the_same_cluster(self):
        """Search Console still reports most traffic under the pre-migration path."""
        canonical = "https://ninadpathak.com/articles/the-taxonomy-of-ai-agents/"
        legacy = "https://ninadpathak.com/blog/the-taxonomy-of-ai-agents/"
        self.assertEqual(gr.page_cluster(legacy, self.SLUGS),
                         gr.page_cluster(canonical, self.SLUGS))
        self.assertEqual(gr.page_cluster(legacy, self.SLUGS), "ai-engineering")

    def test_post_slug_reads_both_prefixes(self):
        self.assertEqual(gr.post_slug("https://ninadpathak.com/blog/kv-cache-eviction/"),
                         "kv-cache-eviction")
        self.assertEqual(gr.post_slug("https://ninadpathak.com/articles/kv-cache-eviction"),
                         "kv-cache-eviction")
        self.assertIsNone(gr.post_slug("https://ninadpathak.com/work/kiwisizing/"))
        self.assertIsNone(gr.post_slug("https://ninadpathak.com/blog/deep/nested/"))


class TestPathSplit(unittest.TestCase):
    def test_canonical_and_legacy_are_counted_apart(self):
        rows = [row("https://ninadpathak.com/articles/a/", 0, 86, 9.0),
                row("https://ninadpathak.com/blog/a/", 0, 1259, 8.0),
                row("https://ninadpathak.com/about/", 0, 66, 8.7)]
        self.assertEqual(gr.path_split(rows),
                         {"canonical": 86, "legacy": 1259, "other": 66})

    def test_no_legacy_traffic_reports_zero(self):
        rows = [row("https://ninadpathak.com/articles/a/", 0, 10, 9.0)]
        self.assertEqual(gr.path_split(rows)["legacy"], 0)


class TestClusterRollup(unittest.TestCase):
    SLUGS = {"a": "ai-engineering", "b": "ai-engineering", "c": "technical-documentation"}

    def test_all_seven_clusters_always_appear(self):
        got = gr.cluster_rollup([], self.SLUGS)
        self.assertEqual([c["cluster"] for c in got], [1, 2, 3, 4, 5, 6, 7])

    def test_empty_cluster_reports_zero_not_absent(self):
        got = {c["cluster"]: c for c in gr.cluster_rollup([], self.SLUGS)}
        self.assertEqual(got[5]["impressions"], 0)
        self.assertIsNone(got[5]["position"])

    def test_position_is_impression_weighted(self):
        rows = [row("https://ninadpathak.com/articles/a/", 0, 90, 10.0),
                row("https://ninadpathak.com/articles/b/", 0, 10, 20.0)]
        got = {c["cluster"]: c for c in gr.cluster_rollup(rows, self.SLUGS)}
        self.assertEqual(got[3]["impressions"], 100)
        self.assertEqual(got[3]["position"], 11.0)  # not the 15.0 a plain mean would give

    def test_unclustered_pages_are_reported_separately(self):
        rows = [row("https://ninadpathak.com/", 1, 50, 4.0)]
        got = gr.cluster_rollup(rows, self.SLUGS)
        tail = got[-1]
        self.assertIsNone(tail["cluster"])
        self.assertEqual(tail["impressions"], 50)

    def test_clicks_and_impressions_are_conserved(self):
        rows = [row("https://ninadpathak.com/articles/a/", 3, 90, 10.0),
                row("https://ninadpathak.com/articles/c/", 1, 10, 5.0),
                row("https://ninadpathak.com/about/", 2, 7, 8.0)]
        got = gr.cluster_rollup(rows, self.SLUGS)
        self.assertEqual(sum(c["clicks"] for c in got), 6)
        self.assertEqual(sum(c["impressions"] for c in got), 107)


if __name__ == "__main__":
    unittest.main()
