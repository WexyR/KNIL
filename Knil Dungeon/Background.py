# -*- coding: utf-8 -*-

import sys
from Tools import *
import Map
import Knil
import Flashlight
import Item

translation = {"UP":("y", -1), "LEFT":("x", -1), "DOWN":("y", 1), "RIGHT":("x", 1)}

special_carac = {1:"░", 2:"▖", 3:"▗", 4:"▘", 5:"▙", 6:"▚", 7:"▛", 8:"▜", 9:"▝",
				10:"▞", 11:"▟", 12:"👻"}

def create(ROWS, COLS, x, y, anchor="nw"):
	"""Initialise l'écran"""

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
	"""Déplace l'origine de la zone à afficher à l'écran"""

	global translation
	direction, sens = translation[steer]
	b[direction] += sens

def canSlide(b, steer):
	"""Teste si on peut déplacer l'origine de l'écran à afficher sans tomber
'hors-map'"""

	global translation
	direction, sens = translation[steer]
	ROWS, COLS = getDimension(b)
	origin = getOrigin(b)
	if sens == -1:
		return origin[direction=="y"] + sens >= 0
	else:
		if direction == "x":
			return origin[0] + COLS + sens <= len(b["map"][0])
		else:
			return origin[1] + ROWS + sens <= len(b["map"])

def show(b, k):
	"""Affiche la zone de la map à afficher à l'écran, en tenant compte des
differents cas particuliers comme la luminosité, ou encore les toits des maisons"""

	x0, y0 = getOrigin(b)
	kx, ky = Knil.getPos(k)
	knil_case = getCase(b, kx+x0, ky+y0)
	ROWS, COLS = getDimension(b)
	special_attrib = bool("special_case" in knil_case.keys())
	if special_attrib:
		special_ID = knil_case["special_case"]["attrib"]["id"]
	if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
		highlighted_case_pos = Flashlight.get_highlighted_case_pos(Item.getFlashlight(), b['map'], x0+kx, y0+ky)
	for j in range(ROWS):
		goto((j+1), 1)
		for i in range(COLS):
			case = getCase(b, x0+i, y0+j)
			if "special_case" in case.keys():
				if special_attrib:
					if special_ID != case["special_case"]["attrib"]["id"]:
						if "object" in case.keys() and case["object"]:
							caracs = '!!'
						case = case["special_case"] # Si la case à un "toit", et si Knil n'est pas sous ce "toit"
													# Alors la case à afficher est ce "toit" et non la case en dessous
						# Par contre, si Knil est sous le "toit", il faut enlever tous les "toits" correspondants
				else:
					case = case["special_case"]

			if "object" in case.keys() and case["object"]:
				caracs = '!!' # S'il y a au moins un objet sur la case, alors les caractères à afficher sont des points d'exclamations
			else:
				caracs = case['c'] # Sinon les caractères normaux

			fontcolor = getFontcolor(case) 	# On récupère les couleurs de la case
			bgcolor = getBgcolor(case)		# en tenant compte de la luminosité si besoin
			if "brightness" in case.keys():
				if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
					if (x0+i, y0+j) in highlighted_case_pos: 	# Mais si elle est éclairée par la lampe
						case = highlight_case(case, Item.getFlashlight())				# Alors on augmente la luminosité
						fontcolor = getFontcolor(case, False)
						bgcolor = getBgcolor(case, False)

			if "object" in case.keys() and case["object"]:	# Si un objet est présent
				red, green, blue = fontcolor				# On l'affiche en augmentant sa dose de rouge
				fontcolor = (min(red*3, 255), green, blue)	# (proportionnellement à la luminosité)
			color(fontcolor=fontcolor, bgcolor=bgcolor)

			for c in caracs:
				if isinstance(c, int):	# Si le caractère à afficher est un nombre et non un chaîne de caractères
					w(special_carac[c]) # Alors c'est donc un caracère spécial (encodage différent) correspondant au nombre qu'il faut afficher
				else:
					w(c)
			reset_attributes()

def add_object(b, x, y, id):
	"""Ajoute un objet sur une case"""

	case = getCase(b, x, y)
	obj = dict()
	obj['executions'] = ['execute_dialog_Vous avez trouvé x1 {id}'.format(id=id),			# Lorsque le joueur trouve l'objet, on le lui signal
						 'execute_grid_removeObject_{x}_{y}_{id}'.format(x=x, y=y, id=id)]	# Et on le fait disparaître
	obj['events'] = ['event_find_{id}'.format(id=id)]	# On génère aussi un évènement qui indiquera aux quêtes que le joueur l'a trouvé


	if "object" in case.keys():
		case["object"][id] = obj
	else:
		case["object"] = dict()
		case["object"][id] = obj

	if "executions" in case.keys():
		case["executions"] += obj['executions']
	else:
		case['executions'] = obj['executions']

	if "events" in case.keys():
		case["events"] += obj['events']
	else:
		case['events'] = obj["events"]

