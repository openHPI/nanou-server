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


class PreferenceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    weight = serializers.SerializerMethodField()

    def get_weight(self, obj):
        socialuser = self.context.get('socialuser')
        if socialuser:
            return float(socialuser.preferences.get(obj, 'weight', default=0.5))
        return 0.5
