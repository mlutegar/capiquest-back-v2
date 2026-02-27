from rest_framework import serializers
from django.utils import timezone
from .models import Tarefa, Crianca, Sessao

class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'concluida', 'data_criacao', 'data_conclusao']
        read_only_fields = ['id', 'data_criacao', 'data_conclusao']


class CriancaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crianca
        fields = ['id', 'nome', 'idade', 'data_cadastro']
        read_only_fields = ['id', 'data_cadastro']


class SessaoSerializer(serializers.ModelSerializer):
    crianca_nome = serializers.CharField(source='crianca.nome', read_only=True)
    crianca_idade = serializers.IntegerField(source='crianca.idade', read_only=True)
    
    class Meta:
        model = Sessao
        fields = ['id', 'crianca', 'crianca_nome', 'crianca_idade', 
                  'data_inicio', 'data_fim', 'pontuacao']
        read_only_fields = ['id', 'data_inicio', 'pontuacao']


class IniciarSessaoSerializer(serializers.Serializer):
    """
    Serializer específico para o endpoint de iniciar sessão
    Recebe nome e idade, cria/obtém criança e inicia sessão
    """
    nome = serializers.CharField(max_length=100)
    idade = serializers.IntegerField(min_value=0, max_value=120)
    
    def create(self, validated_data):
        # Busca ou cria a criança
        crianca, created = Crianca.objects.get_or_create(
            nome=validated_data['nome'],
            idade=validated_data['idade'],
            defaults={'data_cadastro': timezone.now()}
        )
        
        # Cria a sessão
        sessao = Sessao.objects.create(
            crianca=crianca,
            data_inicio=timezone.now()
        )
        
        return sessao