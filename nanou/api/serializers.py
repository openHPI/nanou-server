from rest_framework_json_api import serializers


class VideoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    url = serializers.URLField()
    stream_url = serializers.URLField()
    image_url = serializers.URLField()
    provider_name = serializers.CharField(max_length=100)
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        sorted_categories = sorted(obj.categories, key=lambda cat: obj.categories.get(cat, 'weight', default=0))
        return ','.join([cat.name for cat in sorted_categories])


class HistoryVideoSerializer(serializers.Serializer):
    date = serializers.SerializerMethodField()
    url = serializers.URLField()
    image_url = serializers.URLField()
    name = serializers.CharField(max_length=100)
    progress = serializers.SerializerMethodField()
    provider_name = serializers.CharField(max_length=100)
    stream_url = serializers.URLField()
    tags = serializers.SerializerMethodField()

    def get_date(self, obj):
        socialuser = self.context.get('socialuser')
        if socialuser:
            return socialuser.watched_videos.get(obj, 'date', default='1970-01-01')
        return '1970-01-01'

    def get_progress(self, obj):
        socialuser = self.context.get('socialuser')
        if socialuser:
            return float(socialuser.watched_videos.get(obj, 'progress', default=0))
        return 0

    def get_tags(self, obj):
        sorted_categories = sorted(obj.categories, key=lambda cat: obj.categories.get(cat, 'weight', default=0))
        return ','.join([cat.name for cat in sorted_categories])


class PreferenceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    weight = serializers.SerializerMethodField()

    def get_weight(self, obj):
        socialuser = self.context.get('socialuser')
        if socialuser:
            return float(socialuser.preferences.get(obj, 'weight', default=0.5))
        return 0.5
