# Contributing to the EuroPi Repository

Contributing is welcomed and encouraged for anyone, from programming or synth experts to complete novices. This repo is a collection of resources, so if there are any resources that you have created yourself, or found online that you think others would benefit from, then please consider submitting them here!

Contributions are made via a GitHub Pull Request (PR). The rest of this document covers that process as well as the responsibilities of the PR participants. It is expected that PR authors become familiar with the process described here before submitting their first PR.

# Contents
- [Contributing to the EuroPi Repository](#contributing-to-the-europi-repository)
- [Contents](#contents)
- [Overview](#overview)
- [Responsibilities of PR Participants](#responsibilities-of-pr-participants)
  - [Responsibilities of the PR author](#responsibilities-of-the-pr-author)
  - [Responsibilities of the PR reviewer](#responsibilities-of-the-pr-reviewer)
- [Working with Git](#working-with-git)
- [What to expect during the PR process](#what-to-expect-during-the-pr-process)
  - [Comment labels](#comment-labels)
- [PR guidelines and requirements](#pr-guidelines-and-requirements)
  - [General](#general)
    - [Provide a detailed Description](#provide-a-detailed-description)
    - [Keep PRs cohesive and focused](#keep-prs-cohesive-and-focused)
    - [Respect existing organization](#respect-existing-organization)
    - [Spelling and grammar](#spelling-and-grammar)
  - [Documentation](#documentation)
    - [Markdown must render properly on github](#markdown-must-render-properly-on-github)
    - [Api docs must build successfully](#api-docs-must-build-successfully)
  - [Contrib scripts](#contrib-scripts)
    - [Submission Format](#submission-format)
    - [File Naming](#file-naming)
    - [Menu Inclusion](#menu-inclusion)
  - [Firmware](#firmware)
    - [Code Style Requirements](#code-style-requirements)
    - [Documentation](#documentation-1)
    - [Testing](#testing)



# Overview

A PR is simply a set of changes that the author would like to be added to a repository. In the EuroPi repository, the most common example would be a new script in the contrib directory. The PR process allows the maintainers of the repository manage the contributions in a consistent way, and provides a means for non-maintainers to add changes to the repository.

The PR process consists of a few steps. First, the author makes their desired changes on a branch in their own fork of the main EuroPi repository. Second, the author opens a PR, submitting the changes for review. Next, the reviewers and author work together to ensure that the changes are appropriate for the repository. Finally, the changes are merged into the main repository. The details of this process are described below.

If you need any help with any stage of this process (or anything else), please don't hesitate to ask questions in the [Discord Server](https://discord.gg/2eFyqP2rSs), [Discussions page](https://github.com/Allen-Synthesis/EuroPi/discussions), or email Rory directly at [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.co.uk).


# Responsibilities of PR Participants

It is expected that everyone participating in the PR process acts in a friendly, supportive, and respectful manner. Always assume that the other participants are acting in good faith, towards the common goal of improving the EuroPi project.

## Responsibilities of the PR author

It is the responsibility of the PR author to follow the [guidelines](#pr-guidelines-and-requirements) outlined in this document. Additionally, the PR author should, to the best of their ability, provide a complete and well thought out PR that is ready to merge.

## Responsibilities of the PR reviewer

It is the responsibility of the PR reviewer(s) to guide the author through the review process. They should verify that the author understands their responsibilities as outlined here and what they need to do at each step of the process.

When commenting on a PR, the reviewer should make the intention of each comment clear. Specifically, is the reviewer requesting a change, and is that change required for PR approval. This is done by prefixing each comment with one of the following labels **\[required\]**, **\[optional\]**, **\[question\]**, **\[discussion\]**. A more detailed discussion of these labels can be found [below](#comment-labels). In the absence of an explicit label, consider the comment to be discussion, not a directive.

It is the responsibility of the PR reviewer(s) to reasonably understand the change that they are reviewing, as they are responsible for ensuring that the proposed change has a positive impact on the project and aligns with the project's goals. On the surface, this is done by enforcing the PR guidelines and steering the author towards best practices. At a deeper level, the reviewer must also consider the impact of the PR in the scope of the larger EuroPi project. This is particularly important on changes that impact the EuroPi libraries or documentation.

Finally, the reviewer should not impose any undue requirements on the author. The reviewer should not require that the author make changes to portions of the repository that are unrelated to their code. If a change uncovers an issue in the underlying project, it is not the authors responsibility to fix it. Though the author should understand that the merging of their PR may be contingent on such a fix being completed.


# Working with Git

Working with Git itself is outside the scope of this document, but if you are new to git there are plenty of resources available to help you:

  * [EuroPi's git_help](/git_help.md)
  * [GitHub's own docs:](https://docs.github.com)
    * [Working with Forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks)
    * [Proposing Changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests)
  * [How To: Fork a GitHub Repository & Submit a Pull Request](https://jarv.is/notes/how-to-pull-request-fork-github/)


When making changes that you intend to contribute to the EuroPi project it's important to make use of git's ``branch`` feature. While it is possible to make changes on the ``main`` branch of your fork and submit a PR from there, you will have a much nicer experience if you use a separate branch for each of your PRs. Working with branches means that you can switch between multiple efforts easily. This will be useful for working on a second change while the first makes its way through this PR process. In addition, working on branches will allow your fork's ``main`` to either remain in sync with or diverge from EuroPi's `main` as your needs change.

# What to expect during the PR process
A PR will typically progress through the following steps:
    
  1. PR opened by author
  2. Reviewers add comments in the form of questions, discussion points, suggestions, and required changes.
  3. PR participants discuss the comments
  4. The author makes any requested changes
  5. Repeat steps 2 - 4 until reviewers approve the PR
  6. PR is merged into the main branch

A comment left by a reviewer, even a **\[required\]** change, is not meant to be final, it is meant to be the beginning of a discussion. It is perfectly reasonable for a reviewer to require a change, only to have a discussion with the author that clarifies their understanding and then changes their opinion.

Comments or reviews on Pull Requests are *never* intended to be negative, however if you are not used to the matter of fact way that Git reviews are completed it may seem that way. If you believe someone is being genuinely antagonistic, please contact the Rory [via email](mailto:contact@allensynthesis.co.uk) or [on Discord](https://discordapp.com/users/roryjamesallen#6370).

The PR process is expected to take time, in the range of days to weeks. This repository is run mainly by volunteers, with other jobs and families, so a Pull Request may take some time before it's allowed to merge. This will just depend on what other things the maintainers have going on at any given time, please don't think anyone is ignoring your contributions!

## Comment labels

These labels prefix each of the reviewer's comments in order to indicate their intention. 

| Label |   |
| ----- | - |
| **\[required\]** | The change requested in this comment is required for the reviewers approval. Typically this will be based on the PR guidelines. If the request is not backed up by the PR guidelines, the reviewer should explain their reasoning. |
| **\[optional\]** | The change requested in this comment is a suggestion that the reviewer thinks will improve the PR, but is not required for approval. It can be completed at the author's discretion. |
| **\[question\]** | The reviewer is asking the author a question to better their understanding of the change. No change is requested, but it is likely that an answer to the question is required for the reviewer's understanding, and therefore approval. |
| **\[discussion\]** | The reviewer is starting a discussion on a topic related to the proposed change. The discussion may later result in requesting changes to the PR, the opening of new issues, or opening new PRs at the participants discretion. |

# PR guidelines and requirements

This section outlines the guidelines and requirements that a successful PR must follow.

## General

### Provide a detailed Description

When opening a PR you will have the opportunity to provide a description. This description introduces your changes to the reviewers, provides any necessary context, and is a place for you to describe your motivation. The PR itself shows _what_ is being changed, the description is the _why_. In many cases the description will be relatively simple. For example: "This PR adds a new Harmonic LFO script to the contrib directory" or "This PR updates the documentation for several library functions to make their use more clear." In the case of a more complex change a more detailed description will be necessary.

### Keep PRs cohesive and focused
Please try to keep Pull Requests to as few changes as possible. For example: if you have made some spelling changes to this markdown file, and are also uploading a script to the contrib folder, please try to separate these into two different Pull Requests so that the workload for the maintainers is more manageable. Keeping each PR small will also mean that each can be worked on and merged independently, resulting in faster approvals.

### Respect existing organization

When adding new files to the project, follow the existing organizational structure as summarized here:

| Directory | Purpose |
| ----------| ------- |
| `docs` | Files related to the [API doc site](https://allen-synthesis.github.io/EuroPi/) |
| `hardware` | Files related to the EuroPi's hardware |
| `scripts` | Scripts that are useful during development. |
| `software` | Files related to the EuroPi's software |
| `software/contrib` | User contributed scripts that run on the EuroPi |
| `software/firmware` | Files that make up the EuroPi firmware (API) |
| `software/tests` | Automated tests for both the firmware and contrib scripts. |


### Spelling and grammar

It is expected that any prose is written clearly and follows English grammar rules. British English spelling is favoured.

## Documentation

PRs that make changes to documentation, that is `*.md` files or anything in the [docs](/docs) directory must meet the following requirements.

### Markdown must render properly on github

The markdown must use [github's markdown style](https://docs.github.com/en/get-started/writing-on-github) and render properly when viewing the project on [github.com/Allen-Synthesis](https://github.com/Allen-Synthesis)
  
### Api docs must build successfully

The [API doc site](https://allen-synthesis.github.io/EuroPi/) must build successfully. See the [docs readme](/docs/README.md) for more details.

## Contrib scripts

PRs that add or make changes to scripts in the [contrib](/software/contrib/) directory must meet the following requirements.

### Submission Format

Please include:
- Your name (or username) and the date you uploaded the program (dd/mm/yy) as a comment at the top of the file
- Either a description as a comment at the top of the code itself if the program is very simple/obvious, or as a file with the exact same name as the program but with the '.md' suffix. It's much preferred to always have an 'md' file rather than a comment, as it's a much nicer way to view the program's function and a place for you to explain how the inputs and outputs are used.
- The labels that apply to the program. You can come up with any labels, but some suggestions include:

    LFO, Quantiser, Random, CV Generation, CV Modulation, Sampling, Controller

Just write any labels that apply to your program, including any not listed here but that you think are relevant, in the 'md' file for your program. Think of this as the second most obvious way to see what your program does, after the title.

### File Naming

Please use all lowercase and separate words with underscores for your program names. If additional resources are needed, such as image files, a directory with the same name and suffixed with `docs` can be included. e.g. the files associated with a program for a Sample and Hold function would look as follows:  

```
software/contrib
├── sample_and_hold_docs
│   └── sample_and_hold.png
├── sample_and_hold.md
├── sample_and_hold.py
```

### Menu Inclusion

In order to be included in the menu a program needs to meet a few additional requirements. See [menu.md](/software/contrib/menu.md) for details. Programs are not required to participate in the menu in order to be accepted, but it is nice.



## Firmware

Changes to firmware code must adhere to more stringent requirements than other changes. Firmware changes have the potential to affect every contrib script that runs on the EuroPi as well as the behavior of the module itself. Any change must have a clear and well described purpose and be well tested against the suite of available contrib scripts.

### Code Style Requirements

There are currently no code style requirements for the firmware code, however we should favor python best practices such as [pep8](https://peps.python.org/pep-0008/) when possible.

### Documentation

Changes or additions to public API functions must include the corresponding updates to their documentation and render properly on the [API doc site](https://allen-synthesis.github.io/EuroPi/).

### Testing

All existing automated tests must pass. An effort should be made to improve the test suite by adding tests for new or changed functionality.
