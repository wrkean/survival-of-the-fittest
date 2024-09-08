import pygame
from random import randint
import math
import time

pygame.init()
pygame.mixer.init()

scrn = pygame.display.set_mode((720, 1470))    # This does not matter on my phone
scrn_rect = scrn.get_rect()

entity_count = 30    # entities per type
red_count = entity_count
blue_count = entity_count
green_count = entity_count

munch = pygame.mixer.Sound("munch.mp3")
munch.set_volume(0.1)    # too loud

graph = pygame.Rect(0, 0, scrn_rect.width, 200)
graph.midbottom = scrn_rect.midbottom

pygame.time.Clock().tick(60)

class Entity:
    def __init__(self, type):
        self.radius = 20
        self.x = randint(self.radius, scrn_rect.width - self.radius)
        self.y = randint(self.radius, scrn_rect.height - self.radius - graph.height)
        self.type = type
        self.speed = 2
        self.avoid_edges_r = 100
        self.detection_r = 75
        self.last_eaten = time.time()
        self.hungry_time = 10
        
    def drawme(self):
        if self.type == "red":
            pygame.draw.circle(scrn, "red", (self.x, self.y), self.radius)
        elif self.type == "blue":
            pygame.draw.circle(scrn, "blue", (self.x, self.y), self.radius)
        elif self.type == "green":
            pygame.draw.circle(scrn, "green", (self.x, self.y), self.radius)
            
    
    def avoid_overlap(self, other):
        distance = self.distance_from(other)
        if distance < (self.radius + other.radius):    # checks collisions
            self.move_away_from(other.x, other.y)
            
        
    def move_toward(self, x, y):
        angle = math.atan2(y - self.y, x - self.x)
        self.x += self.speed * math.cos(angle)
        self.y += self.speed * math.sin(angle)
        
        self.avoid_edges()
        
        
    def move_away_from(self, x, y):
        angle = math.atan2(y - self.y, x - self.x)
        self.x -= self.speed * math.cos(angle)
        self.y -= self.speed * math.sin(angle)
        
        self.avoid_edges()
        
        
    def avoid_edges(self):
        if self.x < self.avoid_edges_r:    # avoids left edge
            self.move_toward(self.x + self.avoid_edges_r, self.y)
        if self.x > scrn_rect.width - self.avoid_edges_r:    # avoids right edge
            self.move_toward(self.x - self.avoid_edges_r, self.y)
        if self.y < self.avoid_edges_r:    # avoids top edge
            self.move_toward(self.x, self.y + self.avoid_edges_r)
        if self.y > scrn_rect.height - self.avoid_edges_r - graph.height:    #avoids bottom edge
            self.move_toward(self.x, self.y - self.avoid_edges_r)
            
    
    def distance_from(self, other):
        if other:
            return math.sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)
        else:
            return 0
        
# make entities
entities = [Entity("red") for _ in range(entity_count)] + \
           [Entity("blue") for _ in range(entity_count)] + \
           [Entity("green") for _ in range(entity_count)]
           
           
def movement_brain():
    global red_count, blue_count, green_count
    now = time.time()
    
    for ent in entities:
        if ent.type == "red":
            targets = [tg for tg in entities if tg.type == "green"]
            threats = [th for th in entities if th.type == "blue"]
        elif ent.type == "blue":
            targets = [tg for tg in entities if tg.type == "red"]
            threats = [th for th in entities if th.type == "green"]
        elif ent.type == "green":
            targets = [tg for tg in entities if tg.type == "blue"]
            threats = [th for th in entities if th.type == "red"]
            
        for ent2 in entities:
            if ent2 != ent and ent.type == ent2.type:
                ent.avoid_overlap(ent2)
        
        closest_target = min(targets, key=ent.distance_from, default=None)
        closest_threat = min(threats, key=ent.distance_from, default=None)
        
        if ent.distance_from(closest_threat) < ent.detection_r and closest_threat:
            ent.move_away_from(closest_threat.x, closest_threat.y)
        if ent.distance_from(closest_target) < ent.detection_r and closest_target:
            ent.move_toward(closest_target.x, closest_target.y)
            if ent.distance_from(closest_target) < (ent.radius + closest_target.radius):
                munch.play()
                closest_target.type = ent.type
                ent.last_eaten = now
                if ent.type == "red":
                    red_count += 1
                    green_count -= 1
                elif ent.type == "blue":
                    blue_count += 1
                    red_count -= 1
                elif ent.type == "green":
                    green_count += 1
                    blue_count -= 1
                    
        else:
            ent.move_toward(randint(0, scrn_rect.width), randint(0, scrn_rect.height))
        
        if now - ent.last_eaten > ent.hungry_time:
            entities.remove(ent)
            if ent.type == "red":
                red_count -= 1
            elif ent.type == "blue":
                blue_count -= 1
            elif ent.type == "green":
                green_count -= 1
        
        ent.drawme()
        
def draw_graph():
    font = pygame.font.SysFont("Arial", 24)
    default_width = 30
    pygame.draw.rect(scrn, "white", graph)
    
    pygame.draw.rect(scrn, "red", (graph.left + 200, graph.bottom - 50 - red_count, \
    default_width, red_count))
    pygame.draw.rect(scrn, "green", (graph.right - 200 - default_width, graph.bottom - 50 - green_count, \
    default_width, green_count))
    pygame.draw.rect(scrn, "blue", (graph.width / 2 - (default_width / 2), graph.bottom - 50 - blue_count, \
    default_width, blue_count))
    
    red_text = font.render(f"{red_count}", True, "black")
    blue_text = font.render(f"{blue_count}", True, "black")
    green_text = font.render(f"{green_count}", True, "black")
    
    scrn.blit(red_text, (graph.left + 200, graph.bottom - 50))
    scrn.blit(green_text, (graph.right - 200 - default_width, graph.bottom - 50))
    scrn.blit(blue_text, (graph.width / 2 - (default_width / 2), graph.bottom - 50))
    
    
# main loop        
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        
    scrn.fill((0, 0, 0))
    
    movement_brain()
    draw_graph()
    
    pygame.display.flip()

pygame.quit()