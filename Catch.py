from Game import *

apples=[]
def generateStatic(rows,columns,maxx,maxy):
	global deathline,frames,circles,scoreboard,apples,basket,base
	circles="◔◑◕●"
	scoreboard=Entity("",0,0)
	basket=Entity(
		yellow+
		 "█░░░█"+"\n"
		"\\███/",
		columns//2,maxy-3,
		2,5
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
	frames=Entity("",maxx,0)
	frames.frame=0

generateStatic(rows,columns,maxx,maxy)
addhandler(generateStatic) #update on resize

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
	deathline.update()
	for apple in apples:
		apple.update()
	frames.sprite=[circles[(frames.frame%4)-1]]
	frames.update()
	wait(0.01)

	renderLock.release()

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

def catch(appleN):
	global apples,score,caught
	apple=apples[appleN]
	score+=3+apple.speed
	apples.pop(appleN)
	caught+=1

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
					catch(appleN)
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

def move(direction):
	global apples

	if direction=="w": basket.x-=2
	elif direction=="a": basket.x-=2
	elif direction=="s": basket.x+=2
	elif direction=="d": basket.x+=2
	basket.bound()
	base.x=basket.x
	for appleN in range(len(apples)):
		try:
			apple=apples[appleN]
		except IndexError:
			break
		if apple.inside(base):
			catch(appleN)
	update()
	
running=True
def stop():
	global running
	running=False
	handler.stop()
	ungamescr()
	wait(1/tps)
	quit()

def wrongKey(key):
	fprint('\a')

def start():
	global handler
	gamescr()
	handler=KeyHandler({
		"w":Action(move,"w"),
		"up":Action(move,"w"),
		"a":Action(move,"a"),
		"left":Action(move,"a"),
		"s":Action(move,"s"),
		"down":Action(move,"s"),
		"d":Action(move,"d"),
		"right":Action(move,"d"),
		"q":Action(stop),
		"default":Action(wrongKey)
	})
	handler.handle()

start()

while running:
	tick()
	update()
	wait(1/tps)