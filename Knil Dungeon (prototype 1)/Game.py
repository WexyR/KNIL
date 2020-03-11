# -*- coding: utf-8 -*-
import sys
import Knil
import Background
import PNJ
from Tools import *
import Dialog
import Event
import Quest

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}


def create(ROWS, COLS):
	game = dict()
	b = Background.create(ROWS, COLS, 0, 0, anchor="nw")
	k = Knil.create(11, 3)
	d = Dialog.dialog_box_create(ROWS, COLS*2, 0.25)
	Event.create()
	pnjs = PNJ.create("PNJdata.xml")
	q = Quest.init("QuestData.xml")
	game["background"] = b
	game["knil"] = k
	game["dialog_box"] = d
	game["quests"] = q
	game["pnjs"] = pnjs
	game['COLS'] = COLS
	game['ROWS'] = ROWS
	game['RUN'] = False
	return game

def restart(g):
	ROWS, COLS = getDimension(g)
	new_game = create(ROWS, COLS)
	for key in g:
		g[key] = new_game[key]
	setRunning(g, True)

def move(g, steer):
	global translation

	b = g["background"]
	k = g["knil"]

	direction, sens = translation[steer]

	modification = False

	m = Knil.point(k, steer)
	if m:
		modification = True

	centered = k[direction] != [b["COLS"]//2, b["ROWS"]//2][direction=="y"]
	bgcs = Background.canSlide(b, steer)

	if not Knil.collide(k, steer, b, g["pnjs"]):
		if centered or not bgcs:
			Knil.move(k, steer)
			modification = True
		elif bgcs:
			Background.slide(b, steer)
			modification = True
	return modification

def display(g):
	b = g["background"]
	k = g["knil"]
	pnjs = g["pnjs"]
	ROWS, COLS = getDimension(g)
	Background.show(b, k)
	Knil.show(k, b)
	for pnj in pnjs.keys():
		x, y = PNJ.getPos(pnjs[pnj])
		x0, y0 = Background.getOrigin(b)
		if x >= x0 and x < x0 + COLS and y >= y0 and y < y0 + ROWS:
			PNJ.display(pnjs[pnj], b, k)

	# reset_attributes()
	# goto(33,1)
	# w(str(g["quests"]))


def exe(g):
	b = g["background"]
	k = g["knil"]
	d = g["dialog_box"]
	q = g["quests"]

	x0, y0 = Background.getOrigin(b)
	x1, y1 = Knil.getFrontPos(k)
	nx, ny = x0+x1, y0+y1

	pnjs = g["pnjs"]
	for pnj in pnjs:
		pos = PNJ.getPos(g["pnjs"][pnj])
		if pos == (nx, ny):
			PNJ.exe(g["pnjs"][pnj], q, d)
	return True

def isRunning(g):
	return g["RUN"]

def setRunning(g, v):
	assert type(v) == bool
	g["RUN"] = v

def getDimension(g):
	return g["ROWS"], g["COLS"]
