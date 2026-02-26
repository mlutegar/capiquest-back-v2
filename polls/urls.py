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
    
    # ===== URLs da API REST =====
    path("api/tarefas/", views.TarefaListCreateAPIView.as_view(), name="api_tarefa_list_create"),
    path("api/tarefas/<int:pk>/", views.TarefaRetrieveUpdateDestroyAPIView.as_view(), name="api_tarefa_detail"),
]