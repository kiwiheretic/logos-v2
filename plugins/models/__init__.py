# __init__.py

## This module is so that all plugins can have custom models.py files in
## their own folders and have them picked up with 
## $ python manage.py syncdb

import inspect
import os
from django.conf import settings
from django.db import models

### Import all the model modules from plugins/  ###
__all__ = []

plugin_path = os.path.join(settings.BASE_DIR, 'plugins')
dirs = os.gitlistdir(plugin_path)
for m in dirs:
    pth = os.path.join(plugin_path, m)
    model_pth = os.path.join(pth, "models.py")
    if os.path.isdir(pth) and os.path.isfile(model_pth):
        mod = 'plugins.'+m+'.models'
#            print('importing module '+'plugins.'+m)

        imp_mod = __import__(mod)
        
        m1 = getattr(__import__(mod), m)
        m2 = getattr(m1, "models")
        
        for attr in dir(m2):
            a1 = getattr(m2, attr)
            # Check if the class is a class derived from 
            # bot.PluginDespatch.Plugin
            # but is not the base class only

            if inspect.isclass(a1) and \
            a1 != models.Model and \
            issubclass(a1, models.Model):

                from_path = "plugins."+m+".models"

#                    print('from {} import {}'.format(from_path, a1.__name__))
                globals()[a1.__name__] = a1
                __all__.append(a1.__name__)



###  ====  End plugin models modules Import === ###