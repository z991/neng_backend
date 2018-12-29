"""vuejs_adminlte URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from applications.setup.views import help_center
from django.conf import settings
from applications.goods.upload import upload_image
from django import views
from django.views import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from rest_framework_jwt.views import verify_jwt_token

api_urls = [
    url('^workorder/', include('applications.workorder_manage.urls')),
    url('^data/', include('applications.data_manage.urls')),
    url('^setup/', include('applications.setup.urls')),
    url('^product/', include('applications.production_manage.urls')),
    url('^goods/', include('applications.goods.urls')),
    url('^order/', include('applications.order_manage.urls')),
    url('^user/', include('applications.user_manage.urls')),
    url('^version/', include('applications.version_manage.urls')),
    url('^support/', include('applications.support.urls')),
]

admin.autodiscover()
urlpatterns = [
    url('^api/', include(api_urls)),
    url('^backend/', include('applications.backend.urls')),
    url('^permission/', include('applications.permission_and_staff_manage.urls')),
    url('^operlog/', include('applications.log_manage.urls')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^admin/', admin.site.urls),
    url(r'^setup/', include('applications.setup.urls')),
    url(r'^public/help_center', help_center),
    url(r'^admin/upload/(?P<dir_name>[^/]+)$', upload_image, name='upload_image'),
    url(r"^uploads/(?P<path>.*)$", views.static.serve, {"document_root": settings.MEDIA_ROOT, }),
    url(r'^static/(?P<path>.*)$', static.serve,{'document_root': settings.STATICFILES_DIRS}, name='static'),
]
