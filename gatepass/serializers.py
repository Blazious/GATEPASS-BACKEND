from rest_framework import serializers
from .models import GatepassRequest, GatepassItem


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GatepassItem
        fields = ["item_name","quantity","serial_number","description", "is_custom"]
    
    def validate(self, data):
        is_custom = data.get('is_custom', False)
        serial_number = data.get('serial_number')

        if is_custom and not serial_number:
            raise serializers.ValidationError({
                'serial_number': 'Serial number is required for custom items.'
            })

        return data

class GatepassRequestSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    department = serializers.PrimaryKeyRelatedField(read_only=True)
    items = ItemSerializer(many=True, required=False)

    class Meta:
        model = GatepassRequest
        fields = '__all__'

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        gatepass = GatepassRequest.objects.create(**validated_data)
        for item_data in items_data:
            GatepassItem.objects.create(gatepass=gatepass, **item_data)
        return gatepass

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['items'] = ItemSerializer(instance.items.all(), many=True).data
        return rep
