import pygame
import numpy as np
import random
import sys

# Constantes
G = 6.67e-11  # Constante gravitacional
AU = 1.496e+11  # Unidade astronômica em metros
SCALE = 250 / AU  # Escala inicial

# Definindo cores
COLORS = {
    "white": (255, 255, 255),
    "yellow": (255, 255, 0),
    "gray": (169, 169, 169),
    "cyan": (0, 255, 255),
    "blue": (0, 0, 255),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "light_blue": (173, 216, 230),
    "dark_blue": (0, 0, 139),
    "purple": (128, 0, 128),
    "black": (0, 0, 0),
}

# Classe para Planetas e Sol
class CelestialBody:
    def __init__(self, name, mass, radius, position, velocity, color, fixed_size=False):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.position = np.array(position, dtype='float64')
        self.velocity = np.array(velocity, dtype='float64')
        self.color = color
        self.show_name = False  # Controla se o nome será exibido
        self.fixed_size = fixed_size  # Se True, o tamanho não será afetado pelo zoom
        self.trail = []  # Lista para armazenar rastros

    def update(self, dt, sun_mass):
        r = np.linalg.norm(self.position)
        if r == 0:
            return
        acceleration = -G * sun_mass * self.position / (r ** 3)
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        self.trail.append(self.position.copy())

# Inicializando corpos celestes
sun = CelestialBody("Sol", 1.989e30, 20, [0, 0], [0, 0], COLORS["yellow"], fixed_size=True)
planets = [
    CelestialBody("Mercúrio", 3.285e23, 5, [57.909e9, 0], [0, 47.36e3], COLORS["gray"]),
    CelestialBody("Vênus", 4.867e24, 6, [0.728213 * AU, 0], [0, 35.02e3], COLORS["cyan"]),
    CelestialBody("Terra", 5.972e24, 6, [AU, 0], [0, 29.78e3], COLORS["blue"]),
    CelestialBody("Marte", 6.417e23, 5, [1.524 * AU, 0], [0, 24.07e3], COLORS["red"]),
    CelestialBody("Júpiter", 1.898e27, 10, [5.2 * AU, 0], [0, 13.07e3], COLORS["orange"]),
    CelestialBody("Saturno", 5.683e26, 9, [9.58 * AU, 0], [0, 9.69e3], COLORS["light_blue"]),
    CelestialBody("Urano", 8.681e25, 8, [19.22 * AU, 0], [0, 6.81e3], COLORS["dark_blue"]),
    CelestialBody("Netuno", 1.024e26, 7, [30.07 * AU, 0], [0, 5.43e3], COLORS["purple"]),
    CelestialBody("Plutão", 1.303e22, 4, [39.482 * AU, 0], [0, 4.74e3], COLORS["gray"])
]

# Inicializando Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simulador do Sistema Solar")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14)

# Variáveis de controle
follow_planet = None
dt = 3600  # Tempo em segundos
show_names = False
current_planet_index = -1  # Índice do planeta atual
current_planet_name = sun.name  # Nome do planeta atualmente orbitando

# Gerando estrelas fixas
num_stars = 100
stars = [[random.randint(0, 800), random.randint(0, 600)] for _ in range(num_stars)]

# Função para verificar clique no planeta ou sol
def is_clicked(mouse_pos, body_pos, body_radius):
    distance = np.linalg.norm(np.array(mouse_pos) - np.array(body_pos))
    return distance <= body_radius

# Função para desenhar botão
def draw_toggle_names_button():
    # Definindo propriedades do botão
    button_rect = pygame.Rect(10, 10, 150, 30)
    border_radius = 15  # Raio para bordas arredondadas
    pygame.draw.rect(screen, COLORS["dark_blue"], button_rect, border_radius=border_radius)  # Cor de fundo do botão

    # Adicionando bordas
    pygame.draw.rect(screen, COLORS["white"], button_rect, 2, border_radius)  # Borda do botão

    # Centralizando o texto
    text = font.render("Ativar Nomes", True, COLORS["white"])
    text_rect = text.get_rect(center=button_rect.center)  # Centraliza o texto no botão
    screen.blit(text, text_rect)  # Desenha o texto no botão

    return button_rect

