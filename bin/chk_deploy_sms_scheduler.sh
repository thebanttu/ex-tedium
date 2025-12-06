#!/bin/bash

set -eo pipefail

# Compare the age of the artifact (apps/java/SMSScheduler-0.0.1-SNAPSHOT.jar) with a
# time check file in the parent dir with the same name (apps/java/.SMSScheduler-0.0.1-SNAPSHOT)
# if they match, do nothing if they don't deploy the artifact (~/bin/deploy-sms-scheduler.sh)

JAR_PATH=/mnt/c/Users/ADMIN/Projects/java/sms-scheduler/sms-scheduler/target
JAR=SMSScheduler-0.0.1-SNAPSHOT.jar
artifact=${JAR_PATH}/${JAR}
time_check_file=${HOME}/apps/java/.SMSScheduler-0.0.1-SNAPSHOT
deploy_script=${HOME}/bin/deploy-sms-scheduler.sh

create_time_check_file(){
    if [[ ! -e ${time_check_file} ]]
    then
        echo Creating time check file...
        touch ${time_check_file}
        touch -r ${artifact} ${time_check_file}
    fi
    echo Time check file already exists.
}

while :
do
    create_time_check_file
    if [[ ! -e ${artifact} ]]
    then
        echo Artifact: ${artifact} not found, will check again.
        sleep 5
        continue
    fi
    if [[ $(stat -c %Y ${artifact}) -gt $(stat -c %Y ${time_check_file}) ]]
    then
        echo Changes to the artifact found. Proceeding to deploy.
        . ${deploy_script}
        sleep 2
        touch -r ${artifact} ${time_check_file}
    else
        echo No changes to the current artifact, skipping deploy.
    fi
    sleep 5
done
