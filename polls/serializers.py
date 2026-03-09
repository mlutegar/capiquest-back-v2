from rest_framework import serializers
from django.utils import timezone
from .models import (
    Tarefa, Crianca, Sessao, 
    Capitulo, Caminho, Desafio, Interacao
)

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
    instituicao = serializers.CharField(max_length=200, help_text='Nome da instituição')
    nome = serializers.CharField(max_length=100)
    idade = serializers.IntegerField(min_value=0, max_value=120)
    
    def create(self, validated_data):
        instituicao_nome = validated_data.pop('instituicao')
        
        crianca, created = Crianca.objects.get_or_create(
            nome=validated_data['nome'],
            idade=validated_data['idade'],
            defaults={
                'instituicao': instituicao_nome,
                'data_cadastro': timezone.now()
            }
        )
        
        if not created and crianca.instituicao != instituicao_nome:
            crianca.instituicao = instituicao_nome
            crianca.save()
        
        sessao = Sessao.objects.create(
            crianca=crianca,
            instituicao=instituicao_nome,
            data_inicio=timezone.now()
        )
        
        return sessao


# ===== SERIALIZERS PARA CAPITULOS, CAMINHOS E DESAFIOS =====

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
            'ordem', 'tipo_pista', 'conteudo_pista', 'resposta_correta'
        ]
        read_only_fields = ['id']


class InteracaoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source='aluno.nome', read_only=True)
    desafio_titulo = serializers.CharField(source='desafio.caminho.nome', read_only=True)
    
    class Meta:
        model = Interacao
        fields = [
            'id', 'aluno', 'aluno_nome', 'desafio', 'desafio_titulo',
            'resposta_dada', 'acertou', 'pontos', 'created_at'
        ]
        read_only_fields = ['id', 'acertou', 'pontos', 'created_at']


class SalvarRespostaSerializer(serializers.Serializer):
    aluno_id = serializers.IntegerField()
    desafio_id = serializers.IntegerField()
    resposta_dada = serializers.CharField(max_length=500)
    
    def validate(self, data):
        try:
            Crianca.objects.get(pk=data['aluno_id'])
        except Crianca.DoesNotExist:
            raise serializers.ValidationError({'aluno_id': 'Aluno não encontrado'})
        
        try:
            Desafio.objects.get(pk=data['desafio_id'])
        except Desafio.DoesNotExist:
            raise serializers.ValidationError({'desafio_id': 'Desafio não encontrado'})
        
        return data
    
    def create(self, validated_data):
        desafio = Desafio.objects.get(pk=validated_data['desafio_id'])
        
        interacao, created = Interacao.objects.get_or_create(
            aluno_id=validated_data['aluno_id'],
            desafio_id=validated_data['desafio_id'],
            defaults={
                'resposta_dada': validated_data['resposta_dada'],
            }
        )
        
        if not created:
            interacao.resposta_dada = validated_data['resposta_dada']
            interacao.save()
        
        return interacao


# ===== SERIALIZERS PARA RESULTADOS =====

class ResultadoSerializer(serializers.Serializer):
    """Serializer para documentar a estrutura de resultado"""
    aluno = serializers.DictField()
    capitulo = serializers.DictField()
    resumo = serializers.DictField()
    aproveitamento_por_dificuldade = serializers.DictField()
    caminhos = serializers.ListField()
    ultimas_atividades = serializers.ListField()
    ranking_top5 = serializers.ListField()
    data_consulta = serializers.DateTimeField()