# slack-moderation
Forum-like applications that accept UGC (User-Generated Content) often require active moderation to ensure that content is appropriate. `slack-moderation` is a Django application that uses Slack channels as a moderation tool to review user-generated content. This application was created by CareerVillage.org to use in its slack-based moderation system. The focus is on using moderators to identify inappropriate content so that it can be dealt with appropriately (typically, that means it gets deleted).

## How important is `slack-moderation`?
The moderation service is _**essential**_ core infrastructure for CareerVillage.org. 

## What exactly does it do?
Turns a series of Slack channels into "queues", so that they can be used as kanban-style lists. When a piece of user generated content comes in, it is posted into a channel. When a moderator (any member of that Slack) reviews that content they can either approve or reject the content. If it gets approved, it goes into an "approved" channel (queue).  If it gets rejected, it goes into a "flagged" channel for an admin to review and resolve (when, it goes into yet another "resolved" channel). In this way, it allows a large number of people to use kanban-style queues from within Slack!

## Architecture
![image](https://user-images.githubusercontent.com/830219/135332946-26971bfc-f4b0-4280-835d-733077ba83af.png)

## Setup
Installation instructions are located in the wiki at https://github.com/CareerVillage/slack-moderation/wiki/Run-the-app-on-local-machine

## Is this actively maintained?
Yes. This is "don't fix what isn't broken" software. This application is used _**every**_ day by the CareerVillage.org team to moderate content. Because it "just works", and the Slack API hasn't changed enough to necessitate updates, we haven't needed to make changes very often to the codebase.
