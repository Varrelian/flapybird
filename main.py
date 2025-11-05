# flappy_enhanced.py
# Game Flappy Bird dengan detail visual dan animasi smooth
# Background: gradient kuning-oranye, Pipes: putih 3D, Bird: merah-biru dengan animasi
# Kontrol: spasi/klik mouse untuk melompat

import pygame
import sys
import random
import math

# --- Konfigurasi ---
WIDTH, HEIGHT = 400, 600
FPS = 60

GRAVITY = 0.5
JUMP_VEL = -9.0
PIPE_SPEED = 2.8
PIPE_GAP = 160
PIPE_WIDTH = 70
PIPE_FREQUENCY = 1400  # ms

BIRD_RADIUS = 16

# Warna (RGB)
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (255, 230, 150)
CLOUD_COLOR = (255, 255, 255, 180)
GROUND_DARK = (139, 90, 43)
GROUND_LIGHT = (160, 110, 65)
GRASS_COLOR = (34, 139, 34)
PIPE_BASE = (240, 240, 245)
PIPE_DARK = (200, 200, 210)
PIPE_HIGHLIGHT = (255, 255, 255)
RED = (235, 50, 50)
DARK_RED = (180, 30, 30)
BLUE = (50, 130, 235)
DARK_BLUE = (30, 90, 180)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
YELLOW = (255, 220, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Enhanced Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 42, bold=True)
small_font = pygame.font.SysFont('arial', 20)
tiny_font = pygame.font.SysFont('arial', 16)

# --- Fungsi Utilitas ---
def draw_text_with_shadow(text, x, y, surf, font_obj, color=WHITE, shadow_color=BLACK):
    """Gambar text dengan shadow untuk efek depth"""
    shadow = font_obj.render(text, True, shadow_color)
    shadow_rect = shadow.get_rect(center=(x+2, y+2))
    surf.blit(shadow, shadow_rect)

    img = font_obj.render(text, True, color)
    rect = img.get_rect(center=(x, y))
    surf.blit(img, rect)

