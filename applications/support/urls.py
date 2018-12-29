# __author__ = itsneo1990
from django.conf.urls import url, include
from rest_framework import routers

from . import views,tests

router = routers.DefaultRouter()
router.register(r'client_down', views.ClientDownSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^get_grid_list/$', views.get_grid_list),
    url(r'^kf_manage/$', views.kf_manage),
    url(r'^letao_manage/$', views.letao_manage),
    url(r'^get_siteid_weixin/$', views.get_siteid_weixin),
    url(r'^get_server_siteid/$', views.get_server_siteid),
    url(r'^get_siteid_server/$', views.get_siteid_server),
    url(r'^get_grid_dbcon/$', views.get_grid_dbcon),
    url(r'^get_user_trail/$', views.get_user_trail),
    url(r'^supply_order/$', views.supply_order),
    url(r'^get_robot/$', views.get_robot),
    url(r'^classic_day_pwd/$', views.classic_day_pwd),
    url(r'^classic_week_pwd/$', views.classic_week_pwd),
]


api_urls = router.urls + urlpatterns
