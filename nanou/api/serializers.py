from rest_framework_json_api import serializers


class VideoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class PreferenceSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    weight = serializers.SerializerMethodField()

    def get_weight(self, obj):
        socialuser = self.context.pop('socialuser', None)
        if socialuser:
            return float(socialuser.preferences.get(obj, 'weight', default=1.0))
        return 1.0
