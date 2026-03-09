from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.utils import timezone
from .models import Choice, Question, Tarefa, Crianca, Sessao

# ===== IMPORTS DA API =====
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    TarefaSerializer, CriancaSerializer, SessaoSerializer, 
    IniciarSessaoSerializer, CapituloSerializer, CaminhoSerializer,
    DesafioSerializer, InteracaoSerializer, SalvarRespostaSerializer
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


# ===== VIEWS PARA CRIANÇAS E SESSÕES =====

class IniciarSessaoView(generics.CreateAPIView):
    """
    POST /api/sessoes/iniciar/
    Recebe instituicao, nome e idade, retorna sessão criada
    """
    serializer_class = IniciarSessaoSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        sessao = serializer.save()
        
        response_serializer = SessaoSerializer(sessao)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CriancaListView(generics.ListCreateAPIView):
    """
    GET /api/criancas/ - Lista todas as crianças
    POST /api/criancas/ - Cria uma nova criança
    """
    queryset = Crianca.objects.all()
    serializer_class = CriancaSerializer


class CriancaDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/criancas/{id}/ - Detalhes de uma criança
    PUT /api/criancas/{id}/ - Atualiza uma criança
    DELETE /api/criancas/{id}/ - Deleta uma criança
    """
    queryset = Crianca.objects.all()
    serializer_class = CriancaSerializer


class SessaoListView(generics.ListAPIView):
    """
    GET /api/sessoes/ - Lista todas as sessões
    """
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer


class SessaoDetailView(generics.RetrieveAPIView):
    """
    GET /api/sessoes/{id}/ - Detalhes de uma sessão
    """
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer


class FinalizarSessaoView(generics.UpdateAPIView):
    """
    POST /api/sessoes/{id}/finalizar/
    Finaliza uma sessão
    """
    queryset = Sessao.objects.all()
    serializer_class = SessaoSerializer
    
    def update(self, request, *args, **kwargs):
        sessao = self.get_object()
        sessao.finalizar()
        serializer = self.get_serializer(sessao)
        return Response(serializer.data)


# ===== NOVAS VIEWS PARA CAPITULOS, CAMINHOS E DESAFIOS =====

from .models import Capitulo, Caminho, Desafio, Interacao

class CapituloListView(generics.ListCreateAPIView):
    """
    GET /api/capitulos/ - Lista todos os capítulos
    POST /api/capitulos/ - Cria um novo capítulo
    """
    queryset = Capitulo.objects.all()
    serializer_class = CapituloSerializer


class CapituloDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/capitulos/{id}/ - Detalhes de um capítulo
    PUT /api/capitulos/{id}/ - Atualiza um capítulo
    DELETE /api/capitulos/{id}/ - Deleta um capítulo
    """
    queryset = Capitulo.objects.all()
    serializer_class = CapituloSerializer


class CapituloCaminhosView(generics.ListAPIView):
    """
    GET /api/capitulos/{capitulo_id}/caminhos/ - Lista caminhos de um capítulo
    """
    serializer_class = CaminhoSerializer
    
    def get_queryset(self):
        capitulo_id = self.kwargs['capitulo_id']
        return Caminho.objects.filter(capitulo_id=capitulo_id).order_by('ordem')


class CaminhoDesafiosView(generics.ListAPIView):
    """
    GET /api/caminhos/{caminho_id}/desafios/ - Lista desafios de um caminho
    """
    serializer_class = DesafioSerializer
    
    def get_queryset(self):
        caminho_id = self.kwargs['caminho_id']
        return Desafio.objects.filter(caminho_id=caminho_id).order_by('ordem')


class SalvarRespostaView(generics.CreateAPIView):
    """
    POST /api/interacoes/salvaresposta/ - Salva resposta de um aluno a um desafio
    """
    serializer_class = SalvarRespostaSerializer


# ===== VIEWS DE RESULTADO E RANKING =====

