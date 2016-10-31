from __future__ import unicode_literals

from py2neo.ogm import GraphObject, Related, RelatedObjects

from .utils import NeoGraph


class NeoModel(GraphObject):
    @classmethod
    def all(cls):
        with NeoGraph() as graph:
            return cls.select(graph)

    @classmethod
    def first(cls):
        with NeoGraph() as graph:
            return cls.select(graph).first()

    @property
    def id(self):
        return self.__primaryvalue__

    def update_prop(self, k, v):
        if hasattr(self, k):
            if isinstance(self.__class__.__dict__[k], Related):
                attr = getattr(self, k)
                attr.clear()
                with NeoGraph() as graph:
                    for id_new in v:
                        obj_new = attr.related_class.select(graph, int(id_new)).first()
                        if obj_new:
                            attr.add(obj_new)
            else:
                setattr(self, k, v)

    def value_dict(self):
        return {
            k: self._get_property(k)
            for k in self.__class__.__dict__
            if not k.startswith('_')
        }

    def _get_property(self, k):
        attr = getattr(self, k)
        if isinstance(attr, RelatedObjects):
            return [i.__primaryvalue__ for i in attr]
        else:
            return attr

    def delete(self):
        with NeoGraph() as graph:
            for prop_name, prop in self.__class__.__dict__.items():
                if isinstance(prop, Related):
                    rel_objects = getattr(self, prop_name)
                    rel_objects.clear()
            graph.push(self)
            return graph.delete(self)
