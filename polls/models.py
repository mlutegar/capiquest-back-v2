import datetime
from decimal import Decimal
from django.db.models import Q
from django.utils.text import slugify
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
    
    class Meta:
        verbose_name = 'Desafio'
        verbose_name_plural = 'Desafios'
        ordering = ['ordem']
        unique_together = ['caminho', 'ordem']
    
    def __str__(self):
        return f"Desafio {self.ordem} - {self.caminho.nome}"


# ========== MAPA DE MARCADORES ==========

class MapaMarcador(models.Model):
    """
    Modelo para o mapa de marcadores que classifica as respostas dos jogos
    """
    JOGO_CHOICES = [
        ('piaget', 'Jogo Piaget'),
        ('volta_casa', 'De volta pra casa'),
        ('volta_casa_cog', 'De volta pra casa - Cognitivo'),
    ]
    
    jogo = models.CharField(
        max_length=30,
        choices=JOGO_CHOICES,
        verbose_name='Jogo'
    )
    
    fase = models.CharField(
        max_length=100,
        verbose_name='Fase / Tela',
        help_text='Identificador da tela/fase (deve casar com Acao.fase)'
    )
    
    resposta_chave = models.CharField(
        max_length=100,
        verbose_name='Chave da Resposta',
        help_text='Identificador estável da opção (ex: certa, adjacente, longe)'
    )
    
    sigla = models.CharField(
        max_length=3,
        verbose_name='Sigla da Ação',
        blank=True,
        default=''
    )
    
    nivel = models.IntegerField(
        verbose_name='Nível',
        null=True,
        blank=True,
        help_text='1, 2 ou 3 (jogos por nível). Vazio nos jogos dimensionais.'
    )
    
    rotulo = models.CharField(
        max_length=200,
        verbose_name='Rótulo Qualitativo',
        blank=True,
        default=''
    )
    
    valor_quantitativo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Valor Quantitativo (Marcador)'
    )
    
    descricao_qualitativa = models.TextField(
        verbose_name='Descrição Qualitativa',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Mapa de Marcador'
        verbose_name_plural = 'Mapa de Marcadores'
        unique_together = ['jogo', 'fase', 'resposta_chave']
        ordering = ['jogo', 'fase', '-nivel']
    
    def __str__(self):
        nivel_str = f" (Nível {self.nivel})" if self.nivel is not None else ""
        return f'{self.get_jogo_display()} / {self.fase} / {self.resposta_chave}{nivel_str}'


class MapaMarcador(models.Model):
    """
    Espelha a planilha de marcadores utilizada pelos pesquisadores.
    """

    jogo = models.CharField(
        max_length=50,
        verbose_name="Jogo"
    )

    fase = models.CharField(
        max_length=100,
        verbose_name="Fase"
    )

    resposta_chave = models.CharField(
        max_length=200,
        verbose_name="Resposta Chave"
    )

    sigla = models.CharField(
        max_length=3,
        blank=True,
        default=""
    )

    nivel = models.IntegerField(
        null=True,
        blank=True
    )

    rotulo = models.CharField(
        max_length=100
    )

    valor_quantitativo = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    descricao_qualitativa = models.TextField(
        blank=True,
        default=""
    )

    class Meta:
        verbose_name = "Mapa Marcador"
        verbose_name_plural = "Mapa Marcadores"

        unique_together = (
            "jogo",
            "fase",
            "resposta_chave",
        )

        ordering = (
            "jogo",
            "fase",
            "resposta_chave",
        )

    def __str__(self):
        return f"{self.jogo} | {self.fase} | {self.resposta_chave}"
# ========== MODELO AÇÃO ==========

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
    
    # Qual a fase
    fase = models.CharField(
        max_length=50,
        verbose_name='Fase',
        help_text='pre_fase, capitulo_1, capitulo_2, etc'
    )

    jogo = models.CharField(
    max_length=50,
    blank=True,
    default="",
    verbose_name="Jogo"
    )

    resposta_chave = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Resposta Chave"
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
        help_text='Ex: CLI, DRA, TIP, SEL, ENV, AVN, VOL, DIC, PUL'
    )
    
    nivel = models.IntegerField(
    null=True,
    blank=True,
    verbose_name="Nível"
    )

    rotulo = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Rótulo"
    )

    valor_marcador = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="Valor Marcador"
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
    
    # Tempo de Reação (em segundos)
    tempo_reacao = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Tempo de Reação (s)',
        help_text='Tempo entre o estímulo e o início da resposta',
        null=True,
        blank=True
    )
    
    # Tempo de Resposta (em segundos)
    tempo_resposta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Tempo de Resposta (s)',
        help_text='Tempo total para completar a ação',
        null=True,
        blank=True
    )
    
    # Pontuação
    pontuacao = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name='Pontuação'
    )
    
    # ===== CAMPOS DO MARCADOR =====
    jogo = models.CharField(
        max_length=30,
        verbose_name='Jogo',
        blank=True,
        null=True,
        help_text='piaget, volta_casa, volta_casa_cog'
    )
    
    resposta_chave = models.CharField(
        max_length=100,
        verbose_name='Chave da Resposta',
        blank=True,
        null=True,
        help_text='Identificador da opção escolhida (ex: certa, adjacente, longe)'
    )
    
    nivel = models.IntegerField(
        verbose_name='Nível do Marcador',
        null=True,
        blank=True,
        help_text='1, 2 ou 3 (preenchido automaticamente pelo mapa)'
    )
    
    rotulo = models.CharField(
        max_length=200,
        verbose_name='Rótulo Qualitativo',
        blank=True,
        null=True,
        help_text='Preenchido automaticamente pelo mapa'
    )
    
    valor_marcador = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Valor do Marcador',
        null=True,
        blank=True,
        help_text='Preenchido automaticamente pelo mapa'
    )
    
    # Data/hora
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Ação'
        verbose_name_plural = 'Ações'
        ordering = ['-created_at']
    
    def __str__(self):
        return (
            f"{self.crianca.nome} | "
            f"{self.jogo} | "
            f"{self.fase} | "
            f"{self.rotulo}"
        )
    
    def calcular_pontuacao(self):
        """
        Calcula pontuação baseada apenas no tipo de ação e tempos
        NÃO verifica se a resposta está correta
        """
        from decimal import Decimal
        
        if self.tipo == 'submit':
            # Pontuação baseada no tempo de reação
            if self.tempo_reacao and self.tempo_reacao < 1.0:
                return Decimal('1.5')
            elif self.tempo_reacao and self.tempo_reacao < 2.0:
                return Decimal('1.2')
            elif self.tempo_reacao and self.tempo_reacao < 3.0:
                return Decimal('1.0')
            else:
                return Decimal('0.8')
        
        elif self.tipo == 'hint':
            return Decimal('0.2')
        
        elif self.tipo == 'skip':
            return Decimal('0')
        
        elif self.tipo == 'click':
            return Decimal('0.3')
        
        elif self.tipo == 'select':
            return Decimal('0.4')
        
        elif self.tipo == 'type':
            if self.resposta and len(self.resposta) > 10:
                return Decimal('0.8')
            return Decimal('0.5')
        
        elif self.tipo == 'drag':
            return Decimal('0.6')
        
        elif self.tipo == 'next':
            return Decimal('0.1')
        
        elif self.tipo == 'back':
            return Decimal('0.05')
        
        return Decimal('0.3')
    
    def _derivar_marcador(self):
        """
        Consulta o mapa de marcadores e preenche automaticamente
        os campos derivados.
        """

        if self.nivel is not None:
            return

        if not (
            self.jogo
            and self.fase
            and self.resposta_chave
        ):
            return

        marcador = (
            MapaMarcador.objects
            .filter(
                jogo=self.jogo,
                fase=self.fase,
                resposta_chave=self.resposta_chave
            )
            .first()
        )

        if marcador is None:
            return

        self.nivel = marcador.nivel
        self.rotulo = marcador.rotulo
        self.valor_marcador = marcador.valor_quantitativo

        if marcador.sigla:
            self.sigla = marcador.sigla
            
    def save(self, *args, **kwargs):
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
        
        self._derivar_marcador()

        if self.pontuacao == 0:
            self.pontuacao = self.calcular_pontuacao()
        
        # ===== DERIVAÇÃO DO MARCADOR A PARTIR DO MAPA =====
        if self.jogo and self.resposta_chave and self.nivel is None:
            try:
                mapa = MapaMarcador.objects.filter(
                    jogo=self.jogo,
                    fase=self.fase,
                    resposta_chave=self.resposta_chave
                ).first()
                if mapa:
                    self.nivel = mapa.nivel
                    self.rotulo = mapa.rotulo
                    self.valor_marcador = mapa.valor_quantitativo
                    if mapa.sigla:
                        self.sigla = mapa.sigla
            except Exception:
                # Não quebra se o mapa não existir
                pass
        
        super().save(*args, **kwargs)
        
        if self.sessao:
            from django.db.models import Sum
            total_pontos = Acao.objects.filter(sessao=self.sessao).aggregate(
                total=Sum('pontuacao')
            )['total'] or Decimal('0')
            self.sessao.pontuacao_total = total_pontos
            self.sessao.save()


class Resultado(models.Model):
    titulo = models.CharField(max_length=200)
    valor = models.FloatField()

    def __str__(self):
        return self.titulo

