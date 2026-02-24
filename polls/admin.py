from django.contrib import admin
from django.utils import timezone  
from .models import Question, Choice, Tarefa 

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
    """
    Configuração do admin para o modelo Tarefa
    """
    list_display = ['titulo', 'concluida', 'data_criacao', 'data_conclusao']
    list_filter = ['concluida', 'data_criacao']
    search_fields = ['titulo']
    date_hierarchy = 'data_criacao'
    
    # Ações personalizadas no admin
    actions = ['marcar_como_concluidas']
    
    def marcar_como_concluidas(self, request, queryset):
        """Ação para marcar múltiplas tarefas como concluídas"""
        queryset.update(concluida=True, data_conclusao=timezone.now())
    marcar_como_concluidas.short_description = "Marcar tarefas selecionadas como concluídas"
    
    # Personaliza o formulário de edição
    fieldsets = [
        (None, {
            'fields': ['titulo', 'concluida']
        }),
        ('Informações de Data', {
            'fields': ['data_criacao', 'data_conclusao'],
            'classes': ['collapse']  # Recolhível
        }),
    ]
    
    # Campos somente leitura
    readonly_fields = ['data_conclusao']