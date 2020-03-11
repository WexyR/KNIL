# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import Event
import time
from Tools import w, str_to_tuple
import sys
import Menu
import Dialog

def init(xml_file_path):
    """Initialise les quêtes"""
    assert isinstance(xml_file_path, str)
    root = ET.parse(xml_file_path).getroot()
    q = dict()
    for quest in root.findall("quest"):
        quest_data = dict()
        quest_data["step_lvl"] = int(quest.find("step_lvl").text)
        quest_data["step_way"] = dict([(int(step.get("n")), (step.find("to_do").text, [result.text for result in step.findall('result')]))\
                    for step in quest.findall("step")])
        quest_data["state"] = "enabled"
        quest_data["auto_txt"] = dict([(pnj.get("name"), str_to_tuple(pnj.text))\
                    for pnj in quest.find("auto_txt").findall("pnj")])
        quest_data["details"] = quest.find("details").text

        Event.add(quest_data["step_way"][quest_data["step_lvl"]][0], quest.get("title"))
        q[quest.get("title")] = quest_data
    return q

def check_quests(q, event, k, b, d, g):
    """Verifie si un event fait avancer une/des quête(s) et met à jour cette/ces
    dernière(s). Peut renvoyer le nom d'un texte à afficher, et une action à executer"""
    result = None
    sorted_q = sorted(q.keys(), key=lambda quest_name: q[quest_name]["step_lvl"], reverse=True)
    for quest_name in sorted_q:
        quest = q[quest_name]
        if quest["state"] != "finished":
            if quest["step_way"][quest["step_lvl"]][0] == event:
                Event.remove(quest["step_way"][quest["step_lvl"]][0], quest_name)
                quest["step_lvl"] += 1
                if quest["step_lvl"] > max(quest["step_way"].keys()):
                    Event.generate("event_finish_{0}".format(quest_name), q, k, b, d, g)
                    finish_quest(q, quest_name)
                else:
                    Event.add(quest["step_way"][quest["step_lvl"]][0], quest_name)
                if result is None:
                    result = quest_name + "_" + str(quest["step_lvl"]-1), quest["step_way"][quest["step_lvl"]-1][1]
    if result is None:
        return "", None
    else:
        return result

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


def details(q, quest, d):
    """Lance une boite de dialogue pour afficher les détails d'une quete"""

    assert isinstance(q, dict)
    txt = getDetails(q, quest)
    Dialog.run_dialog(d, txt)


def run_quest_menu(q, d):
    """Lance un menu qui laisse l'utilisateur choisir sur quel genre de quête il aimerait
avoir des détails (celles commencées, ou celles terminées)"""

    quests_finished = dict([(quest, q[quest]) for quest in q.keys() if isFinished(q, quest)])
    quests_started = dict([(quest, q[quest]) for quest in q.keys() if isStarted(q, quest)])
    grid = [[("Commencées", lambda: run_quest_log(quests_started, d))],
            [("Terminées", lambda: run_quest_log(quests_finished, d))],
            [("Retour", lambda: Menu.stop(quest_menu))]]

    quest_menu = Menu.create(grid, 10, 5, 20, 5, 0, 5, autoquit=False, auto_clear='all')
    Menu.run(quest_menu)

def run_quest_log(q, d, detail=True):
    """Lance un sous-menu qui contient tous les quêtes d'une catégorie selectionnée,
et permet d'en afficher les détails"""

    if detail:
        grid = [[(quest_name, lambda: details(q, quest_name, d))] for quest_name in q]
    else:
        grid = [[(quest_name, None)] for quest_name in q]
    grid.append([("Retour", lambda: Menu.stop(quest_log))])
    quest_log = Menu.create(grid, 32, 5, 20, 3, 0, 0, autoquit=False, auto_clear='all')
    Menu.run(quest_log)

def isStarted(q, quest_name):
    """Teste si une quête est commencée"""

    return q[quest_name]["state"] == "enabled" and q[quest_name]["step_lvl"] > 0

def isFinished(q, quest_name):
    """Teste si une quêtes est terminées"""

    return q[quest_name]["state"] == "finished"

def finish_quest(q, quest_name):
    """Change l'état d'une quête à "Terminé" """

    assert isinstance(quest_name, str)
    q[quest_name]["state"] = "finished"

def getDetails(q, quest_name):
    """Récupère les détails concernant une quêtes"""
    return q[quest_name]["details"]
