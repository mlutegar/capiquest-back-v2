from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from decimal import Decimal

from .models import (
    Choice, Question, Tarefa, Crianca, Sessao,
    Capitulo, Caminho, Desafio, Acao
)
from .serializers import (
    TarefaSerializer, CriancaSerializer, SessaoSerializer,
    CapituloSerializer, CaminhoSerializer, DesafioSerializer,
    AcaoSerializer, RegistrarAcaoSerializer
)


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


# ========== VIEWS PARA TAREFAS ==========

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


# ========== VIEWS DA API REST PARA TAREFAS ==========

class TarefaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tarefa.objects.all().order_by('-data_criacao')
    serializer_class = TarefaSerializer
    
    def perform_create(self, serializer):
        serializer.save(data_criacao=timezone.now())


class TarefaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tarefa.objects.all()
    serializer_class = TarefaSerializer
    
    def perform_update(self, serializer):
        tarefa = self.get_object()
        
        if serializer.validated_data.get('concluida') and not tarefa.concluida:
            serializer.save(data_conclusao=timezone.now())
        elif not serializer.validated_data.get('concluida'):
            serializer.save(data_conclusao=None)
        else:
            serializer.save()


# ========== VIEWS PARA CRIANÇAS ==========

class CriancaListView(generics.ListCreateAPIView):
    queryset = Crianca.objects.all()
    serializer_class = CriancaSerializer


class CriancaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Crianca.objects.all()
    serializer_class = CriancaSerializer


# ========== VIEWS PARA SESSÕES ==========

