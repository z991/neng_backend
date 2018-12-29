# __author__ = itsneo1990
from rest_framework.permissions import BasePermission
from rest_framework.response import Response


# 帮助中心设置
class SiteReceptionGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("setup.view_sitereceptiongroup")
        elif request.method == 'POST':
            return request.user.has_perm("setup.add_sitereceptiongroup")
        elif request.method == 'PUT':
            return request.user.has_perm("setup.change_sitereceptiongroup")
        elif request.method == 'DELETE':
            return request.user.has_perm("setup.delete_sitereceptiongroup")
        return False


# 客户行业设置
class IndustryGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("workorder_manage.view_industry")
        elif request.method == 'POST':
            return request.user.has_perm("workorder_manage.add_industry")
        elif request.method == 'PUT':
            return request.user.has_perm("workorder_manage.change_industry")
        elif request.method == 'DELETE':
            return request.user.has_perm("workorder_manage.delete_industry")
        return False


class RoleGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("user_manage.view_role")
        elif request.method == 'POST':
            return request.user.has_perm("user_manage.add_role")
        elif request.method == 'PUT':
            return request.user.has_perm("user_manage.change_role")
        elif request.method == 'DELETE':
            return request.user.has_perm("user_manage.delete_role")
        return False


class SystemUserPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("user_manage.view_system_user")
        elif request.method == 'POST':
            return request.user.has_perm("user_manage.add_system_user")
        elif request.method == 'PUT':
            return request.user.has_perm("user_manage.change_system_user")
        elif request.method == 'DELETE':
            return request.user.has_perm("user_manage.delete_system_user")
        return False


# 用户组(角色)权限
class GroupListPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("auth.view_group")
        elif request.method == 'POST':
            return request.user.has_perm("auth.add_group")
        elif request.method == 'PUT':
            return request.user.has_perm("auth.change_group")
        elif request.method == 'DELETE':
            return request.user.has_perm("auth.delete_group")
        return False

class UserPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("auth.view_user")
        elif request.method == 'POST':
            return request.user.has_perm("auth.add_user")
        elif request.method == 'PUT':
            return request.user.has_perm("auth.change_user")
        elif request.method == 'DELETE':
            return request.user.has_perm("auth.delete_user")
        return False


# 登录配置
class LoginConfigPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("setup.view_loginconfig")
        elif request.method == 'POST':
            return request.user.has_perm("setup.change_loginconfig")
        elif request.method == 'PUT':
            return request.user.has_perm("setup.change_loginconfig")
        return False


# 单品的组权限
class SingleGoodsGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_singlegoods")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_singlegoods")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_singlegoods")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_singlegoods")
        return False


# 广告的组权限
class AdvertisingGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_advertising")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_advertising")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_advertising")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_advertising")
        return False


# 行业解决方案的组权限
class MultipleGoodsGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_multiplegoods")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_multiplegoods")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_multiplegoods")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_multiplegoods")
        return False


# 上架的组权限
class PutawayGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_putaway")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_putaway")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_putaway")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_putaway")
        return False


# 模块的组权限
class GoodsModelGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_goodsmodel")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_goodsmodel")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_goodsmodel")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_goodsmodel")
        return False


# 标签的组权限
class TagClassGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("goods.view_tagclass")
        elif request.method == 'POST':
            return request.user.has_perm("goods.add_tagclass")
        elif request.method == 'PUT':
            return request.user.has_perm("goods.change_tagclass")
        elif request.method == 'DELETE':
            return request.user.has_perm("goods.delete_tagclass")
        return False


# 标签的组权限
class WorkOrderGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("workorder_manage.view_openstationmanage")
        elif request.method == 'POST':
            return request.user.has_perm("workorder_manage.add_openstationmanage")
        elif request.method == 'PUT':
            return request.user.has_perm("workorder_manage.change_openstationmanage")
        elif request.method == 'DELETE':
            return request.user.has_perm("workorder_manage.delete_openstationmanage")
        return False


# 节点的组权限
class GridGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_grid")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_grid")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_grid")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_grid")
        return False


# 服务组的组权限
class ServerGroupsGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_servergroup")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_servergroup")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_servergroup")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_servergroup")
        return False


# 重构版服务的组权限
class ReServerGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_server")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_server")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_server")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_server")
        return False


