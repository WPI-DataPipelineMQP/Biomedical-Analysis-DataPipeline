from django import template

register = template.Library()

######################################
# Input: dictionary - Dictionary you are accessing
# key - key used to access dictionary
# Returns: Value of key for given dictionary
# Description: Helper function for accessing data from a dictionary
# when the key is a variable. This can not be done natively in the Django template language.
# It was previously used in template listStudies.html but is not needed anymore.
######################################
@register.filter
def getByKey(dictionary, key):
    return dictionary.get(key)

######################################
# Input: list - List you are accessing
# i - Index used to access list
# Returns: ith element of given list
# Description: Helper function for accessing data from a list
# when the index is a variable. This can not be done natively in the Django template language.
# It is used in template listStudies.html for accessing the parallel array containing the study ids of the studies.
######################################
@register.filter
def getByIndex(list, i):
    return list[i]