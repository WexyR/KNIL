# -*- coding: utf-8 -*-

import Background
import Knil
import random
import math
import Dialog
import Flashlight
import Item

from Tools import *
import xml.etree.ElementTree as ET

def create(xml_file_path):
	"""Initialise les monstres à partir d'un fichier de données"""

	assert isinstance(xml_file_path, str)
	root = ET.parse(xml_file_path).getroot()
	monsters= dict()
	for m in root.findall("Monster") :
		monsters[m.get("id")]=xml_to_dict(m)
		monsters[m.get("id")]["id"] = m.get("id")
		monsters[m.get("id")]["position"]=list(monsters[m.get("id")]["initial_position"])
		monsters[m.get("id")]["t"] = 0.
	return monsters

def is_Knil_in_sight(monster, k, b):
	"""Retourne si Knil est dans la ligne de mire du monstre"""

	x, y = Knil.getPos(k)
	x0, y0 = Background.getOrigin(b)
	kx, ky = x+x0, y+y0
	mx, my = getPos(monster)
	s = getSight(monster)
	v = kx-mx, ky-my
	if is_Knil_in_room(monster, k, b):
		if abs(norm(v))<s:
			for r in range(int(norm(v))):
				if not Background.isCrossable(Background.getCase(b, mx+int(abs(round(v[0]* r/norm(v)))), my+int(abs(round(v[1]* r/norm(v)))))):
					return False
			return True

	return False

def move(m, k, b):
	"""Fait bouger un monstre dans la direction de Knil s'il est en vue. Sinon le
fait érrer aléatoirement."""

	mx, my = getPos(m)
	x, y = Knil.getPos(k)
	x0, y0 = Background.getOrigin(b)
	kx, ky = x+x0, y+y0
	v= mx-kx, my-ky
	if is_Knil_in_room(m, k, b):
		if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
			highlighted_case_pos = Flashlight.get_highlighted_case_pos(Item.getFlashlight(), b["map"], kx, ky)
			if (mx, my) in highlighted_case_pos:
				return None, False
		if is_Knil_in_sight(m, k, b):
			npos = None
			if mx != kx and my!=ky and Background.isCrossable(Background.getCase(b, mx-v[0]/abs(v[0]) , my-v[1]/abs(v[1]))):
				npos = mx-v[0]/abs(v[0]) , my-v[1]/abs(v[1])
			elif mx==kx and my!=ky:
				npos = mx, my-v[1]/abs(v[1])
			else:
				npos = mx-v[0]/abs(v[0]), my
			if npos is not None:
				ncase = Background.getCase(b, npos[0], npos[1])
				if Background.isCrossable(ncase):
					m['position'] = npos
					return (mx, my), m["position"] != (mx, my)
				else:
					return wander(m, k, b)
		else:
			return wander(m, k, b)
	else:
		return None, False

def check_knil_kill(monsters, k, b):
	"""Teste si la position d'un monstre est confondue avec celle de Knil"""

	for m in monsters:
		x0, y0 = Background.getOrigin(b)
		x, y = Knil.getPos(k)
		kx, ky = x+x0, y+y0
		mx, my = getPos(monsters[m])
		if (mx, my) == (kx, ky):
			return True

def wander(m, k, b):
	"""Fait errer un monstre dans une salle (sans l'en faire sortir)"""

	mx, my = getPos(m)

	neighbors= [(mx+i, my+j) for i in (-1, 0, 1) for j in (-1, 0, 1) \
	if Background.isCrossable(Background.getCase(b, mx+i, my+j)) \
	and Background.is_case_special(b, (mx+i, my+j)) \
	and Background.is_case_special_activated(b, (mx+i, my+j), k)]

	m["position"] = random.choice(neighbors)

	return (mx, my), m["position"] != (mx, my)

def show(m, k, b):
	"""Affiche un monstre en effacant la case sur laquelle il était auparavant"""

	x0, y0 = Background.getOrigin(b)
	ROWS, COLS = Background.getDimension(b)
	kx, ky = Knil.getPos(k)
	x, y = getPos(m)
	mx, my = x-x0, y-y0

	# efface la case précédente
	if 'previous_case' in m.keys() and m['previous_case'] is not None:
		px, py = m['previous_case']
		if (px, py) != (mx, my):
			case = Background.getCase(b, px, py)
			if px >= x0 and px < x0 + COLS and py >= y0 and py < y0 + ROWS:
				bgcolor = Background.getBgcolor(case)
				if "brightness" in case.keys():
					if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
						highlighted_case_pos = Flashlight.get_highlighted_case_pos(Item.getFlashlight(), b['map'], x0+kx, y0+ky)
						if (px, py) in highlighted_case_pos:
							case = Background.highlight_case(case, Item.getFlashlight())
							bgcolor = Background.getBgcolor(case, False)

				color(fontcolor=getColor(m), bgcolor=bgcolor)
				goto((py-y0)+1, (px-x0)*2+1)
				for c in case["c"]:
					if isinstance(c, str):
						w(c)
					else:
						w(Background.special_carac[c])

	# affiche le monstre en tenant compte de la couleur et de la luminosité de la case sur laquelle il se trouve
	# si et seulement si il se trouve dans l'écran
	if x >= x0 and x < x0 + COLS and y >= y0 and y < y0 + ROWS:
		if is_Knil_in_room(m, k, b):
			goto(my+1, mx*2+1);
			case= Background.getCase(b, x, y)
			bgcolor = Background.getBgcolor(case)
			if "brightness" in case.keys():
				if Item.exist("flashlight") and Flashlight.isActivated(Item.getFlashlight()):
					highlighted_case_pos = Flashlight.get_highlighted_case_pos(Item.getFlashlight(), b['map'], x0+kx, y0+ky)
					if (x, y) in highlighted_case_pos:
						case = Background.highlight_case(case, Item.getFlashlight())
						bgcolor = Background.getBgcolor(case, False)
			color(fontcolor=getColor(m), bgcolor=bgcolor)
			for c in m["c"]:
				if isinstance(c, str):
					w(c)
				else:
					w(Background.special_carac[c])


def is_Knil_in_room(m, k, b):
	"""Teste si Knil et un monstre se trouve dans la même salle"""

	x0, y0 = Background.getOrigin(b)
	mx, my = getPos(m)
	if Background.is_case_special(b, (mx, my)):
		if Background.is_case_special_activated(b, (mx, my), k):
			return True
		else:
			return False

def run(monsters, k, b, ROWS, COLS, t):
	"""Fait bouger les monstres s'ils doivent le faire (rapport au temps d'action)"""

	modif = False
	for m_ID, m in monsters.items():
		if t - getCurrentTime(m) >= getUpdateTime(m):
			m['previous_case'], modification = move(m, k, b)
			if modification:
				modif = True
			setCurrentTime(m, t)
	return modif

def reset(ms):
	for m_ID, m in ms.items():
		m['position'] = m['initial_position']
def getPos(m):
	"""Retourne la position d'un monstre"""

	return m['position']

def getSight(m):
	"""Retourn la longueur de la ligne de mire d'un monstre"""

	return m["sight"]

def getUpdateTime(monster):
	"""Retourne le temps auquel les monstres doivent bouger"""

	return monster["updateTime"]

def getCurrentTime(monster):
	"""Retourne le dernier temps où les monstres ont bougé"""

	return monster["t"]

def setCurrentTime(monster, t):
	"""Modifie le temps courant"""

	monster["t"] = t

def getColor(m):
	return m["color"]
