#!/usr/bin/python
import sys
import zerorpc
from PIL import Image, ImageEnhance, ImageMath, ImageChops
import ImageFont, ImageDraw
from colorsys import hsv_to_rgb, rgb_to_hsv
import time
import numpy 
import math
import random
import socket
import gc
import RPi.GPIO as GPIO           # Allows us to call our GPIO pins and names it just GPIO
from dotstar import Adafruit_DotStar


gc.enable()
numpixels = 280          # Number of LEDs in strip
pixelrow = 28 			# num in LEDs in one row
pixelcol = numpixels/pixelrow 			# num in LEDs in one col
pixelBuffer=numpy.array(range(numpixels), dtype=numpy.uint32)

# Here's how to control the strip from any two GPIO pins:
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, 8000000,order='brg') #dropped clock speed from 12m to 8m to reduce "red flicker"

# =================================== Defines hardware utility buttons
buttonpin = 6
debugpin=21
buttonclicklatch = False
GPIO.setmode(GPIO.BCM)           # Set's GPIO pins to BCM GPIO numbering
# GPIO.setup(buttonpin, GPIO.IN)           # Set our input pin to be an input
GPIO.setup(buttonpin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(debugpin, GPIO.IN, pull_up_down = GPIO.PUD_UP)


baseImage=Image.new("RGB",(pixelrow,pixelcol),(204,191,153))
baseDraw=ImageDraw.Draw(baseImage)
baseFader = ImageEnhance.Brightness(baseImage)
basePixels=baseImage.load()

overlayImage=Image.new("RGB",(pixelrow,pixelcol),(204,191,153))
overlayDraw=ImageDraw.Draw(overlayImage)
overlayDraw.fontmode = "1"
usr_font = ImageFont.truetype("FreeMonoBold.ttf", 9)

overlayPixels=overlayImage.load() 
# -------------------- early load functions
def coordToLight (x,y):
	lightPos = y*pixelrow
	if(y%2==1):
		lightPos+=x
	else:
		lightPos+=(pixelrow-x-1)
	return lightPos
def RGBto32(rIn,gIn,bIn):
	pass
	return ( ( rIn << 16 ) | ( gIn << 8 ) | bIn )
def getPixel(x,y):
	global colortuple, basePixels
	colortuple=basePixels[x,y]
	return RGBto32(colortuple[0],colortuple[1],colortuple[2])

def writeBuffer():
	global strip,x,y
	for x in range(0,pixelrow):           # For each column of image...
		for y in range(0,pixelcol):  # For each pixel in column...
			strip.setPixelColor((coordToLight(x,y)),getPixel(x,y))


ImageDraw.Draw(overlayImage)
strip.begin()           # Initialize pins for output

writeBuffer()
strip.show()             # Refresh LED strip



print overlayImage.size
print "waiting 5 seconds"
time.sleep(5)
try:
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('google.com', 0)) 
	wifiIP=s.getsockname()[0]
except Exception:
	wifiIP="NO WIFI"
print "WiFi IP: "+wifiIP
argument = ""
looping=True


startTime=time.time()

# print time.strftime("Start at %H:%M:%S %Z", time.localtime(startTime))
# =================================== server-modifiable params ===========
# class interfaceComm(object):
# 	def getparams(self, params):
# 		print "interfaceComm says:"+str(params)
# 		return params
# listenServer = zerorpc.Server(interfaceComm())
# listenServer.bind("tcp://0.0.0.0:4242")
# listenServer.run()

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")
# print c.hello("RPC")
# print c.broadcastParams("RPC")
clientParams=c.broadcastParams("RPC")
argument="flurry"
if clientParams is None:
	
	clientParams={}
clientParams["brightness"]=255
clientParams["hue"]=32
clientParams["hue2"]=25
clientParams["saturation"]=83
clientParams["count"]=15
clientParams["speed"]=82
clientParams["offset"]=50
clientParams["vecx"]=0
clientParams["vecy"]=0
clientParams["radius"]=3

# print clientParams

