import pygame
import random
import serial
import serial.tools.list_ports

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

# Joystick thresholds — tuned to your readings
# X axis: neutral ~2048, tune if yours differs
# Y axis: neutral ~2880, max 4095
JOY_LEFT    = 1000   # X below this = move left
JOY_RIGHT   = 3000   # X above this = move right
JOY_DEADZONE_LOW  = 1500   # Y below this = speed up
JOY_DEADZONE_HIGH = 3500   # Y above this = slow down

# Lane switch debounce — only switches once per push
lane_switched = False
speed = 8
running = True

while running:
    clock.tick(60)

    joy_x = 2048
    joy_y = 2880  # your neutral

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
    # Only switch when joystick is pushed AND hasn't switched yet
    # Reset lane_switched only when joystick returns to center
    if joy_x < JOY_LEFT:
        if not lane_switched:
            current_lane = max(0, current_lane - 1)
            lane_switched = True
    elif joy_x > JOY_RIGHT:
        if not lane_switched:
            current_lane = min(2, current_lane + 1)
            lane_switched = True
    else:
        # Joystick back to center — ready for next switch
        lane_switched = False

    # --- Speed control from Y axis ---
    # Your joystick: neutral ~2880, pushed forward goes lower, pulled back goes to 4095
    if joy_y < JOY_DEADZONE_LOW:
        speed = 14   # pushed forward
    elif joy_y > JOY_DEADZONE_HIGH:
        speed = 4    # pulled back
    else:
        speed = 8    # neutral

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

    # --- Draw ---
    screen.fill((20, 20, 20))
    pygame.draw.rect(screen, (60, 60, 60), (80, 0, 340, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(screen, (255, 255, 255), (190, y, 8, 20))
        pygame.draw.rect(screen, (255, 255, 255), (290, y, 8, 20))

    car_x = lanes[current_lane] - car_width // 2

    spawn_timer += 1
    if spawn_timer > 45:
        lc = random.choice(lanes)
        obstacles.append([lc - car_width // 2, -100])
        spawn_timer = 0

    for o in obstacles:
        o[1] += speed
    obstacles = [o for o in obstacles if o[1] < HEIGHT + 100]

    for o in obstacles:
        pygame.draw.rect(screen, (255, 0, 0), (o[0], o[1], car_width, car_height))

    pygame.draw.rect(screen, (0, 255, 255), (car_x, car_y, car_width, car_height))

    # --- Collision ---
    player_rect = pygame.Rect(car_x, car_y, car_width, car_height)
    hit = False
    for o in obstacles:
        if player_rect.colliderect(pygame.Rect(o[0], o[1], car_width, car_height)):
            hit = True
            break

    if hit:
        # Tell ESP32 to buzz
        ser.write(b'BUZZ\n')

        # Game over screen
        screen.blit(font.render("GAME OVER", True, (255, 255, 255)), (140, 300))
        screen.blit(font.render(f"Score: {int(score)}", True, (255, 255, 255)), (160, 350))
        pygame.display.update()
        pygame.time.delay(3000)
        running = False

    score += speed * 0.01
    screen.blit(font.render(f"Score: {int(score)}", True, (255, 255, 255)), (20, 20))
    screen.blit(font.render(f"Speed: {speed}", True, (200, 200, 200)), (20, 55))
    screen.blit(font.render(f"X:{joy_x} Y:{joy_y}", True, (150, 150, 150)), (20, 90))

    pygame.display.update()

ser.close()
pygame.quit()
