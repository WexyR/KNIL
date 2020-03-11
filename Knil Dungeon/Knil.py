# -*- coding: utf-8 -*-

import sys
from Tools import *
import Menu
import PNJ
import Background
import Item
import Flashlight
import Event
from math import pi

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}

def create(x, y):
	"""Initialise Knil"""

	knil = dict()
	knil["x"] = x # position relative par rapport au (0, 0) de l'écran
	knil["y"] = y #        //
	knil["front"] = 3 # Sens
	knil["graphism"] = ["← ", "↑ ", "→ ", "↓ "]
	knil["c"] = knil["graphism"][knil["front"]]
	knil["inventory"] = dict()
	knil["life"] = 3
	return knil

def point(k, steer):
	"""Change le sens de Knil"""

	global translation
	direction, sens = translation[steer]
	front = (sens+1)+int(direction=="y")
	if front != k["front"]:
		k["front"] = front # Change le sens
		k["c"] = k["graphism"][front] # Met à jour le caractère
		if is_in_inventory(k, "flashlight"):
			Flashlight.setAlpha(Item.getFlashlight(), -(k["front"]*pi/2.)-pi)
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
	"""Affiche Knil"""

	x = k["x"]
	y = k["y"]
	x0, y0 = Background.getOrigin(b)
	case = Background.getCase(b, x0+x, y0+y)
	if Background.is_case_highlighted(b, k, x0+x, y0+y):
		case = Background.highlight_case(case, Item.getFlashlight())
		bgcolor = Background.getBgcolor(case, False)
	else:
		bgcolor = Background.getBgcolor(case)
	color((0, 0, 0), bgcolor)
	goto(y+1, x*2+1)
	if case['crossable'] != 2:
		w(k["c"])

def show_life(k, x, y):
	"""Affiche la vie restante de Knil dans la zone en dessous de l'écran"""

	goto(y, x)
	reset_attributes()
	color(fontcolor=7)
	w('Vie: ')
	color(fontcolor=(220, 0, 0))
	w("♥ "*k['life'])
	reset_attributes()
	w("  "*(3-k['life']))

def open_inventory(k):
	"""Ouvre l'inventaire"""

	inv = k["inventory"]
	grid = [[None for _ in range(5)] for _ in range(3)]
	vals = []
	if "flashlight" in inv.keys():
		vals.append(inv["flashlight"])
	for item_name, obj in inv.items():
		if item_name != "flashlight":
			vals.append(obj)
	for i, obj in enumerate(vals):
		grid[i//len(grid[0])][i%len(grid[0])] = obj
	grid.append([('Retour', lambda: None)])
	Menu.run(Menu.create(grid, 10, 5, 10, 5, -1, -1))

def add_inventory(k, item, b, d):
	"""Ajoute un item à l'inventaire de Knil"""

	if len(k['inventory']) < 15:
		item_name = Item.getFullName(item)
		k["inventory"][item_name] = (Item.getShape(item), lambda k=k, b=b, d=d:Item.exe(item, k, b, d))
	else:
		Dialog.run_dialog(d, txt="Mon sac est plein, je dois laisser cet objet...", speaker="Knil")

def remove_inventory(k, item):
	"""Retire un item de l'inventaire de Knil"""

	item_name = Item.getFullName(item)
	del k["inventory"][item_name]

def is_in_inventory(k, item_name):
	return item_name in k["inventory"]

def kill(k):
	"""Fait perdre une vie à Knil, retourne True s'il n'a plus de vie"""

	k["life"] -= 1
	if k["life"] <= 0:
		return True
	else:
		return False

def uplife(k):
	"""Redonne une vie à Knil"""

	k['life'] += 1

def isFullLife(k):
	"""Teste si Knil a toute sa vie"""

	return k['life'] == 3

def getPos(k):
	"""Renvoie la position (relative à l'écran) de Knil"""

	return k["x"], k["y"]

def setPos(k, x, y):
	"""Donne une nouvelle position (relative à l'écran) à Knil"""

	assert isinstance(x, int)
	assert x > 0
	assert isinstance(y, int)
	assert y > 0
	k["x"], k["y"] = x, y

def getFrontPos(k, dimension):
	"""Renvoie la position qui se trouve en face de Knil, en tenant compte du bord
de l'écran"""

	q, r = divmod(k['front'], 2)
	direction = ['x', 'y'][r]
	sens = q*2-1
	ROWS, COLS = dimension

	x1 = k["x"] + int(direction=='x')*sens
	x1 = max(0, x1)
	x1 = min(COLS-1, x1)

	y1 = k["y"] + int(direction=='y')*sens
	y1 = max(0, y1)
	y1 = min(ROWS-1, y1)

	return x1, y1
