import pygame
import random
import webbrowser

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 936

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

#define font
font = pygame.font.SysFont('Bauhaus 93', 60)

#define colours
white = (255, 255, 255)

#define game variables
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
last_score_sound = 0
pass_pipe = False

# load images
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

# Inicializar el mezclador de sonido de Pygame
pygame.mixer.init()

# Cargar sonidos
wing_sound = pygame.mixer.Sound('audio/wing.wav')  # Elevación
hit_sound = pygame.mixer.Sound('audio/hit.wav')  # Muerte
point_sound = pygame.mixer.Sound('audio/point.wav')  # Puntos
swoosh_sound = pygame.mixer.Sound('audio/swoosh.wav')  # Fin del juego
die_sound = pygame.mixer.Sound('audio/die.wav')  # Reinicio del juego
yupi_sound = pygame.mixer.Sound('audio/yupi.mp3')  # Nuevo sonido "yupi"

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    last_score_sound = 0
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f"img/roca{num}.png")
            img = pygame.transform.scale(img, (51, 36))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global flying
        if flying == True:
            # apply gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
                # Reproducir sonido de elevación
                wing_sound.play()
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # handle the animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
                self.image = self.images[self.index]

            # rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            # point the bird at the ground
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

hit_sound_played = False
die_sound_played = False

# Definir las combinaciones secretas
konami_code = ['a', 'f', 'r', 'i', 'c', 'a', 'n', 'o']
baki_code = ['b', 'a', 'k', 'i']
fuerza_code = ['f', 'u', 'e', 'r', 'z', 'a']
current_input = []

run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()
    screen.blit(ground_img, (ground_scroll, 768))

    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
                point_sound.play()

                # Reproducir sonido "yupi" si la puntuación es múltiplo de 5 y no ha sonado recientemente
                if score % 5 == 0 and pygame.time.get_ticks() - last_score_sound > 1000:
                    yupi_sound.play()
                    last_score_sound = pygame.time.get_ticks()

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    if not hit_sound_played and (pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0):
        game_over = True
        hit_sound.play()
        hit_sound_played = True

    if not die_sound_played and flappy.rect.bottom >= 768:
        game_over = True
        flying = False
        die_sound.play()
        die_sound_played = True

    if flying == True and game_over == False:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        pipe_group.update()
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    if game_over == True:
        if button.draw():
            swoosh_sound.play()
            game_over = False
            hit_sound_played = False
            die_sound_played = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key).lower()
            current_input.append(key)

            if current_input[-len(konami_code):] == konami_code:
                webbrowser.open("https://www.youtube.com/watch?v=tMNbBKZsm2w")
                current_input = []
            elif current_input[-len(baki_code):] == baki_code:
                webbrowser.open("https://www.youtube.com/watch?v=jzBr7dBUBf0")
                current_input = []
            elif current_input[-len(fuerza_code):] == fuerza_code:
                webbrowser.open("https://youtu.be/4LGw6G1kWn0?si=OlkR0c3dkRtpGoML")
                current_input = []

    pygame.display.update()

pygame.quit()
