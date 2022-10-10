import pygame,sys
from settings import *
from pygame.math import Vector2 as vector
from pytmx.util_pygame import load_pygame
from tile import *
from player import Player
from bullet import Bullet,FireAnimation
from enemy import Enemy
from overlay import Overlay

class Allsprites(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.offset=vector()
		self.display_surface=pygame.display.get_surface()


		#sky
		self.fg_sky=pygame.image.load("../graphics/sky/fg_sky.png").convert_alpha()
		self.bg_sky=pygame.image.load("../graphics/sky/bg_sky.png").convert_alpha()
		self.sky_width=self.bg_sky.get_width()

		self.padding=WINDOW_WIDTH/2
		tmx_map=load_pygame("../data/map.tmx")
		map_width=tmx_map.tilewidth*tmx_map.width+(2*self.padding)
		self.sky_num=int(map_width // self.sky_width)

	def customize_draw(self,player):
		self.offset.x=player.rect.centerx-WINDOW_WIDTH/2
		self.offset.y=player.rect.centery-WINDOW_HEIGHT/2

		for x in range(self.sky_num):
			x_pos=-self.padding+(x*self.sky_width)
			self.display_surface.blit(self.bg_sky,(x_pos-self.offset.x/2.5,800-self.offset.y/2.5))
			self.display_surface.blit(self.fg_sky,(x_pos-self.offset.x/2,800-self.offset.y/2))


		for sprite in sorted(self.sprites(), key= lambda sprite:sprite.z):
			offset_rect=sprite.image.get_rect(center=(sprite.rect.center))
			offset_rect.center-=self.offset
			self.display_surface.blit(sprite.image,offset_rect)

class Game:
	def __init__(self):
		pygame.init()
		self.display_surface=pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
		self.clock=pygame.time.Clock()
		pygame.display.set_caption("Shooter")

		self.all_sprites=Allsprites()
		self.collision_sprites=pygame.sprite.Group()
		self.platform_sprites=pygame.sprite.Group()
		self.bullet_sprites=pygame.sprite.Group()
		self.vulnerable_sprites=pygame.sprite.Group()

		self.bullet_surf=pygame.image.load("../graphics/bullet.png").convert_alpha()
		self.fire_surfs=[pygame.image.load("../graphics/fire/0.png").convert_alpha(),pygame.image.load("../graphics/fire/1.png").convert_alpha()]

		self.music=pygame.mixer.Sound("../audio/music.wav")
		self.music.play(-1)


		self.setup()
		self.overlay=Overlay(self.player)


	def setup(self):
		#tiles
		tmx_map=load_pygame("../data/map.tmx")
		for x,y,surf in tmx_map.get_layer_by_name("Level").tiles():
			CollisionTile((x*64,y*64),surf,[self.all_sprites,self.collision_sprites])

		for layer in ["BG","BG Detail","FG Detail Bottom","FG Detail Top"]:
			for x,y,surf in tmx_map.get_layer_by_name(layer).tiles():
				Tile((x*64,y*64),surf,self.all_sprites,LAYERS[layer])




		#objects
		for obj in tmx_map.get_layer_by_name("Entities"):
			if obj.name=="Player":
				self.player=Player((obj.x,obj.y),[self.all_sprites,self.vulnerable_sprites],"../graphics/player",self.collision_sprites,self.shoot)
			if obj.name=="Enemy":
				Enemy((obj.x,obj.y),"../graphics/enemies/standard",[self.all_sprites,self.vulnerable_sprites],self.shoot,self.player,self.collision_sprites)

		self.platform_border_rects=[]
		for obj in tmx_map.get_layer_by_name("Platforms"):
			if obj.name=="Platform":
				MovingPlatform((obj.x,obj.y),obj.image,[self.all_sprites,self.collision_sprites,self.platform_sprites])
			else:
				border_rect=pygame.Rect(obj.x,obj.y,obj.width,obj.height)
				self.platform_border_rects.append(border_rect)
	

	def platform_collisions(self):
		for platform in self.platform_sprites.sprites():
			for border in self.platform_border_rects:
				if platform.rect.colliderect(border):
					if platform.direction.y <0:
						platform.rect.top=border.bottom
						platform.direction.y=1
					else:
						platform.rect.bottom=border.top
						platform.direction.y=-1
					platform.pos.y=platform.rect.y
				if platform.rect.colliderect(self.player.rect) and self.player.rect.centery>platfrom.rect.centery:
					platform.rect.bottom=self.player.rect.top
					platform.pos.y=platform.rect.y
					platform.direction.y=-1


	def bullet_collisions(self):
		for obstacle in self.collision_sprites.sprites():
			pygame.sprite.spritecollide(obstacle,self.bullet_sprites,True)
		for sprite in self.vulnerable_sprites.sprites():
			if pygame.sprite.spritecollide(sprite,self.bullet_sprites,True,pygame.sprite.collide_mask):
				sprite.damage()


	def shoot(self,pos,direction,entity):
		Bullet(pos,self.bullet_surf,direction,[self.all_sprites,self.bullet_sprites])
		FireAnimation(entity,self.fire_surfs,direction,self.all_sprites)			


	def run_game(self):
		while True:
			for events in pygame.event.get():
				if events.type==pygame.QUIT:
					pygame.quit()
					sys.exit()

			dt=self.clock.tick()/1000

			self.display_surface.fill((249,131,103))
			self.platform_collisions()
			self.all_sprites.update(dt)
			self.bullet_collisions()
			self.all_sprites.customize_draw(self.player)
			self.overlay.display()

			pygame.display.update()