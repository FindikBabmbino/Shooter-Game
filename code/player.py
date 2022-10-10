import pygame,sys
from settings import *
from pygame.math import Vector2 as vector
from entity import Entity


class Player(Entity):
	def __init__(self,pos,groups,path,collision_sprites,shoot):
		super().__init__(pos,path,groups,shoot)
		#collision
		self.collision_sprites=collision_sprites

		#vertical
		self.gravity=15
		self.jump_speed=1400
		self.on_floor=False

		self.moving_floor=None

		self.health=10



	def get_status(self):
		#idle
		if self.direction.x==0 and self.on_floor:
			self.status=self.status.split("_")[0]+"_idle"


		#jump
		if self.direction.y!=0 and not self.on_floor:
			self.status=self.status.split("_")[0]+"_jump"

		#duck
		if self.duck and self.on_floor:
			self.status=self.status.split("_")[0]+"_duck"

	def check_contact(self):
		bottom_rect=pygame.Rect(0,0,self.rect.width,5)
		bottom_rect.midtop=self.rect.midbottom
		for sprite in self.collision_sprites.sprites():
			if sprite.rect.colliderect(bottom_rect):
				if self.direction.y>0:
					self.on_floor=True
				if hasattr(sprite,"direction"):
					self.moving_floor=sprite




	def input(self):
		keys=pygame.key.get_pressed()

		if keys[pygame.K_d]:
			self.direction.x=+1
			if self.on_floor:
				self.status="right"
		elif  keys[pygame.K_a]:
			self.direction.x=-1
			if self.on_floor:
				self.status="left"
		else:
			self.direction.x=0

		if keys[pygame.K_SPACE] and self.on_floor:
			self.direction.y=-self.jump_speed

		if keys[pygame.K_LCTRL]:
			self.duck=True
		else:
			self.duck=False

		if keys[pygame.K_LSHIFT] and self.can_shoot:
			direction=vector(1,0) if self.status.split("_")[0]=="right" else vector(-1,0)
			pos=self.rect.center+direction*80
			y_offset=vector(0,-16) if not self.duck else vector(0,10)
			self.shoot(pos+y_offset,direction,self)
			self.shoot_time=pygame.time.get_ticks()
			self.can_shoot=False

	def collision(self,direction):
		for sprite in self.collision_sprites.sprites():
			if sprite.rect.colliderect(self.rect):
				if direction=="horizontal":
					if self.rect.left<=sprite.rect.right and self.old_rect.left>=sprite.old_rect.right:
						self.rect.left=sprite.rect.right 
					if self.rect.right>=sprite.rect.left and self.old_rect.right<=sprite.rect.left:
						self.rect.right=sprite.rect.left
					self.pos.x=self.rect.x
				else:
					if self.rect.bottom>=sprite.rect.top and self.old_rect.bottom<=sprite.old_rect.top:
						self.rect.bottom=sprite.rect.top 
						self.on_floor=True
					if self.rect.top<=sprite.rect.bottom and self.old_rect.top>=sprite.rect.bottom:
						self.rect.top=sprite.rect.bottom
					self.pos.y=self.rect.y
					self.direction.y=0
		if self.on_floor and self.direction.y!=0:
			self.on_floor=False

	def move(self,dt):

		self.pos.x+=self.direction.x*self.speed*dt
		self.rect.x=round(self.pos.x)
		self.collision("horizontal")

		#gravity
		self.direction.y+=self.gravity
		self.pos.y+=self.direction.y*dt

		#glue the player the the platform
		if self.moving_floor and self.moving_floor.direction.y>0 and self.direction.y>0:
			self.direction.y=0
			self.rect.bottom=self.moving_floor.rect.top
			self.pos.y=self.rect.y
			self.on_floor=True

		self.rect.y=round(self.pos.y)
		self.collision("vertical")
		self.moving_floor=None

	def check_death(self):
		if self.health<=0:
			pygame.quit()
			sys.exit()


	def update(self,dt):
		self.old_rect=self.rect.copy()
		self.input()
		self.move(dt)
		self.check_contact()
		self.animate(dt)
		self.get_status()
		self.reset_shoot()
		self.check_death()
		self.vulnerability_timer()
		self.blink()