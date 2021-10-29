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
from threading import Lock as lock
from time import sleep as wait
from os import get_terminal_size as termsize
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

circles="◔◑◕●"
frames=Entity("",maxx,0)
frames.frame=0
scoreboard=Entity("",0,0)
apples=[]
basket=Entity(
	yellow+
	"█   █"+"\n"
	"◥███◤",
	columns//2,maxy-3,
	2,5
)
inside=Entity(
	yellow+"░░░",
	basket.x+1,maxy-3,
	1,2
)
base=Entity(
	"",
	basket.x,maxy-2,
	1,5
)
deathline=Entity(
	red+("🔥"*(columns//2))+("^"*(columns%2)),
	0,maxy,
	1,columns
)
renderLock=lock()
def update():
	if renderLock.locked():
		return
	renderLock.acquire()

	frames.frame+=1
	fprint(homecursor+cleartoeos)
	scoreboard.sprite=f"Score: {score}\nCaught: {caught}\nMissed: {missed}"
	scoreboard.update()
	basket.update()
	inside.update()
	deathline.update()
	for apple in apples:
		apple.update()
	frames.sprite=[circles[(frames.frame%4)-1]]
	frames.update()
	wait(0.01)

	renderLock.release()

def move(direction):
	if direction=="w": basket.x-=2
	elif direction=="a": basket.x-=2
	elif direction=="s": basket.x+=2
	elif direction=="d": basket.x+=2
	basket.bound()
	inside.x=basket.x+1
	base.x=basket.x
	update()

def spawn(x):
	global apples
	apples+=[
		Entity(
			choice(["🍎","🍏"]),
			x,0,1,2
		)
	]
	apples[-1].speed=random(0,3)
	apples[-1].time=0
	apples[-1].ry=0

tps=6 #game speed
score,caught,missed=0,0,0
def tick(): #spawn and move apples
	global apples,score,caught,missed
	for appleN in reversed(range(len(apples))):
		apple=apples[appleN]
		nextRY=apple.ry+(3+apple.speed)/tps

		try:
			y=apple.y
			for pos in range(1+(int(nextRY)-apple.y)):
				apple.y=y+pos
				if apple.inside(deathline):
					apples.pop(appleN)
					missed+=1
					raise StopIteration
				elif apple.inside(base):
					score+=3+apple.speed
					apples.pop(appleN)
					caught+=1
					raise StopIteration
		except StopIteration:
			continue

		apple.ry=nextRY
		apple.y=int(nextRY)

		if random(1,tps*100)==1:
			if random(0,1):
				apple.x+=1
			else:
				apple.x-=1
		apple.bound()

	if random(1,tps*3)==1:
		spawn(random(0,maxx))
	
running=True
def stop():
	global running
	running=False
	handler.stop()
	fprint(loadscreen+loadcursor+showcursor) #restore terminal
	syscall(["stty","-cbreak"])
	syscall(["stty","echo"])
	wait(1/tps)
	quit()

def start():
	global handler
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
	handler.handle()

start()

while running:
	tick()
	update()
	wait(1/tps)