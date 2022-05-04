# Contributing to the EuroPi Repository

Contributing is welcomed and encouraged for anyone, from programming or synth experts to complete novices.  
This repo is a collection of resources, so if there are any resources that you have created yourself, or found online 
that you think others would benefit from, then please consider submitting them here!

Contributions are made via a GitHub Pull Request (PR). The rest of this document covers that process as well as the responsibilities of the PR participants. It is expected that PR authors become familiar with the process described here
before submitting their first PR.

## Contents
1. [Overview]()
1. [Responsibilities of PR Participants]()
    1. [Responsibilities of the PR author]()
    2. [Responsibilities of the PR reviewer]()
2. [Working with Git](#working-with-git)
3. [PR guidelines and requirements]()
   1. [General]()
   2. [Documentation]()
   3. [Contrib scripts]()
      1. Code conventions 
   4. [Firmware]()

4. [What to expect during the PR process]()


## Overview

A PR is simply a set of changes that the author would like to be added to a repository. In the EuroPi repository, the 
most common example would be a new script in the contrib directory. The PR process allows the maintainers of the 
repository manage the contributions in a consistent way, and provides a means for non-maintainers to add changes to the repository.

The PR process consists of a few steps. First, the author makes their desired changes on a branch in their own fork of 
the main EuroPi repository. Second, the author opens a PR, submitting the changes for review. Next, the reviewers and 
author work together to ensure that the changes are appropriate for the repository. Finally, the changes are merged into
the main repository. The details of this process are described below.

If you need any help with any stage of this process (or anything else), please don't hesitate to ask questions in the 
[Discord Server](https://discord.gg/2eFyqP2rSs), [Discussions page](https://github.com/Allen-Synthesis/EuroPi/discussions), 
or email Rory directly at [contact@allensynthesis.co.uk](mailto:contact@allensynthesis.co.uk).


## Responsibilities of PR Participants

It is expected that everyone participating in the PR process acts in a friendly, supportive, and respectful manner. 
Always assume that participants are acting in good faith, towards the common goal of improving the EuroPi project.

### Responsibilities of the PR author

It is the responsibility of the PR author to follow the [guidelines]() outlined in this document. Additionally, the PR 
author should, to the best of their ability, provide a complete and well thought out PR that is ready to merge.

### Responsibilities of the PR reviewer

It is the responsibility of the PR reviewer(s) to guide the author through the review process. They should verify that 
the author understands their responsibilities as outlined here and what they need to do at each step of the process.

When commenting on a PR, the reviewer should make the intention of each comment clear. Specifically, is the reviewer 
requesting a change, and is that change required for PR approval. This is done by prefixing each comment with one of the
following labels **\[required\]**, **\[optional\]**, **\[question\]**, **\[discussion\]**. A more detailed discussion of these labels can be found [below](#comment-labels).

It is the responsibility of the PR reviewer(s) to reasonably understand the change that they are reviewing, as they are responsible for ensuring that the proposed change has a positive impact on the project and 
aligns with the project's goals. On the surface, this is done by enforcing the PR guidelines and steering the author 
towards best practices. At a deeper level, the reviewer must also consider the impact of the PR in the scope of the 
larger EuroPi project. This is particularly important on changes that impact the EuroPi libraries or documentation.

Finally, the reviewer should not impose any undue requirements on the author. The reviewer should not require that the 
author make changes to portions of the repository that are unrelated to their code. If a change uncovers an issue in 
the underlying project it is not the authors responsibility to fix it. Though the author should understand that the
merging of their PR may be contingent on such a fix being completed.


## Working with Git

Working with Git itself is outside the scope of this document, but if you are new to git there are plenty of resources
available to help you:

  * [GitHub's own docs:](https://docs.github.com)
    * [Working with Forks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks)
    * [Proposing Changes](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests)
  * [How To: Fork a GitHub Repository & Submit a Pull Request](https://jarv.is/notes/how-to-pull-request-fork-github/)


When making changes that you intend to contribute to the EuroPi project it's important to make use of git's ``branch``
feature. While it is possible to make changes on the ``main`` branch of your fork and submit a PR from there, you will
have a much nicer experience if you use a separate branch for each of your PRs. Working with branches means that you can 
switch between multiple efforts easily. This will be useful for working on a second change while the first makes its way 
through this PR process. In addition, working on branches will allow your fork's ``main`` to diverge from EuroPi's if 
you'd like.

## What to expect during the PR process
A PR will typically progress through the following steps:
    
  1. PR opened by author
  2. Reviewers add comments in the form of questions, discussion points, suggestions and required changes.
  3. PR participants discuss the comments
  4. The author makes requested changes
  5. Repeat steps 2 - 4 until reviewers approve the PR
  6. PR is merged into the main branch

A comment left by a reviewer, even a **\[required\]** change, is not meant to be final, it is meant to be the beginning
of a discussion. It is perfectly reasonable for a reviewer to require a change, only to have a discussion with the author
that clarifies their understanding and then changes their opinion.

Comments or reviews on Pull Requests are *never* intended to be negative, however if you are unused to the matter of 
fact way that Git reviews are completed it may seem that way. If you believe someone is being genuinely antagonistic,
please contact the Rory [via email](mailto:contact@allensynthesis.co.uk) or [on Discord](https://discordapp.com/users/roryjamesallen#6370).

The PR process is expected to take time, in the range of days to weeks. This repository is run mainly by volunteers, 
with other jobs and families, so a Pull Request may take some time before it's allowed to merge. This will just 
depend on what other things the maintainers have going on at any given time, please don't think anyone is ignoring your
contributions!

## Comment labels

  * **\[required\]** - The change requested in this comment is required for the reviewers approval. Typically this will be
based on the PR guidelines. If the request is not backed up by the PR guidelines, the reviewer should explain their reasoning.
  * **\[optional\]** - The change requested in this comment is a suggestion that the reviewer thinks will improve the 
PR, but is not required for approval. It can be completed at the author's discretion.
  * **\[question\]** - The reviewer is asking the author a question to better their understanding of the change. No 
change is requested, but it is likely that an answer to the question is required for the reviewer's understanding, and 
therefore approval.
  * **\[discussion\]** - The reviewer is starting a discussion on a topic related to the proposed change. The discussion
may later result in requesting changes to the PR, the opening of new issues, or opening new PRs at the participants
discretion.

## PR guidelines and requirements
  * PR Description requirements
### General

Please try to keep Pull Requests to as few a files as possible. For example: if you have made some spelling changes to a main file, and are also uploading a script to the contrib folder, please try to separate these into two different Pull Requests so that the workload for the maintainers is more manageable. Keeping each PR smaller will also mean that it will be merged much faster!

  * Respect existing organization
  * Spelling and grammar
### Documentation
  * Markdown must render properly on github
  * Api docs must build successfully
### Contrib scripts
  * User documentation
  * Menu participation requirements
### Firmware
  * Pep8 
  * Documentation
  * Testing requirements (automated or otherwise)