masterHue = 0  # 0-255,      corresponds to Wheel() color
brightness = 255 # 0-255,    overall brightness. how the modules handle it will vary

# ========================================================================

twoPi=6.283185307
phaseAlpha=(twoPi)/pixelrow
frameMillis=1.0
lastMillis=time.time()*1000-1
thisMillis=time.time()*1000
timerMillis=1.0

speedcoeff=1.0
speedphase=1.0
incrementR=0.0
incrementG=0.0
incrementB=0.0
chaseFreq=0.0
chasePhase=0.0
phaseAlpha=0.0
flangeAlpha=0.0
speedPhaseIncrementer=0.0
flangephase=0.0
flangePhaseIncrementer=0.0
spread=0.0
parameter=None
loopIterations=0
posx=0.0
posy=0.0
i = 0
j = 0.0
x=0
y=0
h=0
r=0
g=0
b=0
add_r =0
add_g=0
add_b = 0
colortuple=(0,0,0)
pixColor=0
wid=1.5
lightPos=0
FLURRY_COUNT=100
SCURRY_COUNT=100
VORTEX_COUNT=100
scurryList=[]
vortexList=[]
class ScurryElement:
	'defines parameters for one scurry element'
	def __init__(self,x,y,dx,dy,color,radius):
		self.x=x
		self.y=y
		self.dx=dx
		self.dy=dy
		self.color=color
		self.radius=radius

	def step(self):
		spd=float(clientParams["speed"])/50
		self.dx+=(self.x-pixelrow*float(clientParams["offset"])/100)/pixelrow/200+random.uniform(-0.02*spd,.02*spd)
		self.dy+=random.uniform(-0.01*spd,.01*spd)
		self.x+=self.dx
		self.y+=self.dy
		if (self.x<0 or self.x>pixelrow):
			self.x=pixelrow*float(clientParams["offset"])/100
			self.dx=0
			self.dy=0
	def draw(self,idx):
		scaling=1-abs((self.x-(pixelrow/2))/pixelrow)
		bright=float(clientParams["brightness"])/255
		if (idx<=int(clientParams["count"])):
			for x in range(int(self.x-self.radius*scaling),int(self.x+self.radius*scaling+1)):         
				for y in range(int(self.y-self.radius*scaling),int(self.y+self.radius*scaling+1)):  
					addPixel(x%pixelrow,
						y%pixelcol,
						dimColor(
							desaturateColor(Wheel(self.color+int(clientParams["hue"])%256),float(clientParams["saturation"])/100),
							# Wheel(int(clientParams["hue"])),
							max(0,(self.radius*scaling-dist(x,y,self.x,self.y))/self.radius*scaling/2*bright)
						)
					)

class VortexElement:
	'defines parameters for one vortex element'
	def __init__(self,x,y,dx,dy,color,radius):
		# x,y are the initial coordinates of the point
		self.x=x
		self.y=y
		# dx, dy are the initial vector. these will add with user vector params 
		self.dx=dx
		self.dy=dy
		# color is the color offset, modified by the user Hue/Hue2 sliders
		self.color=color
		#radius is the blob radius, with a linear falloff
		# self.radius=radius ------- setting this via slider now
	# active user parameters:
	# speed, brightness, count, hue, hue2, saturation
	# new ones:
	# vecx, vecy, radius
	def step(self):
		spd=float(clientParams["speed"])/50
		self.x+=self.dx+float(clientParams["vecx"])*spd
		self.y+=self.dy+float(clientParams["vecy"])*spd
		#add the x,y mod clamp here
		self.x = self.x%pixelrow
		self.y = self.y%pixelcol
		

	def draw(self,idx):
		
		bright=float(clientParams["brightness"])/255
		if (idx<=int(clientParams["count"])):
			thiscolor = Wheel(self.color+int(clientParams["hue"])%256) if idx%2=0 else Wheel(self.color+int(clientParams["hue2"])%256)
			for x in range(int(self.x-float(clientParams["radius"])),int(self.x+float(clientParams["radius"])+1)):         
				for y in range(int(self.y-float(clientParams["radius"])),int(self.y+float(clientParams["radius"])+1)):  
					addPixel(x%pixelrow,
						y%pixelcol,
						dimColor(
							desaturateColor(thiscolor),float(clientParams["saturation"])/100),
							max(0,(float(clientParams["radius"])-dist(x,y,self.x,self.y))/float(clientParams["radius"])/2*bright)
						)
					)


