# -*- coding: utf-8 -*-

import Menu
import Game
import Tools

def dialog_box_create(ROWS, COLS, percent_size_rows=0.25):
    """Initialise une boite de dialogue"""

    assert isinstance(percent_size_rows, float) and 0 <= percent_size_rows
    d = dict()
    x = 1
    y = int((ROWS-1) * (1-percent_size_rows))+1
    d["ylen"] = int((ROWS-1)*percent_size_rows)
    d["xlen"] = COLS - 4
    d["COLS"] = COLS
    d["ROWS"] = ROWS
    d["x"], d["y"] = x, y
    return d

def run_dialog(d, txt, speaker=''):
    """Lance un texte dans la boite de dialogue, en tenant compte de sa taille (
ajoute des retours à la ligne si elle est trop longue, et des pages si il y a
trop de lignes)"""

    ROWS, COLS = d["ROWS"], d["COLS"]
    pages = txt.split('\n\n') # Sépare tout d'abord les pages

    for page in pages:
        resized_txt_lst = [resized_line for line in page.splitlines() for resized_line in resize_line(line, d["xlen"], '\n')]
        for t in range(0, len(resized_txt_lst), d["ylen"]-int(bool(speaker))):
            text = "".join(resized_txt_lst[t:t+d["ylen"]-int(bool(speaker))])
            if speaker:
                text = Tools.reformat('<bold><underlined>{0} :</>\n'.format(speaker) + text) # Si l'éméteur est précisé, on l'affiche en haut de chaque page en gras souligné
            m = Menu.create([[(text, lambda: None)]], d["x"], d["y"], COLS, d['ylen']+2, text_align="left") # On utilise un menu d'une seule case pour afficher chaque page
            Menu.run(m)

def resize_line(line, size, carac='', pile=None):
    """Fonction récursive qui sépare une chaîne de caractère en blocs de taille donnée, en ajoutant
un caractère entre chaque bloc si besoin"""

    if pile is None:
        pile = [] # Can not put a list as default value for a function
    assert isinstance(line, (str, unicode))
    assert isinstance(size, int) and size > 3
    assert isinstance(pile, list)
    if len(line) > size:
        line1, space, remainder = line[:size+1].rpartition(' ')
        if space:
            line1 += carac
            pile.append(line1)
            line2 = remainder + line[size+1:]
        else:
            line1 = line[:size-1] + "-" + carac
            pile.append(line1)
            line2 = "-" + line[size-1:]
        resize_line(line2, size, carac, pile)
    else:
        pile.append(line + carac)
        return pile
    return pile
