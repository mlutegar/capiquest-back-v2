from rest_framework import serializers
from .models import Tarefa

class TarefaSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Tarefa - converte objetos Python em JSON e vice-versa
    """
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'concluida', 'data_criacao', 'data_conclusao']
        read_only_fields = ['id', 'data_criacao', 'data_conclusao']  