import pygame
import pymunk
import math
import pymunk.pygame_util


pygame.init()

SCREENWIDTH = 1200
SCREENHEIGHT = 678
BOTTOM = 50


screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT + BOTTOM))
pygame.display.set_caption("Pool")


space = pymunk.Space()
static_body = space.static_body
draw_options = pymunk.pygame_util.DrawOptions(screen)


clock = pygame.time.Clock()
FPS = 120

#variables
lives = 3
max_force = 10000
dia = 36
pocket_dia = 66
force = 0
taking_shot = True
powering_up = False
potted_balls = []
force_direction = 1
game_running = True
cue_ball_potted = False


#colors
BACKGROUND = (139,137,137)
GREEN = (0,255,0)
WHITE = (255, 255, 255)


font = pygame.font.SysFont("Lato", 30)
large_font = pygame.font.SysFont("Lato", 60)

#images
cue_image = pygame.image.load("assets/images/cue.png").convert_alpha()
table_image = pygame.image.load("assets/images/table.png").convert_alpha()
ball_images = []
for i in range(1, 17):
  ball_image = pygame.image.load(f"assets/images/ball_{i}.png").convert_alpha()
  ball_images.append(ball_image)


def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#ball movemnt 
def create_ball(radius, pos):
  body = pymunk.Body()
  body.position = pos
  shape = pymunk.Circle(body, radius)
  shape.mass = 5
  shape.elasticity = 0.8
  
  pivot = pymunk.PivotJoint(static_body, body, (0, 0), (0, 0))
  pivot.max_bias = 0 
  pivot.max_force = 1000 

  space.add(body, shape, pivot)
  return shape

#setup 
balls = []
rows = 5

for col in range(5):
  for row in range(rows):
    pos = (250 + (col * (dia + 1)), 267 + (row * (dia + 1)) + (col * dia / 2))
    new_ball = create_ball(dia / 2, pos)
    balls.append(new_ball)
  rows -= 1

pos = (888, SCREENHEIGHT / 2)
cueball = create_ball(dia / 2, pos)
balls.append(cueball)


pockets = [
  (55, 63),
  (592, 48),
  (1134, 64),
  (55, 616),
  (592, 629),
  (1134, 616)
]


cushions = [
  [(88, 56), (109, 77), (555, 77), (564, 56)],
  [(621, 56), (630, 77), (1081, 77), (1102, 56)],
  [(89, 621), (110, 600),(556, 600), (564, 621)],
  [(622, 621), (630, 600), (1081, 600), (1102, 621)],
  [(56, 96), (77, 117), (77, 560), (56, 581)],
  [(1143, 96), (1122, 117), (1122, 560), (1143, 581)]
]


def create_cushion(poly_dims):
  body = pymunk.Body(body_type = pymunk.Body.STATIC)
  body.position = ((0, 0))
  shape = pymunk.Poly(body, poly_dims)
  shape.elasticity = 0.8
  
  space.add(body, shape)

for c in cushions:
  create_cushion(c)


class Cue():
  def __init__(self, pos):
    self.original_image = cue_image
    self.angle = 0
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = pos

  def update(self, angle):
    self.angle = angle

  def draw(self, surface):
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    surface.blit(self.image,
      (self.rect.centerx - self.image.get_width() / 2,
      self.rect.centery - self.image.get_height() / 2)
     )

cuestick = Cue(balls[-1].body.position)


power_bar = pygame.Surface((10, 20))
power_bar.fill(GREEN)


run = True
while run:

  clock.tick(FPS)
  space.step(1 / FPS)

  #background
  screen.fill(BACKGROUND)

  #pool table image
  screen.blit(table_image, (0, 0))

  
  for i, ball in enumerate(balls):
    for pocket in pockets:
      ball_x_dist = abs(ball.body.position[0] - pocket[0])
      ball_y_dist = abs(ball.body.position[1] - pocket[1])
      ball_dist = math.sqrt((ball_x_dist ** 2) + (ball_y_dist ** 2))
      if ball_dist <= pocket_dia / 2:

        if i == len(balls) - 1:
          lives -= 1
          cue_ball_potted = True
          ball.body.position = (-100, -100)
          ball.body.velocity = (0.0, 0.0)
        else:
          space.remove(ball.body)
          balls.remove(ball)
          potted_balls.append(ball_images[i])
          ball_images.pop(i)

 
  for i, ball in enumerate(balls):
    screen.blit(ball_images[i], (ball.body.position[0] - ball.radius, ball.body.position[1] - ball.radius))


  taking_shot = True
  for ball in balls:
    if int(ball.body.velocity[0]) != 0 or int(ball.body.velocity[1]) != 0:
      taking_shot = False


  if taking_shot == True and game_running == True:
    if cue_ball_potted == True:

      balls[-1].body.position = (888, SCREENHEIGHT / 2)
      cue_ball_potted = False

    mouse_pos = pygame.mouse.get_pos()
    cuestick.rect.center = balls[-1].body.position
    x_dist = balls[-1].body.position[0] - mouse_pos[0]
    y_dist = -(balls[-1].body.position[1] - mouse_pos[1]) # -ve because pygame y coordinates increase down the screen
    cue_angle = math.degrees(math.atan2(y_dist, x_dist))
    cuestick.update(cue_angle)
    cuestick.draw(screen)


  if powering_up == True and game_running == True:
    force += 100 * force_direction
    if force >= max_force or force <= 0:
      force_direction *= -1
 
    for c in range(math.ceil(force / 2000)):
      screen.blit(power_bar,
       (balls[-1].body.position[0] - 30 + (c * 15),
        balls[-1].body.position[1] + 30))
  elif powering_up == False and taking_shot == True:
    x_impulse = math.cos(math.radians(cue_angle))
    y_impulse = math.sin(math.radians(cue_angle))
    balls[-1].body.apply_impulse_at_local_point((force * -x_impulse, force * y_impulse), (0, 0))
    force = 0
    force_direction = 1


  pygame.draw.rect(screen, BACKGROUND, (0, SCREENHEIGHT, SCREENWIDTH, BOTTOM))
  draw_text("Number Of Lives: " + str(lives), font, WHITE, SCREENWIDTH - 200, SCREENHEIGHT + 10)

 
  for i, ball in enumerate(potted_balls):
    screen.blit(ball, (10 + (i * 50), SCREENHEIGHT + 10))

 
  if len(balls) == 1:
    draw_text("YOU WIN!", large_font, WHITE, SCREENWIDTH / 2 - 160, SCREENHEIGHT / 2 - 100)
    game_running = False
    
  if lives <= 0:
    draw_text("GAME OVER", large_font, WHITE, SCREENWIDTH / 2 - 160, SCREENHEIGHT / 2 - 100)
    game_running = False


  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN and taking_shot == True:
      powering_up = True
    if event.type == pygame.MOUSEBUTTONUP and taking_shot == True:
      powering_up = False
    if event.type == pygame.QUIT:
      run = False

  
  pygame.display.update()

pygame.quit()