import re
import random

from .common import connect_ldap
from ldap3 import SUBTREE
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from pkcs7 import PKCS7Encoder
from applications.user_manage.models import LdapUser
from django.contrib.auth.models import User, Group


# 生成验证码
def verifycode(request):
    # 定义验证码的备选值
    str1 = 'abcd123efghijk456lmnpqrst789uvwxyz'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 6):
        rand_str += str1[random.randrange(0, len(str1))]
    request.session['verifycode'] = rand_str
    return rand_str


class AES_encrypt(object):
    def __init__(self, key):
        self.key = key
        self.BS = AES.block_size
        self.mode = AES.MODE_CBC
        # pkcs7补位 现在用的是第三方包，注释为实现原理
        self.encoder = PKCS7Encoder()

    def encrypt(self, text):
        # iv 为 b'0000000000000000' 暂时未处理
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        pad_text = self.encoder.encode(text)
        ciphertext = cryptor.encrypt(pad_text)
        # 把加密后的字符串转化为16进制字符串
        return b2a_hex(ciphertext).decode()

    # 解密后，去掉补足的空格用strip()去掉, AES.new.decrypy的返回还是 byte string
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        return self.encoder.decode(plain_text.decode())


# 删除用户所有权限
def member_clear(cn):
    user = LdapUser.objects.get(username=cn)
    user.memberof.clear()
    user.save()


# 获取角色成员
def get_member(role, group):
    try:
        with connect_ldap() as c:
            c.search('cn=%s,cn=%s,ou=Roles,dc=xiaoneng,dc=cn' % (role, group),
                     search_filter='(objectClass=groupOfUniqueNames)',
                     attributes=['*'])
            members = []
            if len(c.response) >= 1:
                mem = c.response[0]['attributes']['uniqueMember']
                for i in mem:
                    c.search(i, search_filter='(objectClass=inetOrgPerson)', attributes=['sn'])
                    if c.response==[]:
                        continue
                    members.append(c.response[0]['attributes']['sn'][0])
        return members
    except Exception as e:
        return str(e.args)


# 获取所有的角色DN
def get_group_role():
    # 目的数据
    """
        [{
            "label": "CSC-Jira - jira-administrators",
            "value": "cn=jira-administrators,cn=CSC-Jira,ou=Roles,dc=xiaoneng,dc=cn"
        },]
    """
    try:
        reg = re.compile("cn=(.*?),cn=(.*?),ou=Roles,dc=xiaoneng,dc=cn")
        response = []
        with connect_ldap() as c:
            c.search('ou=Roles,dc=xiaoneng,dc=cn', search_filter='(objectClass=groupOfUniqueNames)',
                     attributes=['cn'],
                     search_scope=SUBTREE)

            for i in c.entries:
                group = reg.match(i.entry_dn)
                if group:
                    group_name = group.group(2).lower()
                else:
                    group_name = "Unknown"
                response.append({"label": group_name + " - " + i.entry_attributes_as_dict['cn'][0].lower(),
                                 "value": i.entry_dn})
                response.sort(key=lambda x: x['label'])
        return response
    except Exception as e:
        return str(e.args)


# 处理成权限列表
def update_info(target_list):
    purpose_dict = {}
    for item in target_list:
        group = item["label"].split(' - ')[0]  # CSC-Jira <<<< CSC-Jira - jira-administrators
        role = item["label"].split(' - ')[1]  # jira-administrators <<<< CSC-Jira - jira-administrators
        if group not in purpose_dict:
            purpose_dict[group] = {role: 0}
        else:
            purpose_dict.get(group).update({role: 0})
    return purpose_dict


# 把dn列表转换为权限列表
def dn_update_permission(permission, source_permission):
    for each in permission:
        role = each.split(',')[0].split('=')[1].lower()
        group = each.split(',')[1].split('=')[1].lower()
        roles = group + ' - ' + role
        source_permission[group][roles] = 1
    return source_permission


# 把权限列表转换为dn列表
def permission_update_dn(permission_info):
    permission_list = []
    for group, value in permission_info.items():
        value = dict(value)
        for role, permission_value in value.items():
            groups = group + ' - '
            role = role.split(groups)[-1]
            if permission_value == 1:
                permission_list.append("cn=%s,cn=%s,ou=Users,dc=xiaoneng,dc=cn" % (role, group))
    return permission_list


# 获取人员角色
def get_user_role(user):
    try:
        with connect_ldap() as c:
            c.search('cn=%s,ou=Users,dc=xiaoneng,dc=cn' % user,
                     attributes=['sn', 'memberOf'], search_filter='(objectClass=inetOrgPerson)')
            members = {}
            for i in c.entries:
                members['name'] = (i.entry_attributes_as_dict['sn'][0])
                members['role'] = i.entry_attributes_as_dict['memberOf']
        return members
    except Exception as e:
        return str(e.args)


# 获取所有OA角色分组
def get_oa_group():
    group_list = []
    group = Group.objects.all()
    for g in group:
        group_list.append({"id":g.id, "name": g.name, "view": 0})
    return group_list