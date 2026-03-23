from django.contrib import admin
from django.utils import timezone
from .models import (
    Question, Choice, Tarefa, Crianca, Sessao,
    Capitulo, Caminho, Desafio, Interacao
)

# ========== ADMIN PARA ENQUETES (POLLS) ==========

class ChoiceInline(admin.TabularInline):
    """
    Inline para exibir choices dentro da edição de Question
    """
    model = Choice
    extra = 3
    classes = ['collapse']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Question (enquetes)
    """
    fieldsets = [
        (None, {
            'fields': ['question_text'],
            'classes': ['wide']
        }),
        ('Informações de Data', {
            'fields': ['pub_date'],
            'classes': ['collapse']
        }),
    ]
    inlines = [ChoiceInline]
    list_display = ['question_text', 'pub_date', 'was_published_recently']
    list_filter = ['pub_date']
    search_fields = ['question_text']
    date_hierarchy = 'pub_date'
    list_per_page = 20
    
    actions = ['publicar_agora']
    
    def publicar_agora(self, request, queryset):
        """Action para definir a data de publicação como agora"""
        queryset.update(pub_date=timezone.now())
    publicar_agora.short_description = "Definir data de publicação como agora"


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Choice (opções de resposta)
    """
    list_display = ['choice_text', 'question', 'votes']
    list_filter = ['question']
    search_fields = ['choice_text', 'question__question_text']
    list_editable = ['votes']
    autocomplete_fields = ['question']


