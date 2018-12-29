import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models import CASCADE

from ldap_server.configs import LOG_TYPE_CHOICES, TYPE_LOGIN, MODULES_MAP, ACTION_MAP, TYPE_LOGOUT


class OperateLog(models.Model):
    class Meta:
        permissions = (
            ("view_system-log", "Can see available system log"),
            ("view_personal-log", "Can see available personal log"),
        )

    # 1`user`,
    user = models.ForeignKey(User, on_delete=CASCADE, null=True)
    # 2`operationtime`'操作时间',
    operationtime = models.DateTimeField(auto_now=True)
    # 3`ip''用户ip',
    ip = models.CharField(max_length=20, null=True)
    # 4`action`'操作类型：1新增2删除3修改4查看5检索',
    action = models.PositiveSmallIntegerField(null=True, choices=LOG_TYPE_CHOICES)
    # 5`operationmodule`'操作模块',1：登陆 31:产品-产品 32：运维-服务组 33：运维-服务器 34：运维-节点
    operationmodule = models.CharField(max_length=100)
    # 6`operation`'操作内容',
    operation = models.TextField(null=True)
    # 修改操作的标题
    title = models.CharField(max_length=128, null=True, verbose_name="修改的标题")

    # def __str__(self):
    #     return "%s - %s" % (self.user.username, self.operationmodule)

    @classmethod
    def login(cls, request):
        logger = OperateLog(
            ip=cls.get_remote_ip(request),
            user=request.user,
            action=TYPE_LOGIN,
            operationmodule="系统登录",
        )
        logger.save()

    @classmethod
    def logout(cls, request):
        if request.user.is_authenticated:
            logger = OperateLog(
                ip=cls.get_remote_ip(request),
                user=request.user,
                action=TYPE_LOGOUT,
                operationmodule="系统登出",
            )
            logger.save()

    @classmethod
    def get_remote_ip(cls, request):
        if request.META.get("HTTP_X_FORWARDED_FOR"):
            remote_ip = request.META.get("HTTP_X_FORWARDED_FOR")
        else:
            remote_ip = request.META.get("REMOTE_ADDR")
        return remote_ip

    @classmethod
    def log_text_wrapper(cls, request):
        data = {
            "request_path": request.path,
            "request_method": request.method
        }
        if request.body:
            data.update(dict(request_body=json.loads(request.body.decode()), ))
        return json.dumps(data)

    @classmethod
    def create_log(cls, request):
        action_module = request.resolver_match.view_name
        if request.user.is_authenticated:
            logger = OperateLog(
                ip=OperateLog.get_remote_ip(request),
                user=request.user,
                action=ACTION_MAP[request.method],
                operationmodule=MODULES_MAP.get(action_module, 'None'),
                operation=cls.log_text_wrapper(request)
            )
            logger.save()


class DetailLog(models.Model):
    word = models.CharField(max_length=128, null=True, verbose_name="字段")
    name = models.CharField(max_length=128, null=True, verbose_name="名称")
    new_value = models.TextField(null=True, verbose_name="新值")
    old_value = models.TextField(null=True, verbose_name="旧值")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    log_id = models.ForeignKey('OperateLog', related_name="oper_of", on_delete=CASCADE, null=True)

    class Meta:
        verbose_name_plural = verbose_name = "日志详情模块"

    def __str__(self):
        return self.word

