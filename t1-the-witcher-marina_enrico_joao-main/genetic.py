import random
import json

# Definindo os eventos e suas dificuldades
eventos = [
    {"evento": "Wyzim", "dificuldade": 55},
    {"evento": "Stygga", "dificuldade": 60},
    {"evento": "Djinn", "dificuldade": 65},
    {"evento": "Dragão Dourado", "dificuldade": 70},
    {"evento": "Quimera", "dificuldade": 75},
    {"evento": "Montanhas Amell", "dificuldade": 80},
    {"evento": "Velen", "dificuldade": 85},
    {"evento": "Novigrad", "dificuldade": 90},
    {"evento": "Toussaint", "dificuldade": 95},
    {"evento": "Skellige Kraken", "dificuldade": 120},
    {"evento": "Primeira Aparição Caçada", "dificuldade": 125},
    {"evento": "Perseguição Ciri", "dificuldade": 130},
    {"evento": "Kaer Morhen", "dificuldade": 135},
    {"evento": "Skellige Templo", "dificuldade": 150},
    {"evento": "Caranthir Mar de Gelo", "dificuldade": 155},
    {"evento": "Eredin", "dificuldade": 160}
]

# Definindo os personagens e seus fatores de poder
personagens = [
    {"nome": "Ciri", "poder": 1.8},
    {"nome": "Geralt", "poder": 1.6},
    {"nome": "Yennifer", "poder": 1.4},
    {"nome": "Vesemir", "poder": 1.3},
    {"nome": "Triss", "poder": 1.2},
    {"nome": "Dandelion", "poder": 1.0}
]

# Cada personagem tem 5 pontos de energia
energia_inicial = 5

# Função para calcular o tempo gasto em um evento
def calcular_tempo_evento(evento, personagens_escolhidos):
    soma_poder = sum([p['poder'] for p in personagens_escolhidos])
    if soma_poder == 0:  # Evita divisão por zero
        return float('inf')
    return evento["dificuldade"] / soma_poder

# Função para calcular o fitness (tempo total gasto)
def calcular_fitness(solucao, energia_personagens):
    tempo_total = 0
    energia = energia_personagens.copy()
    
    for i, evento in enumerate(eventos):
        personagens_escolhidos = [personagens[j] for j in solucao[i]]
        
        # Verifica se os personagens têm energia suficiente
        for p in personagens_escolhidos:
            if energia[p['nome']] <= 0:
                return float('inf')  # Penalidade se não há energia
        
        # Calcula o tempo do evento
        tempo_evento = calcular_tempo_evento(evento, personagens_escolhidos)
        tempo_total += tempo_evento
        
        # Subtrai energia dos personagens usados
        for p in personagens_escolhidos:
            energia[p['nome']] -= 1
    
    return tempo_total

# Função para criar uma solução aleatória (combinação de personagens para cada evento)
def criar_solucao_aleatoria():
    solucao = []
    for _ in eventos:  # Para cada evento
        num_personagens = random.randint(1, 3)  # Escolhe entre 1 e 3 personagens por evento
        personagens_escolhidos = random.sample(range(len(personagens)), num_personagens)
        solucao.append(personagens_escolhidos)  # Adiciona os personagens escolhidos para o evento
    return solucao

def crossover(pai1, pai2):
    ponto_corte = random.randint(1, len(eventos) - 1)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2

