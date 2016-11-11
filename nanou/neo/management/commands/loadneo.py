import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from py2neo.ogm import RelatedTo

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
                nodes = data.get('nodes', [])
                relationships = data.get('relationships', [])

                # create objects with properties
                for node_entry in nodes:
                    model_class = _model_class(node_entry)
                    obj = model_class()
                    for name, value in node_entry['attributes'].items():
                        setattr(obj, name, value)
                    object_map[node_entry['id']] = obj

                # create relationship between objects
                for rel_entry in relationships:
                    start_obj = object_map[rel_entry['start_node_id']]
                    end_obj = object_map[rel_entry['end_node_id']]
                    selection, to_obj = _find_selection(start_obj, end_obj, rel_entry['type'])
                    selection.add(to_obj, rel_entry['attributes'])
                    relationship_count += 1

            with NeoGraph() as graph:
                for obj in object_map.values():
                    graph.create(obj)
            if self.verbosity >= 1:
                self.stdout.write('{path}: {obj_count} objects and {rel_count} relationships created'.format(**{
                    'path': path,
                    'obj_count': len(object_map),
                    'rel_count': relationship_count,
                }))


def _model_class(entry):
    module_name, _, class_name = entry['model'].rpartition('.')
    module = __import__(module_name, fromlist='.')
    return getattr(module, class_name)


def _find_selection(start_obj, end_obj, rel_type):
    for relationship_name, relationship in start_obj.__class__.__dict__.items():
        if isinstance(relationship, RelatedTo):
            selection = getattr(start_obj, relationship_name)
            if selection._RelatedObjects__match_args[1] == rel_type:
                return selection, end_obj
    for relationship_name, relationship in end_obj.__class__.__dict__.items():
        if isinstance(relationship, RelatedTo):
            selection = getattr(end_obj, relationship_name)
            if selection._RelatedObjects__match_args[1] == rel_type:
                return selection, start_obj
