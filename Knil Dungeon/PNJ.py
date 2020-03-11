# -*- coding: utf-8 -*-

import Background
import Knil
from Tools import *
import xml.etree.ElementTree as ET
import Dialog
import Event
import Quest
import Item

def create(xml_file_path):
    """Initialise les PNJs à partir d'un fichier de données"""

    assert isinstance(xml_file_path, str)
    root = ET.parse(xml_file_path).getroot()
    pnjs= dict()
    for p in root.findall("PNJ") :
        pnjs[p.get("id")]=xml_to_dict(p)
        pnjs[p.get("id")]["name"] = p.get("id")
    return pnjs


def display(pnj, b, k):
    """Affiche un pnj"""

    x0, y0 = Background.getOrigin(b)
    x, y = pnj["position"]
    assert x >= x0 and y >= y0
    px, py = (x-x0), (y-y0)
    if Background.is_case_special(b, (x, y)):
        if Background.is_case_special_activated(b, (x, y), k):
            displaying = True # On affiche un PNJ sous un toit que si Knil est sous ce toit
        else:
            displaying = False
    else:
        displaying = True # Ou s'il n'y a pas de toit
    if displaying:
        goto(py+1, px*2+1);
        case = Background.getCase(b, x, y)
        if Background.is_case_highlighted(b, k, x, y): # On tient compte de la luminosité de la case
            case = Background.highlight_case(case, Item.getFlashlight())
            bgcolor = Background.getBgcolor(case, False)
        else:
            bgcolor = Background.getBgcolor(case)
        color(pnj["color"], bgcolor)
        for c in pnj['c']:
            w(c)

def setColor(pnj, color):
    """Change la couleur d'un pnj"""

    assert isinstance(color, (int, tuple, str))
    pnj["color"] = color


def exe(pnj, q, d, k, b, g):
    """Interagit avec un pnj"""

    txt = Event.generate("event_speak_{0}".format(pnj['name']), q, k, b, d, g) # Genere un evenement associé à la discussion avec ce pnj
    # On recupère (ou non) des détails concernant la quêtes
    if txt:
        f = open("./PNJ_txt/{name}/{txt}.txt".format(name=pnj["name"], txt=txt)) # On selectionne le texte à dire selon la quete associée
    else: # Sinon on balance un texte automatique
        quest_name, num = Quest.auto_txt(q, pnj["name"])
        if quest_name and num:
            f = open("./PNJ_txt/{name}/{quest_name}_auto_{num}.txt".format(name=pnj["name"], quest_name=quest_name, num=num))
        else:
            f = open("./PNJ_txt/{name}/auto.txt".format(name=pnj["name"]))
    t = f.read()
    Dialog.run_dialog(d, t, speaker=pnj["name"])
    f.close()

def getPos(pnj):
    return pnj["position"]
