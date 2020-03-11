# -*- coding: utf-8 -*-

from math import cos, sin, sqrt, pi, acos
import Background
from Tools import norm

def create(scope, alpha, delta, n_vect = 10.0):
    flashlight = dict()
    flashlight["name"] = "flashlight"
    flashlight["alpha"] = alpha
    flashlight["delta"] = delta
    flashlight["scope"] = scope
    flashlight["activated"] = False
    flashlight["n_vect"] = n_vect
    return flashlight

def exe(flashlight):
    flashlight["activated"] = bool((int(flashlight["activated"])+1)%2) # inverse un booléen

def getScope(flashlight):
    return flashlight["scope"]

def isActivated(flashlight):
    return flashlight["activated"]

def setAlpha(flashlight, alpha):
    flashlight["alpha"] = alpha

def get_highlighted_case_pos(flashlight, grid, x, y):
    alpha = flashlight["alpha"]
    delta = flashlight["delta"]
    scope = flashlight["scope"]

    highlighted_case_pos = set()

    t=flashlight["n_vect"]
    for vt in range(-1, int(t)+2):
        v= (cos(delta/2-(vt/t)*delta+alpha), -sin(delta/2-(vt/t)*delta +alpha))
        for l in range(scope):
            if norm((l*v[0], l*v[1])) >= scope:
                break
            yl = int(round(y+l*v[1])-round(sin(alpha)))
            xl = int(round(x+l*v[0])+round(cos(alpha)))
            case = grid[yl][xl]
            highlighted_case_pos.add((xl, yl))
            if not Background.isCrossable(case):
                break

    return highlighted_case_pos
