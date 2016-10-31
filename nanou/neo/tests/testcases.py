from django.core.management import call_command
from django.test import TestCase

from neo.utils import NeoGraph


class NeoTestCase(TestCase):
    neo_fixtures = None

    def _pre_setup(self):
        super(NeoTestCase, self)._pre_setup()
        if self.neo_fixtures:
            call_command('loadneo', *self.neo_fixtures, **{
                'verbosity': 0,
            })

    def _post_teardown(self):
        super(NeoTestCase, self)._post_teardown()
        if self.neo_fixtures:
            with NeoGraph() as graph:
                graph.run('MATCH (a)-[r]->(b) DELETE a, r, b')
                graph.run('MATCH (a) DELETE a')
