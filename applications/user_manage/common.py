#!/usr/bin/env python
# coding:utf-8

from ldap3 import Connection, Server, ANONYMOUS, SIMPLE, SYNC, ASYNC, ALL, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, MODIFY_INCREMENT, SUBTREE, BASE, LEVEL
from contextlib import contextmanager
import traceback, re, json
from pprint import pprint
from django.conf import settings


@contextmanager
def connect_ldap():
    c = None
    try:
        s = Server(settings.AUTH_LDAP_SERVER_URI, get_info=ALL)
        c = Connection(s, user='cn=admin,dc=xiaoneng,dc=cn', password='8ql6,yhY')
        if not c.bind():
            raise Exception(c.request)

        yield c
    except Exception as e:
        traceback.print_exc()
        raise e
    finally:
        try:
            if c:
                c.unbind()
        except:
            pass


def split(dn):
    reg = re.compile('\w+=([\w-]+),(.*)')
    m = reg.match(dn)
    if m:
        return m.groups()
    return None


def digui(c, rdn):
    c.search(rdn, search_filter='(objectClass=*)', attributes=['*'],
             search_scope=LEVEL)
    data = []
    for i in c.entries:
        dn = i.entry_dn
        if 'organizationalUnit' in i.entry_attributes_as_dict['objectClass']:
            children = digui(c, dn)
            d = {
                "id": dn,
                "sortid": "1_" + i.entry_attributes_as_dict['ou'][0],
                "name": i.entry_attributes_as_dict['ou'][0],
                "children": children,
                "type": "ou"
            }
            data.append(d)
        elif 'inetOrgPerson' in i.entry_attributes_as_dict['objectClass']:
            data.append({
                "id": dn,
                "sortid": "2_" + i.entry_attributes_as_dict['cn'][0],
                "name": i.entry_attributes_as_dict['sn'][0],
                "cn": i.entry_attributes_as_dict['cn'][0],
                "type": "cn"
            })
    data.sort(key=lambda o: o['sortid'])
    return data


def main():
    rdn = 'ou=Users,dc=xiaoneng,dc=cn'
    with connect_ldap() as c:
        print(digui(c, rdn))

if __name__ == '__main__':
    main()
