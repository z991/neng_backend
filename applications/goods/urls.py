from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

router = routers.DefaultRouter()
'''zxy'''
router.register(r'tagclass', views.TagManageSet)
router.register(r'goodsmodel', views.GoodsModelSet, base_name='goodsmodel')
router.register(r'filtermodel', views.FilterModelSet, base_name='filtermodel')
router.register(r'single_multiple',views.SingleMultipleSet,base_name='singlemultiple')

'''yzq'''
router.register(r'singleproduct', views.SingleProductManageset)
router.register(r'multipleprodut', views.MultipleProductManageset)
router.register(r'advertising_manage', views.AdvertisingViewSet, base_name='advertising_manage')
router.register(r'specification', views.SpecificationParameterViewSet, base_name='specification')

urlpatterns = [
    url(r'^', include(router.urls)),
    #zxy
    url(r'oa_put_up', views.put_up, name='put_up'),
    url(r'oa_put_off', views.put_off, name='put_off'),
    url(r'listputaway/$',views.list_put_up,name='list_put_up'),
    url(r'put_select/$',views.put_goods, name='put_goods'),
    url(r'create_put_up',views.create_put_up, name='create_put_up'),
    url(r'delete_put', views.delete_put, name='delete_put'),
    url(r'test_put', views.test_put,name="test_put"),


    #yzq
    url(r'^label_list/$', views.label_list),
    url(r'^function/$', views.function_list),
    url(r'^selection/$', views.selection_list),
    url(r'^parent/$', views.parent_list),

    url(r'^pro_list/$', views.product_list),
    url(r'^member_list/$', views.Members_list),
    url(r'^models_list/$', views.models_list),
    url(r'^get_editor/$', views.get_editor),
    url(r'^ad_put/$', views.ad_put),
    url(r'^ad_time/$', views.ad_time),
]

api_urls = router.urls + urlpatterns
