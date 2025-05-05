import pygame
import random
import time

# Initialize pygame
pygame.init()

# Set game window size
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Game with Emojis")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_RED = (30, 0, 0)

# Font settings
font = pygame.font.SysFont('Arial', 30)
emoji_font = pygame.font.SysFont('Segoe UI Emoji', 40)

# Player settings
player_width = 50
player_height = 50
player_x = WIDTH // 2
player_y = HEIGHT - player_height - 10
player_speed = 5
player_health = 3
shield_active = False
shield_duration = 0
teleport_ready = True
teleport_duration = 300

# Bullet settings
bullet_width = 5
bullet_height = 10
bullet_speed = 7
bullets = []
piercing_bullets = []

# Zombie settings
zombie_width = 50
zombie_height = 50
zombie_speed = 3
zombies = []
exploding_zombies = []
ranged_zombies = []

# Boss settings
boss_width = 100
boss_height = 100
boss_speed = 2
boss = None

# Power-up settings
power_up_width = 30
power_up_height = 30
power_ups = []

# Score and level
score = 0
level = 1

# Game clock
clock = pygame.time.Clock()

def move_player(keys):
    global player_x, player_y
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WIDTH - player_width:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < HEIGHT - player_height:
        player_y += player_speed

def move_bullets():
    global bullets, piercing_bullets
    for bullet in bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            bullets.remove(bullet)
    for bullet in piercing_bullets[:]:
        bullet[1] -= bullet_speed
        if bullet[1] < 0:
            piercing_bullets.remove(bullet)

def move_zombies():
    global zombies, exploding_zombies, ranged_zombies, boss
    for zombie in zombies[:]:
        if zombie[0] < player_x:
            zombie[0] += random.randint(0, zombie_speed)
        elif zombie[0] > player_x:
            zombie[0] -= random.randint(0, zombie_speed)
        if zombie[1] < player_y:
            zombie[1] += zombie_speed
        elif zombie[1] > player_y:
            zombie[1] -= zombie_speed
        zombie[0] += random.choice([-1, 0, 1])
        zombie[1] += random.choice([-1, 0, 1])
    for ezombie in exploding_zombies[:]:
        if ezombie[0] < player_x:
            ezombie[0] += random.randint(0, zombie_speed)
        elif ezombie[0] > player_x:
            ezombie[0] -= random.randint(0, zombie_speed)
        if ezombie[1] < player_y:
            ezombie[1] += zombie_speed
        elif ezombie[1] > player_y:
            ezombie[1] -= random.randint(0, zombie_speed)
        if abs(player_x - ezombie[0]) < 50 and abs(player_y - ezombie[1]) < 50:
            exploding_zombies.remove(ezombie)
            if not shield_active:
                global player_health
                player_health -= 1
    for rzombie in ranged_zombies[:]:
        if rzombie[0] < player_x:
            rzombie[0] += random.randint(0, zombie_speed)
        elif rzombie[0] > player_x:
            rzombie[0] -= random.randint(0, zombie_speed)
        if rzombie[1] < player_y:
            rzombie[1] += zombie_speed
        elif rzombie[1] > player_y:
            rzombie[1] -= random.randint(0, zombie_speed)
    if boss:
        if boss[0] < player_x:
            boss[0] += random.randint(0, boss_speed)
        elif boss[0] > player_x:
            boss[0] -= random.randint(0, boss_speed)
        if boss[1] < player_y:
            boss[1] += boss_speed
        elif boss[1] > player_y:
            boss[1] -= boss_speed
        boss[0] += random.choice([-1, 0, 1])
        boss[1] += random.choice([-1, 0, 1])

