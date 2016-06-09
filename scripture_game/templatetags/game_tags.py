from django import template
import operator
from functools import partial

register = template.Library()

    
def max_lookup_value(dict, key):
    """lookup in dictionary via key"""
    if not dict: return None
    value = max(dict.iteritems(), key=lambda d:d[1][key])[1][key]
    return value

def max_lookup_key(dict, key):
    """lookup in dictionary via key"""
    if not dict: return None
    value = max(dict.iteritems(), key=lambda d:d[1][key])[1]['nick']
    return value
    
register.filter('max_lookup_value', max_lookup_value)
register.filter('max_lookup_key', max_lookup_key)
