import datetime
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.urls import reverse

# ========== MODELOS EXISTENTES (ENQUETES E TAREFAS) ==========

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("data published")
    
    def __str__(self):
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text


class Tarefa(models.Model):
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    concluida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'

    def __str__(self):
        return self.titulo

    def marcar_concluida(self):
        self.concluida = True
        self.data_conclusao = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('polls:tarefa_detail', args=[str(self.id)])

    @property
    def dias_desde_criacao(self):
        delta = timezone.now() - self.data_criacao
        return delta.days


# ========== MODELOS PRINCIPAIS ==========

class Crianca(models.Model):
    """
    Modelo para representar uma criança no sistema
    """
    instituicao = models.CharField(
        max_length=200,
        verbose_name='Instituição',
        blank=True,
        null=True
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome'
    )
    
    idade = models.IntegerField(
        verbose_name='Idade'
    )
    
    fase_atual = models.CharField(
        max_length=50,
        verbose_name='Fase Atual',
        default='pre_fase',
        help_text='pre_fase, capitulo_1, capitulo_2, etc'
    )
    
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Cadastro'
    )
    
    class Meta:
        verbose_name = 'Criança'
        verbose_name_plural = 'Crianças'
        ordering = ['nome']
    
    def __str__(self):
        if self.instituicao:
            return f"{self.nome} ({self.idade} anos) - {self.instituicao}"
        return f"{self.nome} ({self.idade} anos)"


class Sessao(models.Model):
    """
    Modelo para representar uma sessão de uma criança
    """
    crianca = models.ForeignKey(
        Crianca,
        on_delete=models.CASCADE,
        related_name='sessoes',
        verbose_name='Criança'
    )
    
    instituicao = models.CharField(
        max_length=200,
        verbose_name='Instituição',
        blank=True,
        null=True
    )
    
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Início'
    )
    
    data_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Fim'
    )
    
    pontuacao_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Pontuação Total'
    )
    
    class Meta:
        verbose_name = 'Sessão'
        verbose_name_plural = 'Sessões'
        ordering = ['-data_inicio']
    
    def __str__(self):
        return f"Sessão de {self.crianca.nome} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def finalizar(self):
        self.data_fim = timezone.now()
        self.save()


class Capitulo(models.Model):
    """
    Modelo para representar um capítulo
    """
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição',
        blank=True,
        null=True
    )
    
    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem'
    )
    
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    class Meta:
        verbose_name = 'Capítulo'
        verbose_name_plural = 'Capítulos'
        ordering = ['ordem', 'titulo']
    
    def __str__(self):
        return self.titulo


class Caminho(models.Model):
    """
    Modelo para representar um caminho dentro de um capítulo
    """
    capitulo = models.ForeignKey(
        Capitulo,
        on_delete=models.CASCADE,
        related_name='caminhos',
        verbose_name='Capítulo'
    )
    
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome'
    )
    
    cor = models.CharField(
        max_length=50,
        verbose_name='Cor',
        default='azul'
    )
    
    dificuldade = models.CharField(
        max_length=50,
        verbose_name='Dificuldade',
        default='médio'
    )
    
    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem'
    )
    
    class Meta:
        verbose_name = 'Caminho'
        verbose_name_plural = 'Caminhos'
        ordering = ['ordem']
    
    def __str__(self):
        return f"{self.capitulo.titulo} - {self.nome}"


class Desafio(models.Model):
    """
    Modelo para representar um desafio dentro de um caminho
    """
    TIPO_PISTA_CHOICES = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('audio', 'Áudio'),
    ]
    
    caminho = models.ForeignKey(
        Caminho,
        on_delete=models.CASCADE,
        related_name='desafios',
        verbose_name='Caminho'
    )
    
    ordem = models.IntegerField(
        verbose_name='Ordem'
    )
    
    tipo_pista = models.CharField(
        max_length=10,
        choices=TIPO_PISTA_CHOICES,
        default='text',
        verbose_name='Tipo de Pista'
    )
    
    conteudo_pista = models.TextField(
        verbose_name='Conteúdo da Pista'
    )
    
    resposta_correta = models.CharField(
        max_length=500,
        verbose_name='Resposta Correta'
    )
    
    class Meta:
        verbose_name = 'Desafio'
        verbose_name_plural = 'Desafios'
        ordering = ['ordem']
        unique_together = ['caminho', 'ordem']
    
    def __str__(self):
        return f"Desafio {self.ordem} - {self.caminho.nome}"


# ========== NOVO MODELO: AÇÃO ==========

