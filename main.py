import pygame
from ia import QLearningAgent
import random

pygame.init()

# Directions
DIRECTIONS = {
    pygame.K_UP: (0, -1),    # Haut
    pygame.K_DOWN: (0, 1),   # Bas
    pygame.K_LEFT: (-1, 0),  # Gauche
    pygame.K_RIGHT: (1, 0)   # Droite
}

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

gameTitle = "Maze"
backgroundColor = BLACK
playerColor = RED
exitColor = GREEN
wallColor = BLACK
wayColor = WHITE
textColor = WHITE


# Positions Initiales
PLAYER_START_X, PLAYER_START_Y = 0, 0
START_POS = (PLAYER_START_Y, PLAYER_START_X)
EXIT_X, EXIT_Y = 30, 30
EXIT_POS = (EXIT_X, EXIT_Y)
EXIT = 2

# Labyrinthe
def generate_maze(size):
    maze = [[1] * size for _ in range(size)]
    
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    # Démarrer le carving depuis l'entrée
    carve(0, 0)
    
    # Marquer l'entrée (déjà fait par carve) et la sortie (via l'algorithme)
    maze[PLAYER_START_X][PLAYER_START_Y] = 0  # Entrée (assuré par carve)
    maze[EXIT_X][EXIT_Y] = EXIT
    # Supprimer la ligne qui force la sortie à 0
    
    return maze

# Générer un labyrinthe 31x31
maze = generate_maze(31)

maze[EXIT_Y][EXIT_X] = EXIT

# Calcul de la taille de l'écran en fonction du labyrinthe
CELL_SIZE = 30
BOTTOM_PADDING = 50
ROWS = len(maze)
COLS = len(maze[0])
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE + BOTTOM_PADDING

# Variables globales pour la position du joueur
player_x, player_y = PLAYER_START_X, PLAYER_START_Y

def draw_maze(maze):
    for y in range(len(maze)):
        for x in range(len(maze[y])):
            rect = (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if maze[y][x] == 1:
                pygame.draw.rect(screen, wayColor, rect)
            elif maze[y][x] == 0:
                pygame.draw.rect(screen, wallColor, rect)
            elif maze[y][x] == EXIT:
                pygame.draw.rect(screen, exitColor, rect)
    
    # Dessiner le joueur
    pygame.draw.rect(screen, playerColor, 
                    (player_x * CELL_SIZE, 
                     player_y * CELL_SIZE, 
                     CELL_SIZE, CELL_SIZE))

def is_move_valid(x, y):
    """Vérifie si le déplacement est valide (pas un mur et dans les limites)."""
    return 0 <= x < COLS and 0 <= y < ROWS and maze[y][x] != 1

def check_win(x, y):
    """Vérifie si le joueur a atteint la sortie."""
    return maze[y][x] == EXIT



# Paramètre et initialisation de l'agent
agent = QLearningAgent(maze=maze, start_pos=START_POS, exit_pos=EXIT_POS)
agent.train(1000)

# Pour visualiser le chemin trouvé
optimal_path = agent.get_optimal_path()
current_step = 0

# Boucle de jeu
def game_loop():
    global current_step
    global player_x, player_y  # Utiliser les variables globales pour la position du joueur
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(gameTitle)

    # Initialiser les polices et le texte
    font = pygame.font.SysFont(None, 36)  # Default font, size 36
    prompt_text = font.render("Press SPACE to launch AI", True, textColor)
    prompt_text2 = font.render("Press 'R' to restart AI", True, textColor)
    text_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT - 30))  # Bottom 
    text2_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT - 30))

    clock = pygame.time.Clock()
    agent_activated = False
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Gestion des touches directionnelles
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Réinitialiser avec la touche R
                    current_step = 0
                    agent_activated = False
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:  # Activer l'agent avec la touche ENTRER ou ESPACE
                    agent_activated = True
                if event.key in DIRECTIONS:
                    dx, dy = DIRECTIONS[event.key]
                    new_x = player_x + dx
                    new_y = player_y + dy
                    # Vérifier si le déplacement est valide
                    if is_move_valid(new_x, new_y):
                        player_x, player_y = new_x, new_y
                        # Vérifier si le joueur a gagné
                        if check_win(player_x, player_y):
                            print("Félicitations ! Vous avez trouvé la sortie !")
                            running = False
        
        screen.fill(backgroundColor)
        draw_maze(maze)

        # Afficher toutes les positions passées en bleu
        if agent_activated:
            for step in range(current_step):
                x, y = optimal_path[step]
                pygame.draw.rect(screen, BLUE, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            # Afficher la position actuelle en rouge (joueur)
            if current_step < len(optimal_path):
                x, y = optimal_path[current_step]
                pygame.draw.rect(screen, RED, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                current_step += 1  # Passer à l'étape suivante
            screen.blit(prompt_text2, text2_rect)
        else:
            screen.blit(prompt_text, text_rect)
        pygame.display.update()  # Mettre à jour l'affichage à chaque frame
        clock.tick(30)  # Contrôler la vitesse d'affichage (10 étapes par seconde)
    
    pygame.quit()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(gameTitle)

game_loop()
