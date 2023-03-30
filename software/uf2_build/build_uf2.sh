#!/bin/sh
set -e

# Run this script from the repo's root directory as `$ ./software/uf2_build/build_uf2.sh`.
# requires docker is installed and running. For docker help: https://docs.docker.com/get-started/

# Build the `europi_buildenv`` docker image. Subsequent builds will reuse the same image.
docker build -t europi_buildenv -f software/uf2_build/Dockerfile ./

# Run the just built docker image, which uses the code in the current directory to build a new uf2
# image, which will be located in `software/uf2_build/europi-dev.uf2`.
docker run -v .:/europi europi_buildenv
