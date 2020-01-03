# -*- coding: utf-8 -*-

from tkinter import *
import math
import random

class Boid:
    """docstring for Boid."""
    def __init__(self, canvas, x, y, xp, yp, alpha, tag, herd):
        super(Boid, self).__init__()
        self.step = 0
        self.x = x
        self.y = y
        self.xp= xp
        self.yp = yp
        self.alpha = alpha
        self.r = 10
        self.canvas = canvas
        self.tag=tag
        self.herd = herd
        self.herdPosSpeed = dict()
        for boid in self.herd:
            self.herdPosSpeed[boid]=[self.x,self.y]
        self.canvas.create_line(self.drawBoid(), tags=self.tag)

    def drawBoid(self):
        x2 = self.x + self.r*math.cos(self.alpha)
        y2 = self.y - self.r*math.sin(self.alpha)
        x1 = self.x + self.r*math.cos(self.alpha+2*math.pi/3)
        y1 = self.y - self.r*math.sin(self.alpha+2*math.pi/3)
        x3 = self.x + self.r*math.cos(self.alpha+4*math.pi/3)
        y3 = self.y - self.r*math.sin(self.alpha+4*math.pi/3)
        return (x1,y1,x2,y2,x3,y3)

    def move(self):
        self.step+=1
        if self.x <= 900 and self.x >= 0:
            self.x+=self.xp
        elif self.x<0:
            self.x = 900+self.xp
        elif self.x>900:
            self.x = self.xp

        if self.y <= 900 and self.y >= 0:
            self.y+=self.yp
        elif self.y<0:
            self.y = 900+self.yp
        elif self.y>900:
            self.y = self.yp

        self.alpha = math.atan2(-self.yp,self.xp)
        self.canvas.coords(self.tag, self.drawBoid())
        self.canvas.after(50, self.updateSpeed)

    def updateSpeed(self):
        c = self.converge()
        d = self.diverge()
        v = self.adjustVelocity()
        self.xp = c[0]+d[0]+v[0]
        self.yp = c[1]+d[1]+v[1]
        self.move()

    def converge(self):
        COM = [0,0]
        for tag in self.herd:
            if not tag == self.tag:
                COMx, COMy = self.getCOM(tag)
                COM[0]+=COMx
                COM[1]+=COMy
        COM[0]/=(len(self.herd)-1)
        COM[1]/=(len(self.herd)-1)
        COMx, COMy = self.getCOM(self.tag)
        return (math.ceil((COM[0]-COMx)/100),math.ceil((COM[1]-COMy)/100))

    def diverge(self):
        d = [0,0]
        th = 10
        COMx, COMy = self.getCOM(self.tag)
        for tag in self.herd:
            if not tag == self.tag:
                COMxi, COMyi = self.getCOM(tag)
                if abs(COMxi-COMx)<th and abs(COMyi-COMy)<th:
                    d[0]-=(COMxi-COMx)
                    d[1]-=(COMyi-COMy)
        return d

    def adjustVelocity(self):
        v = [0,0]
        for tag in self.herd:
            if not tag == self.tag:
                lastPos = self.herdPosSpeed[tag]
                COMx, COMy = self.getCOM(tag)
                self.herdPosSpeed[tag] = [COMx,COMy]
                v[0]+=COMx-lastPos[0]
                v[1]+=COMy-lastPos[1]
        v[0]/=((len(self.herd)-1)*2)
        v[1]/=((len(self.herd)-1)*2)
        return v

    def getCOM(self, tag):
        coordsTag = self.canvas.bbox(tag)
        COMx = int((coordsTag[2]+coordsTag[0])/2)
        if COMx < 0:
            COMx = 900 - COMx
        elif COMx > 900:
            COMx -= 900
        COMy = int((coordsTag[3]+coordsTag[1])/2)
        if COMy < 0:
            COMy = 900 - COMy
        elif COMy > 900:
            COMy -= 900
        return (COMx,COMy)

def main():

    root = Tk()
    root.title("Boids")
    root.resizable(False,False)
    canvas = Canvas(root, width = 900, height = 900)
    canvas.pack()

    # create two ball objects and animate them

    listOfTags = ["boid%s"%i for i in range(1,50)]
    boids={}
    for tag in listOfTags:
        boids[tag] = Boid(canvas, random.randint(1,899), random.randint(1,899), 0, 0, 0, tag, listOfTags)
        boids[tag].move()

    root.mainloop()


if __name__ == '__main__':
    main()
