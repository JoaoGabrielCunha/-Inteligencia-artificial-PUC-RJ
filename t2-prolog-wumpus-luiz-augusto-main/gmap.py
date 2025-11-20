################################################
import pygame
import time
from pyswip import Prolog, Functor, Variable, Query
from queue import PriorityQueue

from threading import Thread
import pathlib
current_path = str(pathlib.Path().resolve())

auto_play_tempo = 0.05
auto_play = True # desligar para controlar manualmente
show_map = False

scale = 60
size_x = 12
size_y = 12
width = size_x * scale  #Largura Janela
height = size_y * scale #Altura Janela

player_pos = (1,1,'norte')
energia = 0
pontuacao = 0

mapa=[['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','',''],
      ['','','','','','','','','','','','']]

visitados = []
certezas = []

prolog = Prolog()
prolog.consult('./main.pl')

last_action = ""


def estado_mapa():
    mapa = [['' for i in range(12)] for _ in range(12)]
    nao_visitados = []
    nao_visitados_sem_inimigos = []
    nao_visitado = False

    x = Variable()
    y = Variable()
    z = Variable()

    memory = Functor("memory", 3)
    memory_query = Query(memory(x,y,z))

    while memory_query.nextSolution():
        node = (x.get_value(),y.get_value())
        nao_visitado = False
        if node not in visitados and node != (player_pos[0],player_pos[1]):
            nao_visitados.append((node[0]-1,node[1]-1))
            nao_visitado = True
        for s in z.value:
            if str(s) == 'brisa':
                mapa[y.get_value()-1][x.get_value()-1] += 'P'
            elif str(s) == 'palmas':
                mapa[y.get_value()-1][x.get_value()-1] += 'T'
            elif str(s) == 'passos':
                mapa[y.get_value()-1][x.get_value()-1] += 'D'
            elif str(s) == 'reflexo':
                mapa[y.get_value()-1][x.get_value()-1] += 'U'
                if nao_visitado:
                    nao_visitados_sem_inimigos.append((node[0]-1,node[1]-1))
            elif str(s) == 'brilho':
                mapa[y.get_value()-1][x.get_value()-1] += 'O'
                if nao_visitado:
                    nao_visitados_sem_inimigos.append((node[0]-1,node[1]-1))
        if not z.value and nao_visitado:
            nao_visitados_sem_inimigos.append((node[0]-1,node[1]-1))
    memory_query.closeQuery()

    return mapa, nao_visitados, nao_visitados_sem_inimigos


# Retorna o valor de um caractere de acordo com a certeza e a energia do jogador
def get_value(c, certeza):
    value = 1

    if certeza:
        if 'P' in c:
            value = 9999
        elif 'T' in c:
            value = 800
        elif 'D' in c:
            value = 900 if energia <= 80 else 400
        elif 'd' in c:
            value = 900 if energia <= 50 else 400
    else:
        if 'P' in c:
            value = 800
        elif 'T' in c:
            value = 600
        elif 'D' in c:
            value = 700 if energia <= 80 else 300
        elif 'd' in c:
            value = 700 if energia <= 50 else 300

    return value


# Retorna o caractere de uma coordenada no mapa
def get_chars_from_map(mapa, coord):
    return mapa[coord[1]][coord[0]]


# Retorna o valor de uma coordenada no mapa
def get_value_from_map(mapa, coord, direcao=None):
    chars = get_chars_from_map(mapa, coord)
    value = get_value(chars, (coord[0]+1,coord[1]+1) in certezas)
    multiplier = 1
    if 'D' in chars:
        multiplier = 4
    elif 'd' in chars:
        multiplier = 2

    if direcao is not None:
        if multiplier > 1:
            # Calcular a posição do próximo vizinho na direção do movimento
            if direcao == 0:  # norte
                vizinho = (coord[0], coord[1] + 1)
            elif direcao == 1:  # leste
                vizinho = (coord[0] + 1, coord[1])
            elif direcao == 2:  # sul
                vizinho = (coord[0], coord[1] - 1)
            elif direcao == 3:  # oeste
                vizinho = (coord[0] - 1, coord[1])

            # Verifica se o vizinho está dentro dos limites do mapa
            if vizinho[0] < 0 or vizinho[0] >= size_x or vizinho[1] < 0 or vizinho[1] >= size_y:
                return value * multiplier

            # Verifica se o vizinho possui inimigos
            vizinho_char = get_chars_from_map(mapa, vizinho)
            if 'D' in vizinho_char or 'd' in vizinho_char or 'P' in vizinho_char or 'T' in vizinho_char:
                value *= multiplier

    return value


