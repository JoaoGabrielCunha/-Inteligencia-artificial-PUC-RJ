from queue import PriorityQueue
import mapsetup
import pygame

map_height = 0
map_width = 0
n_tests = 0
custo_a_estrela = 0
caminho = {}

# Coordenadas a se passar, ordenadas:
coords_dic = {
    "start" : (0,0),
    "event_1" : (0,0),
    "event_2" : (0,0),
    "event_3" : (0,0),
    "event_4" : (0,0),
    "event_5" : (0,0),
    "event_6" : (0,0),
    "event_7" : (0,0),
    "event_8" : (0,0),
    "event_9" : (0,0),
    "event_0" : (0,0),
    "event_B" : (0,0),
    "event_C" : (0,0),
    "event_D" : (0,0),
    "event_E" : (0,0),
    "event_G" : (0,0),
    "event_H" : (0,0),
    "end" : (0,0)
}

def read_file(filename):

    global map_width, map_height
    lines = None

    with open(filename) as file:
        lines = file.readlines()
        j = 0
        for line in lines:
            lines[j] = line.strip('\n')
            
            # Encontrar as coordenadas iniciais e finais:
            if line.find('J') > -1:
                coords_dic['end'] = (line.find('J'), j)
            if line.find('I') > -1:
                coords_dic['start'] = (line.find('I'), j)

            # Encontrar os eventos:
            if line.find('1') > -1:
                coords_dic['event_1'] = (line.find('1'), j)
            if line.find('2') > -1:
                coords_dic['event_2'] = (line.find('2'), j)
            if line.find('3') > -1:
                coords_dic['event_3'] = (line.find('3'), j)
            if line.find('4') > -1:
                coords_dic['event_4'] = (line.find('4'), j)
            if line.find('5') > -1:
                coords_dic['event_5'] = (line.find('5'), j)
            if line.find('6') > -1:
                coords_dic['event_6'] = (line.find('6'), j)
            if line.find('7') > -1:
                coords_dic['event_7'] = (line.find('7'), j)
            if line.find('8') > -1:
                coords_dic['event_8'] = (line.find('8'), j)
            if line.find('9') > -1:
                coords_dic['event_9'] = (line.find('9'), j)
            if line.find('0') > -1:
                coords_dic['event_0'] = (line.find('0'), j)
            if line.find('B') > -1:
                coords_dic['event_B'] = (line.find('B'), j)
            if line.find('C') > -1:
                coords_dic['event_C'] = (line.find('C'), j)
            if line.find('D') > -1:
                coords_dic['event_D'] = (line.find('D'), j)
            if line.find('E') > -1:
                coords_dic['event_E'] = (line.find('E'), j)
            if line.find('G') > -1:
                coords_dic['event_G'] = (line.find('G'), j)
            if line.find('H') > -1:
                coords_dic['event_H'] = (line.find('H'), j)
            j += 1

    map_width = len(lines[0])
    map_height = len(lines)

    return lines


def printMap(lines, actual):

    # print()
    # print()
    # print()
            
    #print("\033[%d;%dH" % (0, 0)) # y, x

    for j in range(map_height):
        for i in range(map_width):
            if actual[0] == i and actual[1] == j:
                print('█', end='')
            else:
                print(lines[j][i], end='')

        print()



def get_value(c):
    
    v = 999   # O custo para passar pelo os eventos serah zero incialmente

    if c == '.' or c == 'J' or c == 'I':
        v = 1
    elif c =='M': 
        v = 200
    elif c == 'A': 
        v = 30
    elif c == 'F':
        v = 15
    elif c == 'R':
        v = 5

    return v

def get_char_from_map(mapa, coord):
    return mapa[coord[1]][coord[0]]

def get_value_from_map(mapa, coord):
    return get_value(get_char_from_map(mapa, coord))


def add_valid_pos(nb, mapa, coord):        
    if get_value_from_map(mapa, coord) > -1:
        nb.append(coord)

def get_neighborhood(mapa, coord):
    
    nb = []
    if coord[0] == 0:
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
    
    elif coord[0] == map_width - 1:
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))
    
    else:    
        add_valid_pos(nb, mapa, (coord[0] + 1, coord[1]))
        add_valid_pos(nb, mapa, (coord[0] - 1, coord[1]))
    

    if coord[1] == 0:
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
    
    elif coord[1] == map_height - 1:
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))
    
    else:    
        add_valid_pos(nb, mapa, (coord[0], coord[1] + 1))
        add_valid_pos(nb, mapa, (coord[0], coord[1] - 1))
    
    return nb

def manhattan_distance(_from, to):
    # |x2 - x1| + |y2 - y1|
    return abs(to[0] - _from[0]) + abs(to[1] - _from[1])

def busca_a_estrela(mapa, local_start, local_end):
    global n_tests, custo_a_estrela
    
    fronteira = PriorityQueue()
    fronteira.put((0,(local_start ,0)))
    
    visitados = set() #[] usar set para ser mais eficiente ?
    
    while fronteira:
        node = fronteira.get()
        coord = node[1][0]
        distacia_atual = node[1][1]
        
        if coord in visitados: 
            continue
        n_tests += 1

        visitados.add(coord) #append(coord)
        
        if coord == local_end: #coords_dic['end']
            custo_a_estrela += distacia_atual
            print(f"Trajeto: {local_start} -> {local_end}")
            print("testes a*",n_tests)
            print("ta chamando a funcao")
            mapsetup.updatemap2(l,mapsetup.window,mapsetup.mapgrid,caminho,local_start,local_end)
            print("terminou de chamar a funcao")
            pygame.time.delay(100)
            if local_end == coords_dic['end']:
                print("custo a* local",distacia_atual)
                print("custo a* total",custo_a_estrela - (999*16))
            else:
                print("custo a* local",distacia_atual - 999)
            return  
        global vizinhos
        vizinhos = get_neighborhood(mapa,coord)

        for vizinho in vizinhos:
            if vizinho not in visitados:
                gx = distacia_atual + get_value_from_map(mapa, vizinho)
                hx = manhattan_distance(vizinho, local_end)
                fx = gx + hx
                fronteira.put((fx, (vizinho,gx)))
                caminho[vizinho] = coord

def percorre_mapa(mapa):
    start = coords_dic['start']
    for coord in coords_dic.values():
        if coord != start:
            local_end = coord
            busca_a_estrela(mapa, start, local_end)
            #print(mapsetup.window)
            #print(mapsetup.mapgrid)
            print(coord)
            print(vizinhos)
            start = local_end

# Main A*:
mapa = read_file('data/mapa_witcher.txt')

#printMap(mapa, start)

global l
l=[]
running = True
while running:
    for event in pygame.event.get():
        running = False
    mapsetup.drawmap(mapsetup.window,mapsetup.mapgrid)
    pygame.display.update()

percorre_mapa(mapa)
# print(coords_dic['start'])
# print(coords_dic['event_1'])
# busca_a_estrela(mapa, coords_dic["start"], coords_dic["event_1"])
# busca_a_estrela(mapa, coords_dic["event_1"], coords_dic["event_2"])
# busca_a_estrela(mapa, coords_dic["event_2"], coords_dic["event_3"])

pygame.quit()