# Função para desenhar retângulos arredondados
def draw_rounded_rect(surface, color, rect, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_navigation_container(current_planet_name):
    container_width = 400
    container_height = 100
    container_rect = pygame.Rect(200, 550, container_width, container_height)

    # Desenha o fundo do container com gradiente
    for i in range(container_height):
        color = (0, 0, 100 + i // 2)  # Gradiente azul
        pygame.draw.line(screen, color, (container_rect.left, container_rect.top + i),
                         (container_rect.right, container_rect.top + i))

    # Botão de navegação para esquerda
    left_button_rect = pygame.Rect(container_rect.left + 10, container_rect.centery - 44, 50, 40)
    draw_rounded_rect(screen, COLORS["dark_blue"], left_button_rect, 10)  # Cor de fundo do botão
    pygame.draw.rect(screen, COLORS["white"], left_button_rect, 2)  # Borda do botão
    left_text = font.render("<", True, COLORS["white"])
    left_text_rect = left_text.get_rect(center=left_button_rect.center)
    screen.blit(left_text, left_text_rect)  # Desenha o texto no botão

    # Botão de navegação para direita
    right_button_rect = pygame.Rect(container_rect.right - 60, container_rect.centery - 44, 50, 40)
    draw_rounded_rect(screen, COLORS["dark_blue"], right_button_rect, 10)  # Cor de fundo do botão
    pygame.draw.rect(screen, COLORS["white"], right_button_rect, 2)  # Borda do botão
    right_text = font.render(">", True, COLORS["white"])
    right_text_rect = right_text.get_rect(center=right_button_rect.center)
    screen.blit(right_text, right_text_rect)  # Desenha o texto no botão

    # Desenha a caixa de texto com o planeta atualmente orbitando
    text = font.render(f"Agora orbitando: {current_planet_name}", True, COLORS["white"])
    text_rect = text.get_rect(center=(container_rect.centerx, container_rect.centery - 30))  # Posição da caixa de texto
    draw_rounded_rect(screen, COLORS["dark_blue"], text_rect.inflate(10, 10), 10)  # Fundo da caixa de texto
    screen.blit(text, text_rect)  # Desenha o texto na caixa

    return left_button_rect, right_button_rect, container_rect


# Loop principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if event.button == 5:  # Zoom in
                SCALE *= 0.9
            elif event.button == 4:  # Zoom out
                SCALE *= 1.1
            else:
                # Verificar se clicou no botão de ativar nomes
                if button_rect.collidepoint(mouse_pos):
                    show_names = not show_names  # Alterna a exibição dos nomes
                    sun.show_name = show_names  # Atualiza a exibição do nome do Sol

                # Verificar se clicou no botão de navegação esquerda
                if left_button_rect.collidepoint(mouse_pos):
                    if follow_planet is not None:  # Se já estamos seguindo um planeta
                        current_planet_index = (current_planet_index - 1) % len(planets)  # Volta para o planeta anterior
                        follow_planet = planets[current_planet_index]  # Atualiza o planeta a seguir
                        current_planet_name = follow_planet.name  # Atualiza o nome do planeta atual
                    else:
                        current_planet_index = (current_planet_index - 1) % len(planets)  # Volta para o último planeta
                        follow_planet = planets[current_planet_index]  # Atualiza o planeta a seguir
                        current_planet_name = follow_planet.name  # Atualiza o nome do planeta atual

                # Verificar se clicou no botão de navegação direita
                if right_button_rect.collidepoint(mouse_pos):
                    if follow_planet is not None:  # Se já estamos seguindo um planeta
                        current_planet_index = (current_planet_index + 1) % len(planets)  # Avança para o próximo planeta
                        follow_planet = planets[current_planet_index]  # Atualiza o planeta a seguir
                        current_planet_name = follow_planet.name  # Atualiza o nome do planeta atual
                    else:
                        current_planet_index = 0  # Se estamos centrados no Sol, inicia pelo primeiro planeta
                        follow_planet = planets[current_planet_index]  # Atualiza o planeta a seguir
                        current_planet_name = follow_planet.name  # Atualiza o nome do planeta atual

                # Verificar se clicou em algum planeta ou sol
                clicked_on_sun = is_clicked(mouse_pos, (400, 300), sun.radius)
                if clicked_on_sun:
                    follow_planet = None  # Retorna ao Sol
                    current_planet_name = sun.name  # Atualiza o nome do planeta atual
                else:
                    for planet in planets:
                        pos_x = int(400 + (planet.position[0] - (follow_planet.position[0] if follow_planet else 0)) * SCALE)
                        pos_y = int(300 + (planet.position[1] - (follow_planet.position[1] if follow_planet else 0)) * SCALE)
                        if is_clicked(mouse_pos, (pos_x, pos_y), planet.radius):
                            follow_planet = planet  # Segue o novo planeta
                            current_planet_index = planets.index(planet)  # Atualiza o índice do planeta atual
                            current_planet_name = planet.name  # Atualiza o nome do planeta atual

    screen.fill(COLORS["black"])
    
    # Desenha estrelas
    for star in stars:
        pygame.draw.circle(screen, COLORS["white"], star, 1)

    # Desenha planetas e suas órbitas
    for planet in planets:
        planet.update(dt, sun.mass)

        # Reposiciona os corpos celestes com base no planeta seguido
        offset_x = planet.position[0] - (follow_planet.position[0] if follow_planet else 0)
        offset_y = planet.position[1] - (follow_planet.position[1] if follow_planet else 0)

        pos_x = int(400 + offset_x * SCALE)
        pos_y = int(300 + offset_y * SCALE)

        # Desenha a órbita do planeta (centralizada no Sol)
        orbit_radius = np.linalg.norm(planet.position) * SCALE  # Raio da órbita
        orbit_center_x = 400 + (0 - (follow_planet.position[0] if follow_planet else 0)) * SCALE
        orbit_center_y = 300 + (0 - (follow_planet.position[1] if follow_planet else 0)) * SCALE
        pygame.draw.circle(screen, COLORS["white"], (int(orbit_center_x), int(orbit_center_y)), int(orbit_radius), 1)  # Círculo da órbita

        pygame.draw.circle(screen, planet.color, (pos_x, pos_y), planet.radius)

        # Desenha a trilha do planeta
        for pos in planet.trail:
            trail_x = int(400 + (pos[0] - (follow_planet.position[0] if follow_planet else 0)) * SCALE)
            trail_y = int(300 + (pos[1] - (follow_planet.position[1] if follow_planet else 0)) * SCALE)
            pygame.draw.circle(screen, planet.color, (trail_x, trail_y), 2)

        # Exibe o nome do planeta se necessário
        if show_names:
            text = font.render(planet.name, True, COLORS["white"])
            screen.blit(text, (pos_x - text.get_width() // 2, pos_y - planet.radius - 15))

    # Desenha o Sol
    sun_pos_x = int(400 - (follow_planet.position[0] if follow_planet else 0) * SCALE)
    sun_pos_y = int(300 - (follow_planet.position[1] if follow_planet else 0) * SCALE)
    pygame.draw.circle(screen, sun.color, (sun_pos_x, sun_pos_y), sun.radius)

    # Exibe o nome do Sol se necessário
    if sun.show_name:
        text = font.render(sun.name, True, COLORS["white"])
        screen.blit(text, (sun_pos_x - text.get_width() // 2, sun_pos_y - sun.radius - 15))

    # Desenha botão de mostrar nomes
    button_rect = draw_toggle_names_button()
   # Desenha o container de navegação, incluindo os botões e a caixa de texto
    left_button_rect, right_button_rect, container_rect = draw_navigation_container(current_planet_name)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()