# 经典版服务的组权限
class ServerGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_server")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_server")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_server")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_server")
        return False


# 经典版产品配置的组权限
class ProductGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_product")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_product")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_product")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_product")
        return False


# 重构版产品配置的组权限
class ReProductGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("production_manage.view_product")
        elif request.method == 'POST':
            return request.user.has_perm("production_manage.add_product")
        elif request.method == 'PUT':
            return request.user.has_perm("production_manage.change_product")
        elif request.method == 'DELETE':
            return request.user.has_perm("production_manage.delete_product")
        return False


# 订单的组权限
class OrderGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("order_manage.view_orderinfo")
        elif request.method == 'POST':
            return request.user.has_perm("order_manage.add_orderinfo")
        elif request.method == 'PUT':
            return request.user.has_perm("order_manage.change_orderinfo")
        return False


# 版本库权限
class VersionPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("version_manage.view_versionrepository")
        elif request.method == 'POST':
            return request.user.has_perm("version_manage.add_versionrepository")
        elif request.method == 'PUT':
            return request.user.has_perm("version_manage.change_versionrepository")
        elif request.method == 'DELETE':
            return request.user.has_perm("version_manage.delete_versionrepository")
        return False


# 版本产品权限
class VersionProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("version_manage.view_versionproduct")
        elif request.method == 'POST':
            return request.user.has_perm("version_manage.add_versionproduct")
        elif request.method == 'PUT':
            return request.user.has_perm("version_manage.change_versionproduct")
        elif request.method == 'DELETE':
            return request.user.has_perm("version_manage.delete_versionproduct")
        return False


# 数据总览权限
class DataOverviewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            a = request.user.has_perm("data_overview.view_data-overview")
            print('a==', a, type(a))
            return request.user.has_perm("data_overview.view_data-overview")
        return False


# 企业数据权限
class CompanyDataPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("data_manage.view_company-inquire")
        return False


# 渠道统计权限
class ChannelDataPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("data_manage.view_channel-inquire")
        return False


# 站点/行业统计权限
class IndustrySiteDataPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("data_manage.view_site-industry")
        return False


# 节点统计权限
class GridDataPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("data_manage.view_grid-inquire")
        return False

# 客户库查看权限
class CustomerKHKPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("workorder_manage.view_customer-khk")
        elif request.method == 'POST':
            return request.user.has_perm("workorder_manage.add_customer-khk")
        elif request.method == 'PUT':
            return request.user.has_perm("workorder_manage.change_customer-khk")
        return False

# 运营工具模块权限
class OperatingToolsPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("operatingtools.view_support")
        if request.method == "POST":
            return request.user.has_perm("operatingtools.view_support")
        if request.method == "PUT":
            return request.user.has_perm("operatingtools.view_support")
        if request.method == "DELETE":
            return request.user.has_perm("operatingtools.view_support")


# 执行脚本权限
class ScriptPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("operatingtools.view_script-execution")


# 培训管理分配讲师
class LecturerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("matter_train.change_distribution-lecturer")
        return False


# 培训管理问题驳回
class RejectPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("matter_train.change_reject")
        return False


# 培训管理创建问题
class CreateTrainPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'POST' or request.method == 'PUT':
            return request.user.has_perm("matter_train.add_create-train")
        return False


# 培训管理调查人员分配
class PersonnelAllocationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_personnel-allocation")
        return False


# 培训管理沟通培训需求创建
class CommunicationPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_communication-requirements")
        return False


# 培训管理培训准备
class TrainingPreparePermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_training-prepare")
        return False


# 培训管理待客户排期
class SetPendingPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("change_set-pending")
        return False


# 培训管理客户终止培训
class TerminationTrainingPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_termination-training")
        return False


# 培训管理培训
class TrainningPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_trainning")
        return False


# 培训管理遗留问题交接
class HandoverIssuesPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_handover-issues")
        return False


# 培训管理确定排期
class DetermineSchedulingPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_determine-scheduling")
        return False


# 培训管理满意度调查
class SatisfactionSurveyPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_satisfaction-survey")
        return False


# 培训管理遗留问题确认
class IdentificationIssuesPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'PUT':
            return request.user.has_perm("change_identification-issues")
        return False


# 培训管理问题备注新增
class RemarkPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'POST':
            return request.user.has_perm("add_remark")
        return False