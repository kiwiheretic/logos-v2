# logos_test_runner.py
import shutil
import os
from logos import settings

# Because our bible database is huge, and takes a long time to generate
# we don't want to regenerate it for every test case.
from django.test.runner import DiscoverRunner, dependency_ordered
import pdb

class LogosDiscoverRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        from django.db import connections, DEFAULT_DB_ALIAS
        verbosity = self.verbosity
        interactive = self.interactive

        script_path = os.path.dirname(os.path.realpath(__file__))
        db_path = os.path.realpath(os.path.join(script_path,"..","..",
                               "sqlite-databases", "bibles.sqlite3.db" ))
        self.test_db_path = os.path.realpath(os.path.join(script_path,"..","..",
                               "sqlite-databases", "test-bibles.sqlite3.db" ))

        if not os.path.exists(self.test_db_path):
            shutil.copyfile(db_path, self.test_db_path)
        

        # First pass -- work out which databases actually need to be created,
        # and which ones are test mirrors or duplicate entries in DATABASES
        mirrored_aliases = {}
        test_databases = {}
        dependencies = {}

        default_sig = connections[DEFAULT_DB_ALIAS].creation.test_db_signature()
        for alias in connections:
            connection = connections[alias]
            test_settings = connection.settings_dict['TEST']
            if test_settings['MIRROR']:
                # If the database is marked as a test mirror, save
                # the alias.b 
                mirrored_aliases[alias] = test_settings['MIRROR']
            else:
                # Store a tuple with DB parameters that uniquely identify it.
                # If we have two aliases with the same values for that tuple,
                # we only need to create the test database once.
                item = test_databases.setdefault(
                    connection.creation.test_db_signature(),
                    (connection.settings_dict['NAME'], set())
                )
                item[1].add(alias)

                if 'DEPENDENCIES' in test_settings:
                    dependencies[alias] = test_settings['DEPENDENCIES']
                else:
                    if alias != DEFAULT_DB_ALIAS and connection.creation.test_db_signature() != default_sig:
                        dependencies[alias] = test_settings.get('DEPENDENCIES', [DEFAULT_DB_ALIAS])

        # Second pass -- actually create the databases.
        old_names = []
        mirrors = []

        for signature, (db_name, aliases) in dependency_ordered(
                test_databases.items(), dependencies):
            test_db_name = None

            # Actually create the database for the first connection
            for alias in aliases:
                print alias
                connection = connections[alias]
                if test_db_name is None:
                    if 'CLOBBER_TEST_DB' not in connection.settings_dict or \
                    connection.settings_dict['CLOBBER_TEST_DB'] == True:
                        test_db_name = connection.creation.create_test_db(
                            verbosity,
                            autoclobber=not interactive,
                            serialize=connection.settings_dict.get("TEST_SERIALIZE", True),
                        )
                        destroy = True
                    else:
                        connection.settings_dict['NAME'] = \
                            connection.settings_dict['TEST']['NAME']
                        destroy = False
                else:
                    connection.settings_dict['NAME'] = test_db_name
                    destroy = False
                old_names.append((connection, db_name, destroy))

        for alias, mirror_alias in mirrored_aliases.items():
            mirrors.append((alias, connections[alias].settings_dict['NAME']))
            connections[alias].settings_dict['NAME'] = (
                connections[mirror_alias].settings_dict['NAME'])

        return old_names, mirrors

    def teardown_databases(self, old_config, **kwargs):
        connections, mirrors = old_config
        for conn, _, _ in connections:
            if 'CLOBBER_TEST_DB' in conn.settings_dict and \
                conn.settings_dict['CLOBBER_TEST_DB'] == False:
                
                conn.close()
            
 
        os.remove(self.test_db_path)
    
