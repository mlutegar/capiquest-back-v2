from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from .models import Choice, Question, Tarefa

# ===== IMPORTS DA API =====
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import TarefaSerializer

# ========== VIEWS EXISTENTES PARA ENQUETES ==========

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[:5]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tarefas_recentes'] = Tarefa.objects.all().order_by('-data_criacao')[:5]
        return context

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        return Question.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

# ========== VIEWS PARA TAREFAS (FRONTEND) ==========

class TarefaListView(generic.ListView):
    model = Tarefa
    template_name = 'polls/tarefa_list.html'
    context_object_name = 'tarefas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        filtro = self.request.GET.get('filtro')
        
        if filtro == 'concluidas':
            return queryset.filter(concluida=True)
        elif filtro == 'pendentes':
            return queryset.filter(concluida=False)
        return queryset

class TarefaDetailView(generic.DetailView):
    model = Tarefa
    template_name = 'polls/tarefa_detail.html'

class TarefaCreateView(generic.CreateView):
    model = Tarefa
    template_name = 'polls/tarefa_form.html'
    fields = ['titulo']
    success_url = reverse_lazy('polls:tarefa_list')
    
    def form_valid(self, form):
        form.instance.data_criacao = timezone.now()
        return super().form_valid(form)

class TarefaUpdateView(generic.UpdateView):
    model = Tarefa
    template_name = 'polls/tarefa_form.html'
    fields = ['titulo', 'concluida']
    success_url = reverse_lazy('polls:tarefa_list')

class TarefaDeleteView(generic.DeleteView):
    model = Tarefa
    template_name = 'polls/tarefa_confirm_delete.html'
    success_url = reverse_lazy('polls:tarefa_list')

class TarefaConcluirView(generic.View):
    def post(self, request, *args, **kwargs):
        return self.marcar_concluida(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.marcar_concluida(request, *args, **kwargs)
    
    def marcar_concluida(self, request, *args, **kwargs):
        tarefa = get_object_or_404(Tarefa, pk=kwargs['pk'])
        
        if not tarefa.concluida:
            tarefa.concluida = True
            tarefa.data_conclusao = timezone.now()
        else:
            tarefa.concluida = False
            tarefa.data_conclusao = None
        
        tarefa.save()
        return redirect('polls:tarefa_list')

# ========== VIEWS DA API REST ==========

class TarefaListCreateAPIView(generics.ListCreateAPIView):
    """
    API Endpoints:
    GET /api/tarefas/ - Lista todas as tarefas
    POST /api/tarefas/ - Cria uma nova tarefa
    """
    queryset = Tarefa.objects.all().order_by('-data_criacao')
    serializer_class = TarefaSerializer
    
    def perform_create(self, serializer):
        """Define a data de criação automaticamente"""
        serializer.save(data_criacao=timezone.now())


class TarefaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API Endpoints:
    GET /api/tarefas/{id}/ - Detalhes de uma tarefa
    PUT /api/tarefas/{id}/ - Atualiza uma tarefa
    DELETE /api/tarefas/{id}/ - Deleta uma tarefa
    """
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
    
    def perform_update(self, serializer):
        """Atualiza data_conclusao quando marcar/desmarcar como concluída"""
        tarefa = self.get_object()
        
        if serializer.validated_data.get('concluida') and not tarefa.concluida:
            serializer.save(data_conclusao=timezone.now())
        elif not serializer.validated_data.get('concluida'):
            serializer.save(data_conclusao=None)
        else:
            serializer.save()


# Views alternativas baseadas em função (comentadas)
"""
@api_view(['GET', 'POST'])
def tarefa_list_api(request):
    if request.method == 'GET':
        tarefas = Tarefa.objects.all().order_by('-data_criacao')
        serializer = TarefaSerializer(tarefas, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = TarefaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(data_criacao=timezone.now())
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def tarefa_detail_api(request, pk):
    try:
        tarefa = Tarefa.objects.get(pk=pk)
    except Tarefa.DoesNotExist:
        return Response({'error': 'Tarefa não encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = TarefaSerializer(tarefa)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = TarefaSerializer(tarefa, data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('concluida') and not tarefa.concluida:
                serializer.save(data_conclusao=timezone.now())
            elif not serializer.validated_data.get('concluida'):
                serializer.save(data_conclusao=None)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        tarefa.delete()
        return Response({'message': 'Tarefa deletada com sucesso'}, status=status.HTTP_204_NO_CONTENT)
"""