def readParams():
	global clientParams, c, argument
	receivedParams = c.broadcastParams("RPC")
	if not receivedParams is None:
		for key in receivedParams:
			if key == "argument":
				# print key+"-"+receivedParams[key]
				argument=receivedParams[key]
			else:
				clientParams[key]=receivedParams[key]


flurryColor=numpy.array(range(FLURRY_COUNT), dtype=numpy.uint32)
# flurryCoeff=[[0 for x in range(FLURRY_COUNT)] for y in range(4)] 
# point number, sin parameter, x/y
flurryCoeff=numpy.zeros((FLURRY_COUNT,4,2))
if (len(sys.argv)>1):
	argument=sys.argv[1]
if (len(sys.argv)>2):
	parameter=sys.argv[2]
shownames=[
"rainbow",
"blank",
"flurry",
"scurry",
"vortex",
"wheelbuster",
"twinkle",
"superwhite",
"testpattern"
]
showcount=len(shownames)
currentShow=0


def rainbowPulse():
	for x in range(0,pixelrow):           # For each column of image...
		for y in range(0,pixelcol):  # For each pixel in column...
			# strip.setPixelColor((coordToLight(x,y)),Wheel((pixelcolor+x*256/30)%256))
			setPixel(x,y,dimColor(
							(Wheel((pixelcolor+x*int(clientParams["speed"]))%256)),
							# Wheel(int(clientParams["hue"])),
							max(0,float(clientParams["brightness"])/255)
						))
def flurryInit():
	for i in range(0,FLURRY_COUNT):
		flurryColor[i]=random.randrange(-30,30)
		flurryCoeff[i][0][0]=random.randrange(628)/100
		for j in range(1,4):
			flurryCoeff[i][j][0]=random.randrange(1000)/1000.0
			flurryCoeff[i][j][1]=random.randrange(1000)/1000.0
def flurry():
	global posx,posy, i,x,y, wid, baseImage
	fade(0.93)
	bright=float(clientParams["brightness"])/255

	# strip.clear()
	# clearImg(baseImage)
	speedIncrement=float(clientParams["speed"])/50*incrementR
	for i in range(0,int(clientParams["count"])):
		posx=((
		 math.sin(flurryCoeff[i][0][0]+flurryCoeff[i][1][0]*speedIncrement)
		+math.sin(flurryCoeff[i][0][0]+flurryCoeff[i][2][0]*speedIncrement)
		+math.sin(flurryCoeff[i][0][0]+flurryCoeff[i][3][0]*speedIncrement)
		)
		/3+.75)*pixelrow
		posy=((
		 math.sin(flurryCoeff[i][0][1]+flurryCoeff[i][1][1]*speedIncrement)
		+math.sin(flurryCoeff[i][0][1]+flurryCoeff[i][2][1]*speedIncrement)
		+math.sin(flurryCoeff[i][0][1]+flurryCoeff[i][3][1]*speedIncrement)
		)
		/3+.75)*(pixelrow)
		thisHue = int(clientParams["hue2"]) if i==int(clientParams["count"])-1 else int(clientParams["hue"])
		for x in range(int(posx-wid),int(posx+wid)):           # For each column of image...
			for y in range(int(posy-wid),int(posy+wid)):  # For each pixel in column...
				
				addPixel(x%pixelrow,
					y%pixelcol,
					dimColor(
						desaturateColor(
						Wheel(
							(flurryColor[i]+thisHue)%256)
							,float(clientParams["saturation"])/100),
							max(0,(wid-dist(x,y,posx,posy))/wid/2*bright)
				# flurryColor[i]
					)
				)


		# for y in range(0,int(numpixels/pixelrow)):  # For each pixel in column...
		# addToPixelColor((coordToLight(int(posx)%pixelrow,y)),dimColor(flurryColor[i],.125))

