---
category: technical-documentation
primary_query: none
siblings:
- runbook-template
- internal-vs-external-docs
bridges:
- slug: ai-agent-failures
  reason: That page covers the postmortem for an agent's own failures, the record this essay asks an on-call agent to leave.
- slug: red-build-nobody-reads
  reason: Both essays are about what agent-rate work does to the attention of the people on call.
date: 2026-11-17
description: SigNoz argues that AI is deskilling SREs. I think the risk is real for junior engineers, the post's evidence comes from doctors and pilots and not from SREs, and the fix it leaves out is making the on-call agent write down what it did.
slug: agents-on-call-runbooks
status: published
title: "I read SigNoz's post on AI deskilling SREs and thought about runbooks"
work_note: "I'm Ninad Pathak, a freelance technical writer for developer-tool companies. Runbooks and incident write-ups only help if someone ran the steps, and I run every step before I write it down. [Work with me on your docs](/services/)."
---

Elizabeth at SigNoz asked a question in [a newsletter post](https://newsletter.signoz.io/p/ai-isnt-replacing-sres-its-deskilling) that reached the front page of Hacker News on October 30: "When AI handles 95% of your incident response, do you get worse at handling the 5% that actually matters?" The post is dated February 28, and the thread on October 30 shows engineers were still arguing over the question eight months later.

I think Elizabeth's worry is right, and I think her list of fixes leaves out a cheap one: nobody in the post asks the agent to write down what it did during an incident.

A written account of an incident is [technical documentation](/articles/technical-documentation/), so I read her post as being about documentation as much as about being on call.

## What I think the post gets right

Elizabeth builds her argument on a 1983 paper, Lisanne Bainbridge's [Ironies of Automation](https://en.wikipedia.org/wiki/Ironies_of_Automation). Bainbridge argued that automating the routine work leaves a person in charge of the rare failure, and gives that person less practice at handling failures every year.

The post maps that onto incident response with a tier model it credits to PagerDuty. Known issues with known fixes go to the agent, partly understood ones get a recommendation a person approves, and the novel outages stay with people.

The post then asks where people get the intuition for novel outages if they never handle the known ones. I think that's the right question, and it matters above all for junior engineers, who the post says may never build the skill at all.

SigNoz makes an observability platform, and the post ends by describing what SigNoz's own product will do about deskilling. I don't hold the product pitch against the argument.

## Where the post is weaker

The post's evidence comes from other professions. Its examples of skill loss are doctors and airline pilots, and it has no numbers from a team of SREs.

For SREs, then, deskilling is a prediction. I think the prediction is reasonable, and nobody has measured it yet.

[A reply on Hacker News](https://news.ycombinator.com/item?id=50306058) also made a point against the post that I can't dismiss. The commenter had a job where only escalations reached them and still debugged whole-system problems without trouble, because they worked on the whole system every day.

The commenter's experience weakens the post's premise. If intuition comes from working on a system and incidents are one part of that work, then taking the routine incidents away costs less than the post assumes.

## Make the agent write it down

The post offers two remedies, and both are about practice. The first is to hand some incidents to people even when the agent could take them, the way pilots are made to fly by hand, and the second is to have people work on a problem alongside the agent instead of approving its answer.

I'd add a third remedy that costs less than either of those. Every incident an agent closes should leave a short account that a person reads: what fired, what the agent checked, what it changed and what it saw afterwards.

A written account helps because a write-up is how an incident teaches the people who weren't on call for it, which is the reason teams write postmortems.

Cloudflare's October report on a KV cache leak is a good model of the long form, and I've written up [what I'd copy from it](/articles/cloudflare-kv-cache-incident-report/).

Reading about an incident is weaker practice than resolving one, and I won't pretend otherwise. But reading a short account takes a few minutes, and it means a person still sees every routine incident the agent closed.

The account also catches mistakes, which is my second reason for wanting it. My [runbook template](/articles/runbook-template/) reports a test with a coding agent as the responder on one Postgres incident, where a prose runbook led it to cancel five legitimate report queries in all but one of four runs.

Each of those runs ended with the alert cleared, so each looked like a resolved incident. Only the record of what the agent did showed that it had cancelled the wrong queries.

So the account is also how you find out that some of the incidents in the agent's 95% were closed badly. Finding bad closes is the concern of [my page on why AI agents fail](/articles/ai-agent-failures/).

## The runbook is still for people

If you take the first remedy and give people some incidents on purpose, they need something to practise from. They practise from the runbook, and the runbook has to work for a person who hasn't handled that kind of incident in months.

So each step in the runbook should say what you'll see when the step works and what to do when you don't see it. An agent can follow a runbook written that way, and so can an engineer who is out of practice, and neither can do much with a bare list of commands.

Keep the agent's accounts where the team keeps its other incident notes. The accounts are internal documents with candid detail about what went wrong, and candid detail is the reason [internal and external documentation](/articles/internal-vs-external-docs/) are kept apart.

The accounts have a cost of their own. Every account is another document asking for someone's attention, and [my essay on a build that is always red](/articles/red-build-nobody-reads/) is about what happens when a team gets more of those requests than it can read.

So keep each account short, and test the practice this way. Take an incident an agent resolved last month and hand its record to someone who wasn't on call.

If that person can say what happened and why the fix was right, the team is still learning from its routine incidents. If there's no record to hand over, nobody outside the on-call shift can learn from that incident at all.
