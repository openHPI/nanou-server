from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


class GlobalPermissionManager(models.Manager):
    def create_global(self, **kwargs):
        db_alias = kwargs['db_alias']
        del kwargs['db_alias']

        ct, _ = ContentType.objects.using(db_alias).get_or_create(
            model='globalpermission',
            app_label=self.model._meta.app_label,
        )

        kwargs.update({'content_type': ct})
        self.using(db_alias).create(**kwargs)


class GlobalPermission(Permission):
    """A global permission, not attached to a model"""

    objects = GlobalPermissionManager()

    class Meta:
        proxy = True
        auto_created = True
