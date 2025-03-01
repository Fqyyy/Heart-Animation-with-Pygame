import pygame, math, random, sys

pygame.init()
W, H = pygame.display.Info().current_w, pygame.display.Info().current_h
screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
clock = pygame.time.Clock()

ctr = pygame.Vector2(W / 2, H / 2)

def draw_heart(s, x, y, size):
    heart_points = [
        (x, y - size),
        (x - size, y),
        (x, y + size),
        (x + size, y),
    ]
    pygame.draw.polygon(s, (255, 0, 0), heart_points)
    pygame.draw.circle(s, (255, 0, 0), (x - size // 2, y - size // 2), size // 2)
    pygame.draw.circle(s, (255, 0, 0), (x + size // 2, y - size // 2), size // 2)

class Rocket:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-9, -7)
        self.exploded = False

    def update(self):
        self.vy += 0.07
        self.x += self.vx
        self.y += self.vy
        if self.vy >= 0 or self.y < H / 2:
            self.exploded = True

    def draw(self, s):
        pygame.draw.circle(s, (255, 255, 255), (int(self.x), int(self.y)), 3)

class FireworkParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 6)
        self.vx, self.vy = speed * math.cos(angle), speed * math.sin(angle)
        self.life = random.randint(40, 80)
        self.age = 0
        self.col = (random.randint(200, 255), random.randint(50, 100), random.randint(50, 100))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05
        self.age += 1
        return self.age < self.life

    def draw(self, s):
        pygame.draw.circle(s, self.col, (int(self.x), int(self.y)), 4)

def gen_outline(n=100):
    pts = []
    for i in range(n):
        t = math.pi - (i / n) * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append(pygame.Vector2(x * 15, -y * 15) + ctr)
    return pts

def in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    p1 = poly[0]
    for i in range(1, n + 1):
        p2 = poly[i % n]
        if y > min(p1.y, p2.y) and y <= max(p1.y, p2.y) and x <= max(p1.x, p2.x):
            xinters = (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y + 1e-9) + p1.x
            if x <= xinters:
                inside = not inside
        p1 = p2
    return inside

def gen_filled(n, outline):
    min_x = min(p.x for p in outline)
    max_x = max(p.x for p in outline)
    min_y = min(p.y for p in outline)
    max_y = max(p.y for p in outline)
    pts = []
    while len(pts) < n:
        x, y = random.uniform(min_x, max_x), random.uniform(min_y, max_y)
        if in_poly((x, y), outline):
            pts.append(pygame.Vector2(x, y))
    return pts

stars = [pygame.Vector2(random.randint(0, W), random.randint(0, H)) for _ in range(200)]
out = gen_outline()
pts = gen_filled(2000, out)
parts = [{"org": p, "pos": p.copy(), "vel": pygame.Vector2(0, 0), "ph": random.uniform(0, 2 * math.pi)} for p in pts]

rockets, particles, falling_hearts = [], [], []
rocket_timer = 0
start_time = pygame.time.get_ticks() / 1000

while True:
    dt = clock.tick(60) / 1000
    elapsed = pygame.time.get_ticks() / 1000 - start_time
    screen.fill((10, 10, 10))

    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), (int(star.x), int(star.y)), 1)

    if elapsed < 10:
        rocket_timer += 1
        if rocket_timer > 10:
            rockets.append(Rocket(random.randint(0, W), random.randint(H // 2, H)))
            rocket_timer = 0

        for r in rockets[:]:
            r.update()
            if r.exploded:
                for _ in range(70):
                    particles.append(FireworkParticle(r.x, r.y))
                rockets.remove(r)

        particles = [p for p in particles if p.update()]
        for r in rockets:
            r.draw(screen)
        for p in particles:
            p.draw(screen)

    if elapsed < 10:
        if random.random() < 0.1:
            for _ in range(2):
                x = random.randint(0, W)
                y = random.randint(-50, 0)
                falling_hearts.append({"pos": pygame.Vector2(x, y), "vy": 8})

        for heart in falling_hearts[:]:
            heart["pos"].y += heart["vy"]
            if heart["pos"].y > H:
                falling_hearts.remove(heart)
            else:
                draw_heart(screen, int(heart["pos"].x), int(heart["pos"].y), 5)

    if 10 <= elapsed < 25:
        m = pygame.Vector2(pygame.mouse.get_pos())
        pressed = pygame.mouse.get_pressed()[0]
        beat = 1 + 0.02 * math.sin(2 * math.pi * 1.5 * elapsed)
        for p in parts:
            target = ctr + (p["org"] - ctr) * beat
            spring = (target - p["pos"]) * 0.02
            dvec = p["pos"] - m
            d = dvec.length() or 0.001
            if pressed:
                rep = dvec.normalize() * 2.5 * 3
            else:
                rep = pygame.Vector2(0, 0)
                if d < 80:
                    rep = dvec.normalize() * 2.5 * (80 - d) / 80
            force = spring + rep
            p["vel"] = (p["vel"] + force) * 0.90
            p["pos"] += p["vel"]
            inten = 155 + 100 * math.sin(2 * elapsed + p["ph"])
            red = max(0, min(255, int(inten + 100)))
            color = (red, 0, 0)
            pygame.draw.circle(screen, color, (int(p["pos"].x), int(p["pos"].y)), 3)

        if random.random() < 0.06:
            for _ in range(2):
                x = random.randint(0, W)
                y = random.randint(-50, 0)
                falling_hearts.append({"pos": pygame.Vector2(x, y), "vy": 8})

        for heart in falling_hearts[:]:
            heart["pos"].y += heart["vy"]
            if heart["pos"].y > H:
                falling_hearts.remove(heart)
            else:
                draw_heart(screen, int(heart["pos"].x), int(heart["pos"].y), 5)

    pygame.display.flip()

    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()
            