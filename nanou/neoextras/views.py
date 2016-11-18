from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

from neo.utils import (NeoGraph, get_neo_node_or_404,
                       get_neo_relationship_or_404)


class NeoRelationshipDetailView(PermissionRequiredMixin, View):
    permission_required = 'base.manage_curriculum'
    template_name = 'neoextras/relationship.html'

    def check_objects(self, pk1, rel_type, pk2):
        with NeoGraph() as graph:
            a = get_neo_node_or_404(int(pk1), graph)
            b = get_neo_node_or_404(int(pk2), graph)
            rel = get_neo_relationship_or_404(a, rel_type, b, graph)
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

    def get(self, request, pk1, rel_type, pk2):
        context = self.create_context_data(*self.check_objects(pk1, rel_type, pk2))
        return render(request, self.template_name, context)

    def post(self, request, pk1, rel_type, pk2, *args, **kwargs):
        a, rel, b = self.check_objects(pk1, rel_type, pk2)
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
