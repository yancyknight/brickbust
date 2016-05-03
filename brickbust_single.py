#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""


#Import Modules
import os, pygame
from pygame.locals import *
from pygame.compat import geterror

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (350,200)

#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

#classes for our game objects
class Brick(pygame.sprite.Sprite):
    """ Places bricks that must be broken by the ball """
    def __init__(self, x, y, strength = 1):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.strength = strength
        self.x = x
        self.y = y
        self.image, self.rect = self.loadBrickImage(self.strength)

    def update(self):
        pos = (self.x * 30, self.y * 10)
        self.rect.topleft = pos

    def loadBrickImage(self, strength):
        if self.strength >= 5:
            return load_image('red_brick.png', -1)
        elif self.strength == 4:
            return load_image('orange_brick.png', -1)
        elif self.strength == 3:
            return load_image('purple_brick.png', -1)
        elif self.strength == 2:
            return load_image('blue_brick.png', -1)
        elif self.strength == 1:
            return load_image('green_brick.png', -1)
        else:
            return load_image('blank_brick.png', -1)

    # lowers strength of brick
    def weaken(self):
        self.strength -= 1
        self.image, self.rect = self.loadBrickImage(self.strength)

    def isActive(self):
        return self.strength > 0


def loadBrickList(name):
    fullname = os.path.join(data_dir, name)
    f = open(fullname, 'r')
    bricks = []
    for line in f:
        brick_row = []
        for num in line:
            if num != '\n':
                brick_row.append(int(num))
        bricks.append(brick_row)
    return bricks

def loadBricks(brickList):
    bricks = []
    x = 0
    y = 0
    for row in brickList:
        brickRow = []
        for strength in row:
            brickRow.append(Brick(x, y, strength))
            x += 1
        bricks.append(brickRow)
        y += 1
        x = 0
    return bricks

class Paddle(pygame.sprite.Sprite):
    """moves a paddle on the screen, following the mouse"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image, self.rect = load_image('paddle.png', -1)

    def update(self):
        "move the paddle based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.midtop = (pos[0], pygame.display.get_surface().get_rect().bottom - 25)

class Ball(pygame.sprite.Sprite):
    """ Ball that bounces around the screen. """
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        self.image, self.rect = load_image('ball.png', -1)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.rect.topleft = 10, 10
        self.movex = 5
        self.movey = 5
        self.sliding = 0

    # bounces ball off paddle relative to where the ball hit the paddle
    def paddleBounce(self, paddle):
        self.movex = int((self.rect.topleft[0] - paddle.rect.midtop[0]) * .75)
        self._reverseYDirection()

    def brickBounce(self, brick):
        if brick.isActive():
            self._reverseYDirection()

    # reverses y direction of ball
    def _reverseYDirection(self):
        self.movey = -self.movey

    # reverses x direction of ball
    def _reverseXDirection(self):
        self.movex = -self.movex

    # returns true if ball is colliding with target
    def hits(self, target):
        return self.rect.colliderect(target.rect)

    # makes the ball slide across the screen unless the life hasn't started yet, then it follows the paddle
    def update(self):
        if self.sliding:
            self._slide()
        else:
            self._followPaddle()

    # returns true if ball hits bottom of screen
    def dies(self):
        if self.rect.bottom > self.area.bottom:
            self.sliding = 0
            self.movex = 5
            return True
        return False

    def _slide(self):
        "slides the ball across the screen, and turn at the ends"
        newpos = self.rect.move((self.movex, self.movey))
        if self.rect.left < self.area.left or \
            self.rect.right > self.area.right:
            self.movex = -self.movex
        if self.rect.top < self.area.top:
            self.movey = -self.movey
        newpos = self.rect.move(self.movex, self.movey)
        self.rect = newpos

    def _followPaddle(self):
        " makes the ball follow the paddle around "
        pos = pygame.mouse.get_pos()
        self.rect.midtop = (pos[0] - 10, pygame.display.get_surface().get_rect().bottom - 35)

    def go(self):
        self.sliding = 1




def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption('Brickbust 1.0.0d')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    ball = Ball()
    paddle = Paddle()
    brickList = loadBrickList('l2.txt')
    bricks = loadBricks(brickList)
    numActiveBricks = len(bricks) * len(bricks[0])
    allsprites = pygame.sprite.RenderPlain((paddle, ball, bricks))
    lives = 3

#Main Loop
    going = True
    while going:
        clock.tick(30)

        #Put Text On The Background, Centered
        if pygame.font:
            background.fill((250,250,250))
            font = pygame.font.Font(None, 36)
            s = "Lives: " + str(lives) + "   Bricks left: " + str(numActiveBricks)
            text = font.render(s, 1, (10, 10, 10))
            textpos = text.get_rect(centerx=background.get_width()/2)
            textpos[1] = 100
            background.blit(text, textpos)

        if ball.hits(paddle):
            ball.paddleBounce(paddle)
        for brickList in bricks:
            for brick in brickList:
                if ball.hits(brick):
                    ball.brickBounce(brick)
                    brick.weaken()
                    if brick.strength == 0:
                        numActiveBricks -= 1

        if ball.dies():
            if lives > 1:
                lives -= 1
            else:
                going = False

        if numActiveBricks == 0:
            text = font.render("You win!!", 1, (10, 10, 10))
            textpos = text.get_rect(centerx=background.get_width()/2)
            textpos[1] = 150
            background.blit(text, textpos)

        #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                going = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False
            elif event.type == MOUSEBUTTONDOWN:
                ball.go()

        allsprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
