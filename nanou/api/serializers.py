from rest_framework_json_api import serializers

from surveys.models import Survey


class VideoSerializer(serializers.Serializer):
    duration = serializers.IntegerField()
    license_name = serializers.SerializerMethodField()
    license_url = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    url = serializers.URLField()
    stream_url = serializers.URLField()
    image_url = serializers.URLField()
    provider_name = serializers.CharField(max_length=100)
    tags = serializers.SerializerMethodField()

    def get_license_name(self, obj):
        value = obj.license_name
        if value is None or len(value) == 0:
            return None
        return value

    def get_license_url(self, obj):
        value = obj.license_url
        if value is None or len(value) == 0:
            return None
        return value

    def get_tags(self, obj):
        sorted_categories = sorted(obj.categories, key=lambda cat: obj.categories.get(cat, 'weight', default=0))
        return ','.join([cat.name for cat in sorted_categories])


class HistoryVideoSerializer(serializers.Serializer):
    count = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    duration = serializers.IntegerField()
    url = serializers.URLField()
    image_url = serializers.URLField()
    license_name = serializers.SerializerMethodField()
    license_url = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=100)
    progress = serializers.SerializerMethodField()
    provider_name = serializers.CharField(max_length=100)
    stream_url = serializers.URLField()
    tags = serializers.SerializerMethodField()

    def get_date(self, obj):
        data = self.context.get(obj.id)
        if data:
            return data[0]
        return '1970-01-01'

    def get_count(self, obj):
        data = self.context.get(obj.id)
        if data:
            return data[1]
        return 1

    def get_progress(self, obj):
        data = self.context.get(obj.id)
        if data:
            return data[2]
        return 1

    def get_license_name(self, obj):
        value = obj.license_name
        if value is None or len(value) == 0:
            return None
        return value

    def get_license_url(self, obj):
        value = obj.license_url
        if value is None or len(value) == 0:
            return None
        return value

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


class SurveySerializer(serializers.Serializer):
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        use_secondary = self.context.get('use_secondary', False)
        return obj.secondary_link if use_secondary and len(obj.secondary_link) > 0 else obj.link

    class Meta:
        model = Survey
