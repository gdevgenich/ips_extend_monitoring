#!/bin/bash

set -e 
set -x

DEB_DATA="extend_client.py ips_extend_checker.py ips_extend_mon.py mail_reporter.py signalr_client.py"
DEB_DIRECTORY="opt/ips_extend_monitoring"
DEB_PACKAGE_NAME="ips_extend_monitoring"
DEB_PACKAGE_VERSION="$(cat version)"
DEB_PACKAGE_DESC="extend monitoring module for ips monitoring"

if [ ! -z "$BUILD_NUMBER" ] && [ ! -z "$SOURCE_GIT_BRANCH" ]
then
    DEB_BUILD_NUMBER="${DEB_PACKAGE_VERSION}.${BUILD_NUMBER}-$(echo ${SOURCE_GIT_BRANCH}|sed 's|_|-|g')+${DEB_OS_PREFIX}"
elif [ ! -z "$CI_PIPELINE_IID" ] && [ ! -z "$CI_COMMIT_REF_NAME" ]
then
    DEB_BUILD_NUMBER="${DEB_PACKAGE_VERSION}.${CI_PIPELINE_IID}-$(echo ${CI_COMMIT_REF_NAME}|sed 's|_|-|g')+${DEB_OS_PREFIX}"
else
    echo "NO BUILD_NUMBER and SOURCE_GIT_BRANCH or CI_PIPELINE_ID and CI_COMMIT_REF_NAME"
    exit 1
fi

if [ -d "$DEB_DIRECTORY" ]
  then rm -r $DEB_DIRECTORY
fi

mkdir -p $DEB_DIRECTORY/
mkdir -p var/tmp/monitoring

for i in $DEB_DATA
  do cp -r $i $DEB_DIRECTORY/
done

ls|grep "${DEB_ARCH}.deb"|while read l
  do echo "Removing $l"
  rm $l;
done

fpm   --name "$DEB_PACKAGE_NAME" \
      --version "$DEB_BUILD_NUMBER" \
      --architecture "${DEB_ARCH}" \
      --maintainer "${DEVEMAIL}" \
      --depends "${PYTHON_BINARY}-audio-functions" \
      --depends "${PYTHON_BINARY}-context" \
      --depends "${PYTHON_BINARY}-graphyte" \
      --depends "${PYTHON_BINARY}-monitoring-cf" \
      --depends "${PYTHON_BINARY}-pynetwork" \
      --depends "${PYTHON_BINARY}-sipde-client" \
      --depends "${PYTHON_BINARY}-siplib" \
      --depends "${PYTHON_BINARY}-reactor" \
      --depends "${PYTHON_BINARY}-step-manager" \
      --depends "${PYTHON_BINARY}-configparser2" \
      --depends "${PYTHON_BINARY}-pytelegraf" \
      --depends "${PYTHON_BINARY}-anymeeting-client = 0.2" \
      --depends "${PYTHON_BINARY}-audio-functions = 2.1" \
      --depends "${PYTHON_BINARY}-base-callfunc = 1.2" \
      --depends "${PYTHON_BINARY}-blf-parser = 1.2" \
      --depends "${PYTHON_BINARY}-call-functions = 7.20" \
      --depends "${PYTHON_BINARY}-configparser2 = 2.2" \
      --depends "${PYTHON_BINARY}-context = 1.4" \
      --depends "${PYTHON_BINARY}-future-comparators = 1.0.1" \
      --depends "${PYTHON_BINARY}-hpbx-base = 2.83" \
      --depends "${PYTHON_BINARY}-hpbx-dm = 7.78" \
      --depends "${PYTHON_BINARY}-ips-client = 5.11" \
      --depends "${PYTHON_BINARY}-ips-control = 1.32" \
      --depends "${PYTHON_BINARY}-log-functions = 1.0" \
      --depends "${PYTHON_BINARY}-mailbox-functions = 2.6" \
      --depends "${PYTHON_BINARY}-mailcc = 2.0" \
      --depends "${PYTHON_BINARY}-msg-util = 1.0.0" \
      --depends "${PYTHON_BINARY}-mwi-parser = 1.0" \
      --depends "${PYTHON_BINARY}-pbxut = 4.5.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-alert-case = 1.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-classic-reporter = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-context = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-context-reader = 1.0.2" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-hpbx-version = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-mail-reporter = 1.1.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-simple-filter = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-summary-case = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-testlink = 1.0.0" \
      --depends "${PYTHON_BINARY}-pbxut-plugin-verbose-reporter = 1.0.1" \
      --depends "${PYTHON_BINARY}-pbxut-util = 4.5.0" \
      --depends "${PYTHON_BINARY}-pynetwork = 2.2" \
      --depends "${PYTHON_BINARY}-reactor = 3.0" \
      --depends "${PYTHON_BINARY}-rmq-client = 1.8" \
      --depends "${PYTHON_BINARY}-robert2 = 2.0" \
      --depends "${PYTHON_BINARY}-rpclient = 1.2" \
      --depends "${PYTHON_BINARY}-sdplib = 1.0" \
      --depends "${PYTHON_BINARY}-sipde-client = 2.4.1" \
      --depends "${PYTHON_BINARY}-siplib = 4.0" \
      --depends "${PYTHON_BINARY}-sipne = 3.5.1" \
      --depends "${PYTHON_BINARY}-soap-client = 1.1" \
      --depends "${PYTHON_BINARY}-step-manager = 2.12" \
      --depends "${PYTHON_BINARY}-testlink = 3.0" \
      --depends "${PYTHON_BINARY}-umsctl-client = 1.10" \
      --depends "${PYTHON_BINARY}-unison-cp-client = 1.22" \
      --depends "${PYTHON_BINARY}-protobuf = 3.17.3" \
      --depends "${PYTHON_BINARY}-pytz" \
      --depends "${PYTHON_BINARY}-waveproc" \
      --depends "${PYTHON_BINARY}-multipart" \
      --depends "${PYTHON_BINARY}-signalrcore" \
      --depends "python3" \
      --depends "python3-requests" \
      --depends "python3-urllib3" \
      --depends "python3-chardet" \
      --depends "python3-certifi" \
      --depends "python3-idna" \
      --depends "python3-slixmpp" \
      --depends "python3-magic" \
      --depends "sipde = 1.3.0-1+deb11" \
      --depends "sipmon = 2.7.1-1+deb11" \
      --depends "libpjproject = 2.11-4+deb11" \
      --depends "intermedia-ring = 0.0.2" \
      --depends "nodejs = 12.22.12~dfsg-1~deb11u1" \
      --depends ffmpeg \
      --depends sipmon \
      --depends sipde \
      --depends libpjproject \
      --depends mailutils \
      --depends xvfb \
      --depends libxss1 \
      --depends xdg-utils \
      --depends libasound2 \
      --deb-user $DEB_USER \
      --deb-group $DEB_USER \
      --description "${DEB_PACKAGE_DESC}" \
      --deb-no-default-config-files \
      -t deb -s dir opt/ var/
