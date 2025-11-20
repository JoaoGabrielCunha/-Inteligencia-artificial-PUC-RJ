#!/usr/bin/env python

"""GameAI.py: INF1771 GameAI File - Where Decisions are made."""
#############################################################
#Copyright 2020 Augusto Baffa
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#############################################################
__author__      = "Augusto Baffa"
__copyright__   = "Copyright 2020, Rio de janeiro, Brazil"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "abaffa@inf.puc-rio.br"
#############################################################

import random
from Map.Position import Position
from queue import PriorityQueue

MAP_HEIGHT = 34
MAP_WIDTH = 59

# <summary>
# Game AI Example
# </summary>
class GameAI():

    player = Position()
    state = "ready"
    dir = "north"
    score = 0
    energy = 0

    mapa = [['' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    visitados = {}
    certezas = []

    tesouros = []
    powerups = []

    recebeu_tiro = False
    inimigo = False
    ataque = False
    dist_ataque = 0
    cont_ataque = 0

    pegou_tesouro = True
    pegou_powerup = True
    target = None
    indo_powerup = False

    # <summary>
    # Refresh player status
    # </summary>
    # <param name="x">player position x</param>
    # <param name="y">player position y</param>
    # <param name="dir">player direction</param>
    # <param name="state">player state</param>
    # <param name="score">player score</param>
    # <param name="energy">player energy</param>
    def SetStatus(self, x, y, dir, state, score, energy):
    
        self.player.x = x
        self.player.y = y
        self.dir = dir.lower()

        self.state = state
        self.score = score
        self.energy = energy
        
        print(state)
        
        if state == "gameover":
            self.mapa = [['' for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
            self.visitados = {}
            self.certezas = []
            self.tesouros = []
            self.powerups = []
            self.ataque = False
            self.dist_ataque = 0
            self.cont_ataque = 0
            self.pegou_tesouro = True
            self.target = None


    # <summary>
    # Get list of observable adjacent positions
    # </summary>
    # <returns>List of observable adjacent positions</returns>
    def GetObservableAdjacentPositions(self):
        ret = []

        ret.append(Position(self.player.x - 1, self.player.y))
        ret.append(Position(self.player.x + 1, self.player.y))
        ret.append(Position(self.player.x, self.player.y - 1))
        ret.append(Position(self.player.x, self.player.y + 1))

        return ret


    # <summary>
    # Get list of all adjacent positions (including diagonal)
    # </summary>
    # <returns>List of all adjacent positions (including diagonal)</returns>
    def GetAllAdjacentPositions(self):
    
        ret = []

        ret.Add(Position(self.player.x - 1, self.player.y - 1))
        ret.Add(Position(self.player.x, self.player.y - 1))
        ret.Add(Position(self.player.x + 1, self.player.y - 1))

        ret.Add(Position(self.player.x - 1, self.player.y))
        ret.Add(Position(self.player.x + 1, self.player.y))

        ret.Add(Position(self.player.x - 1, self.player.y + 1))
        ret.Add(Position(self.player.x, self.player.y + 1))
        ret.Add(Position(self.player.x + 1, self.player.y + 1))

        return ret
    

    # <summary>
    # Get next forward position
    # </summary>
    # <returns>next forward position</returns>
    def NextPosition(self):
    
        ret = None
        
        if self.dir == "north":
            ret = Position(self.player.x, self.player.y - 1)
                
        elif self.dir == "east":
                ret = Position(self.player.x + 1, self.player.y)
                
        elif self.dir == "south":
                ret = Position(self.player.x, self.player.y + 1)
                
        elif self.dir == "west":
                ret = Position(self.player.x - 1, self.player.y)

        return ret


    # <summary>
    # Player position
    # </summary>
    # <returns>player position</returns>
    def GetPlayerPosition(self):
        return self.player


    # <summary>
    # Set player position
    # </summary>
    # <param name="x">x position</param>
    # <param name="y">y position</param>
    def SetPlayerPosition(self, x, y):
        self.player.x = x
        self.player.y = y


    # <summary>
    # Get value from char
    # </summary>
    def get_value(self, c):
        if "P" in c:
            return -1
        elif "B" in c:
            return 10000
        elif "F" in c:
            return 2000
        else:
            return 1


    # <summary>
    # Get value from map
    # </summary>
    # <param name="mapa">map</param>
    # <param name="coord">position</param>
    # <returns>value</returns>
    def get_value_from_map(self, mapa, coord):
        return self.get_value(mapa[coord[1]][coord[0]])


    # <summary>
    # Add valid position to neighborhood
    # </summary>
    # <param name="nb">neighborhood</param>
    # <param name="coord">position</param>
    def add_valid_pos(self, nb, coord):
        if self.get_value_from_map(self.mapa, coord) > -1:
            nb.append(coord)


    # <summary>
    # Get neighborhood of a position
    # </summary>
    # <param name="coord">position</param>
    # <returns>list of valid neighbors</returns>
    def get_neighborhood(self, coord):
        nb = []

        # Confere as bordas esquerda e direita
        if coord[0] == 0: # Esquerda
            self.add_valid_pos(nb, (coord[0] + 1, coord[1]))
        elif coord[0] == MAP_WIDTH - 1: # Direita
            self.add_valid_pos(nb, (coord[0] - 1, coord[1]))
        else:
            self.add_valid_pos(nb, (coord[0] + 1, coord[1]))
            self.add_valid_pos(nb, (coord[0] - 1, coord[1]))

        # Confere as bordas superior e inferior
        if coord[1] == 0: # Superior
            self.add_valid_pos(nb, (coord[0], coord[1] + 1))
        elif coord[1] == MAP_HEIGHT - 1: # Inferior
            self.add_valid_pos(nb, (coord[0], coord[1] - 1))
        else:
            self.add_valid_pos(nb, (coord[0], coord[1] + 1))
            self.add_valid_pos(nb, (coord[0], coord[1] - 1))

        return nb


    # <summary>
    # Manhattan distance between two positions
    # </summary>
    # <param name="_from">from position</param>
    # <param name="to">to position</param>
    # <returns>manhattan distance</returns>
    def manhattan_distance(self, _from, to):
        # |x2 - x1| + |y2 - y1|
        return abs(to[0] - _from[0]) + abs(to[1] - _from[1])


    # <summary>
    # Get direction between two positions
    # </summary>
    # <param name="_from">from position</param>
    # <param name="to">to position</param>
    def get_direction(self, _from, to):
        if _from[0] == to[0]:
            if _from[1] > to[1]:
                return "north"
            else:
                return "south"
        else:
            if _from[0] > to[0]:
                return "west"
            else:
                return "east"


    # <summary>
    # Busca A*
    # </summary>
    # <param name="end">end position</param>
    # <returns>list of positions to reach the end</returns>
    def busca_a_estrela(self, end=None):
        start = (self.player.x, self.player.y)

        fronteira = PriorityQueue()
        fronteira.put((0, start, []))

        custos = {start: 0}

        while not fronteira.empty():
            node = fronteira.get()
            coord = node[1]
            custo_atual = node[0]

            if end:
                if coord == end:
                    return node[2]
            elif (coord[0], coord[1]) not in self.visitados and (coord[0], coord[1]) not in self.certezas:
                return node[2]
            
            for vizinho in self.get_neighborhood(coord):
                custo_coord = self.get_value_from_map(self.mapa, vizinho)
                gx = custo_atual + custo_coord
                if vizinho not in custos or gx < custos[vizinho]:
                    hx = self.manhattan_distance(vizinho, end) if end else 0
                    fx = gx + hx
                    fronteira.put((fx, vizinho, node[2] + [vizinho]))
                    custos[vizinho] = gx


    # <summary>
    # Move to target
    # </summary>
    # <returns>command string to move to target</returns>
    def move_to_target(self):
        if self.target:
            next_step = self.target[0]
            direcao = self.get_direction((self.player.x, self.player.y), next_step)
            if self.dir != direcao:
                if (self.dir, direcao) in (("north", "west"), ("west", "south"), ("south", "east"), ("east", "north")):
                    return "virar_esquerda"
                return "virar_direita"
            self.target.pop(0)
            return "andar"


    # <summary>
    # Observations received
    # </summary>
    # <param name="o">list of observations</param>
    def GetObservations(self, o):
    
        # IMPLEMENTAR
        # como sua solucao vai tratar as observacoes?
        # como seu bot vai memorizar os lugares por onde passou?
        # aqui, recebe-se as observacoes dos sensores para as
        # coordenadas atuais do player

        print("Observations received:")
        print(o)
        if (self.player.x, self.player.y) not in self.visitados:
            self.visitados[(self.player.x, self.player.y)] = 0
        for s in o:
        
            if s == "blocked":
                next_position = self.NextPosition()
                self.mapa[next_position.y][next_position.x] += "P"
                self.certezas.append(next_position)

            elif s == "steps":
                pass

            elif s == "breeze":
                adjacent_positions = self.GetObservableAdjacentPositions()
                for pos in adjacent_positions:
                    if (pos.x, pos.y) not in self.visitados and "B" not in self.mapa[pos.y][pos.x]:
                        self.mapa[pos.y][pos.x] += "B"

            elif s == "flash":
                adjacent_positions = self.GetObservableAdjacentPositions()
                for pos in adjacent_positions:
                    if (pos.x, pos.y) not in self.visitados and "F" not in self.mapa[pos.y][pos.x]:
                        self.mapa[pos.y][pos.x] += "F"

            elif s == "blueLight":
                self.mapa[self.player.y][self.player.x] += "T"
                if (self.player.x, self.player.y) not in self.tesouros:
                    self.tesouros.append(((self.player.x, self.player.y)))

            elif s == "redLight":
                self.mapa[self.player.y][self.player.x] += "R"
                if (self.player.x, self.player.y) not in self.powerups:
                    self.powerups.append(((self.player.x, self.player.y)))

            elif s == "greenLight":
                pass

            elif s == "weakLight":
                pass

            elif s == "damage":
                self.recebeu_tiro = True

            elif s == "hit":
                self.cont_ataque = 0

            elif s.find("enemy#") > -1:
                try:
                    steps = int(s[6:])
                    self.inimigo = True
                    if not self.ataque:
                        self.ataque = True
                        self.dist_ataque = steps
                        self.cont_ataque = 0
                except:
                    pass


    # <summary>
    # No observations received
    # </summary>
    def GetObservationsClean(self):
    
        # IMPLEMENTAR
        # como "apagar/esquecer" as observacoes?
        # devemos apagar as atuais para poder receber novas
        # se nao apagarmos, as novas se misturam com as anteriores
        if (self.player.x, self.player.y) not in self.visitados:
            self.visitados[(self.player.x, self.player.y)] = 0
        self.inimigo = False
        self.recebeu_tiro = False

    # <summary>
    # Get Decision
    # </summary>
    # <returns>command string to new decision</returns>
    def GetDecision(self):

        # IMPLEMENTAR
        # Qual a decisão do seu bot?

        # A cada ciclo, o bot segue os passos:
        # 1- Solicita observações
        # 2- Ao receber observações:
        # 2.1 - chama "GetObservationsClean()" para apagar as anteriores
        # 2.2 - chama "GetObservations(_)" passando as novas observacoes
        # 3- chama "GetDecision()" para perguntar o que deve fazer agora
        # 4- envia decisão ao servidor
        # 5- após ação enviada, reinicia voltando ao passo 1

        print(self.tesouros)
        print(self.powerups)

        for visitado in self.visitados:
            self.visitados[visitado] += 1

        # Se tiver um inimigo para atacar, atacar
        if self.inimigo:
            if self.ataque:
                if self.cont_ataque < self.dist_ataque:
                    self.cont_ataque += 1
                    print("atacar")
                    return "atacar"
                self.ataque = False

        # Se tiver um ouro na posição atual, pegar
        if "T" in self.mapa[self.player.y][self.player.x]:
            self.mapa[self.player.y][self.player.x] = self.mapa[self.player.y][self.player.x].replace("T", "")
            if not self.pegou_tesouro:
                self.tesouros.append(self.tesouros.pop(0))
            self.pegou_tesouro = True
            print("pegar tesouro")
            return "pegar_ouro"
        
        # Se tiver um powerup na posição atual e a energia for menor que 100, pegar
        if "R" in self.mapa[self.player.y][self.player.x] and self.energy < 100:
            self.mapa[self.player.y][self.player.x] = self.mapa[self.player.y][self.player.x].replace("R", "")
            self.pegou_powerup = True
            print("pegar powerup")
            return "pegar_powerup"

        # Se tiver um objetivo, fazer o movimento que o leve em direção a ele
        if self.target:
            # Se tiver com pouca energia e tiver powerups, ir para o mais próximo
            if self.energy < 80 and not self.indo_powerup and self.powerups:
                self.indo_powerup = True
                melhor_powerup = self.powerups[0]
                for powerup in self.powerups:
                    if self.manhattan_distance((self.player.x, self.player.y), powerup) < self.manhattan_distance((self.player.x, self.player.y), melhor_powerup):
                        melhor_powerup = powerup
                self.target = self.busca_a_estrela(melhor_powerup)
                return self.move_to_target()
            return self.move_to_target()

        if self.indo_powerup:
            if not self.pegou_powerup:
                next_position = self.NextPosition()
                # Se a próxima posição for bloqueada, virar para a direita
                if next_position.x < 0 or next_position.x >= MAP_WIDTH or next_position.y < 0 or next_position.y >= MAP_HEIGHT or any(char in self.mapa[next_position.y][next_position.x] for char in "PBF"):
                    return "virar_direita"
                # Se recebeu tiro ou a próxima posição não foi visitada (para descobrir se tem bloqueio na frente), andar
                if self.recebeu_tiro or (next_position.x, next_position.y) not in self.visitados:
                    return "andar"
                return ""
            self.indo_powerup = False


        # Se encontrar tesouros o suficiente, ir para o primeiro na lista
        if len(self.tesouros) >= 4:
            # Se já pegou o tesouro ou o tesouro não está mais na posição, ir para o tesouro
            if self.pegou_tesouro or self.tesouros[0] != (self.player.x, self.player.y):
                self.pegou_tesouro = False
                self.target = self.busca_a_estrela(self.tesouros[0])
                return self.move_to_target()
            else:
                next_position = self.NextPosition()
                # Se a próxima posição for bloqueada, virar para a direita
                if next_position.x >= MAP_WIDTH or next_position.y < 0 or next_position.y >= MAP_HEIGHT or any(char in self.mapa[next_position.y][next_position.x] for char in "PBF") or next_position.x < 0:
                    return "virar_direita"
                # Se recebeu tiro ou a próxima posição não foi visitada (para descobrir se tem bloqueio na frente), andar
                if self.recebeu_tiro or (next_position.x, next_position.y) not in self.visitados:
                    return "andar"
                return ""

        # Se já tiver visitado mais de 40% do mapa, voltar para a casa mais antiga
        if len(self.visitados) > (MAP_HEIGHT * MAP_WIDTH) * 0.4:
            visitado_mais_antigo = max(self.visitados, key=self.visitados.get)
            self.visitados[visitado_mais_antigo] = 0
            self.target = self.busca_a_estrela(visitado_mais_antigo)
            return self.move_to_target()

        # Procurar casa não visitada
        print("busca a estrela")
        self.target = self.busca_a_estrela()
        if self.target:
            return self.move_to_target()

        return ""
