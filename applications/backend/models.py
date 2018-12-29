import ldapdb.models
from ldapdb.models.fields import CharField, ListField


class LdapUser(ldapdb.models.Model):
    base_dn = "ou=Users,dc=xiaoneng,dc=cn"
    object_classes = ['inetOrgPerson']

    username = CharField(db_column='cn', primary_key=True)
    user_sn = CharField(db_column='sn')
    email = CharField(db_column='mail', blank=True)
    phone = CharField(db_column='telephoneNumber', blank=True)
    password = CharField(db_column='userPassword')
    sshpublickey = CharField(db_column='sshpublickey', blank=True)

    def __str__(self):
        return self.username


class LdapRole(ldapdb.models.Model):
    base_dn = "cn=OA,ou=Roles,dc=xiaoneng,dc=cn"
    object_classes = ['groupOfUniqueNames']
    cn = CharField(db_column='cn', max_length=200, primary_key=True)
    member = ListField(db_column='uniqueMember')

    def __str__(self):
        return self.cn


class LdapStructure(ldapdb.models.Model):
    base_dn = "ou=Users,dc=xiaoneng,dc=cn"
    object_classes = ['organizationalUnit']
    ou = CharField(db_column='ou', max_length=200, primary_key=True)

    def __str__(self):
        return self.ou