def draw_gradient_rect(surface, color1, color2, rect):
    """Gambar rectangle dengan gradient vertical"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(surface, (r, g, b), 
                        (rect.x, rect.y + y), 
                        (rect.x + rect.width, rect.y + y))

# --- Kelas Cloud ---
class Cloud:
    def __init__(self, x, y, speed):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = random.randint(30, 60)

    def update(self):
        self.x -= self.speed
        if self.x + self.size < 0:
            self.x = WIDTH + self.size
            self.y = random.randint(50, 200)

    def draw(self, surf):
        # Gambar awan dengan beberapa circle
        alpha_surf = pygame.Surface((self.size * 2, self.size), pygame.SRCALPHA)
        pygame.draw.circle(alpha_surf, CLOUD_COLOR, (int(self.size * 0.5), int(self.size * 0.6)), int(self.size * 0.4))
        pygame.draw.circle(alpha_surf, CLOUD_COLOR, (int(self.size * 0.8), int(self.size * 0.7)), int(self.size * 0.35))
        pygame.draw.circle(alpha_surf, CLOUD_COLOR, (int(self.size * 1.1), int(self.size * 0.6)), int(self.size * 0.3))
        pygame.draw.circle(alpha_surf, CLOUD_COLOR, (int(self.size * 1.4), int(self.size * 0.65)), int(self.size * 0.28))
        surf.blit(alpha_surf, (int(self.x), int(self.y)))

# --- Kelas Bird ---
class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0.0
        self.alive = True
        self.rect = pygame.Rect(self.x - BIRD_RADIUS, self.y - BIRD_RADIUS, BIRD_RADIUS*2, BIRD_RADIUS*2)
        self.angle = 0.0
        self.wing_angle = 0.0
        self.wing_speed = 0.3
        self.animation_time = 0

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel

        # Smooth rotation based on velocity
        target_angle = max(-30, min(90, -self.vel * 5))
        self.angle += (target_angle - self.angle) * 0.2

        # Wing flapping animation
        if self.alive:
            self.wing_angle = math.sin(self.animation_time) * 30
            self.animation_time += self.wing_speed

        self.rect.center = (self.x, int(self.y))

        # Boundary checks
        if self.y - BIRD_RADIUS <= 0:
            self.y = BIRD_RADIUS
            self.vel = 0
        if self.y + BIRD_RADIUS >= HEIGHT - 50:
            self.y = HEIGHT - 50 - BIRD_RADIUS
            self.alive = False

    def jump(self):
        self.vel = JUMP_VEL
        self.wing_speed = 0.5

    def draw(self, surf):
        # Simpan posisi untuk rotasi
        bird_surf = pygame.Surface((BIRD_RADIUS*4, BIRD_RADIUS*4), pygame.SRCALPHA)
        center = (BIRD_RADIUS*2, BIRD_RADIUS*2)

        # Gambar bayangan
        shadow_offset = 3
        pygame.draw.circle(bird_surf, (0, 0, 0, 50), 
                          (center[0] + shadow_offset, center[1] + shadow_offset), 
                          BIRD_RADIUS)

        # Gambar badan (red) dengan highlight
        pygame.draw.circle(bird_surf, RED, center, BIRD_RADIUS)
        pygame.draw.circle(bird_surf, DARK_RED, center, BIRD_RADIUS, 2)

        # Highlight untuk efek 3D
        highlight_pos = (center[0] - BIRD_RADIUS//3, center[1] - BIRD_RADIUS//3)
        pygame.draw.circle(bird_surf, (255, 150, 150), highlight_pos, BIRD_RADIUS//3)

        # Gambar mata
        eye_x = center[0] + int(BIRD_RADIUS * 0.4)
        eye_y = center[1] - int(BIRD_RADIUS * 0.25)
        pygame.draw.circle(bird_surf, WHITE, (eye_x, eye_y), 6)
        pygame.draw.circle(bird_surf, BLACK, (eye_x + 1, eye_y), 4)
        pygame.draw.circle(bird_surf, WHITE, (eye_x + 2, eye_y - 1), 2)

        # Gambar paruh
        beak_points = [
            (center[0] + BIRD_RADIUS, center[1]),
            (center[0] + BIRD_RADIUS + 8, center[1] - 3),
            (center[0] + BIRD_RADIUS + 8, center[1] + 3)
        ]
        pygame.draw.polygon(bird_surf, YELLOW, beak_points)
        pygame.draw.polygon(bird_surf, (200, 170, 0), beak_points, 1)

        # Gambar sayap (blue) dengan animasi
        wing_offset = math.sin(math.radians(self.wing_angle)) * 5
        wing_points = [
            (center[0] - BIRD_RADIUS//4, center[1] + wing_offset),
            (center[0] - BIRD_RADIUS*1.2, center[1] + wing_offset - 5),
            (center[0] - BIRD_RADIUS*1.1, center[1] + BIRD_RADIUS*0.8 + wing_offset),
            (center[0] - BIRD_RADIUS//3, center[1] + BIRD_RADIUS*0.7 + wing_offset)
        ]
        pygame.draw.polygon(bird_surf, BLUE, wing_points)
        pygame.draw.polygon(bird_surf, DARK_BLUE, wing_points, 2)

        # Rotasi bird surface
        rotated = pygame.transform.rotate(bird_surf, self.angle)
        rotated_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, rotated_rect)

# --- Kelas Pipe ---
class Pipe:
    def __init__(self, x, gap_y):
        self.x = x
        self.gap_y = gap_y
        self.passed = False
        self.highlight_time = 0

    def update(self):
        self.x -= PIPE_SPEED
        if self.highlight_time > 0:
            self.highlight_time -= 1

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird):
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y - PIPE_GAP//2)
        bot_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP//2, PIPE_WIDTH, HEIGHT - (self.gap_y + PIPE_GAP//2))

        # Circle-rect collision untuk akurasi lebih baik
        def circle_rect_collision(cx, cy, radius, rect):
            closest_x = max(rect.left, min(cx, rect.right))
            closest_y = max(rect.top, min(cy, rect.bottom))
            dist = math.sqrt((cx - closest_x)**2 + (cy - closest_y)**2)
            return dist < radius

        return (circle_rect_collision(bird.x, bird.y, BIRD_RADIUS-2, top_rect) or 
                circle_rect_collision(bird.x, bird.y, BIRD_RADIUS-2, bot_rect))

    def draw(self, surf):
        top_h = self.gap_y - PIPE_GAP//2
        cap_h = 24
        cap_extra = 4

        # Pipe atas
        # Body
        body_rect = pygame.Rect(int(self.x), 0, PIPE_WIDTH, int(top_h - cap_h))
        pygame.draw.rect(surf, PIPE_BASE, body_rect)
        # 3D effect - sisi kiri lebih gelap
        pygame.draw.rect(surf, PIPE_DARK, (self.x, 0, 8, top_h - cap_h))
        # Highlight sisi kanan
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (self.x + PIPE_WIDTH - 4, 0, 4, top_h - cap_h))
        # Garis vertikal untuk detail
        for i in range(3):
            x_line = self.x + PIPE_WIDTH//4 * (i+1)
            pygame.draw.line(surf, PIPE_DARK, (x_line, 0), (x_line, top_h - cap_h), 1)

        # Cap atas
        cap_rect = pygame.Rect(int(self.x - cap_extra), int(top_h - cap_h), PIPE_WIDTH + cap_extra*2, cap_h)
        pygame.draw.rect(surf, PIPE_BASE, cap_rect)
        pygame.draw.rect(surf, PIPE_DARK, (self.x - cap_extra, top_h - cap_h, 8, cap_h))
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (self.x + PIPE_WIDTH + cap_extra - 4, top_h - cap_h, 4, cap_h))
        pygame.draw.rect(surf, PIPE_DARK, cap_rect, 2)

        # Pipe bawah
        bot_y = self.gap_y + PIPE_GAP//2
        # Cap bawah
        cap_rect_bot = pygame.Rect(int(self.x - cap_extra), int(bot_y), PIPE_WIDTH + cap_extra*2, cap_h)
        pygame.draw.rect(surf, PIPE_BASE, cap_rect_bot)
        pygame.draw.rect(surf, PIPE_DARK, (self.x - cap_extra, bot_y, 8, cap_h))
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (self.x + PIPE_WIDTH + cap_extra - 4, bot_y, 4, cap_h))
        pygame.draw.rect(surf, PIPE_DARK, cap_rect_bot, 2)

        # Body bawah
        body_bot_rect = pygame.Rect(int(self.x), int(bot_y + cap_h), PIPE_WIDTH, int(HEIGHT - (bot_y + cap_h)))
        pygame.draw.rect(surf, PIPE_BASE, body_bot_rect)
        pygame.draw.rect(surf, PIPE_DARK, (self.x, bot_y + cap_h, 8, HEIGHT - (bot_y + cap_h)))
        pygame.draw.rect(surf, PIPE_HIGHLIGHT, (self.x + PIPE_WIDTH - 4, bot_y + cap_h, 4, HEIGHT - (bot_y + cap_h)))
        for i in range(3):
            x_line = self.x + PIPE_WIDTH//4 * (i+1)
            pygame.draw.line(surf, PIPE_DARK, (x_line, bot_y + cap_h), (x_line, HEIGHT), 1)

        # Highlight effect saat melewati pipe
        if self.highlight_time > 0:
            alpha = int(self.highlight_time * 5)
            highlight_surf = pygame.Surface((PIPE_WIDTH + cap_extra*2, HEIGHT), pygame.SRCALPHA)
            highlight_surf.fill((255, 255, 255, alpha))
            surf.blit(highlight_surf, (self.x - cap_extra, 0))

# --- Kelas Particle untuk efek ---
class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1)
        self.life = 30
        self.color = random.choice([RED, BLUE, YELLOW, WHITE])
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1

    def draw(self, surf):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            particle_surf = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*self.color, alpha), (self.size, self.size), self.size)
            surf.blit(particle_surf, (int(self.x - self.size), int(self.y - self.size)))

# --- Main Game ---
def main():
    bird = Bird(90, HEIGHT // 2)
    pipes = []
    clouds = [Cloud(random.randint(0, WIDTH), random.randint(50, 200), random.uniform(0.3, 0.8)) for _ in range(5)]
    particles = []
    score = 0
    high_score = 0
    running = True
    paused = False
    game_started = False

    SPAWNPIPE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWNPIPE, PIPE_FREQUENCY)

    # Animasi ground
    ground_x = 0

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not game_started:
                        game_started = True
                    if bird.alive:
                        bird.jump()
                        # Spawn particles saat jump
                        for _ in range(5):
                            particles.append(Particle(bird.x, bird.y))
                    else:
                        # Restart
                        bird = Bird(90, HEIGHT // 2)
                        pipes.clear()
                        particles.clear()
                        if score > high_score:
                            high_score = score
                        score = 0
                        game_started = False

                if event.key == pygame.K_p and bird.alive:
                    paused = not paused

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not game_started:
                    game_started = True
                if bird.alive:
                    bird.jump()
                    for _ in range(5):
                        particles.append(Particle(bird.x, bird.y))
                else:
                    bird = Bird(90, HEIGHT // 2)
                    pipes.clear()
                    particles.clear()
                    if score > high_score:
                        high_score = score
                    score = 0
                    game_started = False

            if event.type == SPAWNPIPE and bird.alive and not paused and game_started:
                gap_y = random.randint(PIPE_GAP//2 + 60, HEIGHT - PIPE_GAP//2 - 110)
                pipes.append(Pipe(WIDTH + 10, gap_y))

        if not paused and game_started:
            if bird.alive:
                bird.update()

            # Update clouds
            for cloud in clouds:
                cloud.update()

            # Update pipes
            for p in pipes:
                p.update()
                if not p.passed and p.x + PIPE_WIDTH < bird.x:
                    p.passed = True
                    p.highlight_time = 20
                    score += 1
                    # Spawn particles saat score
                    for _ in range(10):
                        particles.append(Particle(bird.x, bird.y))

            # Collision check
            for p in pipes:
                if p.collides_with(bird):
                    bird.alive = False
                    # Spawn banyak particles saat mati
                    for _ in range(30):
                        particles.append(Particle(bird.x, bird.y))
                    break

            # Remove off-screen pipes
            pipes = [p for p in pipes if not p.off_screen()]

            # Update particles
            for particle in particles:
                particle.update()
            particles = [p for p in particles if p.life > 0]

            # Animate ground
            ground_x -= PIPE_SPEED
            if ground_x <= -40:
                ground_x = 0

        # --- Drawing ---
        # Background gradient
        draw_gradient_rect(screen, SKY_TOP, SKY_BOTTOM, pygame.Rect(0, 0, WIDTH, HEIGHT - 50))

        # Clouds
        for cloud in clouds:
            cloud.draw(screen)

        # Pipes
        for p in pipes:
            p.draw(screen)

        # Particles
        for particle in particles:
            particle.draw(screen)

        # Bird
        bird.draw(screen)

        # Ground dengan pattern
        ground_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
        draw_gradient_rect(screen, GROUND_LIGHT, GROUND_DARK, ground_rect)

        # Ground pattern
        for i in range(int(WIDTH / 40) + 2):
            x = int(ground_x + i * 40)
            pygame.draw.rect(screen, GRASS_COLOR, (x, HEIGHT - 50, 35, 4))
            pygame.draw.line(screen, GROUND_DARK, (x, HEIGHT - 50), (x, HEIGHT), 2)

        # HUD
        draw_text_with_shadow(str(score), WIDTH//2, 50, screen, font, WHITE, BLACK)

        if high_score > 0:
            draw_text_with_shadow(f"Best: {high_score}", WIDTH//2, 95, screen, small_font, (255, 215, 0), BLACK)

        if not game_started:
            draw_text_with_shadow("KLIK / SPASI UNTUK MULAI", WIDTH//2, HEIGHT//2 - 50, screen, small_font, WHITE, BLACK)
            draw_text_with_shadow("Terbang Setinggi Langit!", WIDTH//2, HEIGHT//2, screen, tiny_font, YELLOW, BLACK)

        if paused:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            draw_text_with_shadow("PAUSE", WIDTH//2, HEIGHT//2 - 30, screen, font, WHITE, BLACK)
            draw_text_with_shadow("Tekan P untuk lanjut", WIDTH//2, HEIGHT//2 + 20, screen, small_font, WHITE, BLACK)

        if not bird.alive and game_started:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            draw_text_with_shadow("GAME OVER", WIDTH//2, HEIGHT//2 - 50, screen, font, RED, BLACK)
            draw_text_with_shadow(f"Score: {score}", WIDTH//2, HEIGHT//2, screen, small_font, WHITE, BLACK)
            draw_text_with_shadow("KLIK / SPASI UNTUK COBA LAGI", WIDTH//2, HEIGHT//2 + 50, screen, tiny_font, YELLOW, BLACK)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
