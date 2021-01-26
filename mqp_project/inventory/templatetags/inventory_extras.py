from django import template

register = template.Library()

@register.filter
def getByKey(dictionary, key):
    return dictionary.get(key)

@register.filter
def getByIndex(list, i):
    return list[i]