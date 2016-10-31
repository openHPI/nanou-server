import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from py2neo.ogm import Property, Related

from neo.utils import NeoGraph


class Command(BaseCommand):
    help = 'Loads given neo4j models'

    def add_arguments(self, parser):
        parser.add_argument('args', metavar='fixture', nargs='+', help='Fixture labels.')

    def handle(self, *fixture_paths, **options):
        self.verbosity = options['verbosity']

        for path in fixture_paths:
            object_map = dict()
            relationship_count = 0
            with open(os.path.join(settings.BASE_DIR, path), 'r') as fixture_file:
                data = json.load(fixture_file)

                # create objects with properties
                for entry in data:
                    model_class = _model_class(entry)
                    obj = model_class()
                    for prop_name in _properties(model_class):
                        setattr(obj, prop_name, entry['fields'][prop_name])
                    object_map[entry['id']] = obj

                # create relationship between objects
                for entry in data:
                    model_class = _model_class(entry)
                    obj = object_map[entry['id']]
                    for prop_name in _relationships(model_class):
                        related_objects = getattr(obj, prop_name)
                        for related_id in entry['fields'][prop_name]:
                            rel_obj = object_map[related_id]
                            related_objects.add(rel_obj)
                            relationship_count += 1

            with NeoGraph() as graph:
                for obj in object_map.values():
                    graph.create(obj)
            if self.verbosity >= 1:
                self.stdout.write('{path}: {obj_count} objects and {rel_count} relationships created'.format(**{
                    'path': path,
                    'obj_count': len(object_map),
                    'rel_count': relationship_count/2,
                }))


def _model_class(entry):
    module_name, _, class_name = entry['model'].rpartition('.')
    module = __import__(module_name, fromlist='.')
    return getattr(module, class_name)


def _properties(model_class):
    return (
        prop_name
        for prop_name, prop in model_class.__dict__.items()
        if (not(prop_name.startswith('__') and prop_name.endswith('__'))
            and isinstance(prop, Property))
    )


def _relationships(model_class):
    return (
        rel_name
        for rel_name, rel in model_class.__dict__.items()
        if (not(rel_name.startswith('__') and rel_name.endswith('__'))
            and isinstance(rel, Related))
    )
