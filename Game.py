hidecursor="\033[?25l"
showcursor="\033[?25h"

homecursor="\033[H"

savecursor="\033[s"
loadcursor="\033[u"

savescreen="\033[?47h"
loadscreen="\033[?47l"

cleartoeos="\033[0J"
cleartoeol="\033[0K"

movecursor="\033[{row};{column}H"

green="\033[32m"
yellow="\033[33m"
red="\033[31m"
blue="\033[34m"
cyan="\033[36m"
default="\033[39m" #reset text color

bold="\033[1m"

from sys import stdin,stdout
from os import get_terminal_size as termsize
from threading import Thread as thread
from subprocess import run as syscall
from threading import Lock as lock
from time import sleep as wait
from random import randint as random
from random import choice 

def sfprint(*stuff):
	if len(stuff)>1:
		stdout.write(" ".join(stuff))
	else:
		stdout.write(stuff[0])

def fprint(*stuff):
	if len(stuff)>1:
		stdout.write(" ".join(stuff))
	else:
		stdout.write(stuff[0])
	stdout.flush()


class KeyHandler:
		def __init__(self,actions):
			self.actions=actions
			self.thread=None
			self.delay=0.05
			self.tasks=[]

		def _handle(self):
			while self.thread!=None:
				try:
					key=stdin.read(1)
					action=self.actions[key]
				except KeyError:
					try:
						action=self.actions["default"]
					except KeyError:
						continue
				self.tasks+=[[key,thread(target=action[0],args=action[1])]]
				self.tasks[-1][1].start()
				for task in reversed(range(len(self.tasks))):
					if not self.tasks[task][1].is_alive():
						self.tasks.pop(task)
				wait(self.delay)

		def handle(self):
			if self.thread==None:
				self.thread=thread(target=self._handle)
				self.thread.start()

		def stop(self):
			self.thread=None
			self.tasks=[]

size=termsize()
rows=size.lines
columns=size.columns
maxx=columns-1
maxy=rows-1

class Entity:
	def __init__(self,sprite,x,y,*hitbox): 
		assert(type(x+y)==int)
		if type(sprite)==str:
			sprite=sprite.split("\n")
		if len(hitbox)==2:
			self.height=hitbox[0]
			self.width=hitbox[1]
		else:
			self.height=len(sprite)
			self.width=len(sprite[0])
		self.sprite=sprite
		self.x=x
		self.y=y

	def update(self):
		if type(self.sprite)==str:
			self.sprite=self.sprite.split("\n")
		if not self.sprite==[]:
			for row in range(len(self.sprite)):
				fprint(movecursor.format(
					row=row+self.y+1,
					column=self.x+1
				))
				fprint(self.sprite[row])
			fprint(default)

	def bound(self):
		self.x=self.x%(columns-self.width)
		self.y=self.y%(rows-self.height)

	def inside(self,entity):
		return self.x>=entity.x and self.x+self.width<=entity.x+entity.width and \
		       self.y>=entity.y and self.y+self.height<=entity.y+entity.height

def gamescr():
	syscall(["stty","cbreak"])
	syscall(["stty","-echo"])
	fprint(savecursor+savescreen+hidecursor+homecursor+cleartoeos) #save and prepare terminal

def ungamescr():
	fprint(loadscreen+loadcursor+showcursor) #restore terminal
	syscall(["stty","-cbreak"])
	syscall(["stty","echo"])