#!/bin/bash

set -e
set -x

curl -X POST -F file=@"$(ls|grep ""*${DEB_OS_PREFIX}_amd64.deb"")" --user ${APTUSER}:${APTPASS} ${APTURL}/files/${APT_DIR}
curl -X POST --user ${APTUSER}:${APTPASS} ${APTURL}/repos/${APT_LOCAL_REPO}/file/${APT_DIR}
curl -X PUT -H 'Content-Type:application/json' \
--data '{"Sources":[{"Component":"non-free"}], "Architectures":["${DEB_ARCH}"], "Distribution":"${DISTR}"}' \
--user ${APTUSER}:${APTPASS} ${APTURL}/publish/${APT_REPO}/${DISTR}
