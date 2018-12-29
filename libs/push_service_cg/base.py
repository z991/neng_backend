import logging
import requests
logger = logging.getLogger(__name__)

#基础辅助类
class BaseComponent(object):


    #post远程请求
    def post_remote_data(self,url, data):
        self.timout = 30
        try:
            print(url, data)
            logger.info('url：' + str(url)+"\n"+'data:'+str(data))
            resp = requests.post(url=url, json=data, timeout=self.timout,
                                 headers={"token": "dataMigration", 'Content-Type': 'application/json'})
            logger.info('return：' + str(resp.json()))
            print(resp.json())
            return resp.json()
        except requests.ConnectTimeout:
            logger.error(msg=f"POST连接超时: {url}")
            raise

    # push远程请求
    def put_remote_data(self,url, data):
        self.timout = 30
        try:
            print(url, data)
            logger.info('url：' + str(url) + "\n" + 'data:' + str(data))
            resp = requests.put(url=url, json=data, timeout=self.timout, headers={"token": "dataMigration"})
            logger.info('return：' + str(resp.json()))
            print(resp.json())
            return resp.json()
        except requests.ConnectTimeout:
            logger.error(msg=f"POST连接超时: {url}")
            raise

    # get远程请求
    def get_remote_data(self,url):
        self.timout = 30
        try:
            print(url)
            logger.info('url：' + str(url))
            resp = requests.get(url=url, timeout=self.timout)
            logger.info('return：' + str(resp.json()))
            print(resp.json())
            return resp.json()
        except requests.ConnectTimeout:
            logger.error(msg=f"GET连接超时: {url}")
            raise

    # 抛错
    def error_response(self,msg):
        logger.error(msg=msg)
        return False, msg

    #正确返回
    def success_response(self,msg):
        logger.info(msg=msg)
        return True, msg
