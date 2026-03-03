from django.contrib import admin
from django.utils import timezone
from .models import Question, Choice, Tarefa, Crianca, Sessao

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'concluida', 'data_criacao', 'data_conclusao']
    list_filter = ['concluida', 'data_criacao']
    search_fields = ['titulo']
    date_hierarchy = 'data_criacao'
    
    actions = ['marcar_como_concluidas']
    
    def marcar_como_concluidas(self, request, queryset):
        queryset.update(concluida=True, data_conclusao=timezone.now())
    marcar_como_concluidas.short_description = "Marcar tarefas selecionadas como concluídas"


@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'idade', 'instituicao', 'data_cadastro']
    list_filter = ['idade', 'instituicao']
    search_fields = ['nome', 'instituicao']
    date_hierarchy = 'data_cadastro'


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'crianca', 'instituicao', 'data_inicio', 'data_fim', 'pontuacao']
    list_filter = ['data_inicio', 'instituicao', 'crianca']
    search_fields = ['crianca__nome', 'instituicao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['data_inicio']