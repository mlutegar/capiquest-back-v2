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

# ===== NOVO MODELO TAREFA =====
class Tarefa(models.Model):
    """
    Modelo para representar uma tarefa no sistema
    """
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
        """Marca a tarefa como concluída e registra a data"""
        self.concluida = True
        self.data_conclusao = timezone.now()
        self.save()

    def get_absolute_url(self):
        """Retorna a URL para detalhes da tarefa"""
        return reverse('polls:tarefa_detail', args=[str(self.id)])

    @property
    def dias_desde_criacao(self):
        """Retorna quantos dias se passaram desde a criação"""
        delta = timezone.now() - self.data_criacao
        return delta.days