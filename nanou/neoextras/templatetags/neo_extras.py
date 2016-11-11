from django import template

register = template.Library()


@register.inclusion_tag('neoextras/relationships_items.html')
def show_relationship_items(start_obj, selection, label):
    return {
        'selection': selection,
        'label': label,
        'start_obj': start_obj,
        'rel_type': selection._RelatedObjects__match_args[1],
        'reverse_relationship': selection._RelatedObjects__start_node,
    }
