# Github notes

## Create a new branch, then merge back into main
1. Create a new branch from main: `git checkout -b newbranch`
2. Work on new branch until done, then merge: `git checkout master && git merge newbranch`

## Creating a new upstream branch
1. `git checkout -b europi-upstream`
2. `git push --set-upstream origin europi-upstream`
3. Pull in latest from allen-synthesis main: in github.com switch to the europi-upstream branch and fetch upstream

## Pushing to upstream
1. Pull in latest from allen-synthesis main: in github.com switch to the europi-upstream branch 
and fetch upstream
2. Switch to the branch: `git checkout -b europi-upstream`
3. Copy in files from main branch to europi-upstream
4. Push to the branch `git push --set-upstream origin europi-upstream`
5. Create a pull request: in github.com switch to the europi-upstream branch and create pull request


