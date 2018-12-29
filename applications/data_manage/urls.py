from django.conf.urls import url, include
from rest_framework import routers

from . import views, views_home, views_classic, views_script

router = routers.DefaultRouter()
router.register(r'pandect', views.PandectViewSet)
router.register(r'online-client', views.OnlineClientDataViewSet)
router.register(r'channel', views.ChannelInquiriesViewSet)
router.register(r'customer-use', views.CustomerUseViewSet)
router.register(r'online-product', views.OnlineProductViewSet)
router.register(r'site-oper', views.SiteOperViewSet)
router.register(r'grid_inquires', views.GridInquiresView)
router.register(r'sergrp_inquires', views.SerGrpInquriesViewSet)
router.register(r'channel_data', views_classic.ChannelData, base_name='channel_data')


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^channellist/$', views.channellist),
    url(r'^customer_nature_matching/$', views.customer_nature_matching),
    url(r'^get_company_id/$', views.get_company_id),
    url(r'^cost_statistics/$', views.cost_statistics),
    url(r'^contract_amount/$', views.customer_contract_amount),
    url(r'^home_top/$', views_home.home_top, name="home_top"),
    url(r'^home_rest/$', views_home.home_rest, name="home_rest"),
    url(r'^company_data/$', views_home.company_data, name="company_data"),
    # 测试脚本
    url(r'^update_data_test/$', views.get_test),
    url(r'^get_date_test/$', views.get_date_test),

    url(r'^get_channel_data/$', views.channel_data),
    url(r'^get_industry_data/$', views.get_industry_data),
    url(r'^get_grid_data/$', views.get_grid_data),
    # 获取表格数据(节点数据中的表格)
    url(r'^get_form_data/$', views.get_form_data),

    # 站点最上方表格数据
    url(r'^get_action_data/$', views.get_action_data),
    # 站点运营数据变化趋势---------多条折线
    url(r'^get_station_number/$', views.get_station_number),
    # 站点总数变化趋势------一条折线
    url(r'^get_station_total/$', views.get_station_total),
    # 运营指标列表
    url(r'^get_index/$', views.get_index),

    url(r'^jd_company_data/$', views_home.jd_company_data, name="jd_company_data"),
    url(r'^jd_home_top/$', views_home.jd_home_top, name="jd_home_top"),
    url(r'^jd_home_rest/$', views_home.jd_home_rest, name="jd_home_rest"),
    url(r'^jd_grid_data/$', views_home.jd_grid_data, name="jd_grid_data"),
    url(r'^jd_grid_form/$', views_home.jd_grid_form, name="jd_grid_form"),
    # 测试c重构咨询访客
    url(r'^test_channel/$', views_classic.test_channel),

    # 添加历史重构咨询访客  2018-10-31
    url(r'^test_history_channel/$', views_script.test_history_channel),
    # 添加历史经典咨询  2018-11-07
    url(r'^test_consult/$', views_script.get_consult),
    # 添加历史经典访客  2018-11-07
    url(r'^test_visitor/$', views_script.get_visitor),
    # 以grid为维度同步  同步站点 2018-10-31
    url(r'^update_grid/$', views_script.update_grid_open_station),
    # 全部同步  同步站点 2018-10-31
    url(r'^update_all/$', views_script.update_all_open_station),
    url(r'^update_siteid/$', views_script.update_siteid_open_station),
    # 获取脚本名称列表页   2018-11-01
    url(r'^get_script_name/$', views_script.get_script_name),
    # 获取脚本执行记录
    url(r'^get_script_record/$', views_script.get_script_record),
]

api_urls = router.urls + urlpatterns
