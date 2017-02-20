from __future__ import unicode_literals

from py2neo.ogm import GraphObject, Property, Related, RelatedFrom, RelatedObjects, RelatedTo

from .utils import NeoGraph

DEFAULT_PROPS_KEY = 'default_props'


class NeoModel(GraphObject):
    __primarykey__ = 'id'

    id = Property()

    @classmethod
    def all(cls):
        with NeoGraph() as graph:
            return cls.select(graph)

    @classmethod
    def first(cls):
        with NeoGraph() as graph:
            return cls.select(graph).first()

    @classmethod
    def get(cls, pk):
        with NeoGraph() as graph:
            return cls.select(graph, pk).first()

    @classmethod
    def getAll(cls, pks):
        values = pks if isinstance(pks, (list, tuple)) else [pks]
        res = [cls.get(pk) for pk in values]
        return res

    @classmethod
    def none(self):
        return []

    @property
    def pk(self):
        return self.id

    @property
    def node(self):
        return self._GraphObject__ogm.node

    def update_prop(self, k, v):
        if hasattr(self, k):
            if isinstance(self.__class__.__dict__[k], DefaultPropertyMixin):
                int_values = [int(x.id) for x in v]
                default_props = self.__class__.__dict__[k].default_props
                attr = getattr(self, k)
                # Remove deleted objects
                for obj in attr:
                    if obj.id not in int_values:
                        attr.remove(obj)
                # Add new objects
                with NeoGraph() as graph:
                    for id_new in int_values:
                        obj_new = attr.related_class.select(graph, int(id_new)).first()
                        if obj_new and obj_new not in attr:
                            attr.add(obj_new, default_props)
            else:
                setattr(self, k, v)

    def value_dict(self):
        return {
            k: self._get_property(k)
            for k in self.__class__.__dict__
            if not k.startswith('_')
        }

    def property_dict(self):
        return {
            key: getattr(self, key)
            for key, value in self.__class__.__dict__.items()
            if isinstance(value, Property)
        }

    def relationships(self):
        relationships = []
        with NeoGraph() as graph:
            for relationship_name, relationship in self.__class__.__dict__.items():
                if isinstance(relationship, RelatedTo):
                    selection = getattr(self, relationship_name)
                    for obj in selection:
                        rel = graph.match_one(self.node, selection._RelatedObjects__match_args[1], obj.node)
                        relationships.append((self, selection, obj, dict(rel)))
        return relationships

    def _get_property(self, k):
        attr = getattr(self, k)
        if isinstance(attr, RelatedObjects):
            return [i.__primaryvalue__ for i in attr]
        else:
            return attr

    def save(self):
        with NeoGraph() as graph:
            return graph.push(self)

    def delete(self):
        with NeoGraph() as graph:
            for prop_name, prop in self.__class__.__dict__.items():
                if isinstance(prop, Related):
                    rel_objects = getattr(self, prop_name)
                    rel_objects.clear()
            graph.push(self)
            return graph.delete(self)


class DefaultPropertyMixin(object):
    default_props = {}

    def __init__(self, *args, **kwargs):
        if DEFAULT_PROPS_KEY in kwargs:
            props = kwargs.get(DEFAULT_PROPS_KEY)
            if isinstance(props, dict):
                self.default_props = props
            else:
                raise ValueError('default_props has to be a dict')
            del kwargs[DEFAULT_PROPS_KEY]
        super(DefaultPropertyMixin, self).__init__(*args, **kwargs)


class NeoRelated(DefaultPropertyMixin, Related):
    pass


class NeoRelatedFrom(DefaultPropertyMixin, RelatedFrom):
    pass


class NeoRelatedTo(DefaultPropertyMixin, RelatedTo):
    pass
