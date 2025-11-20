import pygame
import os

def readmap(file):
    parentdir = os.path.dirname(os.path.abspath(__file__))
    datafolder = os.path.join(parentdir,'data')
    filepath=os.path.join(datafolder,file)
    with open(filepath, 'r') as f:
        map_data = f.read().splitlines()
    return map_data

mapfile = 'mapa_witcher.txt'
mapgrid = readmap(mapfile)

global widthsize,heightsize
heightsize = 2
widthsize = 1

# Define terrain colors
TERRAIN_COLORS = {
    'A': (114, 227, 252),  # agua - azul
    'M': (120, 76, 55),  # montanha - marrom
    'F': (80, 186, 121),  # floresta - verde
    'R': (89, 83, 79),  # rochas - cinza
    '.': (255, 255, 255),  # campo aberto - branco
    'I': (255, 0, 0),  # inicio - vermelho
    'J': (143, 255, 203),  # destino - verde
}

pygame.init()

global window

width, height = len(mapgrid[0]) * widthsize, len(mapgrid) * heightsize
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Mapa do Jogo')

def drawmap(window, mapgrid):
    for row in range(len(mapgrid)):
        for col in range(len(mapgrid[0])):
            tile = mapgrid[row][col]
            color = TERRAIN_COLORS.get(tile, (0, 0, 0)) 
            pygame.draw.rect(window, color, (col * widthsize, row * heightsize, widthsize, heightsize))

def drawcell(window,x,y,color):
    pygame.draw.rect(window,color,(x*widthsize,y*heightsize,widthsize,heightsize))

def updatemap(window,mapgrid,neighbors):
    drawmap(window,mapgrid)
    #print("CURRENT CELL AQUI MARIN")
    #print(current)
    #print("VIZINHOS AQUI MARINA")
    #print(neighbors)
    #drawcell(window,current[0],current[1],(115,65,210))
    #print(neighbors)
    for neighbor in neighbors:
        print(neighbor)
        drawcell(window,neighbor[0],neighbor[1],(210,65,180))
    pygame.display.flip()

def retornadicionario(d,ini,fim):
    l=[fim]
    while fim!=ini:
        l.append(d[fim])
        fim = d[fim]
    return l

def updatemap2(caminho,window,mapgrid,d,inicio,fim):
    drawmap(window,mapgrid)
    l=retornadicionario(d,inicio,fim)
    caminho.append(l)
    for c in caminho:
        for t in c: 
            drawcell(window,t[0],t[1],(210,65,180))
    pygame.display.flip()




# running = True
# while running:
#     pygame.time.delay(100)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     drawmap(window, mapgrid)
#     pygame.time.delay(300)
#     updatemap(window,mapgrid,(150,150),([160,160],[170,170]))
#     pygame.time.delay(300)
#     updatemap(window,mapgrid,(160,160),([180,160],[190,170]))
#    #pygame.display.update()

# pygame.quit()