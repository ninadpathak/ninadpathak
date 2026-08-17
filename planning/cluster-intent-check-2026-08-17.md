# Intent check on clusters 5 and 6, and what it does to the reweight

**Date:** 2026-08-17 · **Trigger:** writing briefs against the reweighted queue
**Status:** the reweight's Reddit and community allocation is wrong and is being corrected

## What happened

The reweight gave Reddit marketing 11 rows and forums/community 10, on the strength of
`planning/addressable-universe.md`: 33,360/mo at 87% KD≤20 for Reddit, 24,140/mo at 76% for
community. Both were labelled floors because the pull hit the 250-row API cap.

Before writing eleven briefs I checked what those keywords actually are. They do not survive
intent inspection.

## Reddit marketing

`phrase_related` on "reddit marketing", US, volume >100:

| Keyword | Volume |
|---|---:|
| readvertising | 4,400 |
| buy reddit account | 3,600 |
| buy old facebook account reddit | 880 |
| how to get a marketing job reddit | 880 |
| metareddit | 720 |
| reddit ad library | 320 |
| reddit agency | 210 |

Account-buying, ad-platform navigation, job queries, and one term that is not English. None of it
is "how a developer product earns attention on Reddit".

`phrase_fullsearch` on "promote on reddit" is where the actual content intent lives, and it is
tiny:

| Keyword | Volume |
|---|---:|
| how to promote onlyfans on reddit | 90 |
| how to promote on reddit | 40 |
| **how to promote on reddit without getting banned** | **20** |
| everything else | 20 each |

The long tail is OnlyFans, music, YouTube, and NFT promotion. The developer-relevant slice is
roughly 100/mo in total, and **queue row 20's exact target is a 20/mo keyword.**

## Forums and community building

`phrase_fullsearch` on "developer community" returns municipal housing policy:

| Keyword | Volume |
|---|---:|
| community development block grant | 5,400 |
| community development council | 4,400 |
| department of housing and community development | 2,400 |
| action for boston community development | 1,900 |

The analytics pass already stripped 59% of this cluster as HOA and property management. What
survived at the head is the same contamination under a different phrase. The token "community"
matches an entire unrelated public-sector market.

## Why the cluster numbers looked fine

Ahrefs `terms` mode matches token presence, not meaning, which the analytics doc says plainly.
Cleaning removed obvious consumer navigation. It could not remove the structural problem: for
clusters 5 and 6 the *head* of the keyword space belongs to another market, so a volume total and
a KD≤20 share can both be accurate and still describe demand this site cannot serve.

The 87% and 76% winnability figures are real and misleading together. Those keywords are easy to
rank for because they are not contested by anyone in this niche, and they are not contested
because they are not this niche.

## The correction

**Reddit marketing drops from 11 rows to 4. Forums and community drops from 10 to 5.**
Twelve rows return to clusters with verified intent-level demand: Documentation and AI
engineering, where the parent-topic data was checked keyword by keyword in the earlier pass.

What stays in Reddit and community is the part that is genuinely his and genuinely searched:
posting rules, subreddit selection, what gets upvoted, and turning support questions into
documentation. Those remain Experience A and remain worth publishing. They are distribution
practice with a real reader, not a volume play, and the calendar should stop pretending otherwise.

**Cluster 7, events, is not yet re-checked.** Its 33,000/mo carries the same 250-row cap and the
same token-matching risk, and "events" is a word with an enormous unrelated market. Treat its 11
rows as provisional until the same probe is run.

## What this says about the method

Cluster-level volume times winnability was the wrong instrument for deciding a calendar. It is
right for sizing a niche and wrong for choosing ninety articles, because it averages over an
intent distribution that can be almost entirely foreign to the site.

Parent topic is the check that catches this, and it is per keyword rather than per cluster. The
earlier documentation and AI passes used it, which is why those allocations survived contact with
the briefs and these two did not. Any future reweight resolves parent topic before it moves a row.