# Adiciona uma posição válida à lista de vizinhos
def add_valid_pos(nb, mapa, coord):
    if get_value_from_map(mapa, coord) > -1:
        nb.append(coord)


# Retorna a lista de vizinhos de uma coordenada
def get_neighborhood(mapa, coord):
    nb = []

    # Confere as bordas esquerda e direita
    if coord[0] == 0:  # Esquerda
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
    elif coord[0] == size_x - 1:  # Direita
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))
    else:    
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))

    # Confere as bordas superior e inferior
    if coord[1] == 0:  # Superior
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
    elif coord[1] == size_y - 1:  # Inferior
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))
    else:
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))

    return nb


# Calcula a distância de Manhattan entre duas coordenadas
def manhattan_distance(_from, to):
    # |x2 - x1| + |y2 - y1|
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])


# Determina a direção do movimento entre duas coordenadas
def calcula_direcao(atual, vizinho):
    if atual[1] < vizinho[1]:
        return 0 # norte
    elif atual[0] < vizinho[0]:
        return 1 # leste
    elif atual[1] > vizinho[1]:
        return 2 # sul
    elif atual[0] > vizinho[0]:
        return 3 # oeste


# Calcula o custo de rotação
def calcula_custo_rotacao(direcao_atual, nova_direcao, coord):
    custo_base = min(abs(direcao_atual - nova_direcao), 4 - abs(direcao_atual - nova_direcao))
    if 'D' in get_chars_from_map(mapa, coord) or 'd' in get_chars_from_map(mapa, coord):
        custo_base *= 10000
    return custo_base


# Converte uma direção para um inteiro
def direcao_to_int(direcao):
    if direcao == 'norte':
        return 0
    elif direcao == 'leste':
        return 1
    elif direcao == 'sul':
        return 2
    elif direcao == 'oeste':
        return 3


# Busca a estrela
def busca_a_estrela(end=None, powerup=False):
    mapa, nao_visitados, nao_visitados_sem_inimigos = estado_mapa()
    start = (player_pos[0]-1, player_pos[1]-1)
    tiles_com_inimigos = PriorityQueue()

    fronteira = PriorityQueue()

    fronteira.put((0, start, [], direcao_to_int(player_pos[2])))
    visitados_a_estrela = []
    visitados_a_estrela.append(start)

    while not fronteira.empty():
        node = fronteira.get()
        coord = node[1]
        custo_atual = node[0]
        visitados_a_estrela.append(coord)

        chars_coord = get_chars_from_map(mapa, coord)
        if end is not None: # Se for uma busca para um objetivo
            if coord == end: # Retorna ao encontrar o objetivo
                return node[2]
        elif powerup and 'U' in chars_coord: # Se for uma busca por powerup e encontrar um powerup
            return node[2]
        elif coord in nao_visitados_sem_inimigos: # Encontrou um tile sem inimigos e não visitado
            return node[2]
        elif (coord[0]+1, coord[1]+1) not in certezas and coord!=(0,0): # Adiciona o tile com inimigos incerto à lista de tiles com inimigos
            tiles_com_inimigos.put((node[0], node[1], node[2], node[3], chars_coord))

        # Adiciona os vizinhos à fronteira
        for vizinho in get_neighborhood(mapa, coord):
            if vizinho not in visitados_a_estrela and ((vizinho[0],vizinho[1]) in nao_visitados or (vizinho[0]+1,vizinho[1]+1) in visitados):
                nova_direcao = calcula_direcao(coord, vizinho)
                if end is not None:
                    hx = manhattan_distance(vizinho, end)
                elif vizinho in nao_visitados_sem_inimigos:
                    hx = min([manhattan_distance(vizinho, x) for x in nao_visitados_sem_inimigos])
                else:
                    hx = min([manhattan_distance(vizinho, x) for x in nao_visitados])
                gx = custo_atual + get_value_from_map(mapa, vizinho, nova_direcao) + calcula_custo_rotacao(node[3], nova_direcao, coord)
                fx = gx + hx
                fronteira.put((fx, vizinho, node[2] + [vizinho], nova_direcao))

    return tiles_com_inimigos.get()[2]



