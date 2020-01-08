# -*- coding: utf-8 -*-

from tkinter import *
import math
import random

class Boid:
    """docstring for Boid."""
    def __init__(self, canvas, x, y, maxX, maxY, tag, herd, obstacles, preys):
        # super(Boid, self).__init__()
        self.x = x
        self.y = y
        self.xp= 0
        self.yp = 0
        self.maxX = maxX
        self.maxY = maxY
        self.alpha = 0
        self.r = 10
        self.canvas = canvas
        self.tag=tag
        self.herd = herd
        self.herdPosSpeed = dict()
        for boid in self.herd:
            self.herdPosSpeed[boid]=[self.x,self.y]
        self.obstacles = obstacles
        self.offset = 10
        self.preys = preys
        self.canvas.create_line(self.drawBoid(), tags=self.tag)
        self.canvas.create_line(0,0,0,0, tags=self.tag+"speed")

    def drawBoid(self):
        x2 = self.x + self.r*math.cos(self.alpha)
        y2 = self.y - self.r*math.sin(self.alpha)
        x1 = self.x + self.r*math.cos(self.alpha+2*math.pi/3)
        y1 = self.y - self.r*math.sin(self.alpha+2*math.pi/3)
        x3 = self.x + self.r*math.cos(self.alpha+4*math.pi/3)
        y3 = self.y - self.r*math.sin(self.alpha+4*math.pi/3)
        return (x1,y1,x2,y2,x3,y3)

    def drawVector(self):
        COMx, COMy = self.getCOM(self.tag)
        self.canvas.coords(self.tag+"speed", COMx, COMy, COMx+self.xp, COMy+self.yp)

    def move(self):
        boundless = True
        if self.x <= self.maxX and self.x >= 0:
            self.x+=self.xp
        elif self.x<0:
            self.x = self.maxX+self.xp if boundless else 0
        elif self.x>self.maxX:
            self.x = self.xp if boundless else self.maxX
        if self.y <= self.maxY and self.y >= 0:
            self.y+=self.yp
        elif self.y<0:
            self.y = self.maxY+self.yp if boundless else 0
        elif self.y>self.maxY:
            self.y = self.yp if boundless else self.maxY


        self.alpha = math.atan2(-self.yp,self.xp)
        self.canvas.coords(self.tag, self.drawBoid())
        self.drawVector()
        self.canvas.after(50, self.updateSpeed)

    def updateSpeed(self):
        c = self.converge()
        d = self.diverge()
        v = self.adjustVelocity()
        i = self.intertia()
        h = self.hunting()
        self.xp = c[0]+d[0]+v[0]+h[0]
        self.yp = c[1]+d[1]+v[1]+h[1]
        self.move()

    def converge(self):
        c = [0,0]
        cf = 80
        COM = [0,0]
        for tag in self.herd:
            if not tag == self.tag:
                COMx, COMy = self.getCOM(tag)
                COM[0]+=COMx
                COM[1]+=COMy
        COM[0]/=(len(self.herd)-1)
        COM[1]/=(len(self.herd)-1)
        COMx, COMy = self.getCOM(self.tag)
        c[0]=math.ceil((COM[0]-COMx)/cf)
        c[1]=math.ceil((COM[1]-COMy)/cf)
        return c

    def diverge(self):
        d = [0,0]
        th = 20
        df = 5
        COMx, COMy = self.getCOM(self.tag)
        for tag in self.herd:
            if not tag == self.tag:
                COMxi, COMyi = self.getCOM(tag)
                if abs(COMxi-COMx)<th and abs(COMyi-COMy)<th:
                    d[0]-=(COMxi-COMx)/df
                    d[1]-=(COMyi-COMy)/df
        return d

    def adjustVelocity(self):
        v = [0,0]
        vf = 2
        for tag in self.herd:
            if not tag == self.tag:
                lastPos = self.herdPosSpeed[tag]
                COMx, COMy = self.getCOM(tag)
                self.herdPosSpeed[tag] = [COMx,COMy]
                v[0]+=COMx-lastPos[0]
                v[1]+=COMy-lastPos[1]
        v[0]/=((len(self.herd)-1)*vf)
        v[1]/=((len(self.herd)-1)*vf)
        return v

    def intertia(self):
        mass = 0.1
        return [int(self.xp*mass), int(self.yp*mass)]

    def hunting(self):
        h = [0,0]
        hf = 50
        preyCOM = self.getCOM(self.preys)
        selfCOM = self.getCOM(self.tag)
        h[0] = int((preyCOM[0]-selfCOM[0])/hf)
        h[1] = int((preyCOM[1]-selfCOM[1])/hf)
        return h

    def obstacleAvoidance(self, xp, yp):
        o = [0,0]
        for obst in self.obstacles:
            xo0,xo1,yo0,yo1 = self.canvas.bbox(obst)
            r = xo1-xo0


    def getCOM(self, tag):
        coordsTag = self.canvas.bbox(tag)
        COMx = int((coordsTag[2]+coordsTag[0])/2)
        if COMx < 0:
            COMx = self.maxX - COMx
        elif COMx > self.maxX:
            COMx -= self.maxX
        COMy = int((coordsTag[3]+coordsTag[1])/2)
        if COMy < 0:
            COMy = self.maxY - COMy
        elif COMy > self.maxY:
            COMy -= self.maxY
        return [COMx,COMy]

