# -*- coding: utf-8 -*-

import sys
from Tools import *
import Map
import Knil

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}

special_carac = {1:"░", 2:"▖", 3:"▗", 4:"▘", 5:"▙", 6:"▚", 7:"▛", 8:"▜", 9:"▝",
				10:"▞", 11:"▟"}

def create(ROWS, COLS, x, y, anchor="nw"):
	assert ROWS%2 == 1
	assert COLS%2 == 1
	assert anchor in ("n", "e", "s", "w", "ne", "nw", "se", "sw", "c")

	background = dict()
	background["ROWS"] = ROWS
	background["COLS"] = COLS
	background["x"] = x
	background["y"] = y
	background["anchor"] = anchor
	background["map"] = Map.create("data.xml")
	return background

def slide(b, steer):
	global translation
	direction, sens = translation[steer]
	b[direction] += sens

def canSlide(b, steer):
	global translation
	direction, sens = translation[steer]

	origin = getOrigin(b)
	if sens == -1:
		return origin[direction=="y"] + sens >= 0
	else:
		if direction == "x":
			return origin[0] + b["COLS"] + sens <= len(b["map"][0])
		else:
			return origin[1] + b["ROWS"] + sens <= len(b["map"])

def show(b, k):
	x0, y0 = getOrigin(b)
	kx, ky = Knil.getPos(k)
	knil_case = getCase(b, kx+x0, ky+y0)
	special_attrib = bool("special_case" in knil_case.keys())
	if special_attrib:
		special_ID = knil_case["special_case"]["attrib"]["id"]
	for j in range(b["ROWS"]):
		goto((j+1), 1)
		for i in range(b["COLS"]):
			case = getCase(b, x0+i, y0+j)
			if "special_case" in case.keys():
				if special_attrib:
					if special_ID != case["special_case"]["attrib"]["id"]:
						case = case["special_case"]
				else:
					case = case["special_case"]
			color(fontcolor=case["fontcolor"], bgcolor=case["bgcolor"])
			for c in case["c"]:
				if isinstance(c, int):
					w(special_carac[c])
				else:
					w(c)
			reset_attributes()

def getOrigin(b):
	x0 = b["x"]-int("c" in b["anchor"])*(b["COLS"]//2)-2*int("e" in b["anchor"])*(b["COLS"]//2)
	y0 = b["y"]-int("c" in b["anchor"])*(b["ROWS"]//2)-2*int("e" in b["anchor"])*(b["ROWS"]//2)
	return x0, y0

def is_case_special(b, location):
	x, y = location
	case = getCase(b, x, y)
	return "special_case" in case.keys()

def is_case_special_activated(b, location, k):
	x, y = location
	x0, y0 = getOrigin(b)
	kx, ky = Knil.getPos(k)
	knil_case = getCase(b, kx+x0, ky+y0)
	special_attrib = bool("special_case" in knil_case.keys())

	case = getCase(b, x, y)
	if "special_case" in case.keys() and special_attrib:
			special_ID = knil_case["special_case"]["attrib"]["id"]
			if special_ID != case["special_case"]["attrib"]["id"]:
				return False
			else:
				return True
	else:
		return False


def getCase(b, x, y):
	return b["map"][y][x]