def scurryInit():
	global scurryList
	colorBase=0
	scurryList=[
		ScurryElement(pixelrow/2,
		random.randrange(pixelcol),
		0,
		0,
		(colorBase+random.randrange(-20,20)),
		1) for i in range(SCURRY_COUNT)
		]
def scurry():
	global scurryList
	fade(0.8)
	for index, scurryObject in enumerate(scurryList):
		scurryObject.step()
		scurryObject.draw(index)

def vortexInit():
	global vortexList
	colorBase=0
	vortexList=[
		VortexElement(
		random.randrange(pixelrow),
		random.randrange(pixelcol),
		0,
		0,
		(colorBase+random.randrange(-20,20)),
		1) for i in range(VORTEX_COUNT)
		]
def vortex():
	global vortexList
	fade(0.8)
	for index, vortexObject in enumerate(vortexList):
		vortexObject.step()
		vortexObject.draw(index)


def testPattern():
	fade(0.15)
	for y in range(0,(pixelcol)):  # For each pixel in column...
		addPixel(xoff,y, RGBto32( 0,0,255))
	timePrint()
def twinkle():
	bright=float(clientParams["brightness"])/255
	sat=float(clientParams["saturation"])/100
	speed=float(clientParams["speed"])/100
	cnt=int(clientParams["count"])
	hue=int(clientParams["hue"])
	fade(speed)
	for x in range(0,pixelrow):           # For each column of image...
		for y in range(0,pixelcol):  # For each pixel in column...
			if random.randrange(100)<cnt:
			# strip.setPixelColor((coordToLight(x,y)),Wheel((pixelcolor+x*256/30)%256))
				addPixel(x,y,
					dimColor(
						desaturateColor(Wheel((hue+random.randrange(-20,20))%256),sat)
						,bright
					))

def superwhite():
	bright=float(clientParams["brightness"])/255
	speed=float(clientParams["speed"])/100
	cnt=int(clientParams["count"])

	fade(speed)
	for x in range(0,pixelrow):           # For each column of image...
		for y in range(0,pixelcol):  # For each pixel in column...
			if random.randrange(100)<cnt:
			# strip.setPixelColor((coordToLight(x,y)),Wheel((pixelcolor+x*256/30)%256))
				addPixel(x,y,dimColor(int('ffffff',16),bright))


def timePrint():
	timeColor=Wheel(pixelcolor)
	overlayImage.paste((0,0,0),(0,0,pixelrow,pixelcol)) #clears out the old time from the image
	# overlayDraw.text((0, 3), time.strftime("%H%M%S", time.localtime(time.time()-startTime)), 
	# 	(timeColor  >>16,timeColor>> 8 & 0xff,timeColor& 0x000000ff), 
	# 	font=usr_font)
	if(GPIO.input(debugpin) == False):
		overlayDraw.text((30-serialoff/4, -1), wifiIP,(timeColor  >>16,timeColor>> 8 & 0xff,timeColor& 0x000000ff), font=usr_font)
	else:
		overlayDraw.text((0, -1), str(loopIterations),(timeColor  >>16,timeColor>> 8 & 0xff,timeColor& 0x000000ff), font=usr_font)
	overlayPicture(overlayImage.transpose(Image.FLIP_TOP_BOTTOM))
	

def debugOutput():
	global clientParams
	sys.stdout.write("iteration:"+str(loopIterations))
	# # sys.stdout.write("   baseImage size:"+str(baseImage.size))
	sys.stdout.write("    FPS:"+str(int(1.0/(frameMillis/1000)+.5)))
	# sys.stdout.write("    GC:"+str(gc.get_count()))
	# sys.stdout.write("    elapsed seconds:"+str(time.time()-startTime))
	try:
		sys.stdout.write("    params:"+str(clientParams["count"]))
	except:
		pass
	sys.stdout.write("        "+chr(13))

