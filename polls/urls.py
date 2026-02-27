from django.urls import path
from . import views

app_name = "polls"
urlpatterns = [
    # URLs existentes para enquetes
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    
    # URLs para Tarefas (frontend)
    path("tarefas/", views.TarefaListView.as_view(), name="tarefa_list"),
    path("tarefas/nova/", views.TarefaCreateView.as_view(), name="tarefa_create"),
    path("tarefas/<int:pk>/", views.TarefaDetailView.as_view(), name="tarefa_detail"),
    path("tarefas/<int:pk>/editar/", views.TarefaUpdateView.as_view(), name="tarefa_edit"),
    path("tarefas/<int:pk>/deletar/", views.TarefaDeleteView.as_view(), name="tarefa_delete"),
    path("tarefas/<int:pk>/concluir/", views.TarefaConcluirView.as_view(), name="tarefa_concluir"),
    
    # URLs da API REST para Tarefas
    path("api/tarefas/", views.TarefaListCreateAPIView.as_view(), name="api_tarefa_list_create"),
    path("api/tarefas/<int:pk>/", views.TarefaRetrieveUpdateDestroyAPIView.as_view(), name="api_tarefa_detail"),
    
    # ===== NOVAS URLs para Crianças e Sessões =====
    path("api/sessoes/iniciar/", views.IniciarSessaoView.as_view(), name="api_sessao_iniciar"),
    path("api/sessoes/", views.SessaoListView.as_view(), name="api_sessao_list"),
    path("api/sessoes/<int:pk>/", views.SessaoDetailView.as_view(), name="api_sessao_detail"),
    path("api/sessoes/<int:pk>/finalizar/", views.FinalizarSessaoView.as_view(), name="api_sessao_finalizar"),
    
    path("api/criancas/", views.CriancaListView.as_view(), name="api_crianca_list"),
    path("api/criancas/<int:pk>/", views.CriancaDetailView.as_view(), name="api_crianca_detail"),
]