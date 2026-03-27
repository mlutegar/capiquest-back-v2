from django.urls import path
from . import views

app_name = "polls"

urlpatterns = [
    # ===== URLs para AÇÕES =====
    path("api/acoes/registrar/", views.RegistrarAcaoView.as_view(), name="api_acoes_registrar"),
    path("api/acoes/", views.ListarAcoesView.as_view(), name="api_acoes_list"),
    path("api/acoes/<int:pk>/", views.AcaoDetailView.as_view(), name="api_acoes_detail"),
    
    # ===== URLs para CRIANÇAS =====
    path("api/criancas/", views.CriancaListView.as_view(), name="api_crianca_list"),
    path("api/criancas/<int:pk>/", views.CriancaDetailView.as_view(), name="api_crianca_detail"),
    
    # ===== URLs para SESSÕES =====
    path("api/sessoes/iniciar/", views.IniciarSessaoView.as_view(), name="api_sessao_iniciar"),
    path("api/sessoes/", views.SessaoListView.as_view(), name="api_sessao_list"),
    path("api/sessoes/<int:pk>/", views.SessaoDetailView.as_view(), name="api_sessao_detail"),
    path("api/sessoes/<int:pk>/finalizar/", views.FinalizarSessaoView.as_view(), name="api_sessao_finalizar"),
    
    # ===== URLs para CAPÍTULOS =====
    path("api/capitulos/", views.CapituloListView.as_view(), name="api_capitulo_list"),
    path("api/capitulos/<int:pk>/", views.CapituloDetailView.as_view(), name="api_capitulo_detail"),
    path("api/capitulos/<int:capitulo_id>/caminhos/", views.CapituloCaminhosView.as_view(), name="api_capitulo_caminhos"),
    
    # ===== URLs para CAMINHOS =====
    path("api/caminhos/<int:caminho_id>/desafios/", views.CaminhoDesafiosView.as_view(), name="api_caminho_desafios"),
    
    # ===== URLs para PROGRESSÃO =====
    path("api/progressao/<int:crianca_id>/", views.ProgressaoView.as_view(), name="api_progressao"),
    
    # ===== URLs para ENQUETES =====
    path("", views.IndexView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    
    # ===== URLs para TAREFAS =====
    path("tarefas/", views.TarefaListView.as_view(), name="tarefa_list"),
    path("tarefas/nova/", views.TarefaCreateView.as_view(), name="tarefa_create"),
    path("tarefas/<int:pk>/", views.TarefaDetailView.as_view(), name="tarefa_detail"),
    path("tarefas/<int:pk>/editar/", views.TarefaUpdateView.as_view(), name="tarefa_edit"),
    path("tarefas/<int:pk>/deletar/", views.TarefaDeleteView.as_view(), name="tarefa_delete"),
    path("tarefas/<int:pk>/concluir/", views.TarefaConcluirView.as_view(), name="tarefa_concluir"),
    
    # ===== URLs da API REST para TAREFAS =====
    path("api/tarefas/", views.TarefaListCreateAPIView.as_view(), name="api_tarefa_list_create"),
    path("api/tarefas/<int:pk>/", views.TarefaRetrieveUpdateDestroyAPIView.as_view(), name="api_tarefa_detail"),
]