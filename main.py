import pygame
import os
import random
import time
from pygame.locals import KEYDOWN
from game_objects.ships import Laser, Player, Enemy, Boss, collide, HEIGHT, WIDTH
from game_objects.upgrades import Upgrade

pygame.font.init() #you have to initialize font first (if you want to write in the game)

#Window
WIN = pygame.display.set_mode((WIDTH, HEIGHT)) #WIDTH and HEIGHT are now being defined in the ships module.. This is weird, should be in main.. 

pygame.display.set_caption("Space Invader") #Setting the name of the window

#load music
pygame.mixer.init()


#background
BACKGROUND = pygame.image.load(os.path.join("assets", "background-black.png"))
BACKGROUND = pygame.transform.scale(BACKGROUND, (WIDTH, HEIGHT)) # resizing the background to the width and height of the window



def main():
	"""This functions triggers the game to run"""
	run = True
	paused = False
	FPS = 60
	lvl = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 50)
	lost_font = pygame.font.SysFont("comicsans", 60)
	velocity = (FPS*HEIGHT*WIDTH)*0.0000003#(FPS*HEIGHT)/(WIDTH*2)
	
	laser_velocity = velocity*2

	upgrades = {"left":[], "right":[]}

	enemies = []
	wave_length = 0 
	enemy_velocity = velocity/abs(10-lvl)
	enemy_laser_velocity = enemy_velocity*4
	
	player = Player((WIDTH/2)-50, HEIGHT*0.8)

	clock= pygame.time.Clock()
	lost = False
	lost_count = 0 #variable to determine how many seconds to pauze the game before quiting out after losing. 

	songswitch = 2
	# songswitch=play_music(songswitch)
	# pygame.mixer.music.play(-1)

	def redraw_window(): 
		WIN.blit(BACKGROUND, (0,0)) #first draw background as 1st layer --> With BLIT you can draw SOURCE is picture, dest = coordinates
		

		#draw ships: 
		for enemy in enemies: 
			enemy.draw(WIN)

		player.draw(WIN)

		for location in upgrades:
			for upgrade in upgrades[location]: 
				upgrade.draw(WIN)


		#draw text: 
		active_upgrades = ", ".join(player.upgrades)
		upgrades_label = main_font.render(f"Upgrades: {player.upgrades}", 1, (255,255,255 ))
		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255 ))
		level_label = main_font.render(f"LVL: {lvl}", 1, (255,255,255 ))
		WIN.blit(lives_label, (10,HEIGHT-lives_label.get_height()-10))
		WIN.blit(level_label, ((WIDTH-10)-level_label.get_width(),HEIGHT-level_label.get_height()-10))
		WIN.blit(upgrades_label, (WIDTH/2-upgrades_label.get_width()/2, 10))


		if lost: 
			lost_label = lost_font.render("You lost!!", 1, (255,255,255))
			WIN.blit(lost_label, ((WIDTH/2-lost_label.get_width()/2),HEIGHT/2))

		if paused: 
			paused_label = lost_font.render("Game Paused (press 'p' to unpause)", 1, (255,255,255))
			WIN.blit(paused_label, ((WIDTH/2-paused_label.get_width()/2),HEIGHT/2))

		pygame.display.update() #refreshing display

	while run: 
		clock.tick(FPS) #makes sure the game runs at the frames set by FPS
		if not pygame.mixer.music.get_busy():
			songswitch=play_music(songswitch)
		#handeling player input:
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: #  if someone clicks the X in the corner it makes sure the games ends
				run = False
				pygame.mixer.music.stop()
			elif event.type == KEYDOWN:
				if event.key == pygame.K_p: 
					paused = not paused
					if paused: 
						pygame.mixer.music.pause()
					else: 
						pygame.mixer.music.unpause()

		redraw_window() #drawing background
		if not paused:

			if player.health <= 0:
				lives -= 1
				player.health = 100

			if lives <= 0: 
				lost = True 
				lost_count +=1

			if lost_count >= FPS*2: 
				run = False

			if len(enemies) == 0: 
				lvl+=1 
				add_boss = True
				boss_count = lvl/5
				wave_length+=5
				for _ in range(wave_length): 
					enemy = Enemy(random.randint(player.get_width(), (WIDTH-player.get_width())), random.randint(-2500+lvl*100, -50), random.choice(["red", "blue", "green"]))
					enemies.append(enemy)
					if lvl % 5 == 0 and add_boss == True: 
						if boss_count <=1: 
							add_boss = False
						boss = Boss(random.randint(player.get_width(), (WIDTH-player.get_width())), random.randint(-2500+lvl*100, -50), random.choice(["red", "blue", "green"]), lvl)
						enemies.append((boss))
						boss_count -= 1
					#creating upgrades: 
					if random.randrange(0, int(wave_length/2)) == 1:
						upgrade_spawn_location = random.choice(["left", "right"])
						if upgrade_spawn_location == "left":
							upgrades["left"].append(Upgrade(random.randint(-8000+lvl*100, -50), random.randint(0-HEIGHT/2, HEIGHT*1.5))) 
						else:
							upgrades["right"].append(Upgrade(random.randint(WIDTH+50, WIDTH+8000+lvl*100), random.randint(0-HEIGHT/2, HEIGHT*1.5))) 


			player_velocity = (velocity/2)*(1+(player.upgrades["speed"]-1)/10)
			keys = pygame.key.get_pressed()
			if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.y - player_velocity>0:  #move up if not at limit of screen
				player.y -= player_velocity
			if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.y + player_velocity<HEIGHT-player.get_height():  #down
				player.y += player_velocity 
			if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.x - player_velocity>0: #left
				player.x -= player_velocity 
			if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.x + player_velocity<WIDTH-player.get_width(): #right
				player.x += player_velocity 
			if keys[pygame.K_SPACE]: 
				player.shoot()
			

			#moving enemy objects
			for enemy in enemies[:]: 
				enemy.move(enemy_velocity)
				enemy.move_lasers(enemy_laser_velocity, player)
				if enemy.health <= 0 and enemy in enemies: 
					enemies.remove(enemy)
				if enemy.y + enemy.get_height() > HEIGHT: #if enemy moves beyond frame, lose a live
					lives -= 1
					player.health = 100
					enemies.remove(enemy)
				if random.randrange(0,(FPS*2)) == 1: 
					enemy.shoot()

				if collide(player, enemy): 
					player.health -= 10
					if enemy in enemies:
						enemies.remove(enemy)

			for location in upgrades:
				for upgrade in upgrades[location]: 
					if location == "left": 
						upgrade.move(velocity*0.8)
					else: 
						upgrade.move(-velocity*0.8)
					if collide(player, upgrade): 
						player.upgrades[upgrade.upgrade] += 1
						upgrades[location].remove(upgrade)
				# if upgrade.off_screen: 
				# 	upgrades.remove(upgrade)


			player.move_lasers(-laser_velocity, enemies)

def main_menu(): 
	run = True
	title_font = pygame.font.SysFont("comicsans", 100)
	
	while run: 
		WIN.blit(BACKGROUND, (0,0))
		title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
		WIN.blit(title_label, ((WIDTH/2)-title_label.get_width()/2,(HEIGHT/2)-title_label.get_height()/2))
		pygame.display.update()
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT: #  if someone clicks the X in the corner it makes sure the games ends
			 	pygame.mixer.music.stop()
			 	run = False
			if event.type == pygame.MOUSEBUTTONDOWN: 
				main()	
	pygame.quit()


def play_music(songswitch=1):
	"""Deze functie werkt nog niet correct, onderstaande link kan probleem fixen
https://nerdparadise.com/programming/pygame/part3
	"""
	files = os.listdir(os.path.join("assets")) 
	files = [fl for fl in files if fl.endswith(".mp3")] 
	pygame.mixer.music.load(os.path.join("assets", files[(songswitch % 2)]))
	pygame.mixer.music.play()
	return (songswitch+1)

	

main_menu()

