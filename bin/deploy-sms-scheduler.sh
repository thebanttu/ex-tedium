#!/bin/bash

set -eo pipefail
JAR=SMSScheduler-0.0.1-SNAPSHOT.jar
JAR_PATH=/mnt/c/Users/ADMIN/Projects/java/sms-scheduler/sms-scheduler/target
DEST=suresms:/tmp/sms-tests
LOCALDEST=${HOME}/apps/java
cp -fvu ${JAR_PATH}/${JAR} ${LOCALDEST}
JAR_PATH=${HOME}/apps/java
SOURCE_PATH=${JAR_PATH}/${JAR}
CMD="scp ${SOURCE_PATH} ${DEST}"
# echo "${CMD}"
eval "${CMD}"
