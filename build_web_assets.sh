#!/bin/sh

IMAGE_TAG=anki-addon-svelte-build-languagetools:latest

# build image
docker build  \
--build-arg UNAME=$USER \
--build-arg UID=$(id -u) \
--build-arg GID=$(id -g) \
-t lucwastiaux/$IMAGE_TAG \
-f ../anki-addon-svelte-build/Dockerfile .

# run build
docker run -it --rm \
--mount type=bind,source="$(pwd)"/web,target=/workspace/web \
--mount type=bind,source="$(pwd)",target=/workspace/web_build_output \
lucwastiaux/$IMAGE_TAG sh -c "cp -rv /workspace/web/* /workspace/web_build/ && cd /workspace/web_build/ && yarn build && ls -ltr && cp /workspace/web_build/languagetools.css /workspace/web_build/languagetools.js /workspace/web_build_output"  || { echo 'docker for lucwastiaux/anki-addon-svelte-build failed' ; exit 1; }