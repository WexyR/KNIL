# -*- coding: utf-8 -*-

from math import cos, sin, sqrt, pi, acos
import Background
from Tools import *
import random
import time
import sys

def create(scope, alpha, delta, n_vect = 10.0, intensity=70, battery_life=10.):
    """Initialise la lampe"""

    flashlight = dict()
    flashlight["name"] = "flashlight"
    flashlight["alpha"] = alpha # angle dans lequel la lampe éclaire
    flashlight["delta"] = delta # angle "d'ouverture"
    flashlight["scope"] = scope # portée
    flashlight["activated"] = False
    flashlight["n_vect"] = n_vect # Nombre de tests dans l'angle d'ouverture
    flashlight["t"] = 0. # temps initial (sert par la suite pour la batterie)
    flashlight["battery_life"] = battery_life # temps de vie de la batterie (en seconde)
    flashlight["current_battery"] = flashlight["battery_life"] # temps courant de la batterie
    flashlight["intensity"] = intensity
    return flashlight

def exe(f):
    """Change l'état de la lampe: l'allume si elle était éteinte, et inversement"""

    if f["activated"]:
        f['current_battery'] = f["battery_life"]
        f["activated"] = False
    else:
        f['t'] = time.time()
        f["activated"] = True

def improve_battery(f, t):
    """Améliore la lampe"""

    f['battery_life'] += t
    f["current_battery"] = t
    
def getScope(f):
    """Récupère la porté d'éclairage de la lampe"""

    return f["scope"]

def isActivated(f):
    """Teste si la lampe est allumée"""

    return f["activated"]

def setAlpha(f, alpha):
    """Change l'angle vers lequel éclaire la lampe"""

    assert isinstance(alpha, float)
    f["alpha"] = alpha

def get_highlighted_case_pos(f, grid, x, y):
    """Retourne la liste des coordonnées des cases éclairées par la lampe,
lorsqu'elle se trouve en (x, y)"""

    alpha = f["alpha"]
    delta = f["delta"]
    scope = f["scope"]

    highlighted_case_pos = set() # on utilise un set pour éviter les doublons (qui feraient beaucoup ralentir)

    t=f["n_vect"]
    for vt in range(-1, int(t)+2): # on balaie l'angle d'ouverture
        v= (cos(delta/2-(vt/t)*delta+alpha), -sin(delta/2-(vt/t)*delta +alpha))
        for l in range(scope): # pour chaque étape du balayage, on suit le vecteur directeur
            if norm((l*v[0], l*v[1])) >= scope:
                break
            yl = int(round(y+l*v[1])-round(sin(alpha)))
            xl = int(round(x+l*v[0])+round(cos(alpha)))
            case = grid[yl][xl]
            highlighted_case_pos.add((xl, yl))
            if not Background.isCrossable(case): # si on rencontre un mur, on passe à l'étape suivante
                break

    return highlighted_case_pos

def show(f, x, y):
    """Affiche la batterie restante dans la zone en dessous de l'écran"""

    goto(y, x)
    bl = int(round(f["current_battery"]))
    bl_max = int(round(f["battery_life"]))
    reset_attributes()
    color(fontcolor=7)
    w("Batterie: ")
    color(fontcolor=(10, 70, 10), bgcolor=(0, 200, 0))
    w("#"*bl)
    reset_attributes()
    w(" "*(bl_max-bl))

def update(f, t):
    """Mets à jour la batterie de la lampe. Si elle n'en a plus, alors l'éteint"""

    assert isinstance(t, float)
    f["current_battery"] -= t-f["t"]
    f['t'] = t
    if f["current_battery"] <= 0.:
        exe(f)

def getIntensity(f):
    """Renvoie l'intensité de la lampe"""

    return f['intensity']
