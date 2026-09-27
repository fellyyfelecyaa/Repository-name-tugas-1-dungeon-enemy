import pygame
import heapq
import math

pygame.init()

player__image = pygame.image.load("images/player.png")
enemy__image = pygame.image.load("images/enemy.png")

player__image = pygame.transform.scale(player__image, (30, 30))
enemy__image = pygame.transform.scale(enemy__image, (30, 30))

# ukuran layar
width = 800
height = 600
tile = 40

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dungeon Enemy AI - A*")

clock = pygame.time.Clock()

# warna
BLACK = (30, 30, 30)
WHITE = (255, 255, 255)
RED = (250, 50, 50)
BLUE = (50, 100, 220)
GREEN = (50, 200, 100)
GRAY = (100, 100, 100)

# dungeon map
dungeon = [
    "####################",
    "#..................#",
    "#..####............#",
    "#..................#",
    "#......#####.......#",
    "#..................#",
    "#..............###.#",
    "#..................#",
    "#....####..........#",
    "#..................#",
    "####################"
]

rows = len(dungeon)
cols = len(dungeon[0])


# mencari perkiraan jarak dari posisi sekarang ke tujuan
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# mencari posisi yang bisa dilewati
def get_neighbors(position):
    x, y = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    neighbors = []

    for dx, dy in directions:
        nx = x + dx
        ny = y + dy

        if 0 <= nx < cols and 0 <= ny < rows:
            if dungeon[ny][nx] != '#':
                neighbors.append((nx, ny))

    return neighbors


# algoritma A* untuk mencari jalur
def a_star(start, goal):
    open_list = []

    heapq.heappush(open_list, (0, start))

    came_from = {}

    cost = {}
    cost[start] = 0

    while open_list:

        _, current = heapq.heappop(open_list)

        if current == goal:
            path = []

            while current in came_from:
                path.append(current)
                current = came_from[current]

            path.append(start)
            path.reverse()

            return path

        for neighbor in get_neighbors(current):

            new_cost = cost[current] + 1

            if neighbor not in cost or new_cost < cost[neighbor]:

                came_from[neighbor] = current
                cost[neighbor] = new_cost

                priority = new_cost + heuristic(
                    neighbor,
                    goal
                )

                heapq.heappush(
                    open_list,
                    (priority, neighbor)
                )

    return []


# posisi awal player dan enemy
player = (8, 3)
enemy = (2, 1)

range_enemy = 10

enemy_speed = 250
last_enemy_move = pygame.time.get_ticks()

game_over = False
game_over_time = 0

# game loop
running = True

while running:

    # input dari keyboard
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # menggerakkan player
        if event.type == pygame.KEYDOWN:

            new_x, new_y = player

            if event.key == pygame.K_w or event.key == pygame.K_UP:
                new_y -= 1

            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                new_y += 1

            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                new_x -= 1

            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                new_x += 1

            # player tidak boleh melewati dinding
            if (
                0 <= new_x < cols
                and 0 <= new_y < rows
                and dungeon[new_y][new_x] != '#'
            ):
                player = (new_x, new_y)

    # menghitung jarak player dan enemy
    distance = math.dist(player, enemy)

    path = []

    # enemy mengejar player jika masih dalam jangkauan
    current_time = pygame.time.get_ticks()

    if distance <= range_enemy:

        if current_time - last_enemy_move >= enemy_speed:
           
            path = a_star(enemy, player)

            if len(path) > 1:
                enemy = path[1]

            last_enemy_move = current_time

        # mengecek apakah enemy sudah menangkap player
        if enemy == player:
            game_over = True
            game_over_time = current_time

    # menggambar dungeon
    screen.fill(BLACK)

    for y in range(rows):

        for x in range(cols):

            rect = pygame.Rect(
                x * tile,
                y * tile,
                tile,
                tile
            )

            if dungeon[y][x] == '#':
                pygame.draw.rect(screen, GRAY, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1)

    # menggambar jalur A*
    for x, y in path:

        pygame.draw.rect(
            screen,
            BLUE,
            (
                x * tile + 10,
                y * tile + 10,
                tile - 20,
                tile - 20
            )
        )

    # menggambar player
    screen.blit(
        player__image,
        (
            player[0] * tile + 5,
            player[1] * tile + 5,
        )
    )

    # menggambar enemy
    screen.blit(
        enemy__image,
        (
            enemy[0] * tile + 5,
            enemy[1] * tile + 5,
        )
    )

    # menampilkan game over
    if game_over:
        font = pygame.font.Font(None, 80)
        text = font.render("GAME OVER", True, RED)

        text_rect = text.get_rect(
            center=(width // 2, height // 2)
        )

        screen.blit(text, text_rect)
        pygame.display.flip()

        # close the game after 500 milliseconds
        pygame.time.wait(500)
        running = False

        continue

    pygame.display.flip()
    clock.tick(60)

pygame.quit()