class ResultadoCapituloView(generics.GenericAPIView):
    """
    GET /api/capitulos/{capitulo_id}/resultado/{aluno_id}/
    Retorna dados consolidados do desempenho do aluno no capítulo
    """
    def get(self, request, capitulo_id, aluno_id):
        from django.db.models import Sum, Count, Q, Avg
        
        # Verifica se o aluno existe
        try:
            aluno = Crianca.objects.get(pk=aluno_id)
        except Crianca.DoesNotExist:
            return Response(
                {'erro': 'Aluno não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verifica se o capítulo existe
        try:
            capitulo = Capitulo.objects.get(pk=capitulo_id)
        except Capitulo.DoesNotExist:
            return Response(
                {'erro': 'Capítulo não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Busca todos os caminhos do capítulo
        caminhos = Caminho.objects.filter(capitulo=capitulo).order_by('ordem')
        
        # Total de desafios no capítulo
        total_desafios = Desafio.objects.filter(
            caminho__capitulo=capitulo
        ).count()
        
        # Interações do aluno neste capítulo
        interacoes = Interacao.objects.filter(
            aluno=aluno,
            desafio__caminho__capitulo=capitulo
        ).select_related('desafio', 'desafio__caminho').order_by('desafio__ordem')
        
        # Estatísticas gerais
        desafios_feitos = interacoes.count()
        acertos = interacoes.filter(acertou=True).count()
        erros = desafios_feitos - acertos
        total_pontos = interacoes.aggregate(Sum('pontos'))['pontos__sum'] or 0
        media_pontos = interacoes.aggregate(Avg('pontos'))['pontos__avg'] or 0
        
        # Progresso percentual
        progresso = int((desafios_feitos / total_desafios * 100) if total_desafios > 0 else 0)
        
        # Taxa de acertos
        taxa_acertos = int((acertos / desafios_feitos * 100) if desafios_feitos > 0 else 0)
        
        # Dados consolidados por caminho
        caminhos_data = []
        total_pontos_possiveis = 0
        pontos_por_dificuldade = {'fácil': 0, 'médio': 0, 'difícil': 0}
        acertos_por_dificuldade = {'fácil': 0, 'médio': 0, 'difícil': 0}
        total_por_dificuldade = {'fácil': 0, 'médio': 0, 'difícil': 0}
        
        for caminho in caminhos:
            # Desafios deste caminho
            desafios_caminho = Desafio.objects.filter(caminho=caminho).count()
            
            # Interações neste caminho
            caminho_interacoes = interacoes.filter(desafio__caminho=caminho)
            caminho_feitos = caminho_interacoes.count()
            caminho_acertos = caminho_interacoes.filter(acertou=True).count()
            caminho_pontos = caminho_interacoes.aggregate(Sum('pontos'))['pontos__sum'] or 0
            
            # Pontuação máxima possível neste caminho
            pontos_por_acerto = {
                'fácil': 10,
                'médio': 20,
                'difícil': 30
            }.get(caminho.dificuldade.lower(), 10)
            
            pontos_maximos = desafios_caminho * pontos_por_acerto
            
            # Atualiza totais por dificuldade
            dificuldade_key = caminho.dificuldade.lower()
            if dificuldade_key in ['fácil', 'facil']:
                dif_key = 'fácil'
            elif dificuldade_key in ['médio', 'medio']:
                dif_key = 'médio'
            else:
                dif_key = 'difícil'
            
            total_por_dificuldade[dif_key] += desafios_caminho
            acertos_por_dificuldade[dif_key] += caminho_acertos
            pontos_por_dificuldade[dif_key] += caminho_pontos
            total_pontos_possiveis += pontos_maximos
            
            # Detalhes dos desafios deste caminho
            desafios_data = []
            for desafio in Desafio.objects.filter(caminho=caminho).order_by('ordem'):
                interacao = caminho_interacoes.filter(desafio=desafio).first()
                desafios_data.append({
                    'id': desafio.id,
                    'ordem': desafio.ordem,
                    'tipo_pista': desafio.tipo_pista,
                    'respondido': interacao is not None,
                    'acertou': interacao.acertou if interacao else None,
                    'pontos_obtidos': interacao.pontos if interacao else 0,
                    'resposta_dada': interacao.resposta_dada if interacao else None
                })
            
            caminhos_data.append({
                'id': caminho.id,
                'nome': caminho.nome,
                'cor': caminho.cor,
                'dificuldade': caminho.dificuldade,
                'total_desafios': desafios_caminho,
                'desafios_completados': caminho_feitos,
                'acertos': caminho_acertos,
                'erros': caminho_feitos - caminho_acertos,
                'pontos_obtidos': caminho_pontos,
                'pontos_maximos': pontos_maximos,
                'progresso': int((caminho_feitos / desafios_caminho * 100) if desafios_caminho > 0 else 0),
                'taxa_acertos': int((caminho_acertos / caminho_feitos * 100) if caminho_feitos > 0 else 0),
                'desafios': desafios_data
            })
        
        # Calcula aproveitamento por dificuldade
        aproveitamento_dificuldade = {}
        for dificuldade in ['fácil', 'médio', 'difícil']:
            if total_por_dificuldade[dificuldade] > 0:
                aproveitamento_dificuldade[dificuldade] = {
                    'total': total_por_dificuldade[dificuldade],
                    'acertos': acertos_por_dificuldade[dificuldade],
                    'pontos': pontos_por_dificuldade[dificuldade],
                    'taxa_acertos': int((acertos_por_dificuldade[dificuldade] / total_por_dificuldade[dificuldade] * 100))
                }
            else:
                aproveitamento_dificuldade[dificuldade] = None
        
        # Busca últimas atividades
        ultimas_atividades = []
        for interacao in interacoes.order_by('-created_at')[:5]:
            ultimas_atividades.append({
                'desafio_id': interacao.desafio.id,
                'caminho': interacao.desafio.caminho.nome,
                'ordem': interacao.desafio.ordem,
                'acertou': interacao.acertou,
                'pontos': interacao.pontos,
                'data': interacao.created_at
            })
        
        # Ranking simples (top 5 alunos deste capítulo)
        ranking = []
        top_alunos = Interacao.objects.filter(
            desafio__caminho__capitulo=capitulo
        ).values(
            'aluno_id', 'aluno__nome'
        ).annotate(
            total_pontos=Sum('pontos'),
            total_acertos=Count('id', filter=Q(acertou=True)),
            total_interacoes=Count('id')
        ).order_by('-total_pontos')[:5]
        
        for pos, item in enumerate(top_alunos, 1):
            ranking.append({
                'posicao': pos,
                'aluno_id': item['aluno_id'],
                'aluno_nome': item['aluno__nome'],
                'pontos': item['total_pontos'],
                'acertos': item['total_acertos'],
                'interacoes': item['total_interacoes']
            })
        
        # Verifica se o aluno está no ranking
        posicao_aluno = None
        for item in ranking:
            if item['aluno_id'] == aluno.id:
                posicao_aluno = item['posicao']
                break
        
        # Se não estiver no top 5, busca posição exata
        if posicao_aluno is None:
            alunos_acima = Interacao.objects.filter(
                desafio__caminho__capitulo=capitulo
            ).values('aluno_id').annotate(
                total_pontos=Sum('pontos')
            ).filter(total_pontos__gt=total_pontos).count()
            posicao_aluno = alunos_acima + 1
        
        # Retorno consolidado
        return Response({
            'aluno': {
                'id': aluno.id,
                'nome': aluno.nome,
                'instituicao': aluno.instituicao
            },
            'capitulo': {
                'id': capitulo.id,
                'titulo': capitulo.titulo,
                'descricao': capitulo.descricao,
                'total_caminhos': caminhos.count(),
                'total_desafios': total_desafios
            },
            'resumo': {
                'desafios_completados': desafios_feitos,
                'progresso_percentual': progresso,
                'acertos': acertos,
                'erros': erros,
                'total_pontos': total_pontos,
                'pontos_possiveis': total_pontos_possiveis,
                'aproveitamento_percentual': int((total_pontos / total_pontos_possiveis * 100) if total_pontos_possiveis > 0 else 0),
                'taxa_acertos_percentual': taxa_acertos,
                'media_pontos_por_desafio': round(media_pontos, 1),
                'posicao_ranking': posicao_aluno
            },
            'aproveitamento_por_dificuldade': aproveitamento_dificuldade,
            'caminhos': caminhos_data,
            'ultimas_atividades': ultimas_atividades,
            'ranking_top5': ranking,
            'data_consulta': timezone.now()
        })


class RankingCapituloView(generics.GenericAPIView):
    """
    GET /api/capitulos/{capitulo_id}/ranking/
    Retorna o ranking completo dos alunos no capítulo
    """
    def get(self, request, capitulo_id):
        from django.db.models import Sum, Count, Q
        
        # Verifica se o capítulo existe
        try:
            capitulo = Capitulo.objects.get(pk=capitulo_id)
        except Capitulo.DoesNotExist:
            return Response(
                {'erro': 'Capítulo não encontrado'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Busca todos os alunos com interações neste capítulo
        ranking = Interacao.objects.filter(
            desafio__caminho__capitulo=capitulo
        ).values(
            'aluno_id', 'aluno__nome', 'aluno__instituicao'
        ).annotate(
            total_pontos=Sum('pontos'),
            total_acertos=Count('id', filter=Q(acertou=True)),
            total_interacoes=Count('id'),
            media_pontos=Sum('pontos') * 1.0 / Count('id')
        ).order_by('-total_pontos')
        
        # Formata o ranking com posições
        ranking_data = []
        for pos, item in enumerate(ranking, 1):
            ranking_data.append({
                'posicao': pos,
                'aluno_id': item['aluno_id'],
                'aluno_nome': item['aluno__nome'],
                'instituicao': item['aluno__instituicao'],
                'pontos': item['total_pontos'],
                'acertos': item['total_acertos'],
                'interacoes': item['total_interacoes'],
                'aproveitamento': int((item['total_acertos'] / item['total_interacoes'] * 100) if item['total_interacoes'] > 0 else 0),
                'media_pontos': round(item['media_pontos'], 1)
            })
        
        return Response({
            'capitulo_id': capitulo.id,
            'capitulo_titulo': capitulo.titulo,
            'total_alunos': len(ranking_data),
            'ranking': ranking_data
        })