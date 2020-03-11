# -*- coding: utf-8 -*-

import Menu
import Game
import Tools

def dialog_box_create(ROWS, COLS, percent_size_rows=0.25):
    assert isinstance(percent_size_rows, float) and 0 <= percent_size_rows
    d = dict()
    x = 1
    y = int(ROWS * (1-percent_size_rows))
    d["ylen"] = int(ROWS*percent_size_rows)
    d["xlen"] = COLS - 4
    d["COLS"] = COLS
    d["ROWS"] = ROWS
    d["x"], d["y"] = x, y
    return d

def run_dialog(d, txt, speaker=''):
    ROWS, COLS = d["ROWS"], d["COLS"]
    pages = txt.split('\n\n')

    for page in pages:
        resized_txt_lst = [resized_line for line in page.splitlines() for resized_line in resize_line(line, d["xlen"], '\n')]
        for t in range(0, len(resized_txt_lst), d["ylen"]-int(bool(speaker))):
            text = "".join(resized_txt_lst[t:t+d["ylen"]-int(bool(speaker))])
            if speaker:
                text = Tools.reformat('<bold><underlined>{0} :</>\n'.format(speaker) + text)
            m = Menu.create([[(text, lambda: None)]], d["x"], d["y"], COLS, ROWS-d["y"]+1, text_align="left")
            Menu.run(m)

def resize_line(line, size, carac='', pile=None):
    """Recursive function which separate line (str type) by blocks of size and
add carac at the end of each blocks. Returns a list of these blocks"""
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
