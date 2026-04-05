from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ticket, TicketComment, TicketHistory, Agent, KnowledgeBase, Status, Priority

class UserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        if request.user.is_staff or request.user.id == obj.id:
            return obj.email
        return None

    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TicketCustomerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    def get_username(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return f"Customer #{obj.id}"
        if request.user.is_staff or request.user.id == obj.id:
            return obj.username
        return f"Customer #{obj.id}"

    def get_email(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        if request.user.is_staff or request.user.id == obj.id:
            return obj.email
        return None

    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class PrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = Priority
        fields = '__all__'

class TicketCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = TicketComment
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        is_staff = bool(request and request.user and request.user.is_staff)
        text = data.get('comment_text') or ''
        if (not is_staff) and text.startswith('[ESCALATION REVIEW NEEDED]'):
            data['comment_text'] = '[INTERNAL NOTE HIDDEN] This escalation note is visible to staff only.'
        return data

class TicketSerializer(serializers.ModelSerializer):
    customer = TicketCustomerSerializer(read_only=True)
    status = StatusSerializer(read_only=True)
    priority = PrioritySerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True
    )
    priority_id = serializers.PrimaryKeyRelatedField(
        queryset=Priority.objects.all(), source='priority', write_only=True
    )

    class Meta:
        model = Ticket
        fields = '__all__'

class KnowledgeBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeBase
        fields = ['id', 'title', 'content', 'category', 'tags'] 
        # Exclude embeddings from standard API payloads


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
