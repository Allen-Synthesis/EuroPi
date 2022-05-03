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
author make changes to portions of they repository that are unrelated to their code. If a change uncovers an issue in 
the underlying project it is not the authors responsibility to fix it. Though the author should understand that the
merging of their PR may be contingent on such a fix being completed.


## Working with Git
  * Steps to create a PR (from original doc below) (consider third party docs)
  * add branch step (allows fork divergence)
  * add details on how to allow a fork to diverge

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

  * respect existing organization
  * spelling and grammar
### Documentation
  * Markdown must render properly on github
  * Api docs must build successfully
### Contrib scripts
  * user documentation
  * Menu participation requirements
### Firmware
  * pep8 
  * documentation
  * Testing requirements (automated or otherwise)

<br>
<hr>
Original doc is below. It should be incorporated into the above sections.
<hr>

This process is also what you would use to submit your scripts to the contrib folder; simply complete the steps below, and upload your script and description '.md' file to the contrib folder in your 'fork' in step 3 below.

### Steps to submit a new file or change existing files
1. Create a 'fork' of this repository on your own page by clicking the button that says 'Fork' in the top right, between 'Watch' and 'Starred'
2. Navigate to your new fork by going to your profile. It will be listed as your_username/EuroPi instead of Allen-Synthesis/EuroPi
3. Make the relevant changes to your own fork, either uploading files or changing existing ones
4. **IMPORTANT**: Please write informative descriptions for all commits you make to your own fork so that it is obvious what changes you are making and why
5. When you are happy with the changes you've made, click the tab in your own fork that says 'Pull Requests' and then click 'New Pull Request'
6. Check all of the changes shown below are correct, then click 'Create Pull Request'
7. Add a title and an overall description of the changes you are suggesting and/or the new files you've uploaded.  
This description should be informative but doesn't have to be too long if there are descriptions for each commit (as there should be)
8. Please make sure that the checkbox 'Allow edits and access to secrets by maintainers' is turned *on* so that any small changes, such as spelling or grammar, can be completed by any of the maintainers before merging
9. Any of the maintainers may request changes to the pull request.  
Please do not delete the request if this happens, simply make the changes to your branch, and the commits will show up.  
This is important as otherwise we cannot keep track of the changes that have been requested and completed.  
These changes will probably be basic and minimal, and are usually just to make sure that everything is ready before merging so that nothing will have to be changed later.  
Don't worry if it seems like there are a lot of changes requested, or if they seem a little harsh, every request gets the same treatment, even those of the maintainers!  
If you need any help fulfilling a change request, just add a comment and any one of the maintainers can help you out (this is why step 8 is important)
10. After any changes have been completed, your pull request will be merged, and you will see your changes/new files on the official repository
11. Pat yourself on the back for sharing your knowledge with the community!
  
  
