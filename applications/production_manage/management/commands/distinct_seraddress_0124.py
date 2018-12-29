# __author__ = gzh
from time import sleep

from django.core.management import BaseCommand

from applications.production_manage.models import SerAddress, ServerGroup, SerIp


class Command(BaseCommand):
    def handle(self, *args, **options):
        address_ser_id_info = SerAddress.objects.all().values_list('server_id', 'ser_address', 'id')
        address_ser_id_map = map(lambda x: ((x[0], x[1]), x[2]), address_ser_id_info)
        _address_ser_id_dict = {}
        for item in address_ser_id_map:
            _address_ser_id_dict.setdefault(item[0], [])
            _address_ser_id_dict[item[0]].append(item[1])

        address_ser_id_dict = filter(lambda x: len(x[1]) > 2, _address_ser_id_dict.items())

        for address_ser, addr_id_list in address_ser_id_dict:
            keep = SerAddress.objects.get(id=addr_id_list[0])
            for num in range(1, len(addr_id_list)):
                group_list = ServerGroup.objects.all().filter(ser_address_id=addr_id_list[num])
                delete = SerAddress.objects.get(id=addr_id_list[num])
                for group in group_list:
                    group.ser_address.add(keep)
                    group.ser_address.remove(delete)

            sleep(0.1)
            SerIp.objects.all().filter(ser_address_id__in=addr_id_list[1:]).delete()
            sleep(0.1)
            SerAddress.objects.all().filter(id__in=addr_id_list[1:]).delete()
            sleep(0.1)