class Acao(models.Model):
    """
    Modelo unificado para registrar todas as ações do usuário
    """
    TIPO_ACAO_CHOICES = [
        ('click', 'Clique'),
        ('drag', 'Arrastar'),
        ('type', 'Digitar'),
        ('select', 'Selecionar'),
        ('submit', 'Enviar'),
        ('next', 'Avançar'),
        ('back', 'Voltar'),
        ('hint', 'Pedir Dica'),
        ('skip', 'Pular'),
    ]
    
    # Quem fez a ação
    crianca = models.ForeignKey(
        Crianca,
        on_delete=models.CASCADE,
        related_name='acoes',
        verbose_name='Criança'
    )
    
    # Qual a sessão
    sessao = models.ForeignKey(
        Sessao,
        on_delete=models.CASCADE,
        related_name='acoes',
        verbose_name='Sessão',
        null=True,
        blank=True
    )
    
    # Qual a fase (pré-fase ou capítulo)
    fase = models.CharField(
        max_length=50,
        verbose_name='Fase',
        help_text='pre_fase, capitulo_1, capitulo_2, etc'
    )
    
    # Qual o desafio (opcional)
    desafio = models.ForeignKey(
        Desafio,
        on_delete=models.CASCADE,
        related_name='acoes',
        verbose_name='Desafio',
        null=True,
        blank=True
    )
    
    # Sigla da ação
    sigla = models.CharField(
        max_length=3,
        verbose_name='Sigla da Ação',
        help_text='Ex: CLI (clique), DRA (arrastar), TIP (digitar), SEL (selecionar), ENV (enviar)'
    )
    
    # Tipo da ação
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_ACAO_CHOICES,
        verbose_name='Tipo da Ação'
    )
    
    # Resposta do usuário
    resposta = models.TextField(
        verbose_name='Resposta',
        help_text='Resposta dada pelo usuário ou ação realizada',
        blank=True,
        null=True
    )
    
    # ===== CAMPOS DE TEMPO =====
    
    # Tempo de Reação (em segundos)
    tempo_reacao = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Tempo de Reação (s)',
        help_text='Tempo entre o estímulo e o início da resposta do usuário',
        null=True,
        blank=True
    )
    
    # Tempo de Resposta (em segundos)
    tempo_resposta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Tempo de Resposta (s)',
        help_text='Tempo total para completar a ação (inclui tempo de reação)',
        null=True,
        blank=True
    )
    
    # Pontuação (decimal)
    pontuacao = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Pontuação'
    )
    
    # Data/hora da ação
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['-created_at']
    
    def __str__(self):
        reacao = f" - R:{self.tempo_reacao:.2f}s" if self.tempo_reacao else ""
        resposta = f" Rs:{self.tempo_resposta:.2f}s" if self.tempo_resposta else ""
        return f"{self.crianca.nome} - {self.get_tipo_display()} ({self.sigla}){reacao}{resposta} - {self.created_at.strftime('%H:%M:%S')}"
    
    def calcular_pontuacao(self):
        """Calcula pontuação baseada no tipo de ação e tempos"""
        from decimal import Decimal
        
        if self.tipo == 'submit' and self.resposta and self.desafio:
            if self.resposta.strip().lower() == self.desafio.resposta_correta.strip().lower():
                # Bônus por tempo de reação rápido
                if self.tempo_reacao and self.tempo_reacao < 1.0:
                    return Decimal('1.5')  # Bônus máximo
                elif self.tempo_reacao and self.tempo_reacao < 2.0:
                    return Decimal('1.2')  # Bônus médio
                return Decimal('1.0')  # Pontuação base
            return Decimal('0')
        elif self.tipo == 'hint':
            return Decimal('0.2')
        elif self.tipo == 'skip':
            return Decimal('0')
        elif self.tipo in ['click', 'select']:
            return Decimal('0.5')
        
        return Decimal('0.5')
    
    def save(self, *args, **kwargs):
        # Gerar sigla automaticamente baseada no tipo
        if not self.sigla:
            siglas = {
                'click': 'CLI',
                'drag': 'DRA',
                'type': 'TIP',
                'select': 'SEL',
                'submit': 'ENV',
                'next': 'AVN',
                'back': 'VOL',
                'hint': 'DIC',
                'skip': 'PUL',
            }
            self.sigla = siglas.get(self.tipo, 'OUT')
        
        # Calcular pontuação se não definida
        if self.pontuacao == 0:
            self.pontuacao = self.calcular_pontuacao()
        
        super().save(*args, **kwargs)
        
        # Atualizar pontuação total da sessão
        if self.sessao:
            from django.db.models import Sum
            total_pontos = Acao.objects.filter(sessao=self.sessao).aggregate(
                total=Sum('pontuacao')
            )['total'] or Decimal('0')
            self.sessao.pontuacao_total = total_pontos
            self.sessao.save()