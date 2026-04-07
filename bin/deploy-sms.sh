#!/bin/bash

set -eo pipefail
JAR=SMSScheduler-0.0.1-SNAPSHOT.jar
PROPS=application.properties
JAR_PATH=/mnt/c/Users/ADMIN/Projects/java/sms-scheduler/target
DEST="sms:/tmp/sms-tests"
cp -fvu ${JAR_PATH}/${JAR} ${HOME}/apps/java
JAR_PATH=${HOME}/apps/java
SOURCE_PATH=${JAR_PATH}/${JAR}
SSH_CONFIG=${HOME}/.ssh/config
CMD="scp -F ${SSH_CONFIG} -- ${SOURCE_PATH} ${DEST}"
echo "${CMD}"
eval "${CMD}"
