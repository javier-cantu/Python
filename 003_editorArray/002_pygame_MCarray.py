import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
width, height = 800, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Diseñador de Estructuras Minecraft")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)

# Tamaño de la cuadrícula
grid_size = 50
cell_size = width // grid_size

# Función para dibujar la cuadrícula
def draw_grid():
    for x in range(0, width, cell_size):
        for y in range(0, height, cell_size):
            rect = pygame.Rect(x, y, cell_size, cell_size)
            pygame.draw.rect(screen, GREY, rect, 1)

# Array para almacenar colores de las celdas
colors = [[WHITE for _ in range(grid_size)] for _ in range(grid_size)]

# Función para pintar celdas
def paint_cell(x, y, color):
    column = x // cell_size
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
            paint_cell(x, y, BLACK)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Comprobar si el botón izquierdo está presionado
                x, y = event.pos
                paint_cell(x, y, BLACK)

    # Dibujar el fondo y la cuadrícula
    screen.fill(WHITE)
    for row in range(grid_size):
        for col in range(grid_size):
            color = colors[row][col]
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

    draw_grid()
    pygame.display.flip()

pygame.quit()
sys.exit()
