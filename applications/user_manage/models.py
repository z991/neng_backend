import ldapdb.models
from ldapdb.models.fields import CharField, IntegerField, ListField
from django.db import connections, router
from libs.login_set import get_login_model

import ldap
import logging

logger = logging.getLogger('django')


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
#   meta-data
    try:
        user_search = get_login_model()

        base_dn = user_search.user_ldapsearch
    except:
        pass
    object_classes = ['inetOrgPerson']

#    基类已经定义dn
#    dn = CharField(max_length=200, primary_key=True)

    username = CharField(db_column='cn', primary_key=True)
#   定义多处主键时会影响到rdn的生成，最后完整dn生成规则是几个primarykey+base_dn组成。
    user_sn = CharField(db_column='sn')
    email = CharField(db_column='mail', blank=True)
    phone = CharField(db_column='telephoneNumber', blank=True)
    password = CharField(db_column='userPassword')
    sshpublickey =CharField(db_column='sshpublickey', blank=True)
    memberof = ListField(db_column="memberOf", blank=True)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.username

    def _save_table(self, raw=False, cls=None, force_insert=None, force_update=None, using=None, update_fields=None):
        """
        Saves the current instance.
        """
        # Connection aliasing
        connection = connections[using]

        create = bool(force_insert or not self.dn)

        # Prepare fields
        if update_fields:
            target_fields = [
                self._meta.get_field(name)
                for name in update_fields
            ]
        else:
            target_fields = [
                field
                for field in cls._meta.get_fields(include_hidden=True)
                if field.concrete and not field.primary_key
            ]

        def get_field_value(field, instance):
            python_value = getattr(instance, field.attname)
            return field.get_db_prep_save(python_value, connection=connection)

        if create:
            old = None
        else:
            old = cls.objects.using(using).get(pk=self.saved_pk)
        changes = {
            field.db_column: (
                None if old is None else get_field_value(field, old),
                get_field_value(field, self),
            )
            for field in target_fields
        }

        # Actual saving

        old_dn = self.dn
        new_dn = self.build_dn()
        updated = False

        # Insertion
        if create:
            # FIXME(rbarrois): This should be handled through a hidden field.
            hidden_values = [
                ('objectClass', [obj_class.encode('utf-8') for obj_class in self.object_classes])
            ]
            new_values = hidden_values + [
                (colname, change[1])
                for colname, change in sorted(changes.items())
                if change[1] is not None
            ]
            new_dn = self.build_dn()
            logger.debug("Creating new LDAP entry %s", new_dn)
            connection.add_s(new_dn, new_values)

        # Update
        else:
            modlist = []
            for colname, change in sorted(changes.items()):
                old_value, new_value = change
                if old_value == new_value:
                    continue
                modlist.append((
                    ldap.MOD_DELETE if new_value is None else ldap.MOD_REPLACE,
                    colname,
                    new_value,
                ))
#          if new_dn != old_dn:
#               logger.debug("renaming ldap entry %s to %s", old_dn, new_dn)
#               connection.rename_s(old_dn, self.build_rdn())

#            logger.debug("Modifying existing LDAP entry %s", new_dn)
#            connection.modify_s(new_dn, modlist)
#            updated = True
            # FIXME  重写了这个因为 build_dn 有坑
            logger.debug("Modifying existing LDAP entry %s", old_dn)
            connection.modify_s(old_dn, modlist)
            updated = True

        self.dn = new_dn

        # Finishing
        self.saved_pk = self.pk
        return updated

