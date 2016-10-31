from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext as _

from py2neo import Graph


def get_neo_object_or_404(cls, pk, graph):
    obj = cls.select(graph, pk).first()
    if obj is None:
        raise Http404(_('No %(verbose_name)s found matching the query') %
                      {'verbose_name': cls.__name__})
    return obj


class NeoGraph(object):
    def __enter__(self):
        neo_db = settings.TEST_NEO_DATABASE if settings.TESTING else settings.NEO_DATABASE
        return Graph(**neo_db)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
