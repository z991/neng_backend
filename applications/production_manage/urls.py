from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'product', views.ProductViewSet)
router.register(r'ref-product', views.RefProductViewSet)
router.register(r'server', views.ServerViewSet)
router.register(r'group', views.GroupViewSet)
router.register(r'grid', views.GridViewSet)
router.register(r'function', views.FunctionViewSet)
router.register(r'version', views.VersionViewSet)
router.register(r'selection', views.SelectionViewSet)
router.register(r'sertype', views.SerTypeViewSet)
router.register(r'database', views.DataBaseInfoViewSet)
router.register(r'seraddress', views.SerAddressViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^deployway/$', views.deployway),
    url(r'^deploy_way_grid_ship/$', views.deploy_way_grid_ship),
    url(r'^deploy_way_group_ship/$', views.deploy_way_group_ship),
    url(r'^function-selection-import/$', views.function_selection_import),
    url(r'^version_type/$', views.version_type),
    url(r'^func_selec/$', views.func_selec),
    url(r'^auto_group_grid/$', views.auto_group_grid, name="auto_group_grid")
]

api_urls = router.urls + urlpatterns
