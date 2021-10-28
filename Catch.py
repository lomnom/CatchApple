hidecursor="\033[?25l"
showcursor="\033[?25h"

homecursor="\033[H"

savecursor="\033[s"
loadcursor="\033[u"

savescreen="\033[?47h"
loadscreen="\033[?47l"

cleartoeos="\033[0J"
cleartoeol="\033[0K"
clearscreen="\033[H\033[J"

movecursor="\033[{row};{column}H"

green="\033[32m"
yellow="\033[33m"
red="\033[31m"
blue="\033[34m"
cyan="\033[36m"
default="\033[39m" #reset text color

bold="\033[1m"

from subprocess import run as syscall
from sys import stdin
from threading import Thread as thread
from time import sleep as wait

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

def move(direction):
	print("Moving in {}...".format(direction))

def stop():
	global handler
	handler.stop()
	syscall(["stty","-cbreak"])
	syscall(["stty","echo"])
	quit()

def start():
	global handler,stop
	syscall(["stty","cbreak"])
	syscall(["stty","-echo"])
	handler=KeyHandler({
		"w":[move,"w"],
		"a":[move,"a"],
		"s":[move,"s"],
		"d":[move,"d"],
		"q":[stop,()],
		"default":[print,("oW!",)]
	})
	handler.handle()

start()