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
description: SigNoz argues that AI is deskilling SREs. I think the risk is real for juniors, the evidence is borrowed, and the fix it leaves out is making the agent write down what it did.
slug: agents-on-call-runbooks
status: published
title: "I read SigNoz's post on AI deskilling SREs and thought about runbooks"
work_note: "I'm Ninad Pathak, a freelance technical writer for developer-tool companies. Runbooks and incident write-ups only help if someone ran the steps, and I run every step before I write it down. [Hire me for your docs](/services/)."
---

Elizabeth at SigNoz asked a question in [a newsletter post](https://newsletter.signoz.io/p/ai-isnt-replacing-sres-its-deskilling) that reached the front page of Hacker News on October 30: "When AI handles 95% of your incident response, do you get worse at handling the 5% that actually matters?" The post is dated February 28, and the question has aged well.

I think the worry is right, and I think the post's list of fixes leaves out the one I know best. Nobody in the post asks the agent to write anything down.

I read it as a post about [technical documentation](/articles/technical-documentation/) as much as about being on call.

## What I think the post gets right

Elizabeth's frame is a 1983 paper, Lisanne Bainbridge's [Ironies of Automation](https://en.wikipedia.org/wiki/Ironies_of_Automation). The argument is that automating the routine work leaves a person in charge of the rare failure, and gives them less practice for it every year.

The post maps that onto incident response with a tier model it credits to PagerDuty. Known issues with known fixes go to the agent, partly understood ones get a recommendation a person approves, and the novel outages stay with people.

And then it asks where those people get the intuition for the novel ones, if they never touch the others. I think that's the right question, and it's sharpest for juniors, who the post says may never build the skill at all.

SigNoz makes an observability platform, and the post ends on what its own product will do about all this, which I don't hold against the argument.

## Where the post is weaker

The evidence is borrowed. The examples of skill loss come from doctors and from airline pilots, and the post has no numbers from a team of SREs.

For this trade it's a prediction. A reasonable one, I think, but nobody has measured it yet.

And [a reply on Hacker News](https://news.ycombinator.com/item?id=50306058) made a point I can't wave away. The commenter had a job where only escalations reached them and still debugged whole-system problems without trouble, because they worked on the whole system every day.

That matters. If intuition comes from working on a system and incidents are one part of that work, then taking the routine incidents away costs less than the post assumes.

## Make the agent write it down

The post's two remedies are both about practice. Hand some incidents to people even when the agent could take them, the way pilots are made to fly by hand, and keep people working on a problem with the agent instead of approving its answer.

My addition is a third, and it's cheaper than either. Every incident an agent closes should leave a short account that a person reads: what fired, what the agent checked, what it changed and what it saw afterwards.

Why would that help? Because a write-up is how an incident teaches the people who weren't in it, which is the whole reason teams write postmortems.

Reading is weaker practice than doing, and I won't pretend otherwise. But it costs minutes, and it means the routine incidents still pass in front of someone.

There's a second reason I care about the account. My [runbook template](/articles/runbook-template/) reports a test with a coding agent as the responder on one Postgres incident, where a prose runbook led it to cancel five legitimate report queries in all but one of four runs.

Each of those runs looked like a resolved incident from the outside. Only the record of what the agent did showed that it had cleared the wrong sessions.

So the account isn't only training material. It's how you find out that the agent's 95% includes some incidents it closed badly, which is the concern of [my page on why AI agents fail](/articles/ai-agent-failures/).

## The runbook is still for people

If you take the first remedy and give people some incidents on purpose, they need something to practise from. That's the runbook, and it has to work for a person who hasn't done this in months.

So each step should say what you'll see when it works and what to do when you don't. An agent can follow a runbook written that way, and so can a rusty human, which a list of bare commands doesn't allow.

Keep the agent's accounts where the team keeps its other incident notes. They're internal documents with candid detail, and [internal and external documentation](/articles/internal-vs-external-docs/) split along exactly that line.

A caution from the other direction. Every account is another thing asking for someone's attention, and [my essay on a build that is always red](/articles/red-build-nobody-reads/) is about what happens when those requests outrun the people.

Keep it short, and test it this way. Take an incident an agent resolved last month and hand its record to someone who wasn't on call.

If they can say what happened and why the fix was right, the team is still learning from its routine incidents. If there's no record to hand over, the deskilling has a head start whether or not anyone's skills have slipped yet.
