# LogosRouter.py

import logging
from logos.settings import LOGGING
from django.db.models import Count

logger = logging.getLogger(__name__)
logging.config.dictConfig(LOGGING)

from logos.itermodels import plugin_models_finder
# Follows is a list of DB identifier and associated model names

# The routing_data data structure is deprecated.  Use DB_ROUTER or 
# DB_ROUTE_EXCEPTIONS in plugins instead

routing_data = (('bibles', 
                 ('BibleTranslations', 'BibleBooks', 
                  'BibleVerses', 'BibleConcordance', 
                  'BibleDict')),
                ('settings',
                 ('Settings',
                  'BibleColours', 'RoomOptions', 
                  'Plugins', 'NetworkPlugins',  'RoomPlugins')),
                ('game-data',
                 ('GameGames', 'GameUsers', 'GameSolveAttempts',
                  'Scriptures'),),
                  )
                 
            
class LogosRouter(object):
    def db_for_read(self, model, **hints):
        """
        Select DB to read from
        """
        
        for model_module, model_class in plugin_models_finder():
            if hasattr(model_module, 'DB_ROUTER'):
                router = model_module.DB_ROUTER
                if hasattr(model_module, 'DB_ROUTE_EXCEPTIONS'):
                    route_exceptions = model_module.DB_ROUTE_EXCEPTIONS
                else:
                    route_exceptions = None
                iter_klass_name = model_class.__name__
                klass_name = model.__name__
                if klass_name == iter_klass_name:
                    if route_exceptions and klass_name in route_exceptions:
                        router = route_exceptions[klass_name]
#                        logger.debug( "Exception DB READ: selecting {} for model {}".format(router,klass_name))
                    else:
#                        logger.debug( "DB READ: selecting {} for model {}".format(router,klass_name))
                        pass
                    return router


        
        for db_id, models in routing_data:
            if model._meta.object_name in models:
                return db_id
        return None
    
       
    def db_for_write(self, model, **hints):
        """
        Select DB to write to
        """
        
        for model_module, model_class in plugin_models_finder():
            if hasattr(model_module, 'DB_ROUTER'):
                router = model_module.DB_ROUTER
                if hasattr(model_module, 'DB_ROUTE_EXCEPTIONS'):
                    route_exceptions = model_module.DB_ROUTE_EXCEPTIONS
                else:
                    route_exceptions = None
                iter_klass_name = model_class.__name__
                klass_name = model.__name__
                if klass_name == iter_klass_name:
                    if route_exceptions and klass_name in route_exceptions:
                        router = route_exceptions[klass_name]
#                        logger.debug( "Exception DB WRITE: selecting {} for model {}".format(router,klass_name))
                    else:
#                        logger.debug( "DB WRITE: selecting {} for model {}".format(router,klass_name))
                        pass
                    return router
        
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
        
        for model_module, model_class in plugin_models_finder():
            if hasattr(model_module, 'DB_ROUTER'):
                router = model_module.DB_ROUTER
                if hasattr(model_module, 'DB_ROUTE_EXCEPTIONS'):
                    route_exceptions = model_module.DB_ROUTE_EXCEPTIONS
                else:
                    route_exceptions = None                
                iter_klass_name = model_class.__name__
                klass_name = model.__name__
                if klass_name == iter_klass_name:
                    # If we have found the model class in the
                    # plugins folder then we don't want to 
                    # allow it to be sync'd to the 'default' database
                    # so return False here if there is no match
                    if route_exceptions and klass_name in route_exceptions:
                        router = route_exceptions[klass_name]
                    if db == router:
                        return True
                    else:
                        return False

        if db == 'default':
            return True
        else:
            return False        
        
   

        