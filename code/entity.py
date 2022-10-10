import pygame
from settings import *
from pygame.math import Vector2 as vector
from os import walk
from math import sin


class Entity(pygame.sprite.Sprite):
	def __init__(self,pos,path,groups,shoot):
		super().__init__(groups)

		self.import_assets(path)
		self.frame_index=0
		self.status="right"

		self.image=self.animations[self.status][self.frame_index]
		self.rect=self.image.get_rect(topleft=pos)
		self.old_rect=self.rect.copy()
		self.z=LAYERS["Level"]
		self.mask=pygame.mask.from_surface(self.image)

		self.pos=vector(self.rect.topleft)
		self.direction=vector()
		self.speed=500

		#interaction
		self.shoot=shoot
		self.shoot_time=None
		self.fire_rate=200
		self.can_shoot=True
		self.duck=False

		self.health=3
		self.is_vulnerable=True
		self.hit_time=None

		self.hit=pygame.mixer.Sound("../audio/hit.wav")
		self.hit_sound.set_volume(0.2)

	def blink(self):
		if not self.is_vulnerable:
			if self.wave_value():
				mask=pygame.mask.from_surface(self.image)
				white_surf=mask.to_surface()
				white_surf.set_colorkey((0,0,0))
				self.image=white_surf

	def wave_value(self):
		value=sin(pygame.time.get_ticks())
		if value>=0: return True
		else: return False

	def damage(self):
		if self.is_vulnerable:
			self.health=-1
			self.is_vulnerable=False
			self.hit.play()
			self.hit_time=pygame.time.get_ticks()


	def vulnerability_timer(self):
		if not self.is_vulnerable:
			current_time=pygame.time.get_ticks()
			if current_time-self.hit_time>400:
				self.is_vulnerable=True

	def check_death(self):
		if self.health<=0:
			self.kill()

	def animate(self,dt):
		current_animations=self.animations[self.status]

		self.frame_index+=7*dt
		
		if self.frame_index>=len(current_animations):
			self.frame_index=0
		self.image=current_animations[int(self.frame_index)]
		self.mask=pygame.mask.from_surface(self.image)

	def import_assets(self,path):
		self.animations={}

		for index,file_name in enumerate(walk(path)):
			if index==0:
				for name in file_name[1]:
					self.animations[name]=[]

			else:
				for anim_name in sorted(file_name[2],key=lambda string: int(string.split(".")[0])):
					path=file_name[0].replace("\\","/")+"/"+anim_name
					surf=pygame.image.load(path).convert_alpha()
					key=file_name[0].split("\\")[1]
					self.animations[key].append(surf)

	def reset_shoot(self):
		if not self.can_shoot:
			current_time=pygame.time.get_ticks()

			if current_time-self.shoot_time>self.fire_rate:
				self.can_shoot=True