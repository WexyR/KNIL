# -*- coding: utf-8 -*-

import Flashlight
import Knil
import Background
import Dialog

from math import pi

functions = {"flashlight":lambda flashlight, **kwargs:Flashlight.exe(flashlight),
             "key":lambda key, k, b, d, **kwargs:open_door(key, k, b, d),
             "bomb":lambda key, k, b, d, **kwargs:explode(key, k, b, d),
             "powder": lambda key, k, d, **kwargs:uplife(key, k, d)}
items = {}


def summon_item(item_name, values):
    """Crée un item"""

    global items
    if item_name == "flashlight":
        item = Flashlight.create(8, 0, pi/4.)
    else:
        if exist(item_name):
            item_name += '@' + str(len([i for i in items.keys() if item_name in i]))
        item = dict()
        item['name'] = item_name
        if values:
            item['values'] = values
    items[item_name] = item
    return item

def exe(item, k, b, d):
    """Execute la fonction associée à un item"""

    global functions
    functions[getName(item)](item, k=k, b=b, d=d)

def exist(item_name):
    """Teste si un item a été crée au moins une fois"""

    global items
    return item_name in items

def getName(item):
    """Retourne le nom d'un item, sans diférencier les doublons"""

    if '@' in item['name']:
        return item["name"].split('@')[0]
    else:
        return item["name"]

def getFullName(item):
    """Retourne le nom complet d'un item"""

    return item["name"]

def getFlashlight():
    """Retourne la lampe"""

    global items
    assert exist("flashlight")
    return items["flashlight"]

def getShape(item):
    """Retourne le dessin d'un item"""

    drawing = open("items/{item_name}.txt".format(item_name=getName(item)))
    txt = drawing.read()
    drawing.close()
    return txt

def open_door(item, k, b, d):
    """Change le caractère 'crossable' de la porte en face de Knil si l'ID de la porte
correspond à celui de l'item"""

    x0, y0 = Background.getOrigin(b)
    dimension = Background.getDimension(b)
    nx, ny = Knil.getFrontPos(k, dimension)
    x, y = x0+nx, y0+ny
    case = Background.getCase(b, x, y)
    if Background.isDoor(case):
        if Background.getDoorID(case) == item['values'][0]:
            Background.setCrossable(case, 1)
            Dialog.run_dialog(d, txt="La porte s'ouvre")
            Knil.remove_inventory(k, item)
        else:
            Dialog.run_dialog(d, txt="Ce n'est pas la bonne clef")
    else:
        Dialog.run_dialog(d, txt="Une clef, ça sert à ouvrir une porte..")

def explode(item, k, b, d):
    """Casse n'importe mur en face de Knil"""

    x0, y0 = Background.getOrigin(b)
    dimension = Background.getDimension(b)
    nx, ny = Knil.getFrontPos(k, dimension)
    x, y = x0+nx, y0+ny
    case = Background.getCase(b, x, y)
    if not Background.isCrossable(case): # Si c'est bien un mur
        Background.setCrossable(case, 1)
        Background.setCarac(case, "  ")
        Dialog.run_dialog(d, txt="Un passage s'est ouvert")
        Knil.remove_inventory(k, item)
    else:
        Dialog.run_dialog(d, txt="Vaut mieux faire sauter un mur, non?")

def uplife(item, k, d):
    """Essaie d'augmenter la vie de Knil"""

    if not Knil.isFullLife(k):
        Knil.uplife(k)
        Dialog.run_dialog(d, txt="C'est de la poudre de perlimpinpin !", speaker="Knil")
        Knil.remove_inventory(k, item)
    else:
        Dialog.run_dialog(d, txt="Ca serait du gachis de l'utiliser alors que j'ai toute ma vie.", speaker="Knil")
