#!/bin/bash

set -eo pipefail

surebet_api_archive=${HOME}/Projects/surebet-infra/modules/api-testing/files/apps.tar.gz
surebet_admin_archive=${HOME}/Projects/surebet-infra/modules/api-testing/files/admin-dashboard.tar.gz
archive_workspace=${HOME}/archive_workspace
admin_dashboard_env=${archive_workspace}/usr/share/nginx/surebet-admin-new/.env
db_host=sure-apps-2.europe-west1-b.c.surebet-408116.internal

# Fetching apps and configurations

ssh api -- '
    find \
    /apps/java/accounts-service \
    /apps/java/aviatrix \
    /apps/java/bet-api \
    /apps/java/fazi-casino \
    /apps/java/pragmatic \
    /apps/java/registry-service \
    /apps/java/surecoin \
    /etc/systemd/system/account-api-deploy.service \
    /etc/systemd/system/account-api.path \
    /etc/systemd/system/account-api.service \
    /etc/systemd/system/admin-queue.service \
    /etc/systemd/system/aviatrix-deploy.service \
    /etc/systemd/system/aviatrix.path \
    /etc/systemd/system/aviatrix.service \
    /etc/systemd/system/bet-api-deploy.service \
    /etc/systemd/system/bet-api.path \
    /etc/systemd/system/bet-api.service \
    /etc/systemd/system/fazi-casino-deploy.service \
    /etc/systemd/system/fazi-casino.path \
    /etc/systemd/system/fazi-casino.service \
    /etc/systemd/system/pragmatic-deploy.service \
    /etc/systemd/system/pragmatic.path \
    /etc/systemd/system/pragmatic.service \
    /etc/systemd/system/rabbit-consumer.service \
    /etc/systemd/system/surecoin-deploy.service \
    /etc/systemd/system/surecoin.path \
    /etc/systemd/system/surecoin.service \
    /scripts/admin/stop_pragmatic.sh \
    /scripts/admin/start_pragmatic.sh \
    /scripts/admin/deploy_pragmatic.sh \
    /scripts/admin/stop_aviatrix.sh \
    /scripts/admin/start_aviatrix.sh \
    /scripts/admin/deploy_aviatrix.sh \
    /scripts/admin/stop_surecoin.sh \
    /scripts/admin/start_surecoin.sh \
    /scripts/admin/deploy_surecoin.sh \
    /scripts/admin/stop_fazi_casino.sh \
    /scripts/admin/start_fazi_casino.sh \
    /scripts/admin/deploy_fazi_casino.sh \
    /scripts/admin/stop_rabbit_consumer.sh \
    /scripts/admin/start_rabbit_consumer.sh \
    /scripts/admin/stop_account_api.sh \
    /scripts/admin/start_account_api.sh \
    /scripts/admin/deploy_account_api.sh \
    /scripts/admin/stop_bet_api.sh \
    /scripts/admin/start_bet_api.sh \
    /scripts/admin/deploy_bet_api.sh \
    /scripts/admin/stop_intouchvas.sh \
    /scripts/admin/start_intouchvas.sh \
    /scripts/admin/deploy_intouchvas.sh \
    /scripts/admin/start_admin_queue.sh \
    -depth -type f | sudo tar cvzf - -T-
' >${surebet_api_archive}

# Create archive workspace dir
cd ${HOME}
[ -d archive_workspace ] && \
    rm -rfv ${archive_workspace} && \
    mkdir -v ${archive_workspace} || \
mkdir -v ${archive_workspace}

tar xzvf ${surebet_api_archive} -C ${archive_workspace}

app_properties_files=$(find ${archive_workspace}/apps/java -type f -name application.properties | xargs)

# rg mysql ${archive_workspace}

# Change db host on app properties
sed -i '/mysql:\/\/[^:][^:]*/s/^\([^:][^:]*:mysql...\)[^:][^:]*\(:.*\)/\1'${db_host}'\2/' ${app_properties_files}

# Change db name on app properties from surebet (staging) to surebet_prod (prod)
sed -i '/mysql.*surebet?/s/^\([^?][^?]*surebet\)\([?].*\)/\1_prod\2/' ${app_properties_files}

# rg mysql ${archive_workspace}

(cd ${archive_workspace}; find . -depth -type f | tar cvzf ${surebet_api_archive} -T-)

# Fetch admin configs and data
ssh api -- '
    ls \
    /usr/share/nginx/surebet-admin-new/.env \
    /etc/nginx/conf.d/admin-two.conf | \
    sudo tar cvzf - -T-
' >${surebet_admin_archive}

# Create archive workspace dir
cd ${HOME}
[ -d archive_workspace ] && \
    rm -rfv ${archive_workspace} && \
    mkdir -v ${archive_workspace} || \
mkdir -v ${archive_workspace}

tar xzvf ${surebet_admin_archive} -C ${archive_workspace}

# Change db name on admin .env from surebet (staging) to surebet_prod (prod)
sed -i '/DB_DATABASE/s/surebet/&_prod/' ${admin_dashboard_env}

# Change db host on admin .env file
sed -i '/DB_HOST/s/=.*/='${db_host}'/' ${admin_dashboard_env}

(cd ${archive_workspace}; find . -depth -type f | tar cvzf ${surebet_admin_archive} -T-)