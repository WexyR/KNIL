# coding=utf-8

import PNJ
import Quest
from Tools import w

events = None

def create():
    global events
    events = dict()
    # Les events seront des str commencant par "event" auquels correspondront des
    # destinataires, cibles des events.
    return events

def add(event, dest):
    assert isinstance(event, str)
    assert event[:5] == "event"
    global events

    if event in events.keys():
        events[event].append(dest)
    else:
        events[event] = [dest]

def remove(event, dest):
    assert isinstance(event, str)
    assert event[:5] == "event"
    global events

    if event in events.keys():
        if dest in events[event]:
            events[event].remove(dest)


def generate(event, q):
    global events

    assert isinstance(event, str)
    assert event[:5] == "event"

    if "event_finish" in event:
        quest_name = event.replace('event_finish_', '')
        Quest.finish_quest(q, quest_name)
        Quest.check_quests(q, event)

    elif event in events:
        txt, result = Quest.check_quests(q, event)
        return txt
    else:
        return False
