import pygame
import sys
import random
import os
import pygame.mixer


# pygame.mixer.init()
pygame.mixer.pre_init(buffer=512)
pygame.init()


def moving_floor():
    global floor_x_pos
    screen.blit(floor_surface, (floor_x_pos, 600))
    screen.blit(floor_surface, (floor_x_pos + 400, 600))
    if floor_x_pos == -400:
        floor_x_pos = 0


def create_pipe():
    pipe_height = random.choice([350, 400, 500])
    num_pipes = random.choice([1, 2])
    pipe_x_pos = 450
    if num_pipes == 1:
        bottom_pipe = pipe_surface.get_rect(midtop=(pipe_x_pos, pipe_height))
        top_pipe = pipe_surface.get_rect(midbottom=(pipe_x_pos, pipe_height - 200))
        return bottom_pipe, top_pipe
    elif num_pipes == 2:
        bottom_pipe = pipe_surface.get_rect(midtop=(pipe_x_pos, pipe_height))
        bottom_pipe1 = pipe_surface.get_rect(midtop=(pipe_x_pos + bottom_pipe.width, pipe_height))
        top_pipe = pipe_surface.get_rect(midbottom=(pipe_x_pos, pipe_height - 200))
        top_pipe1 = pipe_surface.get_rect(midbottom=(pipe_x_pos + top_pipe.width, pipe_height - 200))
        return bottom_pipe, top_pipe, bottom_pipe1, top_pipe1


def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx -= 9
    return pipes


def draw_pipes(pipes):
    for pipe in pipes:
        if pipe.bottom >= 700:
            screen.blit(pipe_surface, pipe)
        else:
            flip_surface = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_surface, pipe)


def check_collision(pipes):
    for pipe in pipes:
        if bird_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if bird_rect.top <= 0 or bird_rect.bottom >= 600:
        hit_sound.play()
        return False
    return True


def rot_bird(surface):
    new_bird = pygame.transform.rotozoom(surface, -bird_movement * 7, 1)
    return new_bird


def bird_animation():
    new_bird = bird_frames[bird_index]
    new_bird_rect = new_bird.get_rect(center=(100, bird_rect.centery))
    return new_bird, new_bird_rect


def score_display(game_state):
    if game_state == "main_game":
        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(200, 50))
        screen.blit(score_text, score_rect)
    if game_state == "game_over":
        high_score_text = font.render(f'High Score: {high_score}', True, (255, 255, 255))
        score_rect = high_score_text.get_rect(center=(200, 550))
        screen.blit(high_score_text, score_rect)


def score_update(bird_ret, pipes):
    for pipe in pipes:
        if bird_ret.centerx in range(pipe.centerx, (pipe.centerx - 15), -1):
            if not bird_ret.colliderect(pipe):
                point_sound.play()
                return 10
    return 0


def high_score_check(_score, _high_score):
    if _score > _high_score:
        _high_score = _score
        with open("high_score.txt", "w") as _f:
            _f.write(f"{_high_score}")
    return _high_score


# game variables
floor_x_pos = 0
gravity = 0.20
bird_movement = 0
game_active = False
score = 0

# game sounds
flap_sound = pygame.mixer.Sound("sound/sfx_wing.wav")
point_sound = pygame.mixer.Sound("sound/sfx_point.wav")
hit_sound = pygame.mixer.Sound("sound/sfx_hit.wav")

if os.path.exists("high_score.txt"):
    with open("high_score.txt", "r") as f:
        high_score = int(f.read())
else:
    with open("high_score.txt", "w") as f:
        f.write("0")
        high_score = 0

# timer

SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 600)

BIRDFLAP = pygame.USEREVENT + 1
pygame.time.set_timer(BIRDFLAP, 200)

# game screen
screen = pygame.display.set_mode((400, 700))
pygame.display.set_caption("Flappy Bird")
bg_surface = pygame.image.load("assets/background-day.png").convert()
bg_surface = pygame.transform.scale(bg_surface, (400, 700))

# static screen
stat_screen = pygame.image.load("assets/message.png").convert_alpha()
stat_screen = pygame.transform.scale(stat_screen, (250, 300))
stat_rect = stat_screen.get_rect(center=(200, 350))

font = pygame.font.Font("04B_19.ttf", 30)

# floor
floor_surface = pygame.image.load("assets/base.png").convert()
floor_surface = pygame.transform.scale(floor_surface, (400, 100))

# bird
bird_downflap = pygame.transform.scale(pygame.image.load("assets/bluebird-downflap.png").convert_alpha(), (40, 30))
bird_midflap = pygame.transform.scale(pygame.image.load("assets/bluebird-midflap.png").convert_alpha(), (40, 30))
bird_upflap = pygame.transform.scale(pygame.image.load("assets/bluebird-upflap.png").convert_alpha(), (40, 30))
bird_frames = [bird_downflap, bird_midflap, bird_upflap]
bird_index = 0
bird_surface = bird_frames[bird_index]
bird_rect = bird_surface.get_rect(center=(100, 300))

# pipe
pipe_surface = pygame.image.load("assets/pipe-green.png").convert()
pipe_surface = pygame.transform.scale(pipe_surface, (70, 450))
pipe_lst = []

# Clock
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -4
                flap_sound.play()
            if event.key == pygame.K_SPACE and not game_active:
                game_active = True
                pipe_lst.clear()
                bird_rect.centery = 300
                bird_movement = 0
                score = 0
        if event.type == SPAWNPIPE:
            pipe_lst.extend(create_pipe())

        if event.type == BIRDFLAP:
            if bird_index < 2:
                bird_index += 1
            else:
                bird_index = 0
            bird_surface, bird_rect = bird_animation()

    screen.blit(bg_surface, (0, 0))

    if game_active:
        # pipes logic
        pipe_lst = move_pipes(pipe_lst)
        draw_pipes(pipe_lst)

        # collision logic
        game_active = check_collision(pipe_lst)

        # bird logic
        bird_movement += gravity
        rotating_bird = rot_bird(bird_surface)
        bird_rect.centery += bird_movement
        screen.blit(rotating_bird, bird_rect)

        score += score_update(bird_rect, pipe_lst)
        score_display("main_game")
    else:
        screen.blit(stat_screen, stat_rect)
        score_display("main_game")
        high_score = high_score_check(score, high_score)
        score_display("game_over")

    # floor logic
    floor_x_pos -= 4
    moving_floor()

    pygame.display.update()
    clock.tick(60)
