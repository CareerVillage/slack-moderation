# Contributing to Slack-Moderation

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

Please feel free to propose changes to this document in a pull request.

#### Table Of Contents 

[Community Guidelines](#community-guidelines)

[How Can I Contribute?](#how-can-i-contribute)
  * [Understand our priorities](#understand-our-priorities)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)
  * [License of your Contributions](#license-of-your-contributions)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [Django Styleguide](#django-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)


## Community Guidelines

This project and everyone participating in it is governed by the [CareerVillage Community Guidelines linked at the bottom of CareerVillage.org](https://www.careervillage.org/). By participating, you are expected to uphold this code. Please report unacceptable behavior to [hello@careervillage.org](mailto:hello@careervillage.org).

## How Can I Contribute?

### Understand our priorities

We value:
  * **High uptime and service reliability**. Moderation is core infrastructure. When it breaks, the community is at risk. When in doubt, err on the safe side. 
  * **Maintainer time**. We make our code explicit, make our code commments verbose, and try not to do things that will make the service hard to maintain. 
  * **Low-DevOps services**. We minimize the number of dependencies and try to keep our infrastructure and deployment simple. 

### Reporting Bugs

This section guides you through submitting a bug report for Slack-Moderation. Following these guidelines helps maintainers and the community understand your report :pencil:, reproduce the behavior :computer: :computer:, and find related reports :mag_right:.

Before creating bug reports, please check this list as you might find out that you don't need to create one:
* **Check the [discussions](https://github.com/CareerVillage/slack-moderation/discussions)** to see if others have the same common questions and problems.
* **Perform a [cursory search](https://github.com/CareerVillage/slack-moderation/issues?q=is%3Aissue+search+term+here)** to see if the problem has already been reported. If it has **and the issue is still open**, add a comment to the existing issue instead of opening a new one.

> **Note:** If you find a **Closed** issue that seems like it is the same thing that you're experiencing, open a new issue and include a link to the original issue in the body of your new one.


#### How Do I Submit A (Good) Bug Report?

Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue in our repository and provide the following information:

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem. Put `BUG:` at the start of the issue title.
* **Describe the exact steps which reproduce the problem** in as many details as possible. When listing steps, **don't just say what you did, but explain how you did it**. For example, if you clicked on an element in a UI, explain if you used the mouse, or a keyboard shortcut, and if so which one?
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Can you reproduce the problem?**
* **Did the problem start happening recently** (e.g. after updating to a new version) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version?** What's the most recent version in which the problem doesn't happen?
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.
* **Is the problem related to a specific type of content?** for example it might only occur when the underlying content being moderated meets certain conditions.

Include details about your configuration and environment:

* **Which version of slack-moderation are you using?** You can provide the git hash. 
* **What's the name and version of the OS you're using**?
* **What's the name and version of the Slack app you're using**?

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for slack-moderation, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion :pencil: and find related suggestions :mag_right:.
Before creating enhancement suggestions, please provide as much detail as you can. 

Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on this repository and provide the following information:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Include screenshots and animated GIFs** which help you demonstrate the steps or point out the part of the service which the suggestion is related to. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **Explain why this enhancement would be useful**, and to whom the benefit would accrue. 
* **List any other examples of applications where this enhancement exists, if applicable.**

### Your First Code Contribution

#### Local development

Follow the installation instructions on the README

### Pull Requests

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in [the template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)

### License of your Contributions

We've released this code under the MIT License. If you make a contribution, you are licensing your contribution for public use under the terms of [the MIT License](https://en.wikipedia.org/wiki/MIT_License).

## Styleguides

### Git Commit Messages

* Use the present tense ("Adds feature" not "Added feature")
* Use the declarative mood ("Moves cursor to..." not "Move cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when working on CI / CD
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

### Django Styleguide

* It's ok to use either function-based views or class-based views, but try to keep views "together" based on what they do
* Django models should be relatively "flat". Avoid extensive layering of model classes (avoid 2+ layers) or lots of Pseudo models.
* Django models should have docstrings and ideally column comments and descriptive help_text
* Avoid Django signals


### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Use lots of examples


## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests. 

[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in. We  encourage you to read about [other search filters](https://help.github.com/articles/searching-issues/) which will help you write more focused queries.

The labels are loosely grouped by their purpose, but it's not required that every issue has a label from every group or that an issue can't have more than one label from the same group.

#### Type of Issue and Issue State

| Label name | Description |
| --- | --- |
| `Help Wanted` | Community contributions are welcome on this issue. |
| `Core Team Only` | Only CareerVillage core team members should work on this issue (usually because it isn't feasible for community contributors to work on). |

