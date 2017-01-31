from rest_framework_json_api import serializers


class VideoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    url = serializers.URLField()
    stream_url = serializers.URLField()
    image_url = serializers.URLField()


class PreferenceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    weight = serializers.SerializerMethodField()

    def get_weight(self, obj):
        socialuser = self.context.get('socialuser')
        if socialuser:
            return float(socialuser.preferences.get(obj, 'weight', default=1.0))
        return 1.0
