from django.contrib.auth.models import User, Group, Permission
from django.db import models


class Structure(models.Model):
    dpt_name = models.CharField(max_length=200, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        permissions = (
            ("view_structure", "Can see available Structure"),
        )

    def __str__(self):
        return self.dpt_name

    def __unicode__(self):
        return self.dpt_name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey('Structure', null=True, related_name='user', db_constraint=False)

    class Meta:
        permissions = (
            ("view_employee", "Can see available Employee"),
        )
