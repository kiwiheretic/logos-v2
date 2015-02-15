# __init__.py

## This module is so that all plugins can have custom models.py files in
## their own folders and have them picked up with 
## $ python manage.py syncdb

from logos.itermodels import plugin_models_finder
import inspect
import os
from django.conf import settings
from django.db import models


### Import all the model modules from plugins/  ###
__all__ = []

for _, model_class in plugin_models_finder():
    globals()[model_class.__name__] = model_class
    __all__.append(model_class.__name__)
    

###  ====  End plugin models modules Import === ###