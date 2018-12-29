import urllib.request
import xml.dom.minidom
import requests
import logging
import re
from ldap_server.configs import SMSNAME,SMSPWD,SMSSCORPID,SMSSPRDID,SMSTARGET
logger = logging.getLogger('django')
class Sms:

    def __init__(self):
        self.smsname = SMSNAME
        self.smspwd = SMSPWD
        self.smsscorpid = SMSSCORPID
        self.smstarget = SMSTARGET
        self.smssprdid = SMSSPRDID

    def send(self,phone,smsg):
        ret = re.match(r"^1[3456789]\d{9}$", str(phone))
        if ret:
            url = self.smstarget+'/g_Submit?sname='+self.smsname+'&spwd='+self.smspwd+'&scorpid='+self.smsscorpid+'&sprdid='+self.smssprdid+'&sdst='+str(phone)+'&smsg='+urllib.request.quote(smsg)
            logging.info('smsurl：' + url)
            result = requests.get(url=url)
            dom = xml.dom.minidom.parseString(result.text)
            root = dom.documentElement
            State = root.getElementsByTagName("State")
            MsgID = root.getElementsByTagName("MsgID")
            MsgState = root.getElementsByTagName("MsgState")
            Reserve = root.getElementsByTagName("Reserve")
            if int(State[0].firstChild.data) == 0:
                return True
            else:
                logging.error(str(phone)+'-----'+MsgState[0].firstChild.data)
                return False
        else:
            logging.error(str(phone) + '-----手机号格式错误')
            return False

