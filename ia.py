import numpy as np
import random

class QLearningAgent:
    def __init__(self, maze, start_pos, exit_pos):
        self.maze = maze
        self.start_pos = start_pos
        self.exit_pos = exit_pos
        self.actions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # haut, bas, gauche, droite
        self.q_table = np.zeros((len(maze), len(maze[0]), len(self.actions)))
        self.alpha = 0.1  # Taux d'apprentissage
        self.gamma = 0.9  # Facteur de discount
        self.epsilon = 0.1  # Taux d'exploration
        self.y, self.x = start_pos  # Position initiale

    def get_agent_pos(self):
        return (self.x, self.y)  # Retourne (x, y) pour correspondre à Pygame

    def reset(self):
        self.y, self.x = self.start_pos
        return self.get_agent_pos()

    def is_move_valid(self, x, y):
        """Vérifie si le déplacement est valide (pas un mur et dans les limites)."""
        if x < 0 or y < 0 or y >= len(self.maze) or x >= len(self.maze[0]):
            return False
        return self.maze[y][x] != 1

    def is_finished(self):
        """Vérifie si l'agent a atteint la sortie."""
        return (self.x, self.y) == self.exit_pos

    def step(self, action):
        """Effectue un pas dans l'environnement."""
        dx, dy = self.actions[action]
        new_x = self.x + dx
        new_y = self.y + dy

        if self.is_move_valid(new_x, new_y):
            self.x, self.y = new_x, new_y
            reward = 100 if self.is_finished() else -1
        else:
            reward = -10  # Pénalité pour un déplacement invalide

        return self.get_agent_pos(), reward

    def take_action(self, st, q_table, eps):
        """Choisit une action en fonction de la politique epsilon-greedy."""
        if random.uniform(0, 1) < eps:
            return random.randint(0, len(self.actions) - 1)  # Exploration
        else:
            return np.argmax(q_table[st[1]][st[0]])  # Exploitation

    def train(self, episodes):
        """Entraîne l'agent pendant un nombre donné d'épisodes."""
        for _ in range(episodes):
            st = self.reset()
            while not self.is_finished():
                y, x = st[1], st[0]  # Inversion des coordonnées pour la Q-table
                at = self.take_action((x, y), self.q_table, self.epsilon)
                st1, reward = self.step(at)
                y1, x1 = st1[1], st1[0]  # Inversion des coordonnées pour la Q-table

                # Mise à jour de la Q-table
                future_max = np.max(self.q_table[y1][x1])
                self.q_table[y][x][at] += self.alpha * (reward + self.gamma * future_max - self.q_table[y][x][at]) # Q-Fonciton
                st = st1
            print(f"Agent {_ + 1}/{episodes} entraîné.")

    def get_optimal_path(self):
        """Retourne le chemin optimal trouvé par l'agent."""
        path = []
        self.reset()
        pos = self.get_agent_pos()
        while pos != self.exit_pos and len(path) < 100:  # Limite de sécurité pour éviter les boucles infinies
            path.append(pos)
            y, x = pos[1], pos[0]  # Inversion des coordonnées pour la Q-table
            action = np.argmax(self.q_table[y][x])
            dx, dy = self.actions[action]
            new_x = x + dx
            new_y = y + dy

            if not self.is_move_valid(new_x, new_y):
                break  # Arrête si le déplacement est invalide

            pos = (new_x, new_y)
        return path