import pygame 
import random
import time

pygame.init()

W, H = 1200, 800
FPS = 60

screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
clock = pygame.time.Clock()
done = False
bg = (0, 0, 0)

#paddle
paddleW = 150
paddleH = 25
paddleSpeed = 20
paddle = pygame.Rect(W // 2 - paddleW // 2, H - paddleH - 30, paddleW, paddleH)

#Ball
ballRadius = 20
ballSpeed = 6
ball_rect = int(ballRadius * 2 ** 0.5)
ball = pygame.Rect(random.randrange(ball_rect, W - ball_rect), H // 2, ball_rect, ball_rect)
dx, dy = 1, -1

#Game score
game_score = 0
game_score_fonts = pygame.font.SysFont('comicsansms', 40)
game_score_text = game_score_fonts.render(f'Your game score is: {game_score}', True, (0, 0, 0))
game_score_rect = game_score_text.get_rect()
game_score_rect.center = (210, 20)

#Catching sound
collision_sound = pygame.mixer.Sound('catch.mp3')

def detect_collision(dx, dy, ball, block):
    if dx > 0:
        delta_x = ball.right - block.rect.left
    else:
        delta_x = block.rect.right - ball.left
    if dy > 0:
        delta_y = ball.bottom - block.rect.top
    else:
        delta_y = block.rect.bottom - ball.top

    if abs(delta_x - delta_y) < 10:
        dx, dy = -dx, -dy
    if delta_x > delta_y:
        dy = -dy
    elif delta_y > delta_x:
        dx = -dx
    return dx, dy

class Block:
    def __init__(self, x, y, width, height, color, is_breakable, is_bonus=False):  # Добавляем параметр is_bonus
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_breakable = is_breakable
        self.is_bonus = is_bonus  # Устанавливаем атрибут is_bonus

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# Создаем список блоков, включая бонусные блоки



class BonusBlock:
    def __init__(self, x, y, width, height, color, bonus_type):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.bonus_type = bonus_type

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

def giveBonus(bonus_type):
    global ballSpeed, paddleW  # Объявляем переменные как глобальные, чтобы изменять их значение
    
    if bonus_type == 'speedDown':
        ballSpeed -= 1  # Уменьшаем скорость мяча на 1
    elif bonus_type == 'paddle_increase':
        paddleW += 30
        paddle.width = paddleW

#block settings
is_breakable_options = [True, False]
bonusList = ["speedDown", "paddle_increase"]
block_list = [
    Block(10 + 120 * i, 50 + 70 * j, 100, 50, (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)), random.choice(is_breakable_options), is_bonus=random.choice([True, False]))
    for i in range(10) for j in range(4)
]
color_list = [(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)) for i in range(10) for j in range(4)]

#Game over Screen
losefont = pygame.font.SysFont('comicsansms', 40)
losetext = losefont.render('Game Over', True, (255, 255, 255))
losetextRect = losetext.get_rect()
losetextRect.center = (W // 2, H // 2)

#Win Screen
winfont = pygame.font.SysFont('comicsansms', 40)
wintext = winfont.render('You win yay', True, (0, 0, 0))
wintextRect = wintext.get_rect()
wintextRect.center = (W // 2, H // 2)

# Start time for calculating elapsed time
start_time = time.time()
interval_count = 0


while not done:
    current_time = time.time() - start_time
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    screen.fill(bg)
    
    #drawing blocks
    for i, block in enumerate(block_list):
        block.draw(screen)

    pygame.draw.rect(screen, pygame.Color(255, 255, 255), paddle)
    pygame.draw.circle(screen, pygame.Color(255, 0, 0), ball.center, ballRadius)

    #Ball movement
    ball.x += ballSpeed * dx
    ball.y += ballSpeed * dy

    #Collision left 
    if ball.centerx < ballRadius or ball.centerx > W - ballRadius:
        dx = -dx
    #Collision top
    if ball.centery < ballRadius + 50: 
        dy = -dy
    #Collision with paddle
    if ball.colliderect(paddle) and dy > 0:
        if dx > 0:
            delta_x = ball.right - paddle.left
        else:
            delta_x = paddle.right - ball.left
        if dy > 0:
            delta_y = ball.bottom - paddle.top
        else:
            delta_y = paddle.bottom - ball.top

        if abs(delta_x - delta_y) < 10:
            dx, dy = -dx, -dy
        if delta_x > delta_y:
            dy = -dy
        elif delta_y > delta_x:

            dx = -dx

    #Collision blocks
    hitIndex = ball.collidelist(block_list)

    if hitIndex != -1:
        hitBlock = block_list[hitIndex]
        if isinstance(hitBlock, BonusBlock):
            block_list.pop(hitIndex)

        elif hitBlock.is_breakable:
            block_list.pop(hitIndex)
            color_list.pop(hitIndex)
            dx, dy = detect_collision(dx, dy, ball, hitBlock)
            game_score += 1
            collision_sound.play()
            
            if hitBlock.is_bonus:
                choice = random.randint(0, len(bonusList) - 1)
                print(choice)
                giveBonus(bonusList[choice])

        else:
            dx, dy = detect_collision(dx, dy, ball, hitBlock)
        
    #Game score
    game_score_text = game_score_fonts.render(f'Your game score is: {game_score}', True, (255, 255, 255))
    screen.blit(game_score_text, game_score_rect)
    
    #Win/lose screens
    # Lose screen
    if ball.bottom > H:
        screen.blit(losetext, losetextRect)
    # Win screen
    elif not len(block_list):
        screen.blit(wintext, wintextRect)

    # Paddle Control
    key = pygame.key.get_pressed()
    if key[pygame.K_LEFT] and paddle.left > 0:
        paddle.left -= paddleSpeed
    if key[pygame.K_RIGHT] and paddle.right < W:
        paddle.right += paddleSpeed

    # Accelerate ball after 3 seconds
    if current_time >= 3 * interval_count:  # Проверяем, прошло ли уже interval_count интервалов по 10 секунд
        ballSpeed += 0.03
        paddleW -= 10
        paddle.width = paddleW
        interval_count += 1  # Увеличиваем счетчик интервалов

    pygame.display.flip()
    clock.tick(FPS)