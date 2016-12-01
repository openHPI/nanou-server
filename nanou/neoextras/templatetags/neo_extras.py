from django import template

register = template.Library()


@register.inclusion_tag('neoextras/relationships_items.html')
def show_relationship_items(start_obj, selection, label, url_name=None):
    return {
        'selection': selection,
        'label': label,
        'start_obj': start_obj,
        'url_name': url_name,
        'reverse_relationship': selection._RelatedObjects__start_node,
    }
