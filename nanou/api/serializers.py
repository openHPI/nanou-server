from rest_framework_json_api import serializers


class VideoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
