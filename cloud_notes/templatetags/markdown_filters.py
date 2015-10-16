from django import template
import markdown as md
import bleach

register = template.Library()

def markdown(value):
    """convert to markdown"""
    return md.markdown(bleach.clean(value))
    
register.filter('markdown', markdown)