# __author__ = itsneo1990
import datetime, time

import pymysql

from libs.datetimes import datetime_delta, date_to_timestamp, datetime_to_timestamp

# 频道转换
CHANGE_MAP = {-1: -1, 0: 6, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}


class InquiresFetcher(object):
    """获取咨询量worker"""

    def __init__(self, host="", user="", password="", database="kf", port=3306, charset="utf8"):
        try:
            self.db = pymysql.connect(host=host, user=user, password=password, database=database, port=port,
                                  charset=charset,connect_timeout=5)
            self.cursor = self.db.cursor()
        except Exception as e:
            err = f'Cannot connect to MySQL on {host}'
            print(err)

    def _fetch_data(self, from_time, to_time):
        # starttime = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))) * 1000
        # endtime = int(time.mktime(time.strptime(time.strftime('%Y-%m-%d') + ' 23:59:59', '%Y-%m-%d %H:%M:%S'))) * 1000
        params = {

            "from_time": int(from_time)*1000,
            "to_time": int(to_time)*1000
        }
        data = []
        try:
            sql = "SELECT siteid, entrance, count(*)  FROM t2d_chatscene " \
                  "WHERE starttime > {from_time} AND starttime < {to_time} GROUP BY siteid, entrance".format(**params)
            self.cursor.execute(sql)
            _data = self.cursor.fetchall()  # 从数据库取出的数据为元组套元组，需对channel字段进行代码转换

            for _line in _data:
                line = list(_line)  # 将元祖转化为列表
                if not line[1] in CHANGE_MAP.keys():
                    continue
                line[1] = CHANGE_MAP[line[1]]
                data.append(line)
        except:
            pass
        return data

    def fetch_yesterday(self):
        """获取昨天的咨询量"""
        today = datetime.date.today()
        yesterday = datetime_delta(today, days=-1)
        start_str = str(yesterday) + ' 00:00:00'
        end_str = str(yesterday) + " 23:59:59"

        start_strp = time.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end_strp = time.strptime(end_str, '%Y-%m-%d %H:%M:%S')

        today_timestamp = time.mktime(start_strp)
        yesterday_timestamp = time.mktime(end_strp)
        return self._fetch_data(from_time=yesterday_timestamp, to_time=today_timestamp)

    def fetch_today(self):
        """获取今天的咨询量"""
        today = datetime.date.today()
        start_str = str(today) + ' 00:00:00'
        end_str = str(today) + " 23:59:59"

        start_strp = time.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end_strp = time.strptime(end_str, '%Y-%m-%d %H:%M:%S')

        today_timestamp = time.mktime(start_strp)
        now_timestamp = time.mktime(end_strp)
        return self._fetch_data(from_time=today_timestamp, to_time=now_timestamp)

    def fetch_date(self, date):
        """获取指定日期的咨询量"""
        start_str = str(date) + ' 00:00:00'
        end_str = str(date) + " 23:59:59"

        start_strp = time.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end_strp = time.strptime(end_str, '%Y-%m-%d %H:%M:%S')

        today_timestamp = time.mktime(start_strp)
        now_timestamp = time.mktime(end_strp)

        return self._fetch_data(from_time=today_timestamp, to_time=now_timestamp)