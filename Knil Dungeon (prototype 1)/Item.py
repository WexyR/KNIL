# -*- coding: utf-8 -*-

import Flashlight
from math import pi

functions = {"flashlight":lambda flashlight:Flashlight.exe(flashlight)}
items = {}


def summon_item(item_name):
    global items
    if item_name == "flashlight":
        item = Flashlight.create(8, 0, pi/4.)
    else:
        item = dict()
        item['name'] = item_name
    items[item_name] = item
    return item

def exe(item):
    global functions
    functions[getName(item)](item)

def exist(item_name):
    global items
    return item_name in items

def getName(item):
    return item["name"]

def getItem(item_name):
    global items
    return items[item_name]

def getShape(item):
    drawing = open("items/{item_name}.txt".format(item_name=item['name']))
    txt = drawing.read()
    drawing.close()
    return txt
