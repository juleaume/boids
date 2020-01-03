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
        # self.boid = self.drawBoid(self.x, self.y)
        self.canvas.create_line(self.drawBoid(), tags=self.tag)
        print(self.canvas.bbox(self.tag))

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
        for tag in self.herd:
            if tag==self.tag:
                print("This is %s"%tag)
            else:
                print("Other %s is at %s"%(tag, self.canvas.bbox(tag)))
        print('\n')
        self.xp = math.sin(self.step*math.pi/100)*random.randint(-2,2)
        self.yp = math.cos(self.step*math.pi/100)*random.randint(-2,2)
        self.move()


def main():

    root = Tk()
    root.title("Boids")
    root.resizable(False,False)
    canvas = Canvas(root, width = 900, height = 900)
    canvas.pack()

    # create two ball objects and animate them

    listOfTags = ["boid%s"%i for i in range(1,4)]
    boids={}
    for tag in listOfTags:
        boids[tag] = Boid(canvas, random.randint(1,899), random.randint(1,899), random.randint(1,899), random.randint(1,899), 0, tag, listOfTags)
        boids[tag].move()


    root.mainloop()


if __name__ == '__main__':
    main()
