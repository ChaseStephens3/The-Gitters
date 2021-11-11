import pygame
from pygame.locals import *
import pickle
from os import path
#from sensor import *
import time
#I had to comment line 5 and 415 because if you don't have the probe, the game gets a stroke
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 480
screen_height = 480

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

temperature = 0



#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_temperature = pygame.font.SysFont('Times New Roman', 30)


hot = True
cold = False
debug = True




#define game variables
tile_size = 24
game_over = 0
main_menu = True
level = 0
max_levels = 2

#define colors
white = (255, 255, 255)
blue = (0, 0, 125)
black = (0, 0, 0)
red = (125, 0, 0)
green = (0, 125, 0)
colors = white

#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
bg_img_cold = pygame.image.load('img/skycold.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
bg_img = pygame.transform.scale(bg_img, (int((1000//2.08333333333)),int(1000//2.08333333333)))
start_img = pygame.transform.scale(start_img, (int((279//2.08333333333)),int(126//2.08333333333)))
exit_img = pygame.transform.scale(exit_img, (int((240//2.08333333333)),int(126//2.08333333333)))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))
    

def draw_grid():
    for line in range(0, 20):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))
#reset level
def reset_level(level):
    player.reset(int((100//2.08333333333)), screen_height - int((130//2.08333333333)))
    lava_group.empty()
    exit_group.empty()
    water_group.empty()
    ice_group.empty()
    coldlava_group.empty()

    if path.exists('level{}_data'.format(level)):
        pickle_in = open('level{}_data'.format(level), 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world
    
        
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and click conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
                
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        
        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
       self.reset(x, y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 2

        if game_over == 0:
            #get keypresses
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                    self.vel_y = (-12)
                    self.jumped = True
            if key[pygame.K_SPACE] == False:
                    self.jumped = False
            if key[pygame.K_LEFT]:
                    dx -= (5)
                    self.counter += 1
                    self.direction = -1
            if key[pygame.K_RIGHT]:
                    dx += (5)
                    self.counter += 1
                    self.direction = 1
            
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                    self.counter = 0
                    self.index = 0
                    if self.direction == 1:
                            self.image = self.images_right[self.index]
                    if self.direction == -1:
                            self.image = self.images_left[self.index]
 
            #animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]
                
            #adding gravity
            self.vel_y +=1
            if self.vel_y>10:
                self.vel_y = 10
            dy += self.vel_y
            
            #collision checks
            self.in_air = True
            for tile in world.tile_list:
                #collision for x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                
                #collision for y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    #check if below ground i.e. jumping
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False
            #check for collision with lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                game_over = -1

            if pygame.sprite.spritecollide(self, coldlava_group, False):
                if self.vel_y < 0:
                    self.in_air = False
                    self.jumped = False
                elif self.vel_y >= 0:
                    dy = 0
                    self.jumped = False
                    self.in_air = False
            if pygame.sprite.spritecollide(self, ice_group, False):
                if self.vel_y < 0:
                    self.in_air = False
                    self.jumped = False
                elif self.vel_y >= 0:
                    dy = 0
                    self.jumped = False
                    self.in_air = False
                
                if tile[2].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                
                    
                

            #check for collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1
                

            #update coords
            self.rect.x += dx
            self.rect.y += dy
            
        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER! ', font, blue, (screen_width // 2) - 190, screen_height // 2)
            self.rect.y -= 5

        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255,255,255), self.rect, 2)
        return game_over

    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 11):
                img_right = pygame.image.load('img/guy{}.png'.format(num))
                img_right = pygame.transform.scale(img_right, (int(19.2), int(38.4)))
                img_left = pygame.transform.flip(img_right, True, False)
                self.images_right.append(img_right)
                self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True




        
class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')
        ice_img = pygame.image.load('img/ice.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    if hot:
                        coldlava_group.empty()
                        lava = Lava(col_count * tile_size, row_count* tile_size + (tile_size // 2))
                        lava_group.add(lava)
                    elif cold:
                        lava_group.empty()
                        lava = coldLava(col_count * tile_size, row_count* tile_size + (tile_size // 2))
                        coldlava_group.add(lava)
                if tile == 4:
                    exit = Exit(col_count * tile_size, row_count* tile_size - (tile_size // 2))
                    exit_group.add(exit)
                if tile == 5:
                    if hot:
                        ice_group.empty()
                        water = Water(col_count * tile_size, row_count* tile_size)
                        water_group.add(water)
                    elif cold:
                        water_group.empty()
                        water = Ice(col_count * tile_size, row_count* tile_size)
                        water.rect.x = col_count * tile_size
                        water.rect.y = row_count * tile_size
                        ice_group.add(water)
                        img = pygame.transform.scale(ice_img, (tile_size, tile_size))
                        img_rect = img.get_rect()
                        img_rect.x = col_count * tile_size
                        img_rect.y = row_count * tile_size
                        tile = (img, img_rect)
                        self.tile_list.append(tile)
                        
                        
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image= pygame.transform.scale(img, (tile_size,tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



        
class coldLava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/cold_lava.png')
        self.image= pygame.transform.scale(img, (tile_size,tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        pass

    
class Water(pygame.sprite.Sprite):
     def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/water.png')
        self.image= pygame.transform.scale(img, (tile_size,tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
class Ice(pygame.sprite.Sprite):
     def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/ice.png')
        self.image= pygame.transform.scale(img, (tile_size,tile_size))
        self.rect = self.image.get_rect()
        
        
class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image= pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

player = Player(int((100//2.08333333333)), screen_height - int((130//2.08333333333)))
lava_group = pygame.sprite.Group()
coldlava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
ice_group = pygame.sprite.Group()




#load in level data
if path.exists('level{}_data'.format(level)):
    pickle_in = open('level{}_data'.format(level), 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 140, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 50, screen_height // 2, exit_img)


run = True
while run:

    clock.tick(fps)
    key = pygame.key.get_pressed()
    if hot:
        background_img = pygame.transform.scale(bg_img, (int((1000//2.08333333333)),int(1000//2.08333333333)))
        
    elif cold:
        background_img = pygame.transform.scale(bg_img_cold, (int((1000//2.08333333333)),int(1000//2.08333333333)))

    screen.blit(background_img, (0, 0))
    screen.blit(sun_img, (100, 100))
    if key[pygame.K_ESCAPE]:
        run = False
    
    if main_menu == True:
        draw_text('THE GITTER', font, black, (screen_width - 377), screen_height - 347)
        draw_text('THE GITTER', font, black, (screen_width - 383), screen_height - 347)
        draw_text('THE GITTER', font, black, (screen_width - 377), screen_height - 353)
        draw_text('THE GITTER', font, black, (screen_width - 383), screen_height - 353)
        draw_text('THE GITTER', font, (0, 0, 255), (screen_width - 380), screen_height - 350)
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        
        world.draw()
        if game_over == 0: 
            if key[pygame.K_LSHIFT]:
                if path.exists('level{}_data'.format(level)):
                    pickle_in = open('level{}_data'.format(level), 'rb')
                    world_data = pickle.load(pickle_in)
                #temperature = round(read_temp(),2)
                if temperature < 75:
                    cold = True
                    hot = False
                    colors = blue
                    background_img = pygame.transform.scale(bg_img_cold, (int((1000//2.08333333333)),int(1000//2.08333333333)))
                else:
                    hot = True
                    cold = False
                    background_img = pygame.transform.scale(bg_img, (int((1000//2.08333333333)),int(1000//2.08333333333)))
                    colors = red
                world = World(world_data)
                world.draw()
            if temperature == 0:
                colors = white
                draw_text('TEMP NOT SET', font_temperature, colors, tile_size -10,10)
            elif temperature == 1000:
                hot = True
                cold = False
                draw_text('TEMP NOT SET', font_temperature, colors, tile_size -10,10)
                
                
            else:
                draw_text(str(temperature)+'°F', font_temperature, colors, tile_size - 10,10)
            
        
        lava_group.draw(screen)
        water_group.draw(screen)
        ice_group.draw(screen)
        exit_group.draw(screen)
        coldlava_group.draw(screen)
        
        game_over = player.update(game_over)

        #if player died
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0

        #if player completed the level
        if game_over == 1:
            #reset game and go to next level
            level += 1
            if level <= max_levels:
                #reset level
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                hot = True
                cold = False
                temperature = 1000
                draw_text('YOU WIN! ', font, blue, (screen_width // 2) - 140, screen_height // 2)
                #restart game
                if restart_button.draw():
                    hot = True
                    cold = False
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    

        
        
                    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
