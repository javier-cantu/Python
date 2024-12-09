# Ahora con barra izquierda con materiales

import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Diseñador de Estructuras Minecraft")

# Colores y materiales
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (200, 200, 200)

materials = [WHITE, BLACK, RED, GREEN, BLUE]
material_names = ["White", "Black", "Red", "Green", "Blue"]
current_material = BLACK

# Tamaño de la cuadrícula y la barra lateral
grid_size = 50
cell_size = (width - 200) // grid_size  # Restar el ancho de la barra lateral
sidebar_width = 200

# Función para dibujar la cuadrícula
def draw_grid():
    for x in range(sidebar_width, width, cell_size):
        for y in range(0, height, cell_size):
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, GREY, rect, 1)

# Función para dibujar la barra lateral
def draw_sidebar():
    pygame.draw.rect(screen, GREY, pygame.Rect(0, 0, sidebar_width, height))
    for i, color in enumerate(materials):
        rect = pygame.Rect(10, 10 + i * 60, sidebar_width - 20, 50)
        pygame.draw.rect(screen, color, rect)
        if color == current_material:
            pygame.draw.rect(screen, BLACK, rect, 4)

# Array para almacenar colores de las celdas
colors = [[WHITE for _ in range(grid_size)] for _ in range(grid_size)]

# Función para pintar celdas
def paint_cell(x, y, color):
    if x >= sidebar_width:  # Asegurarse de que el clic es en la zona de la cuadrícula
        column = (x - sidebar_width) // cell_size
        row = y // cell_size
        colors[row][column] = color

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x < sidebar_width:  # Clic en la barra lateral
                index = (y - 10) // 60
                if 0 <= index < len(materials):
                    current_material = materials[index]
            else:
                paint_cell(x, y, current_material)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Comprobar si el botón izquierdo está presionado
                x, y = event.pos
                paint_cell(x, y, current_material)

    # Dibujar el fondo, la cuadrícula y la barra lateral
    screen.fill(WHITE)
    draw_sidebar()
    for row in range(grid_size):
        for col in range(grid_size):
            color = colors[row][col]
            rect = pygame.Rect(sidebar_width + col * cell_size, row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)
    draw_grid()
    pygame.display.flip()

pygame.quit()
sys.exit()
