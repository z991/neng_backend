from django.conf.urls import url
from rest_framework import routers
# from rest_framework_jwt.views import obtain_jwt_token

from applications.backend import views,tests
from applications.backend import viewsUtil

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

api_urls = router.urls + [
]

urlpatterns = [
    url(r'^login/$', views.login),
    # url(r'^jwt_login/', obtain_jwt_token),
    url(r'^logout/$', views.logout),
    url(r'^verifycode/$', viewsUtil.verifycode),
    url(r'^push_service_infopush/$', tests.push_service_infopush),
    url(r'^apitest/$', tests.apitest),
    url(r'^new_gongdan/$', tests.new_gongdan),
    url(r'^push_service_infopush/$', tests.push_service_infopush),
    url(r'^celery_push/$', tests.celery_push),
    url(r'^test/$', tests.test),
    url(r'^push_cg/$', tests.push_cg),

]
