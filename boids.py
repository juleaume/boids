# -*- coding: utf-8 -*-

from tkinter import *
import math
import random


class Boid:
    """docstring for Boid."""

    def __init__(
            self, canvas, x, y, max_x, max_y, tag, herd, obstacles, preys
    ):
        # super(Boid, self).__init__()
        self.x = x
        self.y = y
        self.xp = 0
        self.yp = 0
        self.max_x = max_x
        self.max_y = max_y
        self.alpha = 0
        self.r = 10
        self.canvas = canvas
        self.tag = tag
        self.herd = herd
        self.herdPosSpeed = dict()
        for boid in self.herd:
            self.herdPosSpeed[boid] = [self.x, self.y]
        self.obstacles = obstacles
        self.offset = 10
        self.preys = preys
        self.canvas.create_line(self.draw_boid(), tags=self.tag)
        self.canvas.create_line(0, 0, 0, 0, tags=self.tag + "speed")

    def draw_boid(self):
        x2 = self.x + self.r * math.cos(self.alpha)
        y2 = self.y - self.r * math.sin(self.alpha)
        x1 = self.x + self.r * math.cos(self.alpha + 2 * math.pi / 3)
        y1 = self.y - self.r * math.sin(self.alpha + 2 * math.pi / 3)
        x3 = self.x + self.r * math.cos(self.alpha + 4 * math.pi / 3)
        y3 = self.y - self.r * math.sin(self.alpha + 4 * math.pi / 3)
        return x1, y1, x2, y2, x3, y3

    def draw_vector(self):
        com_x, com_y = self.get_center_of_mass(self.tag)
        self.canvas.coords(self.tag + "speed", com_x, com_y, com_x + self.xp,
                           com_y + self.yp)

    def move(self):
        boundless = True
        if self.max_x >= self.x >= 0:
            self.x += self.xp
        elif self.x < 0:
            self.x = self.max_x + self.xp if boundless else 0
        elif self.x > self.max_x:
            self.x = self.xp if boundless else self.max_x
        if self.max_y >= self.y >= 0:
            self.y += self.yp
        elif self.y < 0:
            self.y = self.max_y + self.yp if boundless else 0
        elif self.y > self.max_y:
            self.y = self.yp if boundless else self.max_y
        for obst in self.obstacles:
            coords_obs = self.canvas.bbox(obst)
            xo0, yo0, xo1, yo1 = coords_obs
            if xo0 - self.offset < self.x < xo1 + self.offset and \
                    yo0 - self.offset < self.y < yo1 + self.offset:
                com_x, com_y = self.get_center_of_mass(obst)
                self.x += (com_x - xo0) if self.x >= com_x else -(com_x - xo0)
                self.y += (com_y - yo0) if self.y >= com_y else -(com_y - yo0)

        self.alpha = math.atan2(-self.yp, self.xp)
        self.canvas.coords(self.tag, self.draw_boid())
        self.draw_vector()
        self.canvas.after(50, self.update_speed)

    def update_speed(self):
        c = self.converge()
        d = self.diverge()
        v = self.adjust_velocity()
        i = self.inertia()
        h = self.hunting()
        self.xp = c[0] + d[0] + v[0] + h[0]
        self.yp = c[1] + d[1] + v[1] + h[1]
        self.move()

    def converge(self):
        c = [0, 0]
        cf = 80
        com = [0, 0]
        for tag in self.herd:
            if not tag == self.tag:
                com_x, com_y = self.get_center_of_mass(tag)
                com[0] += com_x
                com[1] += com_y
        com[0] /= (len(self.herd) - 1)
        com[1] /= (len(self.herd) - 1)
        com_x, com_y = self.get_center_of_mass(self.tag)
        c[0] = math.ceil((com[0] - com_x) / cf)
        c[1] = math.ceil((com[1] - com_y) / cf)
        return c

    def diverge(self):
        d = [0, 0]
        th = 20
        df = 5
        com_x, com_y = self.get_center_of_mass(self.tag)
        for tag in self.herd:
            if not tag == self.tag:
                com_xi, com_yi = self.get_center_of_mass(tag)
                if abs(com_xi - com_x) < th and abs(com_yi - com_y) < th:
                    d[0] -= (com_xi - com_x) / df
                    d[1] -= (com_yi - com_y) / df
        return d

    def adjust_velocity(self):
        v = [0, 0]
        vf = 2
        for tag in self.herd:
            if not tag == self.tag:
                last_pos = self.herdPosSpeed[tag]
                com_x, com_y = self.get_center_of_mass(tag)
                self.herdPosSpeed[tag] = [com_x, com_y]
                v[0] += com_x - last_pos[0]
                v[1] += com_y - last_pos[1]
        v[0] /= ((len(self.herd) - 1) * vf)
        v[1] /= ((len(self.herd) - 1) * vf)
        return v

    def inertia(self):
        mass = 0.1
        return [int(self.xp * mass), int(self.yp * mass)]

    def hunting(self):
        h = [0, 0]
        hf = 50
        prey_com = self.get_center_of_mass(self.preys)
        self_com = self.get_center_of_mass(self.tag)
        h[0] = int((prey_com[0] - self_com[0]) / hf)
        h[1] = int((prey_com[1] - self_com[1]) / hf)
        return h

    def get_center_of_mass(self, tag):
        coords_tag = self.canvas.bbox(tag)
        com_x = int((coords_tag[2] + coords_tag[0]) / 2)
        if com_x < 0:
            com_x = self.max_x - com_x
        elif com_x > self.max_x:
            com_x -= self.max_x
        com_y = int((coords_tag[3] + coords_tag[1]) / 2)
        if com_y < 0:
            com_y = self.max_y - com_y
        elif com_y > self.max_y:
            com_y -= self.max_y
        return [com_x, com_y]


