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
from threading import Lock as lock
from time import sleep as wait
from random import randint as random
from time import perf_counter as timecounter
from random import choice 
import termios
fd=stdin.fileno()

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

mappings={
	0:"ctrl 1",
	27:"ctrl 2",
	28:"ctrl 3",
	29:"ctrl 4",
	30:"ctrl 5",
	31:"ctrl 6",
	127:"ctrl 7",
	23:"ctrl w",
	5:"ctrl e",
	18:"ctrl r",
	20:"ctrl t",
	25:"ctrl y",
	21:"ctrl u",
	9:"ctrl i",
	16:"ctrl p",
	1:"ctrl a",
	4:"ctrl d",
	6:"ctrl f",
	7:"ctrl g",
	8:"ctrl h",
	11:"ctrl k",
	12:"ctrl l",
	26:"ctrl z",
	24:"ctrl x",
	3:"ctrl c",
	2:"ctrl b",
	14:"ctrl n",
	ord("\033"):"escape"
}
def proccessTermChar(char):
	if ord(char) in mappings:
		return mappings[ord(char)]
	else: 
		return char

import select

def stdinempty():
	return select.select([stdin,],[],[],0.0)[0]==[]

def readall(blocking=True): #if its one big write (eg. arrow key), it will onnly get first char :(
	data=stdin.read(1) if blocking else ""
	while not stdinempty():
		data+=stdin.read(1)
	return data

arrowChars={"A":"up","B":"down","C":"right","D":"left"}
arrowModifyers={"2":"shift","3":"option","4":"shift option"}
def keys():
	while True:
		data=readall()
		while data!="":
			if data[0]=='\033' and len(data)>1 and data[1]=='[': #arrow key?
				data=data[2:]
				if data.startswith("1"):
					data+=stdin.read(3)
					data=data[2:]
					if data[0] in arrowModifyers:
						modifyer=arrowModifyers[data[0]]
						data=data[1:]
						if data[0] in arrowChars:
							yield modifyer+" "+arrowChars[data[0]]
							data=data[1:]
				elif data[0] in arrowChars:
					yield arrowChars[data[0]]
					data=data[1:]
			elif data[0]=='\033' and len(data)==1:
				data+=stdin.read(2)
			else:
				yield proccessTermChar(data[0])
				data=data[1:]

class Action:
	def __init__(self,func,*args,**kwargs):
		self.func=func
		self.args=args
		self.kwargs=kwargs
	def run(self):
		return self.func(*self.args,**self.kwargs)

class KeyHandler:
		def __init__(self,actions):
			self.actions=actions
			self.thread=None
			self.delay=0.01

		def _handle(self):
			for key in keys():
				try:
					action=self.actions[key]
				except KeyError:
					try:
						action=self.actions["default"]
						action=Action(action.func,key,*action.args,**action.kwargs)
					except KeyError:
						continue
				thread(target=action.run).start()
				wait(self.delay) #timeframe where key handler can be killed (sketch 1000)
				if self.thread==None:
					break

		def handle(self):
			if self.thread==None:
				self.thread=thread(target=self._handle)
				self.thread.start()

		def stop(self):
			self.thread=None

import signal

handlers={}

def addhandler(function):
	global handlers
	assert(function.__name__ not in handlers)
	handlers[function.__name__]=function

def updateSize(*a):
	global size,rows,columns,maxx,maxy,handlers
	size=termsize()
	rows=size.lines
	columns=size.columns
	maxx=columns-1
	maxy=rows-1
	for handler in handlers:
		handlers[handler](rows,columns,maxx,maxy)

signal.signal(signal.SIGWINCH, updateSize)

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

def raw():
	raw=termios.tcgetattr(fd)
	raw[3]=raw[3] & ~(termios.ECHO | termios.ICANON)
	termios.tcsetattr(fd,termios.TCSADRAIN,raw)

def unraw():
	unraw=termios.tcgetattr(fd)
	unraw[3]=unraw[3] | (termios.ECHO | termios.ICANON)
	termios.tcsetattr(fd,termios.TCSADRAIN,unraw)

def noctrlc():
	noctrlc=termios.tcgetattr(fd)
	noctrlc[3]=noctrlc[3] & ~termios.ISIG
	termios.tcsetattr(fd,termios.TCSADRAIN,noctrlc)

def ctrlc():
	ctrlc=termios.tcgetattr(fd)
	ctrlc[3]=ctrlc[3] | termios.ISIG
	termios.tcsetattr(fd,termios.TCSADRAIN,ctrlc)

def gamescr():
	raw()
	noctrlc()
	fprint(savecursor+savescreen+hidecursor+homecursor+cleartoeos) #save and prepare terminal

def ungamescr():
	fprint(loadscreen+loadcursor+showcursor) #restore terminal
	unraw()
	ctrlc()

class Stopwatch:
	def __init__(self):
		self.reset()

	def start(self):
		self.started=timecounter()

	def stop(self):
		if self.started!=-1:
			self.totalElapsed+=timecounter()-self.started
			self.started=-1
		return self.time()
	end=stop

	def reset(self):
		self.started=-1
		self.totalElapsed=0

	def time(self):
		if self.started!=-1:
			return self.totalElapsed+(timecounter()-self.started)
		else:
			return self.totalElapsed