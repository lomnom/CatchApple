from Game import *

def positionBasketInner():
	global insideBasket
	insideBasket=Entity(
		"",
		basket.x+1,maxy-3,
		1,3
	)

apples=[]
def generateStatic(rows,columns,maxx,maxy):
	global deathline,frames,circles,scoreboard,apples,basket,insideBasket
	circles="◔◑◕●"
	scoreboard=Entity("",0,0)
	basket=Entity(
		yellow+
		 "█░░░█"+"\n"
		"\\███/",
		columns//2,maxy-3,
		2,5
	)
	positionBasketInner()
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

def checkAppleCatch(apple):
	return apple.inside(basket) and not apple.inside(insideBasket)

def checkAppleDeath(apple):
	return apple.inside(deathline)

def catch(appleN):
	global apples,score,caught
	apple=apples.pop(appleN)
	score+=3+apple.speed
	caught+=1

def miss(appleN):
	global apples,score,missed
	apple=apples.pop(appleN)
	score-=(4-apple.speed)
	missed+=1

def handleMove(appleN): # handle apple movement
	apple=apples[appleN]
	if checkAppleDeath(apple):
		miss(appleN)
		raise StopIteration
	elif checkAppleCatch(apple):
		catch(appleN)
		raise StopIteration

ticklock=lock()
tps=15 #game speed
score,caught,missed=0,0,0
def tick(): #spawn and move apples
	global apples,score
	ticklock.acquire()
	for appleN,apple in enumerate(apples):
		nextRY=apple.ry+(3+apple.speed)/tps
		try:
			y=apple.y
			for pos in range(1+(int(nextRY)-apple.y)):
				apple.y=y+pos
				handleMove(appleN)
		except StopIteration:
			continue

		apple.ry=nextRY
		apple.y=int(nextRY)

		if random(1,tps*20)==1:
			if random(0,1):
				apple.x+=1
			else:
				apple.x-=1
		apple.bound()

	if random(1,tps*3)==1:
		spawn(random(0,maxx))
	ticklock.release()

def move(direction,amount=2):
	ticklock.acquire()
	global apples

	if direction=="w": basket.x-=amount
	elif direction=="a": basket.x-=amount
	elif direction=="s": basket.x+=amount
	elif direction=="d": basket.x+=amount
	basket.bound()
	positionBasketInner()
	for appleN,apple in enumerate(apples):
		if checkAppleCatch(apple):
			catch(appleN)
	update()
	ticklock.release()
	
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
		"up":Action(move,"w",amount=1),
		"a":Action(move,"a"),
		"left":Action(move,"a",amount=1),
		"s":Action(move,"s"),
		"down":Action(move,"s",amount=1),
		"d":Action(move,"d"),
		"right":Action(move,"d",amount=1),
		"q":Action(stop),
		"default":Action(wrongKey)
	})
	handler.handle()

start()

while running:
	tick()
	update()
	wait(1/tps)
