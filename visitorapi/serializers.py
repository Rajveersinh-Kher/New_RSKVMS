from rest_framework import serializers
from .models import HRUser, Visitor, VisitRequest, VisitorCard

class HRUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HRUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'department', 'employee_id', 'phone']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = HRUser.objects.create_user(**validated_data)
        return user

class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = '__all__'

class VisitRequestSerializer(serializers.ModelSerializer):
    visitor_name = serializers.CharField(source='visitor.__str__', read_only=True)
    host_name = serializers.CharField(source='host.__str__', read_only=True)

    class Meta:
        model = VisitRequest
        fields = '__all__'

class VisitorCardSerializer(serializers.ModelSerializer):
    visitor_name = serializers.CharField(source='visit_request.visitor.__str__', read_only=True)
    visit_date = serializers.DateField(source='visit_request.visit_date', read_only=True)

    class Meta:
        model = VisitorCard
        fields = '__all__' 