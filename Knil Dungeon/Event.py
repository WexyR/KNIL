# -*- coding: utf-8 -*-

import PNJ
import Quest
import Knil
from Tools import w
import Item
import Dialog
import Background
import Game
import Flashlight

events = None

def create():
    """Initialise le système d'évènements"""

    global events
    events = dict()
    # Les events seront des str commencant par "event" auquels correspondront des
    # destinataires, cibles des events.
    return events

def add(event, dest):
    """Ajoute un destinataire à un évènement attendus (ajoute l'évènement s'il n'existe pas encore)"""

    assert isinstance(event, (str, unicode))
    assert event[:5] == "event"
    global events

    if event in events.keys():
        events[event].append(dest)
    else:
        events[event] = [dest]

def remove(event, dest):
    """Enleve le destinataire d'un évènement"""

    assert isinstance(event, (str, unicode))
    assert event[:5] == "event"
    global events

    if event in events.keys():
        if dest in events[event]:
            events[event].remove(dest)
            if not events[event]:
                del events[event]


def generate(event, q, k, b, d, g):
    """Génère un évènement, et teste si cela avance une quête. Si oui, alors retourne
des informations sur la quête sous la forme d'une chaîne de caractère telle que:
"[nom de la quete]_[étape terminé]" """

    global events

    assert isinstance(event, str)
    assert event[:5] == "event"

    if event in events:
        if "event_finish" in event:
            quest_name = event.split('_')[-1]
            Quest.finish_quest(q, quest_name)   # Termine la quête dans le cas ou l'évènement est un évènement de fin de quête
        txt, result = Quest.check_quests(q, event, k, b, d, g)
        if result:
            for r in result:
                execute(r, k, b, d, q, g)
        return txt
    else:
        return None

def execute(execution, k, b, d, q, g):
    """Execute le(s) résultat(s) d'un évènement"""

    assert isinstance(execution, str)
    execution = execution.split("_")

    assert execution[0] == "execute"

    if execution[1] == "give":
        item_name = execution[2]
        values = execution[3:]
        Knil.add_inventory(k, Item.summon_item(item_name, values), b, d)
        generate('event_having_{item_name}'.format(item_name=item_name), q, k, b, d, g)

    elif execution[1] == "dialog":
        if execution[2] == 'path':
            path = "_".join(execution[3:])
            file = open(path, 'r')
            txt = file.read()
            file.close()
            speaker=''
        else:
            if len(execution) == 4:
                speaker = execution[2]
                txt = execution[3]
            else:
                txt = execution[2]
                speaker=''
        Dialog.run_dialog(d, txt=txt, speaker=speaker)

    elif execution[1] == "grid":
        if execution[2] == "crossable":
            x, y = int(execution[3]), int(execution[4])
            value = int(execution[5])
            Background.setCrossable(Background.getCase(b, x, y), value)
        elif execution[2] == "addObject":
            x, y = int(execution[3]), int(execution[4])
            id = execution[5]
            Background.add_object(b, x, y, id)
        elif execution[2] == "removeObject":
            x, y = int(execution[3]), int(execution[4])
            id = execution[5]
            Background.remove_object(b, x, y, id)
    elif execution[1] == "upFashlight":
        t = float(execution[2])
        Flashlight.improve(Item.getFlashlight(), t)

    elif execution[1] == "endGame":
        Game.end_game(g)
