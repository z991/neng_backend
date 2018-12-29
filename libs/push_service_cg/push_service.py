import logging

import requests
from collections import Iterable
from libs.basemodel import BaseModelHelp
from libs.push_service_cg.components import CreateSite,CloseEnterprise, \
    CreateGroup, CreateRole, CreateTag, CreateUser, NoticeAccountCenter1st, NoticeAccountCenter2nd,FunctionProd,Kf_getFlashServer,Visitant_getFlashServer
logger = logging.getLogger(__name__)


#推送业务逻辑
class Push_manage(object):
    def __init__(self, site_id, name,online_status):
        self.site_id = site_id #企业id
        self.name = name #企业名称
        self.online_status = online_status #企业名称

    #推送
    def push_data(self):
        try:
            if self.online_status:
                data = self.get_gridconfig(self.site_id)
                if not data:
                    return False
                self.steps = [
                    FunctionProd,
                    CreateSite,
                    CreateGroup,
                    CreateRole,
                    CreateTag,
                    CreateUser,
                    Kf_getFlashServer,
                    Visitant_getFlashServer,
                ]
                for step in self.steps:
                    step_obj = step(**self.get_params())
                    step_obj.process()
                return True
            else:
                data = self.get_gridconfig(self.site_id)
                if not data:
                    return False
                self.steps = [
                    CloseEnterprise,
                ]
                for step in self.steps:
                    step_obj = step(**self.get_params())
                    step_obj.process()
                return True
        except Exception as e:
            print(e)
            return False


    #重构接口传递的参数
    def get_params(self):
        return {
            "site_id": self.site_id,
            "name": self.name,
            "setting_url": self.setting_center,
            "user_center_url": self.user_center,
            "init": self.init,
            "getFlashserver_kf": self.getFlashserver_kf,
            "getFlashserver_visitant": self.getFlashserver_visitant
        }

    #获取重构节点配置项
    def get_gridconfig(self,siteid):
        try:
            data = BaseModelHelp().get_grid_getFlashserver(siteid)
            domain_name = eval(data[0]['domain_name'])
            self.user_center = domain_name['usercenter'] #用户中心的url
            self.setting_center = domain_name['dolphinsetting'] #设置的url
            self.client = domain_name['client'] #客户端的url
            self.init = domain_name['init'] #getflashserver的url
            self.getFlashserver_kf = data[0]['getFlashserver'] #客户端需传送的json
            self.getFlashserver_visitant = data[0]['visitors'] #访客端需传送的json
            return True
        except Exception as e:
            print(e)
            return False


