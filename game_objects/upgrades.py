import pygame
import random
import os
import sys
sys.path.append("game_objects")
from ships import HEIGHT, WIDTH


class Upgrade: 
	"""
	This object is responsible for player upgrades. The upgrade is rondomly chosen at spawn time. 
	Once the player collides with the upgrade object, the upgrade is added to player

	Different options are: 
	-guns (max 7 guns)
	-cooldown (9 or 10 is continuous firerate)
	-damage (no cap (but regular enemies die in one shot after lvl 6 or so))
	-speed (speed has no cap, doesn't matter at lvl 14)
	"""

	def __init__(self, x, y): 
		self.x, self.y = x, y
		self.start_x_pos, self.start_y_pos = x, y
		self.img = pygame.image.load(os.path.join("assets", "upgrade.png"))
		self.img = pygame.transform.smoothscale(self.img, (int(self.img.get_width()/6), int(self.img.get_height()/6)))
		self.mask = pygame.mask.from_surface(self.img)
		self.upgrade = random.choice(["guns", "cooldown", "damage", "speed"])

	def draw(self, window): 
		window.blit(self.img, (self.x, self.y))

	def move(self, velocity): 
		self.x += velocity
		if self.start_y_pos <= HEIGHT/2 and self.off_screen(): #(self.x >= -10 and self.x<=WIDTH+10): 
			self.y += abs(velocity)
		if self.start_y_pos >= HEIGHT/2 and self.off_screen(): #(self.x >= -10 and self.x<=WIDTH+10):
			self.y -= abs(velocity)

	def off_screen(self):
		return (self.x <= WIDTH+10 and self.x >= -10)

	def collision(self, obj): 
		return collide(self, obj)