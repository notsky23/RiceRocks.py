"""Rice Rocks version 1.12"""
"""Created by Notsky"""

# program template for Spaceship
import pygame
from pygame.locals import *
import math
import random
import sys

pygame.init()

# globals for user interface
WIDTH = 1000
HEIGHT = 750
score = 0
lives = 3
time = 0
blink_constant = 17
blink_counter = blink_constant
delay_counter = 3 #second
splash = True
space_pressed = False

#colors
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

"""
Image Info Class
"""
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

"""
Ship class
"""
class Ship(pygame.sprite.Sprite):
    """ Constructor """
    def __init__(self, pos, vel, angle, image, info):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.radius = info.get_radius()
        self.displayed = True
        self.sound = ship_thrust_sound
        self.blink_timer = 0
        self.blink_duration = 2 * fps  # Blink duration in seconds

        self.original_image1 = image.subsurface(0, 0, info.get_size()[0], info.get_size()[1])
        self.original_image2 = image.subsurface(info.get_size()[0], 0, info.get_size()[0], info.get_size()[1])
        self.image = self.original_image1
        self.image_center = pygame.Vector2(info.get_center())
        self.image_size = pygame.Vector2(info.get_size())
        self.rect = self.image.get_rect(center=pos)

    """ Update method """
    def update(self):
        # update position with regards to velocity and wrap around screen when ship goes off the edge
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        # update friction and velocity
        c = 0.03
        self.vel[0] *= (1 - c)
        self.vel[1] *= (1 - c)
        # update angle with regards to angular velocity
        self.angle += self.angle_vel
        # update vector position
        if self.thrust:
            # get angle
            thrust = pygame.Vector2(0, -0.5).rotate(-self.angle + 90)
            self.vel += thrust
            # draw ship with thrusters on
            self.image = pygame.transform.rotate(self.original_image2, self.angle)
        else:
            # draw ship with thrusters off
            self.image = pygame.transform.rotate(self.original_image1, self.angle)
        # update drawing of ship
        self.rect = self.image.get_rect(center=self.pos)
        # Check if blinking is active
        if self.blink_timer > 0:
            # Decrement the blink timer
            self.blink_timer -= 1
            # Toggle the displayed flag
            if self.blink_timer % (fps // 10) == 0:
                self.displayed = not self.displayed
            # If the blink duration has elapsed, stop blinking
            if self.blink_timer <= 0:
                self.displayed = True
            # If the ship is currently displayed, update the image normally
            if self.displayed:
                if self.thrust:
                    self.image = pygame.transform.rotate(self.original_image2, self.angle)
                else:
                    self.image = pygame.transform.rotate(self.original_image1, self.angle)
            # If the ship is not displayed, set the image to a transparent surface
            else:
                self.image = pygame.Surface((0, 0))
                self.image.set_alpha(0)
        else:
            # check for collision
            if pygame.sprite.spritecollide(self, asteroidGroup, True, pygame.sprite.collide_mask):
                # if collision is detected trigger explosion animation
                self.collision()

    """ get position on method """
    def get_position(self):
        return self.pos

    """ thrusters on method """
    def thrusters_on(self):
        self.thrust = True
        self.image = self.original_image2
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.sound.play()

    """ thrusters off method """
    def thrusters_off(self):
        self.thrust = False
        self.image = self.original_image1
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.sound.stop()

    """ shoot missile method """
    def shoot(self):
        # if blinking is active, do not shoot
        if self.blink_timer > 0:
            return
        # get angle
        thrust = pygame.Vector2(0, -0.5).rotate(-self.angle + 90)
        # set initial position of missile to the tip of the spaceship's cannon
        missile_pos = [self.pos[0] + (thrust[0] * (self.image_size[0] - self.image_center[0])),
                      self.pos[1] + (thrust[1] * (self.image_size[1] - self.image_center[0]))]
        # add a velocity that is a faster than the max speed of the spaceship
        missile_vel = [(self.vel[0] + (thrust[0] * 30)), (self.vel[1] + (thrust[1] * 30))]
        # set a new missile object
        missile = Sprite(missile_pos, missile_vel, 0, 0, missile_image, missile_info, missile_sound)
        missileGroup.add(missile)

    """ collision detection method """
    def collision(self):
        global lives
        # thrusters off
        self.thrusters_off()
        # blink
        self.blink_timer = self.blink_duration
        self.displayed = True
        # take off image from screen
        lives -= 1
        if lives <= 0:
            self.kill()
        # create an explosion animation and add it to explosion group
        explosion = Explosion((self.pos[0], self.pos[1]), explosion_image, explosion_info, explosion_sound)
        explosionGroup.add(explosion)
    

"""
Sprite class
"""
class Sprite(pygame.sprite.Sprite):
    """ Constructor """
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(vel)
        self.angle = ang
        self.angle_vel = ang_vel
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()

        self.original_image = image.subsurface(0, 0, info.get_size()[0], info.get_size()[1])
        self.image = self.original_image
        self.image_center = pygame.Vector2(info.get_center())
        self.image_size = pygame.Vector2(info.get_size())
        self.rect = self.image.get_rect(center=pos)

        self.age = -1
        if sound:
            sound.play()

    """ Update method """
    def update(self):
        # update position and wrap around screen when object goes off the edge
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        # set angular velocity for object rotation
        self.angle += self.angle_vel
        # update drawing of sprite
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
        # set age
        self.age += 1
        if self.age >= self.lifespan:
            self.kill()
        # check for collision between missile and asteroid
        if self in missileGroup and pygame.sprite.spritecollide(self, asteroidGroup, True, pygame.sprite.collide_mask):
            # if collision is detected trigger explosion animation
            self.collision()

    """ Collision detection method """
    def collision(self):
        global score

        # take off image from screen
        self.kill()
        # create an explosion animation and add it to explosion group
        explosion = Explosion((self.pos[0], self.pos[1]), explosion_image, explosion_info, explosion_sound)
        explosionGroup.add(explosion)
        score += 100

"""
Explosion Class
"""
class Explosion(pygame.sprite.Sprite):
    """ Constructor """
    def __init__(self, pos, image, info, sound):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        # loop to append to the list of images for animation
        for frame in range(0, 24):
            img = image.subsurface((frame * info.get_size()[0]), 0, info.get_size()[0], info.get_size()[1])
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.age = 0
        self.lifespan = info.get_lifespan()
        if sound:
            sound.play()

    """ Update method """
    def update(self):
        # update the position of the explosion animation
        if self.index < len(self.images) - 1:
            self.index += 1
            self.image = self.images[self.index]
        self.age += 1
        if self.age >= self.lifespan:
            self.kill()

"""
Helper to calculate distance
"""
def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

"""
Restart Helper
"""
def restart():
    global splash, lives, score, time, space_pressed
    # feature splash screen when lives hit 0
    splash = True
    # Re-initialize globals when lives <= 0
    if splash == True:
        # empty groups
        spaceshipGroup.empty()
        missileGroup.empty()
        asteroidGroup.empty()
        explosionGroup.empty()
        # reset globals
        score = 0
        lives = 3
        time = 0
        space_pressed = False
        # stop sound
        soundtrack.stop()

"""
New Game helper
"""
def newGame():
    """remove splash screen when mouse or button is clicked"""
    global splash
    if splash == True:
        splash = False
        # create player
        my_ship = Ship((WIDTH / 2, HEIGHT / 2), [0, -.5], 90, ship_image, ship_info)
        spaceshipGroup.add(my_ship)
        # play soundtrack during instance of new game
        soundtrack.play()

"""
Timer handler that spawns a rock
"""
def rock_spawner():
    # spawn asteroid randomly
    if len(asteroidGroup) < 12 and len(spaceshipGroup.sprites()) > 0 and len(spaceshipGroup.sprites()):
        # randomize position of asteroid within the screen
        asteroid_spawn_pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        # check to make sure that asteroid is spawning a few units away from the ship
        while dist(spaceshipGroup.sprites()[0].get_position(), asteroid_spawn_pos) < 200:
            asteroid_spawn_pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
        # randomize the velocity of the asteroid
        asteroid_spawn_vel = [random.choice([-1, 1]), random.choice([-1, 1])]
        # randomize the asteroid's speed of rotation
        asteroid_spawn_angle_vel = random.random() * 10 * random.choice([-1, 1])
        # for every 1k points increase rock speed by 20%
        multiplier = score // 1000
        asteroid_spawn_vel[0] += asteroid_spawn_vel[0] * (1 + 0.2) ** multiplier
        asteroid_spawn_vel[1] += asteroid_spawn_vel[1] * (1 + 0.2) ** multiplier
        # create asteroid and add to asteroid group
        asteroidGroup.add(Sprite(asteroid_spawn_pos, asteroid_spawn_vel, 0, asteroid_spawn_angle_vel,
                                 asteroid_image, asteroid_info))

"""
Key helpers
"""
def keydown(event):
    global space_pressed

    # movement of ship
    # move forward
    if event.key == K_UP or event.key == K_w:
        spaceshipGroup.sprites()[0].thrusters_on()
    # rotate left
    if event.key == K_LEFT or event.key == K_a:
        spaceshipGroup.sprites()[0].angle_vel += 10
    # rotate right
    if event.key == K_RIGHT or event.key == K_d:
        spaceshipGroup.sprites()[0].angle_vel -= 10
    # shoot command
    if event.key == K_SPACE:
        space_pressed = True


def keyup(event):
    global space_pressed

    # stop movement of ship
    # stop moving forward
    if event.key == K_UP or event.key == K_w:
        spaceshipGroup.sprites()[0].thrusters_off()
    # stop rotating left
    if event.key == K_LEFT or event.key == K_a:
        spaceshipGroup.sprites()[0].angle_vel -= 10
    # stop rotating right
    if event.key == K_RIGHT or event.key == K_d:
        spaceshipGroup.sprites()[0].angle_vel += 10
    # stop shooting
    if event.key == K_SPACE:
        space_pressed = False


"""
The game event loop
"""
def main():
    global splash

    time = 0
    run = True
    restart_time = None
    # Missile
    shoot_event = pygame.USEREVENT + 1
    pygame.time.set_timer(shoot_event, 100)  # 100ms interval
    # Asteroid
    rock_spawn_event = pygame.USEREVENT + 2  # create a new event
    pygame.time.set_timer(rock_spawn_event, 1000)  # call rock_spawner every second

    while run:
        #frame rate
        clock.tick(fps)

        #draw and animate background
        # forward animation of debris
        time += 1
        wtime = (time / 4) % WIDTH
        screen.blit(nebula_image, (0, 0))
        screen.blit(debris_image, (0 - wtime, 0))
        screen.blit(debris_image, (WIDTH - wtime, 0))

        # alternate backward animation of debris
        # time += 1
        # wtime = (time / 4) % WIDTH
        # screen.blit(nebula_image, (0, 0))
        # screen.blit(debris_image, (wtime - 0, 0))
        # screen.blit(debris_image, (wtime - WIDTH, 0))

        # splash screen instance
        if splash:
            splash_rect = splash_image.get_rect()

            # center the splash image on the screen
            screen_center = (WIDTH / 2, HEIGHT / 2)
            splash_rect.center = screen_center

            # draw the splash image on the screen
            splashScreen = screen.blit(splash_image, splash_rect)

            # event handlers
            for event in pygame.event.get():
                # quit event
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                # mouse click event
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    # clicking on splash screen will enter a new game
                    if splashScreen.collidepoint(event.pos):
                        newGame()

        # Game instance
        else:
            #update spaceship
            spaceshipGroup.update()

            #update sprites
            missileGroup.update()
            asteroidGroup.update()
            explosionGroup.update()

            #draw sprite groups
            spaceshipGroup.draw(screen)
            missileGroup.draw(screen)
            asteroidGroup.draw(screen)
            explosionGroup.draw(screen)

            # draw lives
            font1 = pygame.font.SysFont("candara", 60)
            label1 = font1.render("Lives: " + str(lives), True, WHITE)
            screen.blit(label1, (130, 50))

            # draw scores
            font2 = pygame.font.SysFont("candara", 60)
            label2 = font2.render("Score: " + str(score), True, WHITE)
            screen.blit(label2, (WIDTH - 375, 50))

            # event handlers
            for event in pygame.event.get():
                if len(spaceshipGroup) > 0:
                    if event.type == rock_spawn_event:
                        rock_spawner()
                    # movement of ship
                    if event.type == KEYDOWN:
                        keydown(event)
                    elif event.type == KEYUP:
                        keyup(event)
                    # shoot event
                    elif event.type == shoot_event and space_pressed:
                        spaceshipGroup.sprites()[0].shoot()
                # quit event
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            # clicking on splash screen will enter a new game
            if lives <= 0:
                # draw lives
                font3 = pygame.font.SysFont("candara", 100)
                label3 = font3.render("GAME OVER", True, WHITE)
                # center the label on the screen
                label_rect = label3.get_rect(center=(WIDTH/2, HEIGHT/2))
                screen.blit(label3, label_rect)

                # Set the restart time to be 2 seconds in the future
                if restart_time is None:
                    # set the restart time
                    restart_time = pygame.time.get_ticks() + 3000
                # check if the restart delay has elapsed
                elif pygame.time.get_ticks() >= restart_time:
                    restart()
                    restart_time = None

        #update display
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    # initialize frame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("RiceRocks")

    # Define FPS
    clock = pygame.time.Clock()
    fps = 60

    """Load asset images"""
    # art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim

    # debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
    #                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
    # debris_info = ImageInfo([320, 240], [640, 480])
    debris_image = pygame.image.load("Assets/Graphics/debris2_blue.png")
    debris_image = pygame.transform.scale(debris_image, (WIDTH, HEIGHT))

    # nebula images - nebula_brown.png, nebula_blue.png
    # nebula_info = ImageInfo([400, 300], [800, 600])
    nebula_image = pygame.image.load("Assets/Graphics/nebula_blue.png")
    nebula_image = pygame.transform.scale(nebula_image, (WIDTH, HEIGHT))

    # splash image
    splash_info = ImageInfo([200, 150], [400, 300])
    splash_image = pygame.image.load("Assets/Graphics/splash.png")

    # ship image
    ship_info = ImageInfo([45, 45], [90, 90], 35)
    ship_image = pygame.image.load("Assets/Graphics/double_ship.png")

    # missile image - shot1.png, shot2.png, shot3.png
    missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
    missile_image = pygame.image.load("Assets/Graphics/shot2.png")

    # asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
    asteroid_info = ImageInfo([45, 45], [90, 90], 40)
    asteroid_image = pygame.image.load("Assets/Graphics/asteroid_blue.png")

    # animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
    explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
    explosion_image = pygame.image.load("Assets/Graphics/explosion_alpha.png")

    # sound assets purchased from sounddogs.com, please do not redistribute
    soundMixer = pygame.mixer
    soundMixer.init()
    # soundtrack = soundMixer.sound("Assets/Sounds/soundtrack.mp3")
    missile_sound = soundMixer.Sound("Assets/Sounds/missile.mp3")
    missile_sound.set_volume(.25)
    ship_thrust_sound = soundMixer.Sound("Assets/Sounds/thrust.mp3")
    explosion_sound = soundMixer.Sound("Assets/Sounds/explosion.mp3")

    # alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
    # please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
    soundtrack = soundMixer.Sound("Assets/Sounds/ricerocks_theme.mp3")
    soundtrack.set_volume(.25)

    # create sprite group
    spaceshipGroup = pygame.sprite.Group()
    missileGroup = pygame.sprite.Group()
    asteroidGroup = pygame.sprite.Group()
    explosionGroup = pygame.sprite.Group()

    # get things rolling
    restart()
    main()

    """Created by Notsky"""