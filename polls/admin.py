from django.contrib import admin
from django.utils import timezone
from .models import (
    Question, Choice, Tarefa, Crianca, Sessao,
    Capitulo, Caminho, Desafio, Acao
)


# ========== ADMIN PARA ENQUETES ==========

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]
    search_fields = ["question_text"]


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'votes']
    list_filter = ['question']
    search_fields = ['choice_text']


# ========== ADMIN PARA TAREFAS ==========

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'concluida', 'data_criacao', 'data_conclusao']
    list_filter = ['concluida', 'data_criacao']
    search_fields = ['titulo']
    date_hierarchy = 'data_criacao'
    
    actions = ['marcar_como_concluidas', 'marcar_como_pendentes']
    
    def marcar_como_concluidas(self, request, queryset):
        queryset.update(concluida=True, data_conclusao=timezone.now())
    marcar_como_concluidas.short_description = "✅ Marcar como concluídas"
    
    def marcar_como_pendentes(self, request, queryset):
        queryset.update(concluida=False, data_conclusao=None)
    marcar_como_pendentes.short_description = "⏳ Marcar como pendentes"


# ========== ADMIN PARA CRIANÇAS ==========

@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'idade', 'instituicao', 'fase_atual', 'data_cadastro']
    list_filter = ['idade', 'fase_atual', 'data_cadastro']
    search_fields = ['nome', 'instituicao']
    date_hierarchy = 'data_cadastro'
    list_editable = ['idade', 'instituicao']


# ========== ADMIN PARA SESSÕES ==========

@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ['crianca', 'data_inicio', 'data_fim', 'pontuacao_total', 'duracao']
    list_filter = ['data_inicio', 'crianca']
    search_fields = ['crianca__nome']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['data_inicio', 'pontuacao_total']
    list_select_related = ['crianca']
    
    def duracao(self, obj):
        if obj.data_fim:
            delta = obj.data_fim - obj.data_inicio
            minutos = delta.total_seconds() // 60
            segundos = delta.total_seconds() % 60
            return f"{int(minutos)}m {int(segundos)}s"
        return "Em andamento"
    duracao.short_description = 'Duração'


# ========== ADMIN PARA CAPÍTULOS, CAMINHOS E DESAFIOS ==========

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ['ordem', 'titulo', 'descricao_resumida']
    list_editable = ['ordem']
    list_display_links = ['titulo']
    search_fields = ['titulo', 'descricao']
    
    def descricao_resumida(self, obj):
        if obj.descricao and len(obj.descricao) > 50:
            return obj.descricao[:50] + '...'
        return obj.descricao or '-'
    descricao_resumida.short_description = 'Descrição'


@admin.register(Caminho)
class CaminhoAdmin(admin.ModelAdmin):
    list_display = ['capitulo', 'ordem', 'nome', 'cor', 'dificuldade']
    list_editable = ['ordem']
    list_display_links = ['nome']
    list_filter = ['capitulo', 'dificuldade', 'cor']
    search_fields = ['nome', 'capitulo__titulo']


@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ['caminho', 'ordem', 'tipo_pista', 'conteudo_resumido']
    list_editable = ['ordem']
    list_display_links = ['tipo_pista']
    list_filter = ['tipo_pista', 'caminho__capitulo']
    search_fields = ['conteudo_pista', 'resposta_correta']
    
    def conteudo_resumido(self, obj):
        if obj.conteudo_pista and len(obj.conteudo_pista) > 50:
            return obj.conteudo_pista[:50] + '...'
        return obj.conteudo_pista or '-'
    conteudo_resumido.short_description = 'Conteúdo'


# ========== ADMIN PARA AÇÕES ==========

@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = [
        'crianca', 'sigla', 'tipo', 'fase', 
        'tempo_reacao_formatado', 'tempo_resposta_formatado', 
        'pontuacao_formatada', 'created_at'
    ]
    list_display_links = ['crianca']
    list_filter = ['tipo', 'fase', 'created_at']
    search_fields = ['crianca__nome', 'resposta', 'sigla']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_select_related = ['crianca', 'sessao']
    list_per_page = 30
    
    fieldsets = [
        ('Quem', {
            'fields': ['crianca', 'sessao'],
            'classes': ['wide']
        }),
        ('O que', {
            'fields': ['fase', 'desafio', 'tipo', 'sigla', 'resposta'],
            'classes': ['wide']
        }),
        ('Métricas de Tempo', {
            'fields': ['tempo_reacao', 'tempo_resposta'],
            'classes': ['wide']
        }),
        ('Pontuação', {
            'fields': ['pontuacao'],
            'classes': ['wide']
        }),
        ('Quando', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def tempo_reacao_formatado(self, obj):
        if obj.tempo_reacao is not None:
            return f"{obj.tempo_reacao:.2f}s"
        return '-'
    tempo_reacao_formatado.short_description = 'Tempo Reação'
    tempo_reacao_formatado.admin_order_field = 'tempo_reacao'
    
    def tempo_resposta_formatado(self, obj):
        if obj.tempo_resposta is not None:
            return f"{obj.tempo_resposta:.2f}s"
        return '-'
    tempo_resposta_formatado.short_description = 'Tempo Resposta'
    tempo_resposta_formatado.admin_order_field = 'tempo_resposta'
    
    def pontuacao_formatada(self, obj):
        return f"{obj.pontuacao:.2f}"
    pontuacao_formatada.short_description = 'Pontuação'
    pontuacao_formatada.admin_order_field = 'pontuacao'