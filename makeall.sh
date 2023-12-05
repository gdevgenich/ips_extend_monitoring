#!/bin/bash

set -e 
set -x

DEB_DATA="extend_client.py ips_extend_checker.py ips_extend_mon.py mail_reporter.py signalr_client.py start.sh"
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
      --depends "python-signalrcore" \
      --depends "${PYTHON_BINARY}-audio-functions = 2.1" \
      --depends "${PYTHON_BINARY}-configparser2 = 2.2" \
      --depends "${PYTHON_BINARY}-context = 1.4" \
      --depends "${PYTHON_BINARY}-monitoring-cf = 1.9" \
      --depends "${PYTHON_BINARY}-pynetwork = 2.3" \
      --depends "${PYTHON_BINARY}-reactor = 3.0" \
      --depends "${PYTHON_BINARY}-sipde-client = 2.4.4" \
      --depends "${PYTHON_BINARY}-siplib = 4.0" \
      --depends "${PYTHON_BINARY}-step-manager = 2.12" \
      --depends "${PYTHON_BINARY}-waveproc = 2.11" \
      --depends "${PYTHON_BINARY}-rmq-client = 2.5" \
      --depends "${PYTHON_BINARY}-pika = 1.3.1" \
      --deb-user $DEB_USER \
      --deb-group $DEB_GROUP \
      --description "${DEB_PACKAGE_DESC}" \
      --deb-no-default-config-files \
      -t deb -s dir opt/ var/