class Obstacle:
    def __init__(self, canvas, x, y, r, tag):
        self.x = x
        self.y = y
        self.r = r
        self.canvas = canvas
        self.tag=tag
        self.drawObstacle(self.x, self.y, self.r)

    def drawObstacle(self, x, y, r):
        xtlc = x+r*math.cos(3*math.pi/4)
        ytlc = y+r*math.sin(3*math.pi/4)
        xbrc = x+r*math.cos(7*math.pi/4)
        ybrc = y+r*math.sin(7*math.pi/4)
        self.canvas.create_oval(xtlc,ytlc,xbrc,ybrc, tags=self.tag)

class Prey:
    def __init__(self, canvas, x, y, maxX, maxY, tag, herd, obstacles):
        self.x = x
        self.y = y
        self.xp= 0
        self.yp = 0
        self.maxX = maxX
        self.maxY = maxY
        self.alpha = 0
        self.r = 5
        self.canvas = canvas
        self.tag=tag
        self.obstacles=obstacles
        self.herd = herd
        self.offset = 10
        self.canvas.create_line(self.drawPrey(), tags=self.tag)
        self.canvas.create_line(0,0,0,0, tags=self.tag+"speed")

    def drawPrey(self):
        x2 = self.x + self.r*math.cos(self.alpha)
        y2 = self.y - self.r*math.sin(self.alpha)
        x1 = self.x + self.r*math.cos(self.alpha+2*math.pi/3)
        y1 = self.y - self.r*math.sin(self.alpha+2*math.pi/3)
        x3 = self.x + self.r*math.cos(self.alpha+4*math.pi/3)
        y3 = self.y - self.r*math.sin(self.alpha+4*math.pi/3)
        return (x1,y1,x2,y2,x3,y3)

    def drawVector(self):
        COMx, COMy = self.getCOM(self.tag)
        self.canvas.coords(self.tag+"speed", COMx, COMy, COMx+self.xp, COMy+self.yp)

    def move(self):
        boundless = True
        if self.x <= self.maxX and self.x >= 0:
            self.x+=self.xp
        elif self.x<0:
            self.x = self.maxX+self.xp if boundless else 0
        elif self.x>self.maxX:
            self.x = self.xp if boundless else self.maxX
        if self.y <= self.maxY and self.y >= 0:
            self.y+=self.yp
        elif self.y<0:
            self.y = self.maxY+self.yp if boundless else 0
        elif self.y>self.maxY:
            self.y = self.yp if boundless else self.maxY
        for obst in self.obstacles:
            coordsObs = self.canvas.bbox(obst)
            xo0 = coordsObs[0]
            xo1 = coordsObs[2]
            yo0 = coordsObs[1]
            yo1 = coordsObs[3]
            if self.x > xo0-self.offset and self.x < xo1+self.offset and self.y > yo0-self.offset and self.y < yo1+self.offset:
                COMx, COMy = self.getCOM(obst)
                self.x +=(COMx-xo0) if self.x >= COMx else -(COMx-xo0)
                self.y +=(COMy-yo0) if self.y >= COMy else -(COMy-yo0)

        self.alpha = math.atan2(-self.yp,self.xp)
        self.canvas.coords(self.tag, self.drawPrey())
        self.drawVector()
        self.canvas.after(50, self.updateSpeed)

    def updateSpeed(self):
        maxSpeed = 15
        a = self.avoid()
        c = self.converge()
        self.xp += random.randint(-1,1)+a[0]+c[0]
        if self.xp > maxSpeed:
            self.xp = maxSpeed
        if self.xp < -maxSpeed:
            self.xp = -maxSpeed
        self.yp +=  random.randint(-1,1)+a[1]+c[1]
        if self.yp > maxSpeed:
            self.yp = maxSpeed
        if self.yp < -maxSpeed:
            self.yp = -maxSpeed
        self.move()

    def avoid(self):
        a = [0,0]
        af = -90
        COM = [0,0]
        for tag in self.herd:
            COMx, COMy = self.getCOM(tag)
            COM[0]+=COMx
            COM[1]+=COMy
        COM[0]/=(len(self.herd))
        COM[1]/=(len(self.herd))
        COMx, COMy = self.getCOM(self.tag)
        a[0]=math.ceil((COM[0]-COMx)/af)
        a[1]=math.ceil((COM[1]-COMy)/af)
        return a

    def converge(self):
        c = [0,0]
        cf = 80
        COM = [self.maxX/2,self.maxY/2]
        COMx, COMy = self.getCOM(self.tag)
        c[0]=math.ceil((COM[0]-COMx)/cf)
        c[1]=math.ceil((COM[1]-COMy)/cf)
        return c

    def getCOM(self, tag):
        coordsTag = self.canvas.bbox(tag)
        COMx = int((coordsTag[2]+coordsTag[0])/2)
        if COMx < 0:
            COMx = self.maxX - COMx
        elif COMx > self.maxX:
            COMx -= self.maxX
        COMy = int((coordsTag[3]+coordsTag[1])/2)
        if COMy < 0:
            COMy = self.maxY - COMy
        elif COMy > self.maxY:
            COMy -= self.maxY
        return [COMx,COMy]

def main():

    maxX = 900
    maxY = 900
    root = Tk()
    root.title("Boids")
    root.resizable(False,False)
    canvas = Canvas(root, width = maxX, height = maxY)
    canvas.pack()

    # create two ball objects and animate them
    listOfObstacles = ["obst%s"%i for i in range(1,2)]
    listOfTags = ["boid%s"%i for i in range(1,40)]
    obstacle=dict()
    for obst in listOfObstacles:
        obstacle[obst] = Obstacle(canvas, random.randint(1,maxX-1), random.randint(1,maxY-1), 600, obst)
    prey = Prey(canvas, random.randint(1,maxX-1), random.randint(1,maxY-1), maxX, maxY, "prey", listOfTags, listOfObstacles)
    prey.move()
    boids=dict()
    for tag in listOfTags:
        boids[tag] = Boid(canvas, random.randint(1,maxX-1), random.randint(1,maxY-1), maxX, maxY, tag, listOfTags, listOfObstacles, "prey")
        boids[tag].move()

    root.mainloop()


if __name__ == '__main__':
    main()
