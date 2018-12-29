# __author__ = itsneo1990
import logging

import pymysql

log = logging.getLogger('django')


def mysql_test(host, user, password, db, port=3306, charset="utf8"):
    try:
        connect = pymysql.Connect(host=host,
                                  user=user,
                                  password=password,
                                  db=db,
                                  port=int(port),
                                  charset=charset)

    except Exception as e:
        log.info("mysql_test----exception: %s" % e)
        return False
    else:
        connect.close()
        return True