class IniciarSessaoView(generics.CreateAPIView):
    """POST /api/sessoes/iniciar/ - Cria uma nova sessão para uma criança"""
    serializer_class = SessaoSerializer
    
    def create(self, request, *args, **kwargs):
        crianca_id = request.data.get('crianca_id')
        
        if not crianca_id:
            return Response(
                {'erro': 'crianca_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            crianca = Crianca.objects.get(pk=crianca_id)
        except Crianca.DoesNotExist:
            return Response(
                {'erro': 'Criança não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        sessao = Sessao.objects.create(
            crianca=crianca,
            instituicao=crianca.instituicao
        )
        
        # Registrar ação de início de sessão
        Acao.objects.create(
            crianca=crianca,
            sessao=sessao,
            fase=crianca.fase_atual,
            tipo='next',
            sigla='INI',
            resposta='Sessão iniciada'
        )
        
        serializer = self.get_serializer(sessao)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FinalizarSessaoView(generics.UpdateAPIView):
    """POST /api/sessoes/{id}/finalizar/ - Finaliza uma sessão"""
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer
    
    def update(self, request, *args, **kwargs):
        sessao = self.get_object()
        sessao.finalizar()
        
        # Registrar ação de finalização
        Acao.objects.create(
            crianca=sessao.crianca,
            sessao=sessao,
            fase=sessao.crianca.fase_atual,
            tipo='submit',
            sigla='FIM',
            resposta='Sessão finalizada'
        )
        
        serializer = self.get_serializer(sessao)
        return Response(serializer.data)


class SessaoListView(generics.ListAPIView):
    """GET /api/sessoes/?crianca=1 - Lista sessões"""
    serializer_class = SessaoSerializer
    
    def get_queryset(self):
        queryset = Sessao.objects.all()
        crianca_id = self.request.query_params.get('crianca')
        
        if crianca_id:
            queryset = queryset.filter(crianca_id=crianca_id)
        
        return queryset.order_by('-data_inicio')


class SessaoDetailView(generics.RetrieveAPIView):
    """GET /api/sessoes/{id}/ - Detalhes de uma sessão"""
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer


# ========== VIEWS PARA AÇÕES ==========

class RegistrarAcaoView(generics.CreateAPIView):
    """
    POST /api/acoes/registrar/
    Registra uma nova ação do usuário
    
    Exemplo de corpo:
    {
        "crianca_id": 1,
        "sessao_id": 1,
        "fase": "capitulo_1",
        "desafio_id": 1,
        "tipo": "submit",
        "resposta": "resposta_do_usuario",
        "tempo_resposta": 3.5
    }
    
    Campos:
    - crianca_id: ID da criança (obrigatório)
    - sessao_id: ID da sessão (opcional)
    - fase: pre_fase, capitulo_1, etc (obrigatório)
    - desafio_id: ID do desafio (opcional)
    - tipo: click, drag, type, select, submit, next, back, hint, skip (obrigatório)
    - resposta: resposta dada pelo usuário (opcional)
    - tempo_resposta: tempo em segundos entre apresentação e resposta (opcional)
    """
    serializer_class = RegistrarAcaoSerializer


class ListarAcoesView(generics.ListAPIView):
    """GET /api/acoes/?crianca=1&sessao=1&fase=pre_fase - Lista ações com filtros"""
    serializer_class = AcaoSerializer
    
    def get_queryset(self):
        queryset = Acao.objects.all()
        
        crianca_id = self.request.query_params.get('crianca')
        sessao_id = self.request.query_params.get('sessao')
        fase = self.request.query_params.get('fase')
        tipo = self.request.query_params.get('tipo')
        
        if crianca_id:
            queryset = queryset.filter(crianca_id=crianca_id)
        if sessao_id:
            queryset = queryset.filter(sessao_id=sessao_id)
        if fase:
            queryset = queryset.filter(fase=fase)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        return queryset.order_by('-created_at')


class AcaoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/DELETE /api/acoes/{id}/ - Gerencia uma ação específica"""
    queryset = Acao.objects.all()
    serializer_class = AcaoSerializer


# ========== VIEWS PARA CAPITULOS, CAMINHOS E DESAFIOS ==========

class CapituloListView(generics.ListCreateAPIView):
    queryset = Capitulo.objects.all()
    serializer_class = CapituloSerializer


class CapituloDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Capitulo.objects.all()
    serializer_class = CapituloSerializer


class CapituloCaminhosView(generics.ListAPIView):
    serializer_class = CaminhoSerializer
    
    def get_queryset(self):
        capitulo_id = self.kwargs['capitulo_id']
        return Caminho.objects.filter(capitulo_id=capitulo_id).order_by('ordem')


class CaminhoDesafiosView(generics.ListAPIView):
    serializer_class = DesafioSerializer
    
    def get_queryset(self):
        caminho_id = self.kwargs['caminho_id']
        return Desafio.objects.filter(caminho_id=caminho_id).order_by('ordem')


# ========== VIEWS DE PROGRESSÃO ==========

class ProgressaoView(generics.GenericAPIView):
    """
    GET /api/progressao/{crianca_id}/
    Retorna qual fase/capítulo o aluno deve jogar a seguir
    """
    def get(self, request, crianca_id):
        try:
            crianca = Crianca.objects.get(pk=crianca_id)
        except Crianca.DoesNotExist:
            return Response(
                {'erro': 'Criança não encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Conta ações de submit na pré-fase
        acoes_pre_fase = Acao.objects.filter(
            crianca=crianca,
            fase='pre_fase',
            tipo='submit'
        ).count()
        
        # Se completou 5 ações na pré-fase, avança
        if crianca.fase_atual == 'pre_fase' and acoes_pre_fase >= 5:
            crianca.fase_atual = 'capitulo_1'
            crianca.save()
            
            # Registrar avanço de fase
            Acao.objects.create(
                crianca=crianca,
                fase='capitulo_1',
                tipo='next',
                sigla='AVN',
                resposta='Avançou para o Capítulo 1'
            )
        
        if crianca.fase_atual == 'pre_fase':
            return Response({
                'fase_atual': 'pre_fase',
                'pode_prosseguir': False,
                'mensagem': f'Complete {5 - acoes_pre_fase} ações para avançar',
                'progresso': {
                    'acoes_realizadas': acoes_pre_fase,
                    'total_necessario': 5,
                    'percentual': int((acoes_pre_fase / 5) * 100)
                }
            })
        
        # Lógica para capítulos
        capitulos = Capitulo.objects.all().order_by('ordem')
        
        for capitulo in capitulos:
            # Conta ações de submit neste capítulo
            acoes_capitulo = Acao.objects.filter(
                crianca=crianca,
                fase=f'capitulo_{capitulo.ordem}',
                tipo='submit'
            ).count()
            
            total_desafios_capitulo = Desafio.objects.filter(
                caminho__capitulo=capitulo
            ).count()
            
            if acoes_capitulo < total_desafios_capitulo:
                return Response({
                    'fase_atual': f'capitulo_{capitulo.ordem}',
                    'pode_prosseguir': True,
                    'mensagem': f'Você está no {capitulo.titulo}',
                    'capitulo': {
                        'id': capitulo.id,
                        'titulo': capitulo.titulo,
                        'descricao': capitulo.descricao,
                        'ordem': capitulo.ordem
                    },
                    'progresso': {
                        'acoes_realizadas': acoes_capitulo,
                        'total_desafios': total_desafios_capitulo,
                        'percentual': int((acoes_capitulo / total_desafios_capitulo) * 100) if total_desafios_capitulo > 0 else 0
                    }
                })
        
        return Response({
            'fase_atual': 'concluido',
            'pode_prosseguir': False,
            'mensagem': 'Parabéns! Você completou todos os capítulos!',
            'progresso': {
                'capitulos_concluidos': len(capitulos),
                'total_capitulos': len(capitulos)
            }
        })