def executar_acao(acao):
    exec_prolog(acao)
    update_prolog()
    time.sleep(auto_play_tempo)


# Move o jogador pelo caminho
def mover_caminho(caminho):
        direcao = direcao_to_int(player_pos[2])

        for coord in caminho:
            if coord[0] < player_pos[0]-1: # oeste
                if direcao == 0:
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 1:
                    executar_acao("virar_esquerda")
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 2:
                    executar_acao("virar_direita")
                    executar_acao("andar")
                elif direcao == 3:
                    executar_acao("andar")
                direcao = 3
            elif coord[0] > player_pos[0]-1: # leste
                if direcao == 0:
                    executar_acao("virar_direita")
                    executar_acao("andar")
                elif direcao == 1:
                    executar_acao("andar")
                elif direcao == 2:
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 3:
                    executar_acao("virar_esquerda")
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                direcao = 1
            elif coord[1] > player_pos[1]-1: # norte
                if direcao == 0:
                    executar_acao("andar")
                elif direcao == 1:
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 2:
                    executar_acao("virar_esquerda")
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 3:
                    executar_acao("virar_direita")
                    executar_acao("andar")
                direcao = 0
            elif coord[1] < player_pos[1]-1: # sul
                if direcao == 0:
                    executar_acao("virar_esquerda")
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                elif direcao == 1:
                    executar_acao("virar_direita")
                    executar_acao("andar")
                elif direcao == 2:
                    executar_acao("andar")
                elif direcao == 3:
                    executar_acao("virar_esquerda")
                    executar_acao("andar")
                direcao = 2


def decisao():
    acao = ""

    acoes = list(prolog.query("executa_acao(X)"))
    if len(acoes) > 0:
        acao = acoes[0]['X']

    print(acao)
    return acao


class Th(Thread):

    def __init__ (self, mapa, alg):
        Thread.__init__(self)

    def run(self):

        time.sleep(1)

        while player_pos[2] != 'morto':
            acao = decisao()
            if acao == "buscar":
                caminho = busca_a_estrela()
                mover_caminho(caminho)
            elif acao == "voltar":
                caminho = busca_a_estrela(end=(0,0))
                mover_caminho(caminho)
            elif acao == "powerup":
                caminho = busca_a_estrela(powerup=True)
                mover_caminho(caminho)
            elif acao == "fim":
                break
            else:
                exec_prolog(acao)
                update_prolog()
            time.sleep(auto_play_tempo)


def exec_prolog(a):
    global last_action
    if a != "":
        list(prolog.query(a))
    last_action = a


