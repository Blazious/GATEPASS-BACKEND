from rest_framework import serializers
from .models import GatepassRequest

class GatepassRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    department = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GatepassRequest
        fields = '__all__'