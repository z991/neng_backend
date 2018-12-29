# __author__ = itsneo1990
from django.core.management import BaseCommand

from applications.data_manage.task import InquiresFetcherManager
from libs.datetimes import str_to_date


class Command(BaseCommand):
    """可以输入多个节点名称"""

    def add_arguments(self, parser):
        parser.add_argument('from_date', type=str)
        parser.add_argument('to_date', type=str)

    def handle(self, *args, **options):
        from_date, to_date = str_to_date(options['from_date']), str_to_date(options['to_date'])
        manage = InquiresFetcherManager()
        print('fetch...')
        manage.fetch_history(from_date, to_date)