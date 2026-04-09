from rest_framework import serializers
from decimal import Decimal
from django.utils import timezone
from .models import (
    Tarefa, Crianca, Sessao, Capitulo, Caminho, Desafio, Acao
)


class TarefaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarefa
        fields = ['id', 'titulo', 'concluida', 'data_criacao', 'data_conclusao']
        read_only_fields = ['id', 'data_criacao', 'data_conclusao']


class CriancaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crianca
        fields = ['id', 'instituicao', 'nome', 'idade', 'fase_atual', 'data_cadastro']
        read_only_fields = ['id', 'data_cadastro']


class SessaoSerializer(serializers.ModelSerializer):
    crianca_nome = serializers.CharField(source='crianca.nome', read_only=True)
    
    class Meta:
        model = Sessao
        fields = [
            'id', 'crianca', 'crianca_nome', 'instituicao',
            'data_inicio', 'data_fim', 'pontuacao_total'
        ]
        read_only_fields = ['id', 'data_inicio', 'pontuacao_total']


class CapituloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Capitulo
        fields = ['id', 'titulo', 'descricao', 'ordem', 'data_criacao']
        read_only_fields = ['id', 'data_criacao']


class CaminhoSerializer(serializers.ModelSerializer):
    capitulo_titulo = serializers.CharField(source='capitulo.titulo', read_only=True)
    
    class Meta:
        model = Caminho
        fields = ['id', 'capitulo', 'capitulo_titulo', 'nome', 'cor', 'dificuldade', 'ordem']
        read_only_fields = ['id']


class DesafioSerializer(serializers.ModelSerializer):
    caminho_nome = serializers.CharField(source='caminho.nome', read_only=True)
    caminho_cor = serializers.CharField(source='caminho.cor', read_only=True)
    
    class Meta:
        model = Desafio
        fields = [
            'id', 'caminho', 'caminho_nome', 'caminho_cor',
            'ordem', 'tipo_pista', 'conteudo_pista'
        ]
        read_only_fields = ['id']


class AcaoSerializer(serializers.ModelSerializer):
    crianca_nome = serializers.CharField(source='crianca.nome', read_only=True)
    sessao_info = serializers.CharField(source='sessao.__str__', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Acao
        fields = [
            'id', 'crianca', 'crianca_nome', 'sessao', 'sessao_info',
            'fase', 'desafio', 'sigla', 'tipo', 'tipo_display',
            'resposta', 'tempo_reacao', 'tempo_resposta', 'pontuacao', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'pontuacao']


class RegistrarAcaoSerializer(serializers.Serializer):
    """Serializer para registrar uma nova ação (sem validação de resposta correta)"""
    crianca_id = serializers.IntegerField()
    sessao_id = serializers.IntegerField(required=False, allow_null=True)
    fase = serializers.CharField(max_length=50)
    desafio_id = serializers.IntegerField(required=False, allow_null=True)
    sigla = serializers.CharField(max_length=3, required=False, allow_blank=True)
    tipo = serializers.ChoiceField(choices=Acao.TIPO_ACAO_CHOICES)
    resposta = serializers.CharField(required=False, allow_blank=True)
    tempo_reacao = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    tempo_resposta = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    
    def validate(self, data):
        try:
            Crianca.objects.get(pk=data['crianca_id'])
        except Crianca.DoesNotExist:
            raise serializers.ValidationError({'crianca_id': 'Criança não encontrada'})
        
        if data.get('sessao_id'):
            try:
                Sessao.objects.get(pk=data['sessao_id'])
            except Sessao.DoesNotExist:
                raise serializers.ValidationError({'sessao_id': 'Sessão não encontrada'})
        
        if data.get('desafio_id'):
            try:
                Desafio.objects.get(pk=data['desafio_id'])
            except Desafio.DoesNotExist:
                raise serializers.ValidationError({'desafio_id': 'Desafio não encontrado'})
        
        tempo_reacao = data.get('tempo_reacao')
        if tempo_reacao is not None and tempo_reacao < 0:
            raise serializers.ValidationError({'tempo_reacao': 'Tempo de reação não pode ser negativo'})
        
        tempo_resposta = data.get('tempo_resposta')
        if tempo_resposta is not None and tempo_resposta < 0:
            raise serializers.ValidationError({'tempo_resposta': 'Tempo de resposta não pode ser negativo'})
        
        return data
    
    def create(self, validated_data):
        return Acao.objects.create(
            crianca_id=validated_data['crianca_id'],
            sessao_id=validated_data.get('sessao_id'),
            fase=validated_data['fase'],
            desafio_id=validated_data.get('desafio_id'),
            sigla=validated_data.get('sigla', ''),
            tipo=validated_data['tipo'],
            resposta=validated_data.get('resposta', ''),
            tempo_reacao=validated_data.get('tempo_reacao'),
            tempo_resposta=validated_data.get('tempo_resposta'),
        )