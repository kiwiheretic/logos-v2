# LogosRouter.py

# Follows is a list of DB identifier and associated model names
routing_data = (('bibles', 
                 ('BibleTranslations', 'BibleBooks', 
                  'BibleVerses', 'BibleConcordance', 
                  'BibleDict')),
                ('settings',
                 ('Settings',
                  'BibleColours', 'RoomOptions', 'Plugins')),
                ('game-data',
                 ('GameGames', 'GameUsers', 'GameSolveAttempts',
                  'Scriptures'),),
                  )
                 
            
class LogosRouter(object):
    def db_for_read(self, model, **hints):
        """
        Select DB to read from
        """
        for db_id, models in routing_data:
            if model._meta.object_name in models:
                return db_id
        return None
    
       
    def db_for_write(self, model, **hints):
        """
        Select DB to write to
        """
        for db_id, models in routing_data:
            if model._meta.object_name in models:
                return db_id
        return None        

    def allow_relation(self, obj1, obj2, **hints):
        """
        No opinion
        """
        return None

    def allow_migrate(self, db, model):
        """
        Whether to allow data migrations on this model
        manage.py loaddata seems to not work without this
        """

        for db_id, models in routing_data:

            if model._meta.object_name in models:
                if db == db_id:
                    return True
                else:
                    return False
        if db == 'default':
            return True
        else:
            return False        
        
   

        