#!/usr/bin/env python3
"""Per-page attribution: does anything the campaign ships actually earn?

Every other Search Console tool here reports the site. This one reports individual
shipped pages against their own publish date, which is the only way to tell which lever
works while the sitewide numbers are all zero. A zero sitewide says nothing about whether
tools beat articles; that question is per-page and time-since-publish, not sitewide.

For each page published or substantially changed since TRACK_FROM, and for every tool
regardless of age:

    days to first impression
    days to first human impression
    days to first human click
    position trajectory since publish
    cluster

THE BET THIS IS BUILT TO TEST, AND WHAT IT CANNOT TEST
------------------------------------------------------
The campaign originally weighted tools over articles because the keyword research said no
build-a-tool keyword carried an AI Overview while all 15 top keywords did. Live SERP reads
later falsified that premise and tool building stopped at five. **That was a claim about
other people's SERPs, and this tool could never verify it.** Search Console has no AI
Overview dimension: there is no first-party way to see whether one appeared above our
result. Anything claiming otherwise would be invented.

What is measurable is the bet's downstream consequence. If tool pages are less exposed to
AI Overview click suppression, they should reach impressions sooner and convert
impressions to clicks better than articles at comparable positions. Days-to-first-impression
is measurable now. The click comparison needs clicks, and the site has none, so that column
stays empty and says so.

HOW A MISSING NUMBER IS REPORTED
--------------------------------
Three states, never collapsed into a zero:

    no data yet     the page is younger than the Search Console lag, so absence of an
                    impression is not evidence of anything
    not yet, N days observable for N days and still no impression - this IS a measurement
    a number        days from publish to the first impression

A zero would read as "it happened on day zero", which is the opposite of "we cannot know".

    tools/gsc_attribution.py              # upsert today's planning/attribution.md section
    tools/gsc_attribution.py --dry-run
    tools/gsc_attribution.py --track-from 2026-08-01
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gsc_report as gr  # noqa: E402
import report_log as rl  # noqa: E402

LOG = gr.ROOT / "planning" / "attribution.md"
TRACK_FROM = dt.date(2026, 8, 14)
# A commit touching a post by at least this many lines counts as a republish for
# attribution: a reader-visible rewrite resets what Google is being asked to rank.
SUBSTANTIAL_LINES = 30
# A page needs at least this many observable days before its lifetime performance says
# anything. Below it, silence is just youth.
AGED_DAYS = 30
# Median days-to-first-impression within this many days of each other is one figure, not
# two. Guards against reading a 2-day gap on a sample of one as a finding.
INDISTINGUISHABLE_DAYS = 7
BASE = "https://ninadpathak.com"

# The tools are tracked regardless of age because they are the priority lever and the
# whole calendar weighting rests on them. Template path -> live URL.
TOOLS = {
    "templates/linter.html": "/linter/",
    "templates/llms_txt_generator.html": "/llms-txt-generator/",
    "templates/llms_txt_validator.html": "/llms-txt-validator/",
    "templates/ai_overviews_checker.html": "/ai-overviews-checker/",
    "templates/ai_crawler_checker.html": "/ai-crawler-checker/",
}