def update_prolog():
    global player_pos, mapa, energia, pontuacao,visitados, show_map

    list(prolog.query("atualiza_obs, verifica_player"))

    x = Variable()
    y = Variable()
    visitado = Functor("visitado", 2)
    visitado_query = Query(visitado(x,y))
    visitados.clear()
    while visitado_query.nextSolution():
        visitados.append((x.value,y.value))
    visitado_query.closeQuery()
    
    x = Variable()
    y = Variable()
    certeza = Functor("certeza", 2)
    certeza_query = Query(certeza(x,y))
    certezas.clear()
    while certeza_query.nextSolution():
        certezas.append((x.value,y.value))
    certeza_query.closeQuery()
        
    if show_map:    
        x = Variable()
        y = Variable()
        z = Variable()    
        tile = Functor("tile", 3)
        tile_query = Query(tile(x,y,z))
        while tile_query.nextSolution():
            mapa[y.get_value()-1][x.get_value()-1] = str(z.value)
        tile_query.closeQuery()

    else:

        y = 0
        for j in mapa:
            x = 0
            for i in j:
                mapa[y][x] = ''
                x  += 1
            y +=  1

        x = Variable()
        y = Variable()
        z = Variable()    
        memory = Functor("memory", 3)
        memory_query = Query(memory(x,y,z))
        while memory_query.nextSolution():
            for s in z.value:
                
                if str(s) == 'brisa':
                    mapa[y.get_value()-1][x.get_value()-1] += 'P'
                elif str(s) == 'palmas':
                    mapa[y.get_value()-1][x.get_value()-1] += 'T'
                elif str(s) == 'passos':
                    mapa[y.get_value()-1][x.get_value()-1] += 'D'
                elif str(s) == 'reflexo':
                    mapa[y.get_value()-1][x.get_value()-1] += 'U'
                elif str(s) == 'brilho':
                    mapa[y.get_value()-1][x.get_value()-1] += 'O'
            
        memory_query.closeQuery()

    x = Variable()
    y = Variable()
    z = Variable()

    posicao = Functor("posicao", 3)
    position_query = Query(posicao(x,y,z))
    position_query.nextSolution()
    player_pos = (x.value,y.value,str(z.value))
    position_query.closeQuery()

    x = Variable()
    energia = Functor("energia", 1)
    energia_query = Query(energia(x))
    energia_query.nextSolution()
    energia = x.value
    energia_query.closeQuery()

    x = Variable()
    pontuacao = Functor("pontuacao", 1)
    pontuacao_query = Query(pontuacao(x))
    pontuacao_query.nextSolution()
    pontuacao = x.value
    pontuacao_query.closeQuery()

    #print(mapa)
    #print(player_pos)


