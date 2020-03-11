# -*- coding: utf-8 -*-

import sys
from Tools import *
import Menu
import PNJ
import Background
translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}

def create(x, y):
	knil = dict()
	knil["x"] = x # position relative par rapport au (0, 0) de l'écran
	knil["y"] = y #        //
	knil["front"] = 3 # Sens
	knil["graphism"] = ["← ", "↑ ", "→ ", "↓ "]
	knil["c"] = knil["graphism"][knil["front"]]

	return knil

def point(k, steer):
	"""Change le sens de Knil"""
	global translation
	direction, sens = translation[steer]
	front = (sens+1)+int(direction=="y")
	if front != k["front"]:
		k["front"] = front # Change le sens
		k["c"] = k["graphism"][front] # Met à jour le caractère
		return True

def move(k, steer):
	"""Fait avancer Knil"""
	global translation
	direction, sens = translation[steer]
	k[direction] += sens

def collide(k, steer, b, pnjs):
	"""Test si Knil peut atteindre la prochaine case"""
	global translation
	direction, sens = translation[steer]

	x0, y0 = Background.getOrigin(b)

	x1 = k["x"] + int(direction=="x")*sens
	y1 = k["y"] + int(direction=="y")*sens


	if x1 < 0 or x1 >= b["COLS"] or y1 < 0 or y1 >= b["ROWS"]:
		return True # Hors-écran

	for pnj in pnjs:
		px, py = PNJ.getPos(pnjs[pnj])
		if x1+x0 == px and y1+y0 == py:
			return True # Collision avec un pnj

	ncase = Background.getCase(b, x0+x1, y0+y1)

	if not ncase["crossable"]:
		return True # Case dure

	return False

def show(k, b):
	x = k["x"]
	y = k["y"]
	x0, y0 = Background.getOrigin(b)
	case = Background.getCase(b, x0+x, y0+y)
	bgcolor = case["bgcolor"]
	color("black", bgcolor)
	goto(y+1, x*2+1)
	if case["crossable"] not in (2,):
		w(k["c"])


def getPos(k):
    return k["x"], k["y"]

def getFrontPos(k):
    q, r = divmod(k["front"], 2)
    direction = ["x", "y"][r]
    sens = q*2-1

    x1 = k["x"] + int(direction=="x")*sens
    y1 = k["y"] + int(direction=="y")*sens

    return x1, y1
