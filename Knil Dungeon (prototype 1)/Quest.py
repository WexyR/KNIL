# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import Event
import time
from Tools import w, str_to_tuple
import sys

def init(xml_file_path):
    assert isinstance(xml_file_path, str)
    root = ET.parse(xml_file_path).getroot()
    q = dict()
    for quest in root.findall("quest"):
        quest_data = dict()
        quest_data["step_lvl"] = int(quest.find("step_lvl").text)
        quest_data["step_way"] = dict([(int(step.get("n")), (step.find("to_do").text, [result.text for result in step.findall('result')]))\
                    for step in #sorted(quest.findall("step"), key=lambda step: int(step.get("n")))])
                    quest.findall("step")])
        quest_data["state"] = "enabled"
        quest_data["auto_txt"] = dict([(pnj.get("name"), str_to_tuple(pnj.text)) for pnj in quest.find("auto_txt").findall("pnj")])
        Event.add(quest_data["step_way"][quest_data["step_lvl"]][0], quest.get("title"))
        # else:
        #     quest_data["state"] = "disabled"
        q[quest.get("title")] = quest_data

    return q

def check_quests(q, event):
    """Verifie si un event fait avancer une/des quête(s) et met à jour cette/ces
    dernière(s). Peut renvoyer le nom d'un texte à afficher, et une action à executer"""

    sorted_q = sorted(q.keys(), key=lambda quest_name: q[quest_name]["step_lvl"], reverse=True)
    for quest_name in sorted_q:
        quest = q[quest_name]
        if quest["state"] != "finished":
            if quest["step_way"][quest["step_lvl"]][0] == event:
                Event.remove(quest["step_way"][quest["step_lvl"]][0], quest_name)
                quest["step_lvl"] += 1
                if quest["step_lvl"] > max(quest["step_way"].keys()):
                    Event.generate("event_finish_{0}".format(quest_name), q)
                    quest["state"] = "finished"
                elif quest["step_lvl"] <= 0:
                    continue
                else:
                    Event.add(quest["step_way"][quest["step_lvl"]][0], quest_name)
                return quest_name + "_" + str(quest["step_lvl"]-1), quest["step_way"][quest["step_lvl"]-1][1]
    return "", None

def auto_txt(q, pnj):
    """Si une action sur un pnj ne fait pas avancer de quête, le pnj va parler.
    Le pnj peut alors parler inutilement, ou bien, si il fait partie d'une quête
    en cours, donner des indications pour la résolution de la quête. Cette
    fonction revoie le nom du texte à ouvrir en différenciant les cas cités
    précedement"""

    sorted_q = [qu for qu in sorted(q.keys(), key=lambda quest_name: q[quest_name]["step_lvl"], reverse=True) if q[qu]["state"] != "finished"] # Trie les quêtes non-terminées par ordre d'avancée
    quest = None
    for quest_name in sorted_q:
        if isStarted(q, quest_name) and pnj in q[quest_name]["auto_txt"].keys():
            quest = quest_name
            break
    if not quest:
        return "", None
    else:
        auto_txt = q[quest]["auto_txt"][pnj]
        if isinstance(auto_txt, tuple):
            for i, num in enumerate(auto_txt):
                if num == q[quest]["step_lvl"]:
                    txt_num = auto_txt[i]
                    break
                elif num == q[quest]["step_lvl"]:
                    txt_num = auto_txt[i-1]
                    break
        elif isinstance(auto_txt, int):
            txt_num = auto_txt
        return quest, txt_num

def isStarted(q, quest_name):
    return q[quest_name]["state"] == "enabled" and q[quest_name]["step_lvl"] > 0

def finish_quest(q, quest_name):
    q[quest_name]["state"] = "finished"
