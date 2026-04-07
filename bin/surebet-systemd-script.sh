#!/bin/bash

set -eo pipefail

if [ ${#} -eq 0 ]
then
	NEW_SERVICE=eurovirtuals
else
	NEW_SERVICE=${1}
fi
SOURCE_SERVICE=pragmatic
SYSTEMD_PATH=/etc/systemd/system
SCRIPT_PATH=/scripts/admin
SERVICE_PATH_PREFIX=${SYSTEMD_PATH}/${NEW_SERVICE}
JAVA_DIR=/apps/java/${NEW_SERVICE}
APP_CONFIG=${JAVA_DIR}/application.properties

# cleanup
systemctl stop ${NEW_SERVICE}.path || true
systemctl stop ${NEW_SERVICE}.service || true
systemctl disable ${NEW_SERVICE}.service || true
rm -fv /etc/systemd/system/${NEW_SERVICE}* /scripts/admin/{deploy,start,stop}_${NEW_SERVICE}.sh || true
rmdir -v /tmp/${NEW_SERVICE} || true

cd ${SYSTEMD_PATH}

cp -fvu ${SOURCE_SERVICE}-deploy.service ${NEW_SERVICE}-deploy.service
cp -fvu ${SOURCE_SERVICE}.service ${NEW_SERVICE}.service
cp -fvu ${SOURCE_SERVICE}.path ${NEW_SERVICE}.path

cd ${SCRIPT_PATH}

cp -fvu deploy_${SOURCE_SERVICE}.sh deploy_${NEW_SERVICE}.sh
cp -fvu start_${SOURCE_SERVICE}.sh start_${NEW_SERVICE}.sh
cp -fvu stop_${SOURCE_SERVICE}.sh stop_${NEW_SERVICE}.sh


# modify deploy service
deploy_service_path=${SERVICE_PATH_PREFIX}-deploy.service

perl -i -ple '
/^Description/&&s/'${SOURCE_SERVICE}'/\u'${NEW_SERVICE}'/i;
!/^Description/&&s/'${SOURCE_SERVICE}'/'${NEW_SERVICE}'/' \
${deploy_service_path}

[ -d /tmp/${NEW_SERVICE} ] || mkdir -pvm 777 /tmp/${NEW_SERVICE}

# modify path service
path_service_path=${SERVICE_PATH_PREFIX}.path

sed -i 's/'${SOURCE_SERVICE}'/'${NEW_SERVICE}'/' \
${path_service_path}

# modify service
service_path=${SERVICE_PATH_PREFIX}.service

perl -i -ple '
/^Description/&&s/'${SOURCE_SERVICE}'/\u'${NEW_SERVICE}'/i;
!/^Description/&&s/'${SOURCE_SERVICE}'/'${NEW_SERVICE}'/' \
${service_path}

# modify deploy script
deploy_script=${SCRIPT_PATH}/deploy_${NEW_SERVICE}.sh

sed -i 's/'${SOURCE_SERVICE}'/'${NEW_SERVICE}'/' \
${deploy_script}

# Daemon reload
systemctl daemon-reload

# start path service
systemctl start ${NEW_SERVICE}.path

# enable service
systemctl enable ${NEW_SERVICE}.service

# start service
systemctl restart ${NEW_SERVICE}.service

# assuming that the name of the service is the name of
# java app directory
if [ ! -d ${JAVA_DIR} ]
then
    mkdir -pv ${JAVA_DIR}
    echo Application is yet to be deployed >&2
    exit 22
fi
#jar_file=$(basename $(ls ${JAVA_DIR}/*.jar | head -1))
jar_file=EuroVirtuals-1.0.jar
app_port=$(grep server.port ${APP_CONFIG} | awk -F= '{print $2}')

# modify start script
start_script=${SCRIPT_PATH}/start_${NEW_SERVICE}.sh

sed -i 's/'${SOURCE_SERVICE}'/'${NEW_SERVICE}'/' \
${start_script}
sed -i '/^\(JAR=\).*/s//\1'${jar_file}'/' ${start_script}

# modify stop script
stop_script=${SCRIPT_PATH}/stop_${NEW_SERVICE}.sh

sed -i '/^\(JAR=\).*/s//\1'${jar_file}'/' ${stop_script}
sed -i '/^\(PORT_1=\).*/s//\1'${app_port}'/' ${stop_script}

# modify application logging configs
sed -i '/^\(logging[^=]\+=\).*/s//\1DEBUG/' ${APP_CONFIG}
sed -i '/^\(logging.level.root=\).*/s//\1INFO/' ${APP_CONFIG}


