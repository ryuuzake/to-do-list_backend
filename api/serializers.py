from rest_framework import serializers

from .models import Task


class TaskSerializer(serializers.ModelSerializer):

    owner = serializers.ReadOnlyField(source="owner.username")
    date = serializers.DateField(format="%Y-%m-%d", required=False)

    class Meta:
        model = Task
        fields = "__all__"