# ========== ADMIN PARA TAREFAS ==========

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Tarefa
    """
    list_display = ['titulo', 'concluida', 'data_criacao', 'data_conclusao', 'dias_desde_criacao']
    list_filter = ['concluida', 'data_criacao']
    search_fields = ['titulo']
    date_hierarchy = 'data_criacao'
    list_editable = ['concluida']
    list_per_page = 20
    
    actions = ['marcar_como_concluidas', 'marcar_como_pendentes']
    
    def marcar_como_concluidas(self, request, queryset):
        """Action para marcar tarefas como concluídas"""
        queryset.update(concluida=True, data_conclusao=timezone.now())
    marcar_como_concluidas.short_description = "✅ Marcar como concluídas"
    
    def marcar_como_pendentes(self, request, queryset):
        """Action para marcar tarefas como pendentes"""
        queryset.update(concluida=False, data_conclusao=None)
    marcar_como_pendentes.short_description = "⏳ Marcar como pendentes"
    
    fieldsets = [
        (None, {
            'fields': ['titulo', 'concluida'],
            'classes': ['wide']
        }),
        ('Informações de Data', {
            'fields': ['data_criacao', 'data_conclusao'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['data_criacao', 'data_conclusao']
    
    def dias_desde_criacao(self, obj):
        """Exibe quantos dias desde a criação"""
        return obj.dias_desde_criacao
    dias_desde_criacao.short_description = 'Dias desde criação'
    dias_desde_criacao.admin_order_field = 'data_criacao'


# ========== ADMIN PARA CRIANÇAS E SESSÕES ==========

@admin.register(Crianca)
class CriancaAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Crianca
    """
    list_display = ['nome', 'idade', 'instituicao', 'data_cadastro', 'total_sessoes']
    list_filter = ['idade', 'instituicao', 'data_cadastro']
    search_fields = ['nome', 'instituicao']
    date_hierarchy = 'data_cadastro'
    list_per_page = 20
    list_editable = ['idade', 'instituicao']
    
    fieldsets = [
        ('Informações Pessoais', {
            'fields': ['nome', 'idade', 'instituicao'],
            'classes': ['wide']
        }),
        ('Informações do Sistema', {
            'fields': ['data_cadastro'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['data_cadastro']
    
    def total_sessoes(self, obj):
        """Retorna o total de sessões da criança"""
        return obj.sessoes.count()
    total_sessoes.short_description = 'Total de Sessões'
    
    actions = ['exportar_dados']
    
    def exportar_dados(self, request, queryset):
        """Action para exportar dados das crianças (exemplo)"""
        self.message_user(request, f"Dados de {queryset.count()} crianças exportados com sucesso!")
    exportar_dados.short_description = "Exportar dados das crianças selecionadas"


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Sessao
    """
    list_display = [
        'id', 'crianca', 'instituicao', 'data_inicio', 
        'data_fim', 'duracao', 'pontuacao', 'status'
    ]
    list_filter = ['data_inicio', 'instituicao', 'crianca', 'data_fim']
    search_fields = ['crianca__nome', 'instituicao']
    date_hierarchy = 'data_inicio'
    readonly_fields = ['data_inicio']
    list_per_page = 20
    list_select_related = ['crianca']
    
    fieldsets = [
        ('Criança', {
            'fields': ['crianca', 'instituicao'],
            'classes': ['wide']
        }),
        ('Tempo', {
            'fields': ['data_inicio', 'data_fim'],
            'classes': ['collapse']
        }),
        ('Desempenho', {
            'fields': ['pontuacao'],
            'classes': ['wide']
        }),
    ]
    
    def duracao(self, obj):
        """Calcula a duração da sessão"""
        if obj.data_fim:
            delta = obj.data_fim - obj.data_inicio
            minutos = delta.total_seconds() // 60
            segundos = delta.total_seconds() % 60
            return f"{int(minutos)}m {int(segundos)}s"
        return "Em andamento"
    duracao.short_description = 'Duração'
    
    def status(self, obj):
        """Status da sessão (ativa/finalizada)"""
        if obj.data_fim:
            return '<span style="color: green;">✅ Finalizada</span>'
        return '<span style="color: blue;">⏳ Ativa</span>'
    status.short_description = 'Status'
    status.allow_tags = True
    
    actions = ['finalizar_sessoes']
    
    def finalizar_sessoes(self, request, queryset):
        """Action para finalizar sessões"""
        count = 0
        for sessao in queryset.filter(data_fim__isnull=True):
            sessao.finalizar()
            count += 1
        self.message_user(request, f"{count} sessões finalizadas com sucesso!")
    finalizar_sessoes.short_description = "Finalizar sessões selecionadas"


# ========== ADMIN PARA CAPÍTULOS, CAMINHOS E DESAFIOS ==========

class DesafioInline(admin.TabularInline):
    """
    Inline para exibir desafios dentro da edição de Caminho
    """
    model = Desafio
    extra = 1
    fields = ['ordem', 'tipo_pista', 'conteudo_pista', 'resposta_correta']
    classes = ['collapse']


class CaminhoInline(admin.TabularInline):
    """
    Inline para exibir caminhos dentro da edição de Capítulo
    """
    model = Caminho
    extra = 1
    fields = ['nome', 'cor', 'dificuldade', 'ordem']
    classes = ['collapse']


@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Capitulo
    """
    list_display = ['ordem', 'titulo', 'descricao_resumida', 'total_caminhos', 'data_criacao']
    list_display_links = ['titulo']
    list_editable = ['ordem']
    search_fields = ['titulo', 'descricao']
    list_filter = ['ordem', 'data_criacao']
    date_hierarchy = 'data_criacao'
    list_per_page = 20
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': ['titulo', 'descricao', 'ordem'],
            'classes': ['wide']
        }),
        ('Informações do Sistema', {
            'fields': ['data_criacao'],
            'classes': ['collapse']
        }),
    ]
    
    readonly_fields = ['data_criacao']
    inlines = [CaminhoInline]
    
    def descricao_resumida(self, obj):
        """Resumo da descrição para a listagem"""
        if obj.descricao and len(obj.descricao) > 50:
            return obj.descricao[:50] + '...'
        return obj.descricao or '-'
    descricao_resumida.short_description = 'Descrição'
    
    def total_caminhos(self, obj):
        """Total de caminhos no capítulo"""
        return obj.caminhos.count()
    total_caminhos.short_description = 'Caminhos'
    
    actions = ['duplicar_capitulo']
    
    def duplicar_capitulo(self, request, queryset):
        """Action para duplicar capítulo (exemplo)"""
        for capitulo in queryset:
            capitulo.pk = None
            capitulo.titulo = f"Cópia de {capitulo.titulo}"
            capitulo.save()
        self.message_user(request, f"{queryset.count()} capítulos duplicados com sucesso!")
    duplicar_capitulo.short_description = "Duplicar capítulos selecionados"


@admin.register(Caminho)
class CaminhoAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Caminho
    """
    list_display = [
        'capitulo', 'ordem', 'nome', 'cor_visual', 
        'dificuldade', 'total_desafios'
    ]
    list_display_links = ['nome']
    list_editable = ['ordem', 'dificuldade']
    list_filter = ['capitulo', 'dificuldade', 'cor']
    search_fields = ['nome', 'capitulo__titulo']
    list_per_page = 20
    list_select_related = ['capitulo']
    
    fieldsets = [
        ('Relação', {
            'fields': ['capitulo'],
            'classes': ['wide']
        }),
        ('Informações do Caminho', {
            'fields': ['nome', 'cor', 'dificuldade', 'ordem'],
            'classes': ['wide']
        }),
    ]
    
    inlines = [DesafioInline]
    
    def cor_visual(self, obj):
        """Exibe um bloco colorido para representar a cor"""
        cores = {
            'vermelho': '#FF0000',
            'azul': '#0000FF',
            'verde': '#00FF00',
            'amarelo': '#FFFF00',
            'roxo': '#800080',
            'laranja': '#FFA500',
        }
        cor_hex = cores.get(obj.cor.lower(), '#CCCCCC')
        return f'<span style="display:inline-block; width:20px; height:20px; background-color:{cor_hex}; border-radius:4px;"></span> {obj.cor}'
    cor_visual.short_description = 'Cor'
    cor_visual.allow_tags = True
    
    def total_desafios(self, obj):
        """Total de desafios no caminho"""
        return obj.desafios.count()
    total_desafios.short_description = 'Desafios'


@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Desafio
    """
    list_display = [
        'caminho', 'ordem', 'tipo_pista_icone', 
        'conteudo_resumido', 'resposta_correta'
    ]
    list_display_links = ['tipo_pista_icone']
    list_editable = ['ordem']
    list_filter = ['tipo_pista', 'caminho__capitulo', 'caminho']
    search_fields = ['conteudo_pista', 'resposta_correta']
    list_per_page = 20
    list_select_related = ['caminho', 'caminho__capitulo']
    
    fieldsets = [
        ('Relação', {
            'fields': ['caminho'],
            'classes': ['wide']
        }),
        ('Configuração do Desafio', {
            'fields': ['ordem', 'tipo_pista'],
            'classes': ['wide']
        }),
        ('Conteúdo', {
            'fields': ['conteudo_pista', 'resposta_correta'],
            'classes': ['wide']
        }),
    ]
    
    def tipo_pista_icone(self, obj):
        """Ícone para o tipo de pista"""
        icones = {
            'text': '📝 Texto',
            'image': '🖼️ Imagem',
            'audio': '🔊 Áudio',
        }
        return icones.get(obj.tipo_pista, obj.tipo_pista)
    tipo_pista_icone.short_description = 'Tipo'
    
    def conteudo_resumido(self, obj):
        """Resumo do conteúdo para a listagem"""
        if obj.conteudo_pista and len(obj.conteudo_pista) > 30:
            return obj.conteudo_pista[:30] + '...'
        return obj.conteudo_pista or '-'
    conteudo_resumido.short_description = 'Conteúdo'


@admin.register(Interacao)
class InteracaoAdmin(admin.ModelAdmin):
    """
    Administração para o modelo Interacao
    """
    list_display = [
        'aluno', 'desafio_info', 'resposta_resumida', 
        'acertou_icone', 'pontos', 'created_at'
    ]
    list_display_links = ['aluno']
    list_filter = [
        'acertou', 'created_at', 'desafio__caminho__capitulo',
        'desafio__caminho'
    ]
    search_fields = ['aluno__nome', 'resposta_dada']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    list_per_page = 30
    list_select_related = ['aluno', 'desafio', 'desafio__caminho']
    
    fieldsets = [
        ('Quem', {
            'fields': ['aluno'],
            'classes': ['wide']
        }),
        ('O quê', {
            'fields': ['desafio', 'resposta_dada'],
            'classes': ['wide']
        }),
        ('Resultado', {
            'fields': ['acertou', 'pontos'],
            'classes': ['wide']
        }),
        ('Quando', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def desafio_info(self, obj):
        """Informações do desafio"""
        return f"{obj.desafio.caminho.nome} - #{obj.desafio.ordem}"
    desafio_info.short_description = 'Desafio'
    desafio_info.admin_order_field = 'desafio__caminho__nome'
    
    def resposta_resumida(self, obj):
        """Resumo da resposta dada"""
        if obj.resposta_dada and len(obj.resposta_dada) > 30:
            return obj.resposta_dada[:30] + '...'
        return obj.resposta_dada or '-'
    resposta_resumida.short_description = 'Resposta'
    
    def acertou_icone(self, obj):
        """Ícone para acerto/erro"""
        if obj.acertou:
            return '<span style="color: green;">✅ Sim</span>'
        return '<span style="color: red;">❌ Não</span>'
    acertou_icone.short_description = 'Acertou?'
    acertou_icone.allow_tags = True
    
    actions = ['recalcular_pontos']
    
    def recalcular_pontos(self, request, queryset):
        """Action para recalcular pontos das interações"""
        for interacao in queryset:
            interacao.save()  # O save já recalcula os pontos
        self.message_user(request, f"Pontos recalculados para {queryset.count()} interações!")
    recalcular_pontos.short_description = "Recalcular pontos das interações"


# ========== PERSONALIZAÇÃO DO SITE ADMIN ==========

admin.site.site_header = 'Administração do Sistema Polls'
admin.site.site_title = 'Polls Admin'
admin.site.index_title = 'Bem-vindo ao Painel de Administração'

# ===== ADMIN PARA PRÉ-FASE (VERSÃO CORRIGIDA) =====

from .models import PreFaseDesafio, InteracaoPreFase


@admin.register(PreFaseDesafio)
class PreFaseDesafioAdmin(admin.ModelAdmin):
    """
    Administração para os desafios da pré-fase
    """
    list_display = ['ordem', 'tipo_pista', 'conteudo_resumido', 'resposta_correta', 'dica_resumida']
    list_display_links = ['tipo_pista']  # Tipo da pista vira link
    list_editable = ['ordem']  # Ordem editável diretamente na lista
    search_fields = ['conteudo_pista', 'resposta_correta']
    list_filter = ['tipo_pista']
    list_per_page = 20
    
    fieldsets = [
        ('Configuração', {
            'fields': ['ordem', 'tipo_pista'],
            'classes': ['wide']
        }),
        ('Conteúdo', {
            'fields': ['conteudo_pista', 'resposta_correta', 'dica'],
            'classes': ['wide']
        }),
    ]
    
    def conteudo_resumido(self, obj):
        """Resumo do conteúdo para a listagem"""
        if obj.conteudo_pista and len(obj.conteudo_pista) > 50:
            return obj.conteudo_pista[:50] + '...'
        return obj.conteudo_pista or '-'
    conteudo_resumido.short_description = 'Conteúdo'
    
    def dica_resumida(self, obj):
        """Resumo da dica para a listagem"""
        if obj.dica:
            if len(obj.dica) > 40:
                return obj.dica[:40] + '...'
            return obj.dica
        return '-'
    dica_resumida.short_description = 'Dica'


@admin.register(InteracaoPreFase)
class InteracaoPreFaseAdmin(admin.ModelAdmin):
    """
    Administração para as interações da pré-fase
    """
    list_display = ['aluno', 'desafio', 'acertou_icone', 'tentativas', 'created_at']
    list_display_links = ['aluno']  # Aluno vira link
    list_filter = ['acertou', 'created_at']
    search_fields = ['aluno__nome', 'resposta_dada']
    readonly_fields = ['created_at']
    list_per_page = 30
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Quem', {
            'fields': ['aluno'],
            'classes': ['wide']
        }),
        ('Desafio', {
            'fields': ['desafio', 'resposta_dada'],
            'classes': ['wide']
        }),
        ('Resultado', {
            'fields': ['acertou', 'tentativas'],
            'classes': ['wide']
        }),
        ('Quando', {
            'fields': ['created_at'],
            'classes': ['collapse']
        }),
    ]
    
    def acertou_icone(self, obj):
        """Ícone para acerto/erro"""
        if obj.acertou:
            return '<span style="color: green;">✅ Sim</span>'
        return '<span style="color: red;">❌ Não</span>'
    acertou_icone.short_description = 'Acertou?'
    acertou_icone.allow_tags = True
    
    def desafio_info(self, obj):
        """Informações do desafio"""
        return f"Desafio {obj.desafio.ordem}"
    desafio_info.short_description = 'Desafio'