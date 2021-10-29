import pygame
from pygame.locals import *
import sys
 
pygame.init()
 
vec = pygame.math.Vector2 
HEIGHT = 400
WIDTH = 400
ACC = 0.5
FRIC = -0.12
FPS = 60
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")
 
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load('rock.jpeg')
        
        self.rect = self.image.get_rect()
   
        self.pos = vec((10, 385))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
 
    def move(self):
        self.acc = vec(0,0)
    
        pressed_keys = pygame.key.get_pressed()            
        if pressed_keys[K_LEFT]:
            self.acc.x = -ACC
        if pressed_keys[K_RIGHT]:
            self.acc.x = ACC
             
        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
         
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH
        apexOfJump = self.pos.y+400
        if (self.pos.y <= apexOfJump):
            self.vel.y = 2
    
        
            
        self.rect.midbottom = self.pos
    def jump(self):
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            self.vel.y = -5
            
            
        
        
 
 
    def update(self):
        hits = pygame.sprite.spritecollide(P1 ,platforms, False)
        if P1.vel.y > 0:        
            if hits:
                self.vel.y = 0
                self.pos.y = hits[0].rect.top + 1
 
class platform(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((WIDTH, 20))
        self.surf.fill((255,0,0))
        self.rect = self.surf.get_rect(center = (WIDTH/2, HEIGHT - 10))
 
PT1 = platform()
P1 = Player()
 
all_sprites = pygame.sprite.Group()
all_sprites.add(PT1)

playerSprite = pygame.sprite.Group()
playerSprite.add(P1)


platforms = pygame.sprite.Group()
platforms.add(PT1)
 
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:    
            if event.key == pygame.K_SPACE:
                P1.jump()
     
    displaysurface.fill((0,0,0))
    P1.update()
 
    for entity in platforms:
        displaysurface.blit(entity.surf, entity.rect)
    for entity in playerSprite:
        displaysurface.blit(entity.image, entity.rect)
        entity.move()
    
    pygame.display.update()
    FramePerSec.tick(FPS)
