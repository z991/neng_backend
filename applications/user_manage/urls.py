from django.conf.urls import url, include
from rest_framework import routers

from . import views, views_reset, views_personal

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^', include(router.urls)),
    # 用户列表
    url(r'^user_list/$', views.user_list),
    # 用户详情
    url(r'^user_detail/$', views.user_detail),
    # 用户组列表&新增
    url(r'^user_add/$', views.user_add),
    # 用户修改
    url(r'^user_put/$', views.user_put),
    # 用户删除
    url(r'^user_delete/$', views.user_delete),
    # 用户新增
    url(r'^all_permission/$', views.get_all_groups),

    # views_reset
    url(r'^reset_passwd/$', views_reset.resetpasswd_url),
    url(r'^reset/$', views_reset.reset),
    url(r'^verify_code/$', views_reset.verify_code),
    # 个人修改密码
    url(r'^change_pwd/$', views_personal.personal_changepassword),

    # ldap用户同步到本地数据库
    url(r'^ldap_local/$', views.ldap_local),

]
api_urls = router.urls + urlpatterns