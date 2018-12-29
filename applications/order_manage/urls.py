from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

router = routers.DefaultRouter()
'''zxy'''
router.register(r'oa_order_list', views.OaOrderListViewSet, base_name='oa_order_list')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^create_status/$',views.status_create,name='status_create'),
]
api_urls = router.urls + urlpatterns