def remove_object(b, x, y, id):
	"""Enleve un objet d'une case"""

	case = getCase(b, x, y)
	obj = case['object'][id]

	case['executions'] = list(set(case['executions']) - set(obj['executions']))	# On supprime les executions correspondantes
	if not case['executions']:
		del case['executions']

	case['events'] = list(set(case['events']) - set(obj['events']))				# Ainsi que les évènements
	if not case['events']:
		del case['events']

	del case['object'][id]

def highlight_case(case, f):
	"""Renvoie une copie d'une case avec une luminosité augmenté par la lampe"""

	case = dict(case)
	brightness = getBrightness(case) + Flashlight.getIntensity(f)
	case['fontcolor'] = tuple([min(clr*min(brightness, 100)//100, 255) for clr in case["fontcolor"]])
	case['bgcolor'] = tuple([min(clr*min(brightness, 100)//100, 255) for clr in case["bgcolor"]])
	return case

def is_case_highlighted(b, k, x, y):
	"""Teste si une case est éclairée par la lampe"""

	x0, y0 = getOrigin(b)
	kx, ky = Knil.getPos(k)
	if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
		highlighted_case_pos = Flashlight.get_highlighted_case_pos(Item.getFlashlight(), b['map'], x0+kx, y0+ky)
		return (x, y) in highlighted_case_pos
	else:
		return False

def getOrigin(b):
	"""Renvoie l'origine de l'écran dans la map, en tenant compte de l'ancrage"""

	x0 = b["x"]-int("c" in b["anchor"])*(b["COLS"]//2)-2*int("e" in b["anchor"])*(b["COLS"]//2)
	y0 = b["y"]-int("c" in b["anchor"])*(b["ROWS"]//2)-2*int("s" in b["anchor"])*(b["ROWS"]//2)
	return x0, y0

def is_case_special(b, location):
	"""Teste si une case est spéciale, c'est-à-dire qu'elle a un "toit" """

	x, y = location
	case = getCase(b, x, y)
	return "special_case" in case.keys()

def is_case_special_activated(b, location, k):
	"""Teste si le toit n'est pas affiché en raison de la position de Knil"""

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

def getDimension(b):
	"""Renvoie les dimensions de l'écran"""

	return b['ROWS'], b["COLS"]

def getBgcolor(case, with_brightness=True):
	"""Retourne la couleur d'arrière-fond de la case, en tenant compte de la luminosité (par défaut) si besoin"""

	if with_brightness:
		if "brightness" in case:
			return tuple([clr*getBrightness(case)//100 for clr in case["bgcolor"]])
	return case["bgcolor"]

def getFontcolor(case, with_brightness=True):
	"""Retourne la couleur de police de la case, en tenant compte de la luminosité (par défaut) si besoin"""

	if with_brightness:
		if "brightness" in case:
			return tuple([clr*getBrightness(case)//100 for clr in case["fontcolor"]])
	return case["fontcolor"]

def isCrossable(case):
	"""Teste si une case est traversable"""

	return case["crossable"] != 0

def setCrossable(case, v):
	"""Modifie le caractère "traversable" d'une case"""

	assert isinstance(v, int)
	case["crossable"] = v

def setCarac(case, c):
	"""Modifie les caractères à afficher d'une case"""

	assert isinstance(c, str)
	case["c"] = c

def isExecutable(case):
	"""Teste si une case est interactive"""

	return "executions" in case.keys()

def getExecutions(case):
	"""Retourne la liste des interactions de la case intéractive"""

	assert isExecutable(case)
	return case["executions"]

def hasEvents(case):
	"""Teste si une case génère des évènements lors d'une intéraction"""

	return "events" in case.keys()

def getEvents(case):
	"""Retourne la liste des events de la case intéractive"""
	assert hasEvents(case)
	return case['events']

def isDoor(case):
	"""Teste si la case est une porte"""

	if "special_type" in case.keys():
		return case['special_type'] == "door"
	else:
		return False

def getDoorID(case):
	"""Retourne l'ID de la porte"""

	assert isDoor(case)
	if "doorID" in case.keys():
		return case['doorID']
	else:
		return ''

def getBrightness(case):
	"""Retourne la luminosité d'une case"""

	assert "brightness" in case
	return case["brightness"]

def getMap(b):
	"""Renvoie la map"""

	return b["map"]

def getCase(b, x, y):
	"""Retourne la case aux coordonnées (x, y)"""

	return b["map"][y][x]

def setOrigin(b, x, y):
	"""Modifie l'origine de l'écran en tenant compte de l'ancrage"""

	b["x"] = x-int("c" in b["anchor"])*(b["COLS"]//2)-2*int("e" in b["anchor"])*(b["COLS"]//2)
	b["y"] = y-int("c" in b["anchor"])*(b["ROWS"]//2)-2*int("s" in b["anchor"])*(b["ROWS"]//2)
