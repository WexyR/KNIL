# -*- coding: utf-8 -*-
import sys
import Knil
import Background
import PNJ
from Tools import *
import Dialog
import Event
import Quest
import Flashlight
import Item
import Monster

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}

def create(ROWS, COLS):
	"""Initialise le jeu"""

	game = dict()
	b = Background.create(ROWS, COLS, 0, 0, anchor="nw")
	k = Knil.create(11, 3)
	d = Dialog.dialog_box_create(ROWS, COLS*2, 0.25)
	Event.create()
	pnjs = PNJ.create("PNJdata.xml")
	monsters = Monster.create("MonsterData.xml")
	q = Quest.init("QuestData.xml")
	game["background"] = b
	game["knil"] = k
	game["dialog_box"] = d
	game["quest_details_box"] = Dialog.dialog_box_create(ROWS, COLS*2, 1.)
	game["quests"] = q
	game["pnjs"] = pnjs
	game["monsters"]= monsters
	game['COLS'] = COLS
	game['ROWS'] = ROWS
	game['RUN'] = False
	return game

def restart(g):
	"""Réinitialise la partie"""

	ROWS, COLS = getDimension(g)
	new_game = create(ROWS, COLS)
	for key in g:
		g[key] = new_game[key]
	setRunning(g, True)

def move(g, steer):
	"""Tente de bouger dans la direction donnée, en tenant compte des collisions
des différents éléments du jeu"""

	global translation

	b = g["background"]
	k = g["knil"]
	ROWS, COLS = getDimension(g)
	direction, sens = translation[steer]

	modification = False

	m = Knil.point(k, steer)
	if m:
		modification = True

	centered = k[direction] != [COLS//2, ROWS//2][direction=="y"]
	bgcs = Background.canSlide(b, steer)

	if not Knil.collide(k, steer, b, g["pnjs"]):
		if centered or not bgcs:
			Knil.move(k, steer)
			modification = True
		elif bgcs:
			Background.slide(b, steer)
			modification = True
		x0, y0 = Background.getOrigin(b)
		x, y = Knil.getPos(k)
		event = "event_pos_at_{x}_{y}".format(x=x+x0, y=y+y0)
		goto(40, 1); w(event)
		Event.generate(event, g['quests'], k, b, g["dialog_box"], g)
	return modification

def display(g):
	"""Affiche ce qui doit être affiché à l'écran"""

	b = g["background"]
	k = g["knil"]
	pnjs = g["pnjs"]
	monsters = g["monsters"]
	ROWS, COLS = getDimension(g)

	Background.show(b, k)
	Knil.show(k, b)
	for pnj in pnjs.keys():
		x, y = PNJ.getPos(pnjs[pnj])
		x0, y0 = Background.getOrigin(b)
		if x >= x0 and x < x0 + COLS and y >= y0 and y < y0 + ROWS:
			PNJ.display(pnjs[pnj], b, k)

	for monster_ID, monster in monsters.items():
		Monster.show(monster, k, b)

	reset_attributes()
	goto(34,1)
	x1, y1 = Knil.getFrontPos(k, getDimension(g))
	Knil.show_life(k, 1, g['ROWS']+2)

def i(g):
	"""Appelle l'ouverture de l'inventaire"""

	k = g["knil"]
	Knil.open_inventory(k)
	return True

def j(g):
	"""Appelle l'ouverture du journal des quêtes"""

	Quest.run_quest_menu(g["quests"], g["quest_details_box"])
	return True

def exe(g):
	"""Tente de faire une intéraction"""

	b = g["background"]
	k = g["knil"]
	d = g["dialog_box"]
	q = g["quests"]

	x0, y0 = Background.getOrigin(b)
	x1, y1 = Knil.getFrontPos(k, getDimension(g))
	nx, ny = x0+x1, y0+y1

	pnjs = g["pnjs"]
	for pnj in pnjs:
		pos = PNJ.getPos(g["pnjs"][pnj])
		if pos == (nx, ny):
			PNJ.exe(g["pnjs"][pnj], q, d, k, b, g)

	nc = Background.getCase(b, nx, ny)
	if Background.hasEvents(nc):
		for event in Background.getEvents(nc):
			Event.generate(event, q, k, b, d, g)

	if Background.isExecutable(nc):
		for execution in Background.getExecutions(nc):
			Event.execute(execution, k, b, d, q, g)
	return True

def update_Flashlight(g, t):
	"""Fait la mise à jour de la batterie de la lampe. Renvoie True si elle s'eteint
à cause d'une panne de batterie, afin de mettre à jour l'écran"""

	if Knil.is_in_inventory(g['knil'], 'flashlight'):
		f = Item.getFlashlight()
		if Flashlight.isActivated(f):
			Flashlight.update(f, t)
			Flashlight.show(f, 1, g['ROWS']+3)
			return not Flashlight.isActivated(f)
		else:
			False
	else:
		return False

def update_Monsters(g, t):
	"""Fait la mise à jour des monstres, et donc teste si l'un d'entre eux tue Knil"""

	d = g["dialog_box"]
	k = g['knil']
	ms = g['monsters']
	b = g['background']
	ROWS, COLS = getDimension(g)
	modif = False

	if Monster.run(ms, k, b, ROWS, COLS, t):
		modif = True
	kill = Monster.check_knil_kill(ms, k, b)
	if kill:
		Dialog.run_dialog(d, txt="Tu es mort")
		dead = Knil.kill(k)
		if dead:
			return end_game(g)
		else:
			Background.setOrigin(b, 0, 0)
			Knil.setPos(k, 11, 3)
			Knil.point(k, "DOWN")
			Monster.reset(ms)
			modif = True
	return modif

def end_game(g):
	"""Ecran de fin de jeu affichant "GAME OVER" et les résultats en ascii art"""

	reset_attributes()
	clear()
	file = open('ascii_art/game_over.txt', 'r')
	game_over_txt = file.read()
	file.close()
	file = open('ascii_art/score.txt', 'r')
	score_txt = file.read()
	file.close()
	file = open('ascii_art/percent.txt', 'r')
	percent_txt = file.read()
	file.close()
	ascii_numbers = dict()
	for i in range(10):
		file = open('ascii_art/{0}.txt'.format(i), 'r')
		ascii_numbers[str(i)] = file.read()
		file.close()

	quests = g["quests"]
	finished_quest = len([q for q in quests if Quest.isFinished(quests, q)])
	percent = str(int(round((float(finished_quest)/len(quests)*100))))

	goto(6, 6)
	w(game_over_txt)
	goto(15, 1)
	w(score_txt)
	for i, c in enumerate(percent):
		x = len(score_txt.splitlines()[0]) + 4
		for j in range(i):
			x += len(ascii_numbers[percent[j]].splitlines()[0]) + 2

		number_txt = ascii_numbers[c].splitlines()
		for y, line in enumerate(number_txt):
			goto(15+y, x)
			w(line)
	x = len(score_txt.splitlines()[0]) + 4
	for i in range(len(percent)):
		x += len(ascii_numbers[percent[i]].splitlines()[0]) + 2
	percent_txt = percent_txt.splitlines()
	for y, line in enumerate(percent_txt):
		goto(15+y, x)
		w(line)
	goto(35, 1)
	sys.stdout.flush()
	setRunning(g, False)

def isRunning(g):
	return g["RUN"]

def setRunning(g, v):
	assert type(v) == bool
	g["RUN"] = v

def getDimension(g):
	return g["ROWS"], g["COLS"]
