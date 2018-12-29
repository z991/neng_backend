import redis
from libs.environment import ENV
current_env = ENV()

class Redis_base:
    def __init__(self):
        try:
            self.conn = redis.Redis(host=current_env.get_config("REDIS_SERVER"), port=6379,db=1)
        except Exception as e:
            print('redis连接失败，错误信息%s' % e)

    #根据key值获取
    def get(self,key):
        res = self.conn.get(key)
        if res:
            return res.decode()
        else:
            return False

    #写入了一个键值对
    def set(self, key, value):
        return self.conn.set(key, value)

    #将一个或多个值 value 插入到列表 key 的表头
    def lpush(self,key,value):
        return self.conn.lpush(key,value)

    #获取在存储于列表的key索引的元素
    def lindex(self,key,index):
        res = self.conn.lindex(key,index)
        if res:
            return res.decode()

    #返回列表 key 的长度
    def llen(self,key):
        return self.conn.llen(key)

    #让列表只保留指定区间内的元素，不在指定区间之内的元素都将被删除
    def ltrim(self,key,start,end):
        return self.conn.ltrim(key,start,end)

    #删除指定的键
    def delete(self, key):
        try:
            self.conn.delete(key)
            return True
        except:
            return False

    def exists(self,key):
        return self.conn.exists(key)



