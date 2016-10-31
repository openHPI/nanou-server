from django.conf import settings
from django.core.management.commands.test import Command as TestCommand
from neokit import Warehouse

TEST_NEO_DB_NAME = '_test'


class Command(TestCommand):
    help = '''
        Discover and run tests in the specified modules or the current directory.
        In addition start a neo4j database for testing. For this the default
        neo4j database has to be stopped,but will be started again afterwards.
    '''

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        last_db = None
        warehouse = Warehouse()

        # Stop running neo db
        if self.verbosity >= 1:
            self.stdout.write('Stopping running neo4j database ...')
        for db_name, graph_server in warehouse.directory().items():
            if graph_server.running() is not None:
                last_db = db_name
                graph_server.stop()

        # Create test neo db if not existiant
        if TEST_NEO_DB_NAME not in warehouse.directory():
            if self.verbosity >= 1:
                self.stdout.write('Installing test neo4j database ...')
            warehouse.install(TEST_NEO_DB_NAME)
            test_db = warehouse.get(TEST_NEO_DB_NAME)
            test_db.http_port = settings.TEST_NEO_DATABASE['http_port']
            test_db.auth_enabled = False
        else:
            if self.verbosity >= 2:
                self.stdout.write('(Skip) Installing test neo4j database')

        # Start test neo db
        if self.verbosity >= 1:
            self.stdout.write('Starting test neo4j database ...')
        warehouse.get(TEST_NEO_DB_NAME).start()

        # Run tests
        super(Command, self).handle(*args, **options)

        # Stop test neo db
        if self.verbosity >= 1:
            self.stdout.write('Stopping test neo4j database ...')
        warehouse.get(TEST_NEO_DB_NAME).stop()

        # Start paused neo db
        if last_db:
            if self.verbosity >= 1:
                self.stdout.write('Starting last neo4j database ...')
            warehouse.get(last_db).start()
        else:
            if self.verbosity >= 2:
                self.stdout.write('(Skip) Starting last neo4j database')
