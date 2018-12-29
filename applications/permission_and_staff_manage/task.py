import logging

from celery import shared_task
from django.contrib.auth.models import User, Group

from applications.backend.models import LdapStructure, LdapUser, LdapRole
from applications.permission_and_staff_manage.models import Structure

logger = logging.getLogger(__name__)


@shared_task
def sync_ldap():
    logger.info("start sync ldap data")
    build_structure()
    build_user()
    build_role()
    logger.info("sync ldap data complete")


def build_structure():
    structures = LdapStructure.objects.all()
    structure_tree = []
    structure_ids = []
    for structure in structures:
        ou_list = []
        for ou in structure.dn.split(","):
            if ou.startswith("ou="):
                ou_list.append(ou)
        if ou_list:
            structure_tree.append(ou_list)
    structure_tree.sort(key=len)

    for each in structure_tree:
        # 根级目录
        if len(each) == 1:
            obj, _ = Structure.objects.update_or_create(dpt_name=each[0].split("ou=")[1],
                                                        defaults={"parent": None})
            structure_ids.append(obj.id)
        # 子级目录
        else:
            obj, _ = Structure.objects.update_or_create(
                dpt_name=each[0].split("ou=")[1],
                defaults={"parent": Structure.objects.get(dpt_name=each[1].split("ou=")[1])}
            )
            structure_ids.append(obj.id)

    Structure.objects.exclude(id__in=structure_ids).delete()


def build_user():
    users = LdapUser.objects.all()
    user_ids = []
    for user in users:
        defaults = {
            "username": user.username,
            "last_name": user.user_sn,
            "email": user.email,
            "password": user.password
        }
        obj, _ = User.objects.update_or_create(username=user.username, defaults=defaults)
        user_ids.append(obj.id)
    superusers = [user.id for user in User.objects.filter(is_superuser=True)]
    user_ids.extend(superusers)
    User.objects.exclude(id__in=user_ids).delete()


def get_users(members: list):
    user_names = []
    for member in members:
        for element in member.split(","):
            if element.startswith("cn="):
                user_names.append(element.split("cn=")[1])
                break
    return User.objects.filter(username__in=user_names)


def build_role():
    roles = LdapRole.objects.all()
    role_ids = []
    users_have_group = set()
    for role in roles:
        obj, _ = Group.objects.get_or_create(name=role.cn)
        role_ids.append(obj.id)
        users = get_users(role.member)
        obj.user_set.set(objs=users)
        users_have_group.update(users.values_list("id", flat=True))
    Group.objects.exclude(id__in=role_ids).delete()
    default_group = Group.objects.get(name="小能人")
    default_group.user_set.set(User.objects.exclude(id__in=users_have_group))
