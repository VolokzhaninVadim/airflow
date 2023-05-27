#!/bin/bash

#sudo apt-get install p7zip-full
# Создаем резервную копию
cd /mnt/backup/documents
tar cvpzf /mnt/backup/backup/document/"$(date '+%Y-%m-%d').tar.gz" ./
cd /mnt/backup/backup/document/
7za a -tzip -p$ARCHIVE_DOCUMENT -mem=AES256  /mnt/backup/backup/document/"$(date '+%Y-%m-%d').zip" /mnt/backup/backup/document/"$(date '+%Y-%m-%d').tar.gz"
rm /mnt/backup/backup/document/"$(date '+%Y-%m-%d').tar.gz"
# Удаляем архивы резервной копии старше n дней
find /mnt/backup/backup/document/ -mtime +0 -type f -delete

# restore
# 7za e /mnt/backup/backup/document/2021-10-09.zip
# cd /mnt/backup/documents & tar xpvzf /mnt/backup/backup/document/2021-10-09.tar.gz

