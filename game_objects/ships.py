import pygame
import random
import os
import sys
sys.path.append("space_shooter")

WIDTH, HEIGHT =  1200, 700

#load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

RED_SHIP_HEALTH = 150
GREEN_SHIP_HEALTH = 100
BLUE_SHIP_HEALTH = 50

#player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))


#lasers
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))



class Ship: 
	"""Parent class for defining ships"""
	COOLDOWN = 30

	def __init__(self, x, y, health = 100):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cooldown_counter = 0

	def cooldown(self): 
		if self.cooldown_counter >= self.COOLDOWN: 
			self.cooldown_counter = 0
		elif self.cooldown_counter > 0:
			self.cooldown_counter += 1

	def shoot(self): 
		if self.cooldown_counter == 0: 
			laser = Laser(self.x, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cooldown_counter = 1

	def draw(self, window): 
		window.blit(self.ship_img, (self.x, self.y))
		self.healthbar(window)
		for laser in self.lasers: 
			laser.draw(window)
		# pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50),0)

	def move_lasers(self, velocity, obj): 
		self.cooldown()
		for laser in self.lasers: 
			laser.move(velocity)
			if laser.off_screen(HEIGHT): 
				self.lasers.remove(laser)
			elif laser.collision(obj): 
				obj.health -= 10 
				self.lasers.remove(laser)

	def get_width(self): 
		return self.ship_img.get_width()

	def get_height(self): 
		return self.ship_img.get_height()

	def healthbar(self, window): 
		pygame.draw.rect(window, (255,0,0), (self.x, (self.y-30), self.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, (self.y-30), self.get_width()*(self.health/self.max_health), 10))

"""
Player:
"""
class Player(Ship): 
	COOLDOWN = 30
	STARTING_COOLDOWN = COOLDOWN
	DAMAGE = 15
	STARTING_DAMAGE = DAMAGE

	def __init__(self, x, y, health=100):
		super().__init__(x, y, health)
		self.ship_img = YELLOW_SPACE_SHIP
		self.laser_img = YELLOW_LASER
		# self.cooldown_counter = 3
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health
		self.upgrades = {"guns": 1, "cooldown": 1, "damage": 1, "speed": 1}

	def move_lasers(self, velocity, objs): 
		self.cooldown()
		for laser in self.lasers: 
			laser.move(velocity)
			if laser.off_screen(HEIGHT): 
				self.lasers.remove(laser)
			else: 
				for obj in objs: 
					if laser.collision(obj) and obj in objs: 
						obj.health -= self.DAMAGE #damage enemies
						# objs.remove(obj) 
						if laser in self.lasers:
							self.lasers.remove(laser)

	def shoot(self): 
		super().shoot()
		for upgrade in self.upgrades: 
			if upgrade == "cooldown": 
				self.COOLDOWN = self.STARTING_COOLDOWN * (1-self.upgrades[upgrade]/10)
			elif upgrade == "damage": 
				self.DAMAGE = self.STARTING_DAMAGE*self.upgrades[upgrade]
			elif upgrade == "guns": 
				if self.cooldown_counter == 1:
					extra_guns = []
					gun_positions = [(self.x-self.get_width()/2+10), (self.x+self.get_width()/2-10), 
					(self.x-self.get_width()/1.5), (self.x+self.get_width()/1.5), (self.x-self.get_width()/1.3), 
					(self.x+self.get_width()/1.3)]
					for i in range(self.upgrades[upgrade]-1): 
						if i < len(gun_positions):
							extra_guns.append(Laser(gun_positions[i], self.y+30, self.laser_img))
					self.lasers.extend(extra_guns)
					self.cooldown_counter = 2

	def healthbar(self, window): 
		pygame.draw.rect(window, (255,0,0), (self.x, (self.y+self.get_height()+10), self.get_width(), 10))
		pygame.draw.rect(window, (0,255,0), (self.x, (self.y+self.get_height()+10), self.get_width()*(self.health/self.max_health), 10))


"""
ENEMY SHIPS:
"""

class Enemy(Ship): 
	COLOR_MAP = {
				"red": (RED_SPACE_SHIP, RED_LASER, RED_SHIP_HEALTH),
				"green": (GREEN_SPACE_SHIP, GREEN_LASER, GREEN_SHIP_HEALTH),
				"blue": (BLUE_SPACE_SHIP, BLUE_LASER, BLUE_SHIP_HEALTH)
				}

	def __init__(self, x, y, color): 
		super().__init__(x, y)
		self.ship_img, self.laser_img, self.health = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = self.health		

	def move(self, velocity): 
		self.y += velocity

	def shoot(self): 
		if self.cooldown_counter == 0: 
			laser = Laser((self.x-self.get_width()/2), self.y, self.laser_img)
			self.lasers.append(laser)
			self.cooldown_counter = 1
		

def collide(obj1, obj2): 
	offset_x = int(obj2.x - obj1.x)
	offset_y = int(obj2.y - obj1.y)
	return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


class Boss(Enemy): 
	COOLDOWN = 5

	def __init__(self, x, y, color, lvl_multiplier): 
		super().__init__(x, y, color)
		self.ship_img = pygame.transform.smoothscale(self.ship_img, (int(self.ship_img.get_width()*4), int(self.ship_img.get_height()*4)))
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.health *= (3*lvl_multiplier)
		self.max_health = self.health
		self.move_up = False
		self.move_left = False

	def shoot(self): 
		super().shoot()
		if self.cooldown_counter == 1:
			extra_guns = []
			gun_positions = [(self.x-self.get_width()/2), (self.x+self.get_width()/2), 
			(self.x-self.get_width()/2.5), (self.x+self.get_width()/2.5)]
			for gun_pos in gun_positions: 
				extra_guns.append(Laser(gun_pos, self.y, self.laser_img))
			self.lasers.extend(extra_guns)
			self.cooldown_counter = 2
		
	def move(self, velocity): 
		
		if self.x <= 20: 
			self.move_left = False
		elif self.x >= WIDTH-self.get_width(): 
			self.move_left = True
		if self.move_left: 
			self.x -= velocity
		else: 
			self.x += velocity
		
		#Height control
		if self.y > HEIGHT/2-self.get_height():
			self.move_up = True
		elif self.y < 50: 
			self.move_up = False
		if self.move_up: 
			self.y -= velocity
		else: 
			self.y += velocity 


class Laser: 

	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window): 
		window.blit(self.img, (self.x, self.y))

	def move(self, velocity): 
		self.y += velocity

	def off_screen(self, height):
		return not(self.y <= height and self.y >= -50)

	def collision(self, obj): 
		return collide(self, obj)