def check_collisions():
    global player_health, zombies, bullets, score, power_ups, piercing_bullets, boss, exploding_zombies
    for zombie in zombies[:]:
        if player_x < zombie[0] + zombie_width and player_x + player_width > zombie[0] and player_y < zombie[1] + zombie_height and player_y + player_height > zombie[1]:
            if not shield_active:
                player_health -= 1
            zombies.remove(zombie)
        for bullet in bullets[:]:
            if bullet[0] < zombie[0] + zombie_width and bullet[0] + bullet_width > zombie[0] and bullet[1] < zombie[1] + zombie_height and bullet[1] + bullet_height > zombie[1]:
                zombies.remove(zombie)
                bullets.remove(bullet)
                score += 1
                break
        for bullet in piercing_bullets[:]:
            if bullet[0] < zombie[0] + zombie_width and bullet[0] + bullet_width > zombie[0] and bullet[1] < zombie[1] + zombie_height and bullet[1] + bullet_height > zombie[1]:
                zombies.remove(zombie)
                score += 1
                break
    for ezombie in exploding_zombies[:]:
        for bullet in bullets[:]:
            if bullet[0] < ezombie[0] + zombie_width and bullet[0] + bullet_width > ezombie[0] and bullet[1] < ezombie[1] + zombie_height and bullet[1] + bullet_height > ezombie[1]:
                exploding_zombies.remove(ezombie)
                bullets.remove(bullet)
                score += 1
    for power_up in power_ups[:]:
        if player_x < power_up[0] + power_up_width and player_x + player_width > power_up[0] and player_y < power_up[1] + power_up_height and player_y + player_height > power_up[1]:
            power_ups.remove(power_up)
            apply_power_up()
    if boss:
        for bullet in bullets[:]:
            if bullet[0] < boss[0] + boss_width and bullet[0] + bullet_width > boss[0] and bullet[1] < boss[1] + boss_height and bullet[1] + bullet_height > boss[1]:
                boss = None
                score += 10

def apply_power_up():
    global player_health, bullet_speed, shield_active, shield_duration
    power_up_type = random.choice(['health', 'speed', 'shield'])
    if power_up_type == 'health':
        player_health = min(player_health + 1, 5)
    elif power_up_type == 'speed':
        bullet_speed = min(bullet_speed + 2, 15)
    elif power_up_type == 'shield':
        shield_active = True
        shield_duration = 500

def teleport_player():
    global player_x, player_y
    player_x = random.randint(0, WIDTH - player_width)
    player_y = random.randint(0, HEIGHT - player_height)

def draw_game():
    screen.fill(DARK_RED)  # Horror background
    screen.blit(emoji_font.render("🦇", True, WHITE), (player_x, player_y))
    for bullet in bullets:
        pygame.draw.rect(screen, WHITE, (bullet[0], bullet[1], bullet_width, bullet_height))
    for bullet in piercing_bullets:
        pygame.draw.rect(screen, (0, 255, 255), (bullet[0], bullet[1], bullet_width, bullet_height))
    for zombie in zombies:
        screen.blit(emoji_font.render("🧟", True, WHITE), (zombie[0], zombie[1]))
    for ezombie in exploding_zombies:
        screen.blit(emoji_font.render("💥", True, WHITE), (ezombie[0], ezombie[1]))
    for rzombie in ranged_zombies:
        screen.blit(emoji_font.render("🎯", True, WHITE), (rzombie[0], rzombie[1]))
    if boss:
        screen.blit(emoji_font.render("👹", True, WHITE), (boss[0], boss[1]))
    for power_up in power_ups:
        pygame.draw.rect(screen, (255, 255, 0), (power_up[0], power_up[1], power_up_width, power_up_height))
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Health: {player_health}", True, WHITE), (10, 40))
    if shield_active:
        screen.blit(font.render("Shield: Active", True, WHITE), (10, 70))
    pygame.display.update()

def game_loop():
    global score, level, player_health, shield_active, teleport_ready, teleport_duration, shield_duration
    running = True
    while running:
        pygame.time.delay(20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
                if event.key == pygame.K_t and teleport_ready:
                    teleport_player()
                    teleport_ready = False
                    teleport_duration = 300
        keys = pygame.key.get_pressed()
        move_player(keys)
        move_bullets()
        move_zombies()
        check_collisions()
        if teleport_ready is False:
            teleport_duration -= 1
            if teleport_duration <= 0:
                teleport_ready = True
        if shield_active:
            shield_duration -= 1
            if shield_duration <= 0:
                shield_active = False
        if random.random() < 0.02:
            zombies.append([random.randint(0, WIDTH - zombie_width), 0])
        if random.random() < 0.01:
            power_ups.append([random.randint(0, WIDTH - power_up_width), random.randint(0, HEIGHT - power_up_height)])
        if score > level * 10:
            level += 1
        draw_game()
        if player_health <= 0:
            screen.fill(BLACK)
            game_over_text = font.render("Game Over! Press any key to exit.", True, WHITE)
            screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2))
            pygame.display.update()
            wait_for_key()
            running = False
    pygame.quit()

def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                waiting = False

game_loop()
