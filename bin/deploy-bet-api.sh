#!/bin/bash

set -eo pipefail
JAR=SurebetAPI-1.0-SNAPSHOT.jar
JAR_PATH=/mnt/c/Users/ADMIN/Projects/java/surebet-bet-api-service/target
DEST=prod:/tmp/bet-api
LOCALDEST=${HOME}/apps/java
cp -fvu ${JAR_PATH}/${JAR} ${LOCALDEST}
SOURCE_PATH=${LOCALDEST}/${JAR}
CMD="scp ${SOURCE_PATH} ${DEST}"
# echo "${CMD}"
eval "${CMD}"
