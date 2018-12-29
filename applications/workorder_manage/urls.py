from django.conf.urls import url, include
from rest_framework import routers

from . import views, views_matter, views_product

router = routers.DefaultRouter()
router.register(r'openstation', views.OpenStationManageSet, base_name='openstation')
router.register(r'companyinfo', views.CompanyInfoSet)
router.register(r'stationinfo', views.StationInfoSet)
router.register(r'industry', views.IndustrySet)
router.register(r'areainfo', views.AreaInfoSet)
router.register(r'khkcompany', views.CompanyManageSet)
router.register(r'khkorder', views.OrderManageSet)
router.register(r'matter_flow', views_matter.MatterFlowViewsets)
router.register(r'simple_matter', views_matter.SimpleMatterViewsets)
router.register(r'product_config', views_product.ProductConfigurationSet)
router.register(r'simple_config', views_product.SimpleProductConfigurationSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='workorder_rest_framework')),
    url(r'^customer-oper/$', views.customer_oper_type),
    # 以site为维度同步
    url(r'^update_site/$', views.update_site_open_station),
    # 同步站点行业信息（导入）
    url(r'^syn_industry/$', views.syn_station_industry),
    # 同步cli_version 客户版本到企业信息表
    url(r'^cli_version/$', views.update_cli_version),
]