def load():
    global sys_font, clock, img_wall, img_grass, img_start, img_finish, img_path
    global img_gold,img_health, img_pit, img_bat, img_enemy1, img_enemy2,img_floor
    global bw_img_gold,bw_img_health, bw_img_pit, bw_img_bat, bw_img_enemy1, bw_img_enemy2,bw_img_floor
    global img_player_up, img_player_down, img_player_left, img_player_right, img_tomb

    sys_font = pygame.font.Font(pygame.font.get_default_font(), 20)
    clock = pygame.time.Clock() 

    img_wall = pygame.image.load('wall.jpg')
    #img_wall2_size = (img_wall.get_width()/map_width, img_wall.get_height()/map_height)
    img_wall_size = (width/size_x, height/size_y)
    
    img_wall = pygame.transform.scale(img_wall, img_wall_size)

    
    img_player_up = pygame.image.load('player_up.png')
    img_player_up_size = (width/size_x, height/size_y)
    img_player_up = pygame.transform.scale(img_player_up, img_player_up_size)

    img_player_down = pygame.image.load('player_down.png')
    img_player_down_size = (width/size_x, height/size_y)
    img_player_down = pygame.transform.scale(img_player_down, img_player_down_size)

    img_player_left = pygame.image.load('player_left.png')
    img_player_left_size = (width/size_x, height/size_y)
    img_player_left = pygame.transform.scale(img_player_left, img_player_left_size)

    img_player_right = pygame.image.load('player_right.png')
    img_player_right_size = (width/size_x, height/size_y)
    img_player_right = pygame.transform.scale(img_player_right, img_player_right_size)


    img_tomb = pygame.image.load('tombstone.png')
    img_tomb_size = (width/size_x, height/size_y)
    img_tomb = pygame.transform.scale(img_tomb, img_tomb_size)


    img_grass = pygame.image.load('grass.jpg')
    img_grass_size = (width/size_x, height/size_y)
    img_grass = pygame.transform.scale(img_grass, img_grass_size)

    img_floor = pygame.image.load('floor.png')
    img_floor_size = (width/size_x, height/size_y)
    img_floor = pygame.transform.scale(img_floor, img_floor_size)

    img_gold = pygame.image.load('gold.png')
    img_gold_size = (width/size_x, height/size_y)
    img_gold = pygame.transform.scale(img_gold, img_gold_size)

    img_pit = pygame.image.load('pit.png')
    img_pit_size = (width/size_x, height/size_y)
    img_pit = pygame.transform.scale(img_pit, img_pit_size)

    img_enemy1 = pygame.image.load('enemy1.png')
    img_enemy1_size = (width/size_x, height/size_y)
    img_enemy1 = pygame.transform.scale(img_enemy1, img_enemy1_size)

    img_enemy2 = pygame.image.load('enemy2.png')
    img_enemy2_size = (width/size_x, height/size_y)
    img_enemy2 = pygame.transform.scale(img_enemy2, img_enemy2_size)

    img_bat = pygame.image.load('bat.png')
    img_bat_size = (width/size_x, height/size_y)
    img_bat = pygame.transform.scale(img_bat, img_bat_size)

    img_health = pygame.image.load('health.png')
    img_health_size = (width/size_x, height/size_y)
    img_health = pygame.transform.scale(img_health, img_health_size)    
    
    bw_img_floor = pygame.image.load('bw_floor.png')
    bw_img_floor_size = (width/size_x, height/size_y)
    bw_img_floor = pygame.transform.scale(bw_img_floor, bw_img_floor_size)

    bw_img_gold = pygame.image.load('bw_gold.png')
    bw_img_gold_size = (width/size_x, height/size_y)
    bw_img_gold = pygame.transform.scale(bw_img_gold, bw_img_gold_size)

    bw_img_pit = pygame.image.load('bw_pit.png')
    bw_img_pit_size = (width/size_x, height/size_y)
    bw_img_pit = pygame.transform.scale(bw_img_pit, bw_img_pit_size)

    bw_img_enemy1 = pygame.image.load('bw_enemy1.png')
    bw_img_enemy1_size = (width/size_x, height/size_y)
    bw_img_enemy1 = pygame.transform.scale(bw_img_enemy1, bw_img_enemy1_size)

    bw_img_enemy2 = pygame.image.load('bw_enemy2.png')
    bw_img_enemy2_size = (width/size_x, height/size_y)
    bw_img_enemy2 = pygame.transform.scale(bw_img_enemy2, bw_img_enemy2_size)

    bw_img_bat = pygame.image.load('bw_bat.png')
    bw_img_bat_size = (width/size_x, height/size_y)
    bw_img_bat = pygame.transform.scale(bw_img_bat, bw_img_bat_size)

    bw_img_health = pygame.image.load('bw_health.png')
    bw_img_health_size = (width/size_x, height/size_y)
    bw_img_health = pygame.transform.scale(bw_img_health, bw_img_health_size)  


def update(dt, screen):
    pass


def key_pressed():
    
    global show_map
    #leitura do teclado
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
    
            if event.key==pygame.K_LEFT: #tecla esquerda
                exec_prolog("virar_esquerda")
                update_prolog()

            elif event.key==pygame.K_RIGHT: #tecla direita
                exec_prolog("virar_direita")
                update_prolog()

            elif event.key==pygame.K_UP: #tecla  cima
                exec_prolog("andar")
                update_prolog()
    
            if event.key==pygame.K_m:
                show_map = not show_map
                update_prolog()

            if event.key==pygame.K_SPACE:
                exec_prolog("pegar")
                update_prolog()


