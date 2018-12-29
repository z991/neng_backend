# __author__ = itsneo1990
from django.db.models import DateTimeField, Model, BooleanField, Manager, QuerySet, CharField, SmallIntegerField, \
    DateField

from ldap_server.configs import DEPLOY_WAYS, CLI_CHOICES


class SoftDeleteQueryset(QuerySet):
    def delete(self):
        self.update(is_enable=False)

    def hard_delete(self):
        return super(SoftDeleteQueryset, self).delete()


class SoftDeleteManager(Manager):
    def get_queryset(self):
        return SoftDeleteQueryset(self.model, using=self._db)

    def all(self):
        queryset = self.get_queryset()
        return queryset.filter(is_enable=True)

    def items_all(self):
        return self.get_queryset()


class SoftDeleteModel(Model):
    class Meta:
        abstract = True

    is_enable = BooleanField(default=True, help_text="是否可用")
    objects = SoftDeleteManager()

    def delete(self, using=None, keep_parents=False):
        self.is_enable = False
        self.save()

    def recover(self):
        self.is_enable = True
        self.save()

    def hard_delete(self, using=None):
        return super(SoftDeleteModel, self).delete(using)


class TimeStampModel(Model):
    class Meta:
        abstract = True

    created_at = DateTimeField(auto_now_add=True, help_text="创建时间")
    updated_at = DateTimeField(auto_now=True, help_text="更新时间")


class DataHistoryModel(Model):
    class Meta:
        abstract = True

    industry = CharField(max_length=60, help_text="所属行业")
    deploy_way = SmallIntegerField(choices=DEPLOY_WAYS, help_text="部署方式")
    cli_version = SmallIntegerField(choices=CLI_CHOICES, help_text="客户版本")

    created_at = DateTimeField(auto_now=True, help_text="创建时间")
    updated_at = DateTimeField(auto_now_add=True, help_text="更新时间")
    date = DateField(help_text="记录时间")