def wheelBuster():
	bright=float(clientParams["brightness"])/255
	speedIncrement=float(clientParams["speed"])/50*incrementR
	cnt=int(clientParams["count"])
	for x in range(0,pixelrow):           # For each column of image...
		for y in range(0,pixelcol):  # For each pixel in column...
			basePixels[x,y]=dimColor(
						Wheel((x*cnt+y*cnt+int(float(pixelcolor)*speedIncrement))%256),
							bright
					)
					
	# debugOutput()


def Wheel(WheelPos):
	# Input a value 0 to 255 to get a color value.
	# The colours are a transition r - g - b - back to r.
	# WheelPos=WheelPos%256
	if (WheelPos < 85):
		return RGBto32(WheelPos * 3, 255 - WheelPos * 3, 0)
	elif (WheelPos < 170):
		# WheelPos -= 85
		return RGBto32(255 - (WheelPos-85) * 3, 0, (WheelPos-85) * 3)
	else:
		# WheelPos -= 170
		return RGBto32(0, (WheelPos-170) * 3, 255 - (WheelPos-170) * 3)
def setPixel(x,y,color):
	global basePixels
	pass
	basePixels[x,y]=(color  >>16, color  >> 8 & 0xff, color & 0x000000ff)
def dimColor(color, fadeCoeff):
	global add_r, add_g, add_b
	add_r=color  >>16
	add_g=color  >> 8 & 0xff
	add_b=color & 0x000000ff
	return RGBto32(min(int(add_r*fadeCoeff),255),min(int(add_g*fadeCoeff),255),min(int(add_b*fadeCoeff),255))

def addPixel (x,y,color):
	global colortuple, basePixels, add_r, add_g, add_b

	colortuple=basePixels[x,y]
	add_r=color  >>16
	add_g=color  >> 8 & 0xff
	add_b=color & 0x000000ff

	basePixels[x,y]=(min(colortuple[0]+add_r,255),min(colortuple[1]+add_g,255),min(colortuple[2]+add_b,255))


def addToPixelColorRGB(pixel,r,g,b):
	pixColor =pixelBuffer[pixel]
	orig_r=pixColor  >>16
	orig_g=pixColor  >> 8 & 0xff
	orig_b=pixColor & 0x000000ff
	# ( ( r << 16 ) | ( g << 8 ) | b )

	pixelBuffer[pixel]=RGBto32(min(orig_r+r,255),min(orig_g+g,255),min(orig_b+b,255))

def addToPixelColor(pixel,color):
	pixColor =pixelBuffer[pixel]
	orig_r=pixColor  >>16
	orig_g=pixColor  >> 8 & 0xff
	orig_b=pixColor & 0x000000ff
	add_r=color  >>16
	add_g=color  >> 8 & 0xff
	add_b=color & 0x000000ff
	pixelBuffer[pixel]=RGBto32(min(orig_r+add_r,255),min(orig_g+add_g,255),min(orig_b+add_b,255))
def dimColor(pixColor,ratio):
	r=pixColor  >>16
	g=pixColor  >> 8 & 0xff
	b=pixColor & 0x000000ff
	return RGBto32(int(r*ratio),int(g*ratio),int(b*ratio))
def desaturateColor(pixColor, saturation):
	normalized_color = ((pixColor  >>16)/256., (pixColor  >> 8 & 0xff)/256., (pixColor & 0x000000ff)/256.)
	hsv_color = rgb_to_hsv(*normalized_color)
	grayed_hsv_color = (hsv_color[0], saturation, hsv_color[2])
	grayed_rgb_color = hsv_to_rgb(*grayed_hsv_color)
	denormalized_rgb_color = (int(grayed_rgb_color[0]*256), int(grayed_rgb_color[1]*256), int(grayed_rgb_color[2]*256))
	return RGBto32(denormalized_rgb_color[0],denormalized_rgb_color[1],denormalized_rgb_color[2])
def clearImg(img):
	img.paste((0,0,0),(0,0,pixelrow,pixelcol)) #clears out the old time from the image
	return img
def dist(x1,y1,x2,y2):
	pass
	return math.hypot((x2-x1),(y2-y1))
