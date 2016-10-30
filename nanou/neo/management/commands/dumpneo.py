from importlib import import_module
import inspect
import json

from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.core.management.base import BaseCommand
from django.utils.module_loading import module_has_submodule

from neo.models import NeoModel


class Command(BaseCommand):
    help = 'Dumps all neo4j models'

    def handle(self, *args, **options):
        export = list()
        for app_config in apps.app_configs.values():
            if module_has_submodule(app_config.module, MODELS_MODULE_NAME):
                models_module_name = '{}.{}'.format(app_config.name, MODELS_MODULE_NAME)
                models_module = import_module(models_module_name)
                for member_name, member in inspect.getmembers(models_module, inspect.isclass):
                    if issubclass(member, NeoModel) and member != NeoModel:
                        for obj in member.all():
                            export.append({
                                'model': '{}.{}'.format(member.__module__, member_name),
                                'id': obj.id,
                                'fields': obj.value_dict()
                            })
        self.stdout.write(json.dumps(export, indent=4))
