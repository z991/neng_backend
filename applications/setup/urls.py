# __author__ = itsneo1990
from django.conf.urls import url, include
from rest_framework import routers

from applications.setup import views

router = routers.DefaultRouter()
router.register('site-reception-group', views.SiteReceptionGroupView)
router.register(r'cli-industry', views.CliIndustrySet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^reception-groups', views.reception_groups),
    url(r'^avatar-upload', views.avatar_upload),
    url(r'^login_config', views.login_config),
    url(r'^login_models', views.login_models),
    url(r'^sync_user', views.sync_user),
    url(r'^save_accessory', views.save_accessory),
]

api_urls = router.urls + urlpatterns
