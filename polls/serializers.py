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
        fields = ['id', 'instituicao', 'nome', 'idade', 'data_cadastro']
        read_only_fields = ['id', 'data_cadastro']


class SessaoSerializer(serializers.ModelSerializer):
    crianca_nome = serializers.CharField(source='crianca.nome', read_only=True)
    crianca_idade = serializers.IntegerField(source='crianca.idade', read_only=True)
    
    class Meta:
        model = Sessao
        fields = [
            'id', 'crianca', 'crianca_nome', 'crianca_idade',
            'instituicao', 'data_inicio', 'data_fim', 'pontuacao'
        ]
        read_only_fields = ['id', 'data_inicio']


class IniciarSessaoSerializer(serializers.Serializer):
    """
    Serializer específico para o endpoint de iniciar sessão
    Agora instituição é apenas um texto simples
    """
    instituicao = serializers.CharField(max_length=200, help_text='Nome da instituição')
    nome = serializers.CharField(max_length=100)
    idade = serializers.IntegerField(min_value=0, max_value=120)
    
    def create(self, validated_data):
        instituicao_nome = validated_data.pop('instituicao')
        
        # Busca ou cria a criança (agora com instituição como texto)
        crianca, created = Crianca.objects.get_or_create(
            nome=validated_data['nome'],
            idade=validated_data['idade'],
            defaults={
                'instituicao': instituicao_nome,
                'data_cadastro': timezone.now()
            }
        )
        
        # Se a criança já existia, atualiza a instituição
        if not created and crianca.instituicao != instituicao_nome:
            crianca.instituicao = instituicao_nome
            crianca.save()
        
        # Cria a sessão
        sessao = Sessao.objects.create(
            crianca=crianca,
            instituicao=instituicao_nome,  # Salva o nome da instituição
            data_inicio=timezone.now()
        )
        
        return sessao