def fade(fadeCoeff):
	global baseImage, baseFader, basePixels
	baseFader = ImageEnhance.Brightness(baseImage)
	baseImage=baseFader.enhance(fadeCoeff)
	basePixels=baseImage.load()


def fadeColor(rCof,gCof,bCof):
	global baseImage, basePixels
	# sys.stdout.write("   baseImage size:"+str(baseImage.size)+chr(13))
	r,g,b=baseImage.split()
	r = r.point(lambda i: i * rCof)
	g = g.point(lambda i: i * gCof)
	b = b.point(lambda i: i * bCof)
	baseImage = Image.merge('RGB', (r, g, b))
	basePixels=baseImage.load()

	# baseImage=out
	# sys.stdout.write("   baseImage size:"+str(baseImage.size)+chr(13))

def forceBlack():
	for h in range(0,numpixels):
		strip.setPixelColor(h,0,0,0)
def dump_garbage():
	gc.collect()
def overlayPicture(thisImg):
	# overlayPixels
	global baseImage, basePixels
	baseImage=ImageChops.add(baseImage,thisImg)
	basePixels=baseImage.load()

	# for x in range(pixelrow):           # For each column of image...
	# 	for y in range(pixelcol):  # For each pixel in column...
	# 		value = overlayPixels[x, y]   # Read pixel in image
	# 		addPixel(x,y, RGBto32(value[0],value[1],value[2]))

xoff=0
yoff=0
serialoff=0
pixelcolor=0
flurryInit()
scurryInit()

# Load image in RGB format and get dimensions:
print "Loading..."


print "Displaying..."
while looping==True:                              # Loop forever
	xoff+=1
	xoff=xoff%pixelrow
	yoff+=1
	yoff=yoff%(pixelcol)
	serialoff+=1
	serialoff=serialoff%(pixelrow*pixelcol)
	pixelcolor+=1
	pixelcolor=pixelcolor%256
	loopIterations+=1
	thisMillis=time.time()*1000
	frameMillis=thisMillis-lastMillis
	lastMillis=thisMillis
	speedPhaseIncrementer=thisMillis/20000
	flangePhaseIncrementer=thisMillis/50000
	speedphase=math.cos(speedPhaseIncrementer)
	flangephase=(math.sin(flangePhaseIncrementer))*4
	incrementR+=.0100*speedcoeff*speedphase*frameMillis/5
	incrementG+=.0103*speedcoeff*speedphase*frameMillis/5
	incrementB+=.0107*speedcoeff*speedphase*frameMillis/5



	if (GPIO.input(buttonpin) == True):
		if buttonclicklatch:
			flurryInit()
			scurryInit()
			currentShow+=1
			currentShow=currentShow%showcount
			argument=shownames[currentShow]
			print "...Button click: "+argument

			buttonclicklatch=False
		
	else:
		buttonclicklatch=True


	if(GPIO.input(debugpin) == False):
		testPattern()
		timePrint()

	elif (argument=="rainbow"):
		rainbowPulse()
		# timePrint()

	elif (argument=="testpattern"):
		testPattern()
		#timePrint()

	elif (argument=="blank"):
		fade(.999)

		# strip.clear()
		# baseImage.paste((0,0,0),(0,0,pixelrow,pixelcol)) #clears out the old time from the image
		# basePixels[15,3]=		Wheel(pixelcolor)
		# timePrint()


		debugOutput()
	elif (argument=="flurry"):
		flurry()
		# timePrint()
	elif (argument=="scurry"):
		scurry()
		# timePrint()

	elif (argument=="vortex"):
		vortex()
		# timePrint()

	elif (argument=="wheelbuster"):
		wheelBuster()
		# timePrint()

	elif (argument=="twinkle"):
		twinkle()
	elif (argument=="superwhite"):
		superwhite()
	elif ((argument=="clear")|(argument=="off")):
		strip.clear()
		looping=False
	else:
		testPattern()


	writeBuffer()
	strip.show()             # Refresh LED strip
	debugOutput()

	time.sleep(max(0,.016667-(time.time()-lastMillis/1000)))
	if (loopIterations%6==0): #polls 10 times a second
		pass
		readParams()
