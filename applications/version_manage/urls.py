from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'versionrepository', views.VersionRepositoryManage, base_name='versionrepository')
router.register(r'versionproduct', views.VersionProductManage, base_name='versionproduct')

urlpatterns = [
    url(r'^', include(router.urls)),
]

api_urls = router.urls + urlpatterns
