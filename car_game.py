import pygame
import random
import serial
import serial.tools.list_ports
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def find_esp32_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "CP210" in p.description or "CH340" in p.description or "USB" in p.description:
            return p.device
    return None

port = find_esp32_port()
if port is None:
    print("ESP32 not found!")
    exit()

ser = serial.Serial(port, 115200, timeout=0.02)
print(f"Connected to {port}")

pygame.init()
WIDTH, HEIGHT = 500, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Endless Car Runner")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 40)

lanes = [125, 225, 325]
current_lane = 1
car_width, car_height = 50, 90
car_y = HEIGHT - 120
score = 0
spawn_timer = 0
obstacles = []

# Joystick thresholds
JOY_LEFT          = 1000
JOY_RIGHT         = 3000
JOY_DEADZONE_LOW  = 1500
JOY_DEADZONE_HIGH = 3500

lane_switched = False
speed = 8

# --- Load images ---
player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (car_width, car_height))

enemy_imgs = []
for i in range(1, 13):
    img = pygame.image.load(f"enemy{i}.png").convert_alpha()
    img = pygame.transform.scale(img, (car_width, car_height))
    enemy_imgs.append(img)

running = True

while running:
    clock.tick(60)

    joy_x = 2048
    joy_y = 2880

    try:
        if ser.in_waiting:
            line = ser.readline().decode("utf-8").strip()
            parts = line.split(",")
            if len(parts) == 2:
                joy_x = int(parts[0])
                joy_y = int(parts[1])
    except:
        pass

    # --- Lane control ---
    if joy_x < JOY_LEFT:
        if not lane_switched:
            current_lane = max(0, current_lane - 1)
            lane_switched = True
    elif joy_x > JOY_RIGHT:
        if not lane_switched:
            current_lane = min(2, current_lane + 1)
            lane_switched = True
    else:
        lane_switched = False

    # --- Speed control ---
    if joy_y < JOY_DEADZONE_LOW:
        speed = 14
    elif joy_y > JOY_DEADZONE_HIGH:
        speed = 4
    else:
        speed = 8

    # --- Keyboard fallback ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                current_lane = max(0, current_lane - 1)
            if event.key == pygame.K_RIGHT:
                current_lane = min(2, current_lane + 1)
            if event.key == pygame.K_UP:
                speed = 14
            if event.key == pygame.K_DOWN:
                speed = 4

    # --- Draw background ---
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (60, 60, 60), (80, 0, 340, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, (255, 255, 255), (190, y, 8, 20))
        pygame.draw.rect(screen, (255, 255, 255), (290, y, 8, 20))

    car_x = lanes[current_lane] - car_width // 2

    # --- Spawn obstacles ---
    spawn_timer += 1
    if spawn_timer > 45:
        lc = random.choice(lanes)
        img_index = random.randint(0, len(enemy_imgs) - 1)
        obstacles.append([lc - car_width // 2, -100, img_index])
        spawn_timer = 0

    # --- Move obstacles ---
    for o in obstacles:
        o[1] += speed
    obstacles = [o for o in obstacles if o[1] < HEIGHT + 100]

    # --- Draw obstacles ---
    for o in obstacles:
        screen.blit(enemy_imgs[o[2]], (o[0], o[1]))

    # --- Draw player ---
    screen.blit(player_img, (car_x, car_y))

    # --- Collision ---
    player_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    hit = False
    for o in obstacles:
        if player_rect.colliderect(pygame.Rect(o[0], o[1], car_width, car_height)):
            hit = True
            break

    if hit:
        ser.write(b'BUZZ\n')
        screen.blit(font.render("GAME OVER", True, (255, 255, 255)), (140, 300))
        screen.blit(font.render(f"Final Score: {int(score)}", True, (255, 255, 255)), (120, 350))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    # --- HUD ---
    score += speed * 0.01
    screen.blit(font.render(f"Score: {int(score)}", True, (255, 255, 255)), (20, 20))
    screen.blit(font.render(f"Speed: {speed}", True, (200, 200, 200)), (20, 55))
    screen.blit(font.render(f"X:{joy_x} Y:{joy_y}", True, (150, 150, 150)), (20, 90))

    pygame.display.update()

ser.close()
pygame.quit()
