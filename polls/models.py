import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.urls import reverse

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
        help_text='Digite o título da tarefa',
        verbose_name='Título'
    )
    
    concluida = models.BooleanField(
        default=False,
        verbose_name='Concluída?',
        help_text='Marque se a tarefa já foi concluída'
    )
    
    data_criacao = models.DateTimeField(
        default=timezone.now,
        verbose_name='Data de Criação',
        help_text='Data e hora em que a tarefa foi criada'
    )
    
    data_conclusao = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Data de Conclusão',
        help_text='Data em que a tarefa foi concluída'
    )

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


class Crianca(models.Model):
    """
    Modelo para representar uma criança no sistema
    """
    instituicao = models.CharField(
        max_length=200,
        verbose_name='Instituição',
        help_text='Nome da escola/instituição da criança',
        blank=True,
        null=True
    )
    
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome',
        help_text='Nome da criança'
    )
    
    idade = models.IntegerField(
        verbose_name='Idade',
        help_text='Idade da criança em anos'
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
        else:
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
        help_text='Instituição da criança no momento da sessão',
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
    
    pontuacao = models.IntegerField(
        default=0,
        verbose_name='Pontuação'
    )
    
    class Meta:
        verbose_name = 'Sessão'
        verbose_name_plural = 'Sessões'
        ordering = ['-data_inicio']
    
    def __str__(self):
        if self.instituicao:
            return f"Sessão de {self.crianca.nome} - {self.instituicao} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
        else:
            return f"Sessão de {self.crianca.nome} - {self.data_inicio.strftime('%d/%m/%Y %H:%M')}"
    
    def save(self, *args, **kwargs):
        if not self.instituicao and self.crianca_id:
            self.instituicao = self.crianca.instituicao
        super().save(*args, **kwargs)
    
    def finalizar(self):
        self.data_fim = timezone.now()
        self.save()


# ===== MODELOS: CAPITULO, CAMINHO, DESAFIO, INTERACAO =====

class Capitulo(models.Model):
    """
    Modelo para representar um capítulo do jogo educativo
    """
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
        help_text='Título do capítulo'
    )
    
    descricao = models.TextField(
        verbose_name='Descrição',
        help_text='Descrição do capítulo',
        blank=True,
        null=True
    )
    
    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição do capítulo'
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
        verbose_name='Nome',
        help_text='Nome do caminho'
    )
    
    cor = models.CharField(
        max_length=50,
        verbose_name='Cor',
        help_text='Cor para identificação visual (ex: "vermelho", "#FF0000")',
        default='azul'
    )
    
    dificuldade = models.CharField(
        max_length=50,
        verbose_name='Dificuldade',
        help_text='Nível de dificuldade (fácil, médio, difícil)',
        default='médio'
    )
    
    ordem = models.IntegerField(
        default=0,
        verbose_name='Ordem',
        help_text='Ordem de exibição do caminho'
    )
    
    class Meta:
        verbose_name = 'Caminho'
        verbose_name_plural = 'Caminhos'
        ordering = ['capitulo__ordem', 'ordem', 'nome']
    
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
        verbose_name='Ordem',
        help_text='Ordem do desafio dentro do caminho'
    )
    
    tipo_pista = models.CharField(
        max_length=10,
        choices=TIPO_PISTA_CHOICES,
        verbose_name='Tipo de Pista',
        default='text'
    )
    
    conteudo_pista = models.TextField(
        verbose_name='Conteúdo da Pista',
        help_text='Texto, URL da imagem ou áudio'
    )
    
    resposta_correta = models.CharField(
        max_length=500,
        verbose_name='Resposta Correta',
        help_text='Resposta esperada para o desafio'
    )
    
    class Meta:
        verbose_name = 'Desafio'
        verbose_name_plural = 'Desafios'
        ordering = ['caminho__ordem', 'ordem']
        unique_together = ['caminho', 'ordem']
    
    def __str__(self):
        return f"Desafio {self.ordem} - {self.caminho.nome}"


class Interacao(models.Model):
    """
    Modelo para registrar as interações dos alunos com os desafios
    """
    aluno = models.ForeignKey(
        Crianca,
        on_delete=models.CASCADE,
        related_name='interacoes',
        verbose_name='Aluno'
    )
    
    desafio = models.ForeignKey(
        Desafio,
        on_delete=models.CASCADE,
        related_name='interacoes',
        verbose_name='Desafio'
    )
    
    resposta_dada = models.CharField(
        max_length=500,
        verbose_name='Resposta Dada',
        help_text='Resposta fornecida pelo aluno'
    )
    
    acertou = models.BooleanField(
        verbose_name='Acertou?',
        help_text='Se o aluno acertou o desafio'
    )
    
    pontos = models.IntegerField(
        default=0,
        verbose_name='Pontos',
        help_text='Pontuação obtida'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )
    
    class Meta:
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'
        ordering = ['-created_at']
        unique_together = ['aluno', 'desafio']
    
    def __str__(self):
        return f"{self.aluno.nome} - Desafio {self.desafio.id} - {'✅' if self.acertou else '❌'}"
    
    def calcular_pontos(self):
        """Calcula a pontuação baseada na dificuldade do caminho"""
        if not self.acertou:
            return 0
        
        dificuldade = self.desafio.caminho.dificuldade.lower()
        
        # Mapeamento de pontuação por dificuldade
        tabela_pontos = {
            'fácil': 10,
            'facil': 10,
            'médio': 20,
            'medio': 20,
            'difícil': 30,
            'dificil': 30,
        }
        
        return tabela_pontos.get(dificuldade, 10)
    
    def save(self, *args, **kwargs):
        """Auto-preenche acertou e pontos"""
        if not self.pk:  # Só na criação
            self.acertou = self.resposta_dada.strip().lower() == self.desafio.resposta_correta.strip().lower()
        
        self.pontos = self.calcular_pontos()
        
        super().save(*args, **kwargs)