# Função de mutação com estratégias combinadas 
def mutacao(solucao, energia_personagens):
    # Escolhe um evento aleatório
    evento_index = random.randint(0, len(eventos) - 1)
    
    # Obtém a soma de poder dos personagens atuais
    poder_atual = sum([personagens[j]['poder'] for j in solucao[evento_index]])
    
    # Mutação direcionada pela aptidão (se o poder atual for baixo, força uma mutação)
    if poder_atual < 2.5:
        personagens_escolhidos = random.sample(range(len(personagens)), random.randint(2, 3))
    else:
        personagens_escolhidos = random.sample(range(len(personagens)), random.randint(1, 3))
    solucao[evento_index] = personagens_escolhidos
    
    # Troca de personagens entre eventos
    evento2_index = random.randint(0, len(eventos) - 1)
    solucao[evento_index], solucao[evento2_index] = solucao[evento2_index], solucao[evento_index]

    # Mutação baseada em energia (se um personagem tiver pouca energia, substitua)
    for j, personagem_index in enumerate(solucao[evento_index]):
        if energia_personagens[personagens[personagem_index]['nome']] <= 1:
            solucao[evento_index][j] = random.choice(range(len(personagens)))

# Algoritmo genético com mutação adaptativa
def algoritmo_genetico(tamanho_populacao, geracoes, taxa_mutacao):
    populacao = [criar_solucao_aleatoria() for _ in range(tamanho_populacao)]
    energia_inicial_personagens = {p['nome']: energia_inicial for p in personagens}
    energia_inicial_personagens["Dandelion"] -= 1
    print("Energia inicial:", energia_inicial_personagens)
    
    melhor_geracao_fitness = None
    sem_melhoria_contador = 0
    
    for geracao in range(geracoes):
        print("Geração:", geracao)
        fitness_populacao = [(solucao, calcular_fitness(solucao, energia_inicial_personagens)) for solucao in populacao]
        fitness_populacao.sort(key=lambda x: x[1])
        
        melhor_fitness_atual = fitness_populacao[0][1]
        if melhor_geracao_fitness is None or melhor_fitness_atual < melhor_geracao_fitness:
            melhor_geracao_fitness = melhor_fitness_atual
            sem_melhoria_contador = 0
        else:
            sem_melhoria_contador += 1
        
        # Se não houver melhoria por várias gerações, aumenta temporariamente a taxa de mutação
        if sem_melhoria_contador > 100:
            taxa_mutacao_atual = min(taxa_mutacao * 2, 0.5)
        else:
            taxa_mutacao_atual = taxa_mutacao
        
        populacao = [x[0] for x in fitness_populacao[:tamanho_populacao // 2]]
        
        nova_populacao = []
        while len(nova_populacao) < tamanho_populacao:
            pai1, pai2 = random.sample(populacao, 2)
            filho1, filho2 = crossover(pai1, pai2)
            nova_populacao.extend([filho1, filho2])
        
        for solucao in nova_populacao:
            if random.random() < taxa_mutacao_atual:
                mutacao(solucao, energia_inicial_personagens)
        
        populacao = nova_populacao
    
    melhor_solucao = fitness_populacao[0][0]
    melhor_fitness = fitness_populacao[0][1]
    return melhor_solucao, melhor_fitness

# Parâmetros do algoritmo genético
tamanho_populacao = 1500
geracoes = 1000
taxa_mutacao = 0.01


melhor_solucao, melhor_fitness = algoritmo_genetico(tamanho_populacao, geracoes, taxa_mutacao)
melhor_solucao_formatada = []

with open('data/melhor_solucao.json', 'r') as arquivo:
    dados = json.load(arquivo)

print("Melhor solução encontrada (personagens escolhidos para cada evento):")
for i, solucao_evento in enumerate(melhor_solucao):
    personagens_evento = [personagens[j]['nome'] for j in solucao_evento]
    melhor_solucao_formatada.append(f"Evento {eventos[i]['evento']}: Personagens escolhidos: {personagens_evento}")
    print(f"Evento {eventos[i]['evento']}: Personagens escolhidos: {personagens_evento}")

if dados['tempo'] > melhor_fitness:
    with open('data/melhor_solucao.json', 'w') as arquivo:
        json.dump({'solucao': melhor_solucao_formatada, 'tempo': melhor_fitness}, arquivo, indent=2)

print(f"Tempo total mínimo: {melhor_fitness} minutos")
