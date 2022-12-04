# Workflows

This repository performs various jobs when actions are taken against this GIT repository. These jobs are documented below.

## Compile to uf2

When a new tag is pushed to the main repository, this workflow will freeze the EuroPi firmware, experimental, and contrib folders as a module in a clone of the MicroPython source. Then the source is compiled into a uf2 binary which includes the Menu script as a main entrypoint. This file is renamed to include the tag version and a release is created with that file attached.

See  [`software/create_custom_firmware_uf2.md`](/software/create_custom_firmware_uf2.md) for more details on the steps to create a custom uf2 firmware file.

## Continuous Integration

This is an encompassing workflow for the workflows that make up our continuous integration process. Currently it runs
[PyTest workflow](#pytest), and then, if that passed, runs the [Publish to PyPI workflow](#publish-to-pypi).

## Publish Docs

To be completed.

## Publish To PyPi

This workflow publishes the `micropython-europi` and `micropython-europi-contrib` distributions to the public PyPi
repositories. These distributions are described by the [`software/firmware/setup.py`](/software/firmware/setup.py) and [`software/setup.py`](/software/setup.py) files respectively.

### test.pypi.org

Pushes to [test.pypi.org](https://test.pypi.org/project/micropython-europi/#history) occur on every commit in order to
exercise the release process. Most of these will fail silently as a specific version can only be pushed to PyPi once.

### pypi.org

Pushes to the main [pypi.org](https://pypi.org/project/micropython-europi/#history) occur with each new tag.

## Release process

1. Decide which version number to release.
1. Update [`software/firmware/version.py`](/software/firmware/version.py) with the new version number.
1. Commit and push to `main`.
1. Verify that the new release was pushed to [test.pypi.org](https://test.pypi.org/project/micropython-europi/#history). If it was not, look for errors associated with the commit on the [actions tab](https://github.com/Allen-Synthesis/EuroPi/actions). Commit new changes until a successful release is created.
1. Tag the release locally using `git tag -a v<version_number> -m 'message'`, for example `git tag -a v0.0.1 -m 'release v0.0.1'`
1. Push the tag to the remote repository with `git push origin <version_number>`, for example `git push origin v0.0.1`.
1. Verify that the new release was pushed to [pypi.org](https://pypi.org/project/micropython-europi/#history) and is installable.
1. Update the generated [GitHub Release](https://github.com/Allen-Synthesis/EuroPi/releases) with a description of the changes and publish.
1. Announce the release to the Discord server.

## PyTest

To be completed.
