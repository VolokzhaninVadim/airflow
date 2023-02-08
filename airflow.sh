#!/bin/bash

# Create backup
cd /home/volokzhanin/docker/airflow
tar cvpzf /mnt/backup/backup/vvy_airflow/"$(date '+%Y-%m-%d').tar.gz" ./
# Delete old versions
find /mnt/backup/backup/vvy_airflow/ -mtime +3 -type f -delete

# Restore
# cd /home/volokzhanin/docker/vvy_airflow/ & tar xpvzf /mnt/backup/backup/vvy_airflow/2021-10-09.tar.gz
