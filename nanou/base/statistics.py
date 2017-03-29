from neo.utils import NeoGraph
from videos.models import Video


def _parse_count(data):
    if not isinstance(data, list):
        return 0
    if len(data) == 0:
        return 0
    count = data[0].get('count')
    if not isinstance(count, int):
        return 0
    return count


# suggestions
def overall_suggestions_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)-[w:WAS_SUGGESTED]->(u:SocialUser)
            RETURN COUNT(DISTINCT w) as count
        ''')
        return _parse_count(cursor.data())


def overall_suggestions_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)-[w:WAS_SUGGESTED]->(u:SocialUser)
            RETURN COUNT(DISTINCT u) as count
        ''')
        return _parse_count(cursor.data())


def suggestions_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)-[w:WAS_SUGGESTED]->(u:SocialUser)
            RETURN v, COUNT(w) as suggestion_count, COUNT(DISTINCT u) as user_count
            ORDER BY suggestion_count DESC, user_count DESC
        ''')
        return [{
            'video': Video.wrap(d['v']),
            'suggestion_count': d['suggestion_count'],
            'user_count': d['user_count']
        } for d in cursor.data()]


# watch
def overall_watch_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress > 0
            RETURN COUNT(DISTINCT w) as count
        ''')
        return _parse_count(cursor.data())


def overall_watch_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress > 0
            RETURN COUNT(DISTINCT u) as count
        ''')
        return _parse_count(cursor.data())


def watch_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress > 0
            RETURN v, COUNT(w) as watch_count, COUNT(DISTINCT u) as user_count
            ORDER BY watch_count DESC, user_count DESC
        ''')
        return [{
            'video': Video.wrap(d['v']),
            'watch_count': d['watch_count'],
            'user_count': d['user_count']
        } for d in cursor.data()]


# dismiss
def overall_dismiss_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress = 0
            RETURN COUNT(DISTINCT w) as count
        ''')
        return _parse_count(cursor.data())


def overall_dismiss_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress = 0
            RETURN COUNT(DISTINCT u) as count
        ''')
        return _parse_count(cursor.data())


def dismiss_user_count():
    with NeoGraph() as graph:
        cursor = graph.run('''
            MATCH (v:Video)<-[w:WATCHED]-(u:SocialUser)
            WHERE w.progress = 0
            RETURN v, COUNT(w) as dismiss_count, COUNT(DISTINCT u) as user_count
            ORDER BY dismiss_count DESC, user_count DESC
        ''')
        return [{
            'video': Video.wrap(d['v']),
            'dismiss_count': d['dismiss_count'],
            'user_count': d['user_count']
        } for d in cursor.data()]
