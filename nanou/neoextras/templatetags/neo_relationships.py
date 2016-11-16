import inspect
from importlib import import_module

from django import template
from django.apps import apps
from django.apps.config import MODELS_MODULE_NAME
from django.utils.module_loading import module_has_submodule

from neo.models import NeoModel

register = template.Library()


def _find_neomodel_class(node):
    for app_config in apps.app_configs.values():
        if module_has_submodule(app_config.module, MODELS_MODULE_NAME):
            models_module_name = '{}.{}'.format(app_config.name, MODELS_MODULE_NAME)
            models_module = import_module(models_module_name)
            for member_name, member in inspect.getmembers(models_module, inspect.isclass):
                if member.__module__ == models_module_name and issubclass(member, NeoModel) and member != NeoModel:
                    if member.__primarylabel__ in node._Node__labels:
                        return member


def _find_neomodel(node):
    cls = _find_neomodel_class(node)
    return cls.wrap(node)


@register.simple_tag
def model_for_node(node):
    obj = _find_neomodel(node)
    return obj.get_absolute_url()
