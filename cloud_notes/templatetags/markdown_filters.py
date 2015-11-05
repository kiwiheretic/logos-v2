from django import template
import markdown as md
import bleach
import copy

register = template.Library()

def markdown(value):
    """convert to markdown"""
    allowed_tags = bleach.ALLOWED_TAGS + ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    return bleach.clean(md.markdown(value), tags = allowed_tags)
    
register.filter('markdown', markdown)