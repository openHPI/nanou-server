from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.views import View

from neo.utils import NeoGraph, get_neo_object_or_404, get_neo_relationship_or_404


class NeoRelationshipUpdateView(View):
    template_name = 'neoextras/relationship.html'
    relationship_name = None
    start_model = None
    end_model = None

    def get_relationship_name(self):
        if self.relationship_name:
            return self.relationship_name
        else:
            raise ImproperlyConfigured(
                '{0} is missing a relationship name. Define {0}.relationship_name.'.format(self.__class__.__name__)
            )

    def get_start_model(self):
        if self.start_model:
            return self.start_model
        else:
            raise ImproperlyConfigured(
                '{0} is missing a start model. Define {0}.start_model.'.format(self.__class__.__name__)
            )

    def get_end_model(self):
        if self.end_model:
            return self.end_model
        else:
            raise ImproperlyConfigured(
                '{0} is missing a end model. Define {0}.end_model.'.format(self.__class__.__name__)
            )

    def check_objects(self, pk1, pk2):
        with NeoGraph() as graph:
            a = get_neo_object_or_404(self.get_start_model(), int(pk1), graph).node
            b = get_neo_object_or_404(self.get_end_model(), int(pk2), graph).node
            rel = get_neo_relationship_or_404(a, self.get_relationship_name(), b, graph)
            return a, rel, b

    def create_context_data(self, a, rel, b):
        return {
            'start_node': {
                'node': a,
                'label': '|'.join(a._Node__labels),
                'props': dict(a),
            },
            'end_node': {
                'node': b,
                'label': '|'.join(b._Node__labels),
                'props': dict(b),
            },
            'relationship': {
                'props': dict(rel),
                'type': rel._Relationship__type,
            },
        }

    def validate_post_data(self, data, rel):
        return (
            all(key in data for key in rel) and
            all(key in rel for key in data if key != 'csrfmiddlewaretoken') and
            len(rel) > 0
        )

    def get(self, request, pk1, pk2):
        context = self.create_context_data(*self.check_objects(pk1, pk2))
        return render(request, self.template_name, context)

    def post(self, request, pk1, pk2, *args, **kwargs):
        a, rel, b = self.check_objects(pk1, pk2)
        valid = self.validate_post_data(request.POST, rel)
        messages = {}
        if valid:
            with NeoGraph() as graph:
                for key in rel:
                    rel[key] = request.POST[key]
                graph.push(rel)
            messages.update({'success': ['Relationship updated']})
        else:
            messages.update({'error': ['Saving failed: Invalid data']})
        context = self.create_context_data(a, rel, b)
        context.update({'messages': messages})
        return render(request, self.template_name, context)
