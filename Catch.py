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

from subprocess import run as syscall
from sys import stdin,stdout
from threading import Thread as thread
from time import sleep as wait
from os import get_terminal_size as termsize

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
		for row in range(len(self.sprite)):
			fprint(movecursor.format(
				row=row+self.y+1,
				column=self.x+1
			))
			fprint(self.sprite[row])

	def bound(self):
		self.x=self.x%(columns-self.width)
		self.y=self.y%(rows-self.height)

basket=Entity(
	yellow+
	"█   █"+"\n"
	"◥███◤",
	columns//2,maxy-3,
	2,5
)
def move(direction):
	if direction=="w": basket.x-=1
	elif direction=="a": basket.x-=1
	elif direction=="s": basket.x+=1
	elif direction=="d": basket.x+=1
	basket.bound()
	print(homecursor+cleartoeos)
	basket.update()

def stop():
	global handler
	handler.stop()
	fprint(loadscreen+loadcursor+showcursor) #restore terminal
	syscall(["stty","-cbreak"])
	syscall(["stty","echo"])
	quit()

def start():
	global handler,stop,basket
	syscall(["stty","cbreak"])
	syscall(["stty","-echo"])
	fprint(savecursor+savescreen+hidecursor+homecursor+cleartoeos) #save and prepare terminal
	handler=KeyHandler({
		"w":[move,"w"],
		"a":[move,"a"],
		"s":[move,"s"],
		"d":[move,"d"],
		"q":[stop,()],
		"default":[fprint,("\a",)]
	})
	basket.update()
	handler.handle()

start()