# Github notes

## Create a new branch, then merge back into main
1. Create a new branch from main: `git checkout -b newbranch`
2. Work on new branch until done, then merge: `git checkout master && git merge newbranch`

## Pushing upstream to Allen-Synthesis (if differences are required in your repo)
1. Commit and push all required changes to main
2. Create and switch to a new upstream branch: `git checkout -b europi-upstream`
3. Remove any files that should not be pushed upstream
4. Commit and push changes: `git add * && git commit -m 'update message' && git push --set-upstream origin europi-upstream`
5. Create a pull request from europi-upstream to Allen-Synthesis/EuroPi