class Obstacle:
    def __init__(self, canvas, x, y, r, tag):
        self.x = x
        self.y = y
        self.r = r
        self.canvas = canvas
        self.tag = tag
        self.draw_obstacle(self.x, self.y, self.r)

    def draw_obstacle(self, x, y, r):
        xtlc = x + r * math.cos(3 * math.pi / 4)
        ytlc = y + r * math.sin(3 * math.pi / 4)
        xbrc = x + r * math.cos(7 * math.pi / 4)
        ybrc = y + r * math.sin(7 * math.pi / 4)
        self.canvas.create_oval(xtlc, ytlc, xbrc, ybrc, tags=self.tag)


class Prey:
    def __init__(self, canvas, x, y, max_x, maxy, tag, herd, obstacles):
        self.x = x
        self.y = y
        self.xp = 0
        self.yp = 0
        self.max_x = max_x
        self.max_y = maxy
        self.alpha = 0
        self.r = 5
        self.canvas = canvas
        self.tag = tag
        self.obstacles = obstacles
        self.herd = herd
        self.offset = 10
        self.canvas.create_line(self.draw_prey(), tags=self.tag)
        self.canvas.create_line(0, 0, 0, 0, tags=self.tag + "speed")

    def draw_prey(self):
        x2 = self.x + self.r * math.cos(self.alpha)
        y2 = self.y - self.r * math.sin(self.alpha)
        x1 = self.x + self.r * math.cos(self.alpha + 2 * math.pi / 3)
        y1 = self.y - self.r * math.sin(self.alpha + 2 * math.pi / 3)
        x3 = self.x + self.r * math.cos(self.alpha + 4 * math.pi / 3)
        y3 = self.y - self.r * math.sin(self.alpha + 4 * math.pi / 3)
        return x1, y1, x2, y2, x3, y3

    def draw_vector(self):
        com_x, com_y = self.getCOM(self.tag)
        self.canvas.coords(self.tag + "speed", com_x, com_y, com_x + self.xp,
                           com_y + self.yp)

    def move(self):
        boundless = True
        if self.max_x >= self.x >= 0:
            self.x += self.xp
        elif self.x < 0:
            self.x = self.max_x + self.xp if boundless else 0
        elif self.x > self.max_x:
            self.x = self.xp if boundless else self.max_x
        if self.max_y >= self.y >= 0:
            self.y += self.yp
        elif self.y < 0:
            self.y = self.max_y + self.yp if boundless else 0
        elif self.y > self.max_y:
            self.y = self.yp if boundless else self.max_y
        for obst in self.obstacles:
            coords_obs = self.canvas.bbox(obst)
            xo0, yo0, xo1, yo1 = coords_obs
            if xo0 - self.offset < self.x < xo1 + self.offset and \
                    yo0 - self.offset < self.y < yo1 + self.offset:
                com_x, com_y = self.getCOM(obst)
                self.x += (com_x - xo0) if self.x >= com_x else -(com_x - xo0)
                self.y += (com_y - yo0) if self.y >= com_y else -(com_y - yo0)

        self.alpha = math.atan2(-self.yp, self.xp)
        self.canvas.coords(self.tag, self.draw_prey())
        self.draw_vector()
        self.canvas.after(50, self.update_speed)

    def update_speed(self):
        max_speed = 15
        a = self.avoid()
        c = self.converge()
        self.xp += random.randint(-1, 1) + a[0] + c[0]
        if self.xp > max_speed:
            self.xp = max_speed
        if self.xp < -max_speed:
            self.xp = -max_speed
        self.yp += random.randint(-1, 1) + a[1] + c[1]
        if self.yp > max_speed:
            self.yp = max_speed
        if self.yp < -max_speed:
            self.yp = -max_speed
        self.move()

    def avoid(self):
        a = [0, 0]
        af = -90
        com = [0, 0]
        for tag in self.herd:
            com_x, com_y = self.getCOM(tag)
            com[0] += com_x
            com[1] += com_y
        com[0] /= (len(self.herd))
        com[1] /= (len(self.herd))
        com_x, com_y = self.getCOM(self.tag)
        a[0] = math.ceil((com[0] - com_x) / af)
        a[1] = math.ceil((com[1] - com_y) / af)
        return a

    def converge(self):
        c = [0, 0]
        cf = 80
        com = [self.max_x / 2, self.max_y / 2]
        com_x, com_y = self.getCOM(self.tag)
        c[0] = math.ceil((com[0] - com_x) / cf)
        c[1] = math.ceil((com[1] - com_y) / cf)
        return c

    def getCOM(self, tag):
        coordsTag = self.canvas.bbox(tag)
        com_x = int((coordsTag[2] + coordsTag[0]) / 2)
        if com_x < 0:
            com_x = self.max_x - com_x
        elif com_x > self.max_x:
            com_x -= self.max_x
        com_y = int((coordsTag[3] + coordsTag[1]) / 2)
        if com_y < 0:
            com_y = self.max_y - com_y
        elif com_y > self.max_y:
            com_y -= self.max_y
        return [com_x, com_y]


def main():
    max_x = 900
    max_y = 900
    root = Tk()
    root.title("Boids")
    root.resizable(False, False)
    canvas = Canvas(root, width=max_x, height=max_y)
    canvas.pack()

    # create two ball objects and animate them
    list_of_obstacles = ["obst%s" % i for i in range(1, 20)]
    list_of_tags = ["boid%s" % i for i in range(1, 40)]
    obstacle = dict()
    for obst in list_of_obstacles:
        obstacle[obst] = Obstacle(canvas, random.randint(1, max_x - 1),
                                  random.randint(1, max_y - 1), 10, obst)
    prey = Prey(
        canvas, random.randint(1, max_x - 1), random.randint(1, max_y - 1),
        max_x, max_y, "prey", list_of_tags, list_of_obstacles
    )
    prey.move()
    boids = dict()
    for tag in list_of_tags:
        boids[tag] = Boid(
            canvas, random.randint(1, max_x - 1), random.randint(1, max_y - 1),
            max_x, max_y, tag, list_of_tags, list_of_obstacles, "prey"
        )
        boids[tag].move()

    root.mainloop()


if __name__ == '__main__':
    main()
