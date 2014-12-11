# LogosRouter.py
import pdb

bible_tables = ('BibleTranslations', 'BibleBooks', 
               'BibleVerses', 'BibleConcordance', 
               'BibleDict')

settings_tables = ('Settings',
                 'BibleColours', 'RoomOptions',)

#settings_tables = ('BibleReading', 
#                   'Settings',
#                 'BibleSearchHeader','BibleSearchResults',
#                 'UserWords',
#                 'BibleColours', 'RoomOptions',
#                 'StatusMessages')


scripture_game_tables = ('GameGames', 'GameUsers', 'GameSolveAttempts')

class LogosRouter(object):
    def db_for_read(self, model, **hints):
        """
        Select DB to read from
        """
        if model._meta.object_name in bible_tables:
            return 'bibles'
        elif model._meta.object_name in settings_tables:
            return 'settings'
        elif model._meta.object_name in scripture_game_tables:
            return 'game-data'        
        else:
            return None
        
    def db_for_write(self, model, **hints):
        """
        Select DB to write to
        """
        if model._meta.object_name in bible_tables:
            return 'bibles'
        elif model._meta.object_name in settings_tables:
            return 'settings'
        elif model._meta.object_name in scripture_game_tables:
            return 'game-data'
        else:
            return None        


    def allow_relation(self, obj1, obj2, **hints):
        """
        No opinion
        """
        return None

    def allow_syncdb(self, db, model):
        """
        Sync the tables to appropriate databases
        """
#        print "syncdb",  db, model._meta.object_name
        if model._meta.object_name in bible_tables:
            if db == 'bibles':
                return True
            else:
                return False
            
        elif model._meta.object_name in settings_tables:
            if db == 'settings':
                return True
            else:
                return False                                         
                                         
        elif db == 'default':
            return True
        else:
            return False
        