def draw_screen(screen):
    screen.fill((0,0,0))
 
    y = 0
    for j in mapa:
        x = 0
        for i in j:

            if (x+1,12-y) in visitados:
                screen.blit(img_floor, (x * img_floor.get_width(), y * img_floor.get_height()))
            else:
                screen.blit(bw_img_floor, (x * bw_img_floor.get_width(), y * bw_img_floor.get_height()))

            if mapa[11-y][x].find('P') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_pit, (x * img_pit.get_width(), y * img_pit.get_height()))                            
                else:
                    screen.blit(bw_img_pit, (x * bw_img_pit.get_width(), y * bw_img_pit.get_height()))                            

            if mapa[11-y][x].find('T') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_bat, (x * img_bat.get_width(), y * img_bat.get_height()))
                else:
                    screen.blit(bw_img_bat, (x * bw_img_bat.get_width(), y * bw_img_bat.get_height()))

            if mapa[11-y][x].find('D') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_enemy1, (x * img_enemy1.get_width(), y * img_enemy1.get_height()))                                               
                else:
                    screen.blit(bw_img_enemy1, (x * bw_img_enemy1.get_width(), y * bw_img_enemy1.get_height()))                                               
                            
            if mapa[11-y][x].find('d') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_enemy2, (x * img_enemy2.get_width(), y * img_enemy2.get_height()))                                               
                else:
                    screen.blit(bw_img_enemy2, (x * bw_img_enemy2.get_width(), y * bw_img_enemy2.get_height()))                                               

            if mapa[11-y][x].find('U') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_health, (x * img_health.get_width(), y * img_health.get_height()))                               
                else:
                    screen.blit(bw_img_health, (x * bw_img_health.get_width(), y * bw_img_health.get_height()))                               

            if mapa[11-y][x].find('O') > -1:
                if (x+1,12-y) in certezas:
                    screen.blit(img_gold, (x * img_gold.get_width(), y * img_gold.get_height()))                
                else:
                    screen.blit(bw_img_gold, (x * bw_img_gold.get_width(), y * bw_img_gold.get_height()))                
            
            if x ==  player_pos[0]-1  and  y == 12 -player_pos[1] :
                if player_pos[2] == 'norte':
                    screen.blit(img_player_up, (x * img_player_up.get_width(), y * img_player_up.get_height()))                                               
                elif player_pos[2] == 'sul':
                    screen.blit(img_player_down, (x * img_player_down.get_width(), y * img_player_down.get_height()))                                               
                elif player_pos[2] == 'leste':
                    screen.blit(img_player_right, (x * img_player_right.get_width(), y * img_player_right.get_height()))                                               
                elif player_pos[2] == 'oeste':
                    screen.blit(img_player_left, (x * img_player_left.get_width(), y * img_player_left.get_height()))                                                                                                           
                else:
                    screen.blit(img_tomb, (x * img_tomb.get_width(), y * img_tomb.get_height()))                                                                                                           
            x  += 1
        y +=  1

    t = sys_font.render("Pontuação: " + str(pontuacao), False, (255,255,255))
    screen.blit(t, t.get_rect(top = height + 5, left=40))

    t = sys_font.render(last_action, False, (255,255,255))
    screen.blit(t, t.get_rect(top = height + 5, left=width/2-40))
    
    t = sys_font.render("Energia: " + str(energia), False, (255,255,255))
    screen.blit(t, t.get_rect(top = height + 5, left=width-140))


def main_loop(screen):  
    global clock
    running = True
    while running:
        for e in pygame.event.get(): 
            if e.type == pygame.QUIT:
                running = False
                break

        # Define FPS máximo
        clock.tick(60)        
 
        # Calcula tempo transcorrido desde
        # a última atualização 
        dt = clock.get_time()

        key_pressed()
        
        # Atualiza posição dos objetos da tela
        update(dt, screen)

        # Desenha objetos na tela 
        draw_screen(screen)

        # Pygame atualiza o seu estado
        pygame.display.update() 


update_prolog()

pygame.init()
pygame.display.set_caption('INF1771 Trabalho 2 - Agente Lógico')
screen = pygame.display.set_mode((width, height+30))
load()

if auto_play:
    a = Th("","")
    a.start() 

main_loop(screen)
pygame.quit()



