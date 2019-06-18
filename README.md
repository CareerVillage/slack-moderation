# slack-moderation
A Django application that uses Slack channels as a moderation tool to review user-generated content. This application was created by CareerVillage.org to use in its slack-based moderation system. The focus is on using moderators to identify inappropriate content so that it can be dealt with appropriately (typically, that means it gets deleted).

## What exactly does it do?
Turns a series of Slack channels into "queues", so that they can be used as kanban-style lists. When a piece of user generated content comes in, it is posted into a channel. When a moderator (any member of that Slack) reviews that content they can either approve or reject the content. If it gets approved, it goes into an "approved" channel (queue).  If it gets rejected, it goes into a "flagged" channel for an admin to review and resolve (when, it goes into yet another "resolved" channel). In this way, it allows a large number of people to use kanban-style queues from within Slack!

## Actively maintained?
Sort of. Not really. This application is used every day by the CareerVillage.org team. Because it "just works", and the Slack API hasn't changed enough to necessitate updates, we haven't needed to make many changes to the codebase.
