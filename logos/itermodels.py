# itermodels.py
import inspect
import os
from django.conf import settings
from django.db import models
import pdb

def plugin_models_finder():
    plugin_path = os.path.join(settings.BASE_DIR, 'plugins')
    dirs = os.listdir(plugin_path)
    for m in dirs:
        pth = os.path.join(plugin_path, m)
        model_pth = os.path.join(pth, "models.py")
        if os.path.isdir(pth) and os.path.isfile(model_pth):
            mod = 'plugins.'+m+'.models'

            imp_mod = __import__(mod)
            
            m1 = getattr(__import__(mod), m)
            models_module = getattr(m1, "models")
            
            for attr in dir(models_module):
                model_class = getattr(models_module, attr)
                # Check if the class is a class derived from 
                # models.Model but is not the base class only

                if inspect.isclass(model_class) and \
                model_class != models.Model and \
                issubclass(model_class, models.Model):

                    yield models_module, model_class


