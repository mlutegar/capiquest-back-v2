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
    AGORA COM INSTITUIÇÃO COMO CAMPO DE TEXTO SIMPLES
    """
    instituicao = models.CharField(
        max_length=200,
        verbose_name='Instituição',
        help_text='Nome da escola/instituição da criança',
        blank=True,  # Permite vazio
        null=True    # Permite nulo no banco
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
    
    # Instituição agora é apenas uma cópia/reflexo do campo da criança
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
        # Auto-preenche instituição baseado na criança se não foi fornecido
        if not self.instituicao and self.crianca_id:
            self.instituicao = self.crianca.instituicao
        super().save(*args, **kwargs)
    
    def finalizar(self):
        self.data_fim = timezone.now()
        self.save()