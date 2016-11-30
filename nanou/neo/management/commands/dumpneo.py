import inspect
import json
from importlib import import_module

from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.core.management.base import BaseCommand
from django.utils.module_loading import module_has_submodule

from neo.models import NeoModel


class Command(BaseCommand):
    help = 'Dumps all neo4j models'

    def handle(self, *args, **options):
        export = {
            'nodes': [],
            'relationships': [],
        }
        for app_config in apps.app_configs.values():
            if module_has_submodule(app_config.module, MODELS_MODULE_NAME):
                models_module_name = '{}.{}'.format(app_config.name, MODELS_MODULE_NAME)
                models_module = import_module(models_module_name)
                for member_name, member in inspect.getmembers(models_module, inspect.isclass):
                    if member.__module__ == models_module_name and issubclass(member, NeoModel) and member != NeoModel:
                        for obj in member.all():
                            export['nodes'].append({
                                'model': '{}.{}'.format(member.__module__, member_name),
                                'id': obj.id,
                                'attributes': obj.property_dict()
                            })
                            for start_obj, relationship, end_obj, attrs in obj.relationships():
                                export['relationships'].append({
                                    'start': {
                                        'model': '{}.{}'.format(start_obj.__module__, start_obj.__class__.__name__),
                                        'id': start_obj.id,
                                    },
                                    'end': {
                                        'model': '{}.{}'.format(end_obj.__module__, end_obj.__class__.__name__),
                                        'id': end_obj.id,
                                    },
                                    'type': relationship._RelatedObjects__match_args[1],
                                    'attributes': attrs,
                                })

        self.stdout.write(json.dumps(export, indent=4))
