from libs.push_service_cg import resource
from libs.push_service_cg.base import BaseComponent
import json

class NoticeAccountCenter1st(BaseComponent):
    """1.开站前通知账号中心"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "1.开站前通知账号中心"
    def process(self):
        self.exists_url = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFeature"
        self.post_sources = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFeature"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if not code == 200 or not code == True:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, {})
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}\n{resp['message']}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class NoticeAccountCenter2nd(BaseComponent):
    """2.开站后通知账号中心"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "2.开站后通知账号中心"

    def process(self):
        self.exists_url = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFunction"
        self.post_sources = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFunction"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if code == True:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, {})
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class CreateSite(BaseComponent):
    """1.创建企业"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.name = kwargs['name']
        self.title = "3.创建企业"

    def process(self):
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}"
        self.post_sources = f"{self.user_center_url}/enterprise/{self.site_id}"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if code == True or code == 200:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, resource.create_site(self.site_id, self.name))
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class CreateGroup(BaseComponent):
    """4.创建行政组"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "4.创建行政组"

    def process(self):
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}/group/{self.site_id}_9999"
        self.post_sources = f"{self.user_center_url}/enterprise/{self.site_id}/group"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if code == 200:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, resource.create_group(self.site_id))
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class CreateRole(BaseComponent):
    """5.创建角色"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "5.创建角色"
        self.exists_url = (
            f"{self.user_center_url}/enterprise/{self.site_id}/role/admin",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/kf",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/groupleader"
        )
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_admin(self.site_id)),
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_kf(self.site_id)),
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_group_leader(self.site_id))
        )

    def process(self):
        for each in self.exists_url:
            resp = self.get_remote_data(each)
            code = resp.get("code", None) or resp.get("status", None) or resp.get('success', None)
            if code == 200 or code == True:
                return self.success_response(f"执行成功-->{self.title}")
            else:
                for each in self.post_sources:
                    resp = self.post_remote_data(each[0], each[1])
                    code = resp.get("code", None) or resp.get("status", None)
                    if code == 200:
                        return self.success_response(f"执行成功-->{self.title}")
                    else:
                        return self.error_response(f"执行失败-->{self.title}")


class CreateTag(BaseComponent):
    """6.创建默认标签"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "6.创建个性化功能"

    def process(self):
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}/tag/isExist"
        self.post_sources = f"{self.user_center_url}/enterprise/{self.site_id}/tag"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if code == 200 or code == True:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, resource.create_tag(self.site_id))
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class CreateUser(BaseComponent):
    """7.创建超级管理员"""

    def __init__(self, *args, **kwargs):
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "7.创建超级管理员"

    def process(self):
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}/user/{self.site_id}_admin"
        self.post_sources = f"{self.user_center_url}/enterprise/{self.site_id}/user"
        resp = self.get_remote_data(self.exists_url)
        code = resp.get("code", None) or resp.get("status", None) or resp.get("success", None)
        if code == 200:
            return self.success_response(f"执行成功-->{self.title}")
        else:
            resp = self.post_remote_data(self.post_sources, resource.create_user(site_id=self.site_id))
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")


class FunctionProd(BaseComponent):
    """8.功能开关批量开通"""

    def __init__(self, *args, **kwargs):
        self.setting_url = kwargs['setting_url']
        self.user_center_url = kwargs['user_center_url']
        self.site_id = kwargs['site_id']
        self.title = "8.功能开关批量开通"

    def process(self):
        url = f"{self.user_center_url}/usercenter/productPoint"
        data = resource.productFunction(url, self.site_id)
        self.post_sources = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFunction"
        resp = self.post_remote_data(self.post_sources, data)
        code = resp.get("code", None) or resp.get("status", None)
        if not code == 200:
            self.post_sources = f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFunction"
            resp = self.put_remote_data(self.post_sources, data)
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return self.error_response(f"执行失败-->{self.title}")
            else:
                return self.success_response(f"执行成功-->{self.title}")
        else:
            return self.success_response(f"执行成功-->{self.title}")


class Kf_getFlashServer(BaseComponent):
    """9.激活服务端"""


    def __init__(self,*args,**kwargs):
        self.getFlashserver_kf = kwargs['getFlashserver_kf']
        self.init = kwargs['init']
        self.site_id = kwargs['site_id']
        self.title = "9.客服端插入接口"

    def process(self):
        data = json.loads(self.getFlashserver_kf)
        resp = self.post_remote_data(url=f"{self.init}/api/gate/kf/{self.site_id}?sourcetype=0",
                                     data=data)
        code = resp.get("code", None) or resp.get("status", None)
        if not code == 200:
            return self.error_response(f"执行失败-->{self.title}")
        return self.success_response(f"执行成功-->{self.title}")



class Visitant_getFlashServer(BaseComponent):
    """10.激活客户端"""
    def __init__(self,*args,**kwargs):
        self.getFlashserver_visitant = kwargs['getFlashserver_visitant']
        self.init = kwargs['init']
        self.site_id = kwargs['site_id']
        self.title = "10.访客端插入接口"

    def process(self):
        data = json.loads(self.getFlashserver_visitant)
        resp = self.post_remote_data(url=f"{self.init}/api/gate/visitant/{self.site_id}?sourcetype=0",
                                     data=data)
        code = resp.get("code", None) or resp.get("status", None)
        if not code == 200:
            return self.error_response(f"执行失败-->{self.title}")
        return self.success_response(f"执行成功-->{self.title}")

class CloseEnterprise(BaseComponent):
    """关闭企业"""
    def __init__(self,*args,**kwargs):
        self.site_id = kwargs['site_id']
        self.user_center_url = kwargs['user_center_url']
        self.title = "关闭企业"

    def process(self):
        resp = self.post_remote_data(url=f"{self.user_center_url}/enterprise/{self.site_id}/close",
                                     data={})
        code = resp.get("code", None) or resp.get("status", None)
        if not code == 200:
            return self.error_response(f"执行失败-->{self.title}")
        return self.success_response(f"执行成功-->{self.title}")