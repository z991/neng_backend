from __future__ import absolute_import, unicode_literals

import datetime
import logging
import os

from celery import Celery, shared_task
from django.conf import settings

from ldap_server.settings import BACKUP_PATH
from libs.datetimes import date_to_str
from libs.environment import ENV

logger = logging.getLogger(__name__)
current_env = ENV()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ldap_server.settings')

app = Celery('ldap_server',
             broker=settings.REDIS_URL,
             backend=settings.REDIS_URL,
             include=["applications.permission_and_staff_manage.task",
                      "applications.data_manage.task",
                      "applications.production_manage.ksyun_api",
                      "applications.production_manage.aliyun_api"])

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


#@shared_task
def db_backup():
    logger.info("db_backup start")
    current_date = datetime.date.today()
    file_dir = os.path.join(BACKUP_PATH, f"{current_date.year}-{current_date.month}")
    file_path = os.path.join(file_dir, f"{date_to_str(current_date)}.sql")
    print(file_dir)
    os.makedirs(file_dir, exist_ok=True)
    db = settings.DATABASES["default"]
    command = f"mysqldump -h{db['HOST']} -u{db['USER']} -p{db['PASSWORD']} -P{db['PORT']} {db['NAME']} " \
              f"|gzip > {file_path}.gzip"
    print(command)
    os.system(command)
    logger.info("backup finished")


@shared_task
def test_beat():
    logger.info("bang!")
    print("bang")
