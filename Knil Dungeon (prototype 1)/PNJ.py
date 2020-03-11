# -*- coding: utf-8 -*-

import Background
import Knil
from Tools import *
import xml.etree.ElementTree as ET
import Dialog
import Event
import Quest

def create(xml_file_path):
    assert isinstance(xml_file_path, str)
    root = ET.parse(xml_file_path).getroot()
    pnjs= dict()
    for p in root.findall("PNJ") :
        pnjs[p.get("id")]=xml_to_dict(p)
        pnjs[p.get("id")]["name"] = p.get("id")
        # if pnjs[p.get("id")]["step"] == 0:
        #     Event.add(pnjs[p.get("id")]["quest"]["q0"], p.get("id"))
            # raw_input(pnjs[p.get("id")]["quest"])
    return pnjs

def xml_to_dict(element):
    d= dict()
    for subelement in element:
        if list(subelement) :
            d[subelement.tag]=xml_to_dict(subelement)
        else:
            d[subelement.tag]=str_to_tuple(subelement.text)
    return d

def display(pnj, b, k):
    x0, y0 = Background.getOrigin(b)
    x, y = pnj["position"]
    assert x >= x0 and y >= y0
    px, py = (x-x0), (y-y0)
    if Background.is_case_special(b, (x, y)):
        if Background.is_case_special_activated(b, (x, y), k):
            displaying = True
        else:
            displaying = False
    else:
        displaying = True
    if displaying:
        goto(py+1, px*2+1);
        bgcolor = Background.getCase(b, x, y)["bgcolor"]
        color(pnj["color"], bgcolor)
        w(pnj["c"][0])

def setColor(pnj, color):
    pnj["color"] = color

def next(pnj):
    pnj["step"] += 1

def exe(pnj, q, d):
    txt = Event.generate("event_speak_{0}".format(pnj['name']), q)
    if txt:
        f = open("./PNJ_txt/{name}/{txt}.txt".format(name=pnj["name"], txt=txt))
    else:
        quest_name, num = Quest.auto_txt(q, pnj["name"])
        if quest_name and num:
            f = open("./PNJ_txt/{name}/{quest_name}_auto_{num}.txt".format(name=pnj["name"], quest_name=quest_name, num=num))
        else:
            f = open("./PNJ_txt/{name}/auto.txt".format(name=pnj["name"]))
    t = f.read()
    Dialog.run_dialog(d, t, speaker=pnj["name"])

def execute_event(pnj, event):
    raw_input(pnj + "; " + event)


def getPos(pnj):
    return pnj["position"]
