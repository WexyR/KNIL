# -*- coding: utf-8 -*-
import sys, os
import time
from Tools import *

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}
framings = ["      ", ["┌", "─", "┐", "│", "└", "┘"], ["╔", "═", "╗", "║", "╚", "╝"], "######"]

def create(grid, x0, y0, case_xmax, case_ymax, dx=0, dy=0, autoquit=True, framing=True, auto_clear="zone", text_align="center"):
	"""Initialise un menu"""

	assert text_align in ("left", "right", "center")
	assert auto_clear in ("all", "zone", None)
	menu = dict()
	menu["grid"] = grid
	menu["xmax"] = len(grid[0])
	menu["ymax"] = len(grid)
	menu["RUN"] = False
	menu["cursor_x"] = 0
	menu["cursor_y"] = 0
	menu["cx"] = case_xmax
	menu["cy"] = case_ymax
	menu["dx"] = dx
	menu["dy"] = dy
	menu["x0"] = x0
	menu["y0"] = y0
	menu["autoquit"] = autoquit
	menu["framing"] = framing
	menu["auto_clear"] = auto_clear
	menu["text_align"] = text_align
	return menu

def move(m, steer):
	"""Bouge le curseur de sélection dans une direction donnée, en tenant compte des collisions"""

	global translation
	direction, sens = translation[steer]
	if m["cursor_{0}".format(direction)] + sens >= 0:
		if direction == "x" and m["cursor_x"] + sens < len(m["grid"][m["cursor_y"]]):
			m["cursor_{0}".format(direction)] += sens
		elif direction == "y" and m["cursor_y"] + sens < len(m["grid"]):
			if m["cursor_x"] < len(m["grid"][m["cursor_y"] + sens]):
				m["cursor_{0}".format(direction)] += sens

def show_all(m):
	"""fonction qui (ré)affiche toutes les cases et leur contenu"""
	global framings

	x0, y0 = m["x0"], m["y0"]
	x, y = x0, y0
	cx, cy = m["cx"], m["cy"]
	ftype = framings[1]

	for j, line in enumerate(m["grid"]):
		for i, case in enumerate(line):
			if m["framing"]:
				display_frame(x, y, cx, cy, ftype)
			if case:
				msg = case[0].splitlines()
			else:
				msg = [" "*(cx-2) for _ in range(cy-2)]
			for cpt, string in enumerate(msg):
				if m["text_align"] == "right":
					sy = y + 1
					sx = x + 2
					string = string.rjust(cx-2)
				elif m["text_align"] == "left":
					sy = y + 1
					sx = x + 2
				else: # centered
					sy = y + cy//2 - len(msg)//2
					sx = x + cx//2 - len(string)//2

				goto(sy+cpt, sx); w(string)
			x += m["cx"] + m["dx"]
		x = m["x0"]
		y += m["cy"] + m["dy"]

		show_cursor_framing(m)

def show_cursor_framing(m, *args):
	"""Affiche le cadre du curseur de sélection"""
	global framings

	ftype = framings[2]
	x = m["x0"]+m["cursor_x"]*(m["cx"]+m["dx"])
	y = m["y0"]+m["cursor_y"]*(m["cy"]+m["dy"])
	cx, cy = m["cx"], m["cy"]
	display_frame(x, y, cx, cy, ftype)
	sys.stdout.flush()

def display_frame(x, y, cx, cy, ftype):
	"""Affiche le cadre par defaut d'une case (peut être des espaces)"""

	goto(y, x); w(ftype[0] + ftype[1]*(cx-2) + ftype[2])
	for l in range(cy-2):
		goto(y+l+1, x); w(ftype[3])
		goto(y+l+1, x+cx-1); w(ftype[3])
	goto(y+cy-1, x); w(ftype[4] + ftype[1]*(cx-2) + ftype[5])

def clear_zone(m):
	"""Efface les zones où se trouverons les cases du menu"""

	for j, line in enumerate(m["grid"]):
		y = m["y0"] + j*(m["cy"] + m["dy"])
		for i, case in enumerate(line):
			x = m["x0"] + i*(m["cx"] + m["dx"])
			goto(y, x)
			for j2 in range(m["cy"]+1):
				w(" "*m["cx"])
				goto(y+j2, x)

def erase_case(m, *args):
	"""fonction qui affiche (intélligement) seulement les cases qui ont besoin
d'etre réafichées"""

	global framings

	cx, cy = m["cx"], m["cy"]
	x = m["x0"]+m["cursor_x"]*(m["cx"]+m["dx"])
	y = m["y0"]+m["cursor_y"]*(m["cy"]+m["dy"])

	if m["framing"]:
		ftype = framings[1]
	else:
		ftype = framings[0]
	display_frame(x, y, cx, cy, ftype)

def validate(m):
	"""Exécute la fonction associée à la case selectionnée"""

	x, y = m["cursor_x"], m["cursor_y"]
	if m["grid"][y][x]:
		if m["grid"][y][x][1]:
			function = m["grid"][y][x][1]
			function()
			if m["autoquit"]: # L'execution d'une fonction du menu entraine la fermeture du menu dans ce cas-ci
				m["RUN"] = False
			else: # Sinon on refait juste l'affichage complet du menu (au cas où la fonction aurait modifié quelque chose à l'écran)
				reset_attributes()
				if m["auto_clear"]:
					if m["auto_clear"] == "all":
						home(); clear()
					else:
						clear_zone(m)

				show_all(m)

def run(m):
	"""Lance la boucle de menu"""
	m["RUN"] = True
	reset_attributes()
	if m["auto_clear"]:
		if m["auto_clear"] == "all":
			home(); clear()
		else:
			clear_zone(m)

	show_all(m)
	while m["RUN"]:
		interact(m, readData(), (("UP", "LEFT", "DOWN", "RIGHT"), (erase_case, move, show_cursor_framing)), EXE=validate, ESC=stop)

	return True

def stop(m):
	"""Arrete la boucle du menu"""
	m["RUN"] = False
