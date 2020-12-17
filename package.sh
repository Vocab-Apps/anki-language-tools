#!/bin/sh

VERSION_NUMBER=$1 # for example 0.1
GIT_TAG=v${VERSION_NUMBER}

echo "ANKI_LANGUAGE_TOOLS_VERSION='${VERSION_NUMBER}'" > version.py
git commit -a -m "upgraded version to ${VERSION_NUMBER}"
git push
git tag -a ${GIT_TAG} -m "version ${GIT_TAG}"
git push origin ${GIT_TAG}

# create .addon file
ADDON_FILENAME=${HOME}/anki-addons-releases/anki-language-tools-${VERSION}.ankiaddon
zip -r ${ADDON_FILENAME} *



