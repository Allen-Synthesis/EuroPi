docker build --tag europi_buildenv --file software/uf2_build/Dockerfile
docker run --rm -it -v %cd%:/europi europi_buildenv