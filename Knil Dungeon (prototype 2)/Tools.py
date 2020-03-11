# -*- coding: utf-8 -*-
import ast
import sys
import select
from threading import Thread
from math import sqrt

KEYWORDS = {"z":"UP", "q":"LEFT", "s":"DOWN", "d":"RIGHT", "e":"EXE", "\x1b":"ESC", "i":"i", "j":"j"}

def interact(dest, c, *arg_func, **func):
    global KEYWORDS
    # arg_func est la liste des fonctions qui sont appellees par plusieurs touches et/ou qui ont besoin
    # de la touche appuyée en argument;
    # Exemple: [(("z", "s"), move_vertically), (("q", "d"), move_horizontally)]
    # NB: on peut executer plusieurs fonctions pour les mêmes touches en donnant
    # une liste ou un tuple de focntions à la place d'une simple fonction. Dans
    # ce cas, les fonctions sont éxecutées dans l'ordre donné.

    # func est un dictionnaire crée à partir des paramètres, il prend le nom du paramètre comme touche à appuyer
    # et comme valeur la fonction associée
    # Exemple: interact(dest, m=move) executera la fonction "move" si on appuie sur "m"
    c = c.lower()
    if c in KEYWORDS.keys():
        c = KEYWORDS[c]
    else:
        # La touche n'est pas définie dans le jeu
        return None # quitte interact rapidement, pour éviter de faire la suite inutile
    for keys, f in arg_func:
        if c in keys:
            if type(f) in (tuple, list):
                return [function(dest, c) for function in f]
            else:
                return f(dest, c)
    if c in func.keys():
        return func[c](dest)

def w(string, file=sys.stdout):
    """écrit dans file"""
    file.write(string)

def xpath(element, path):
    """Fonction récursive permettant de se balader dans un arbre xml, en donnant
l'un des élément de l'arbre pour racine, et le chemin pour arriver à l'élément
voulu"""

    assert isinstance(path, (str, list))
    #assert type(element) ==  type(ET.Element)
    if isinstance(path, str):
        lst_path = path.split("/")
    else:
        lst_path = path

    if lst_path:
        if lst_path[0]:
            return xpath(element.find(lst_path.pop(0)), lst_path)
        else:
            lst_path.pop(0)
            return xpath(element, lst_path)
    else:
        return element

def xml_to_dict(element):
    d= dict()
    for subelement in element:
        if list(subelement) :
            d[subelement.tag]=xml_to_dict(subelement)
        else:
            d[subelement.tag]=str_to_tuple(subelement.text)
    return d

def str_to_tuple(string, max_len_str=None):
    if not string:
        return None

    lst = []
    for elt in string.split(','):
        try:
            lst.append(ast.literal_eval(elt.strip()))
        except:
            if not max_len_str:
                lst.append(elt)
            else:
                lst.append(elt[len(elt)-max_len_str:len(elt)])
    if len(lst) == 1:
        return lst[0]
    else:
        return tuple(lst)

def reformat(string):
    format_lst = [("<bold>", "\033[1m"), ("<italic>", "\033[3m"), \
     ("<highlighted>", "\033[7m"), ("<underlined>", "\033[4m"), \
     ("<crossed>", "\033[9m"), ("</>", "\033[0m"), ("<arrow>", "⇲") ]
    for old, new in format_lst:
        string = string.replace(old, new)
    return string

# def isNormalString(string):
#     for c in string:
#         if not (c.isalnum() or c in """.:;"'?!-_() éèàùçêôî"""):
#             return False
#     return True

class Read(Thread):
    """Méthode permettant de récupérer les entrées clavier en parallèle du jeu.
Cette mathode évite le remplissage de la pile dans le cas d'un appui long sur
une touche. Aussi, lors d'une demande de lecture est faite, seule la dernière
touche est renvoyée. De ce fait, les ordres sont instantanés."""

    def __init__(self):
        Thread.__init__(self)
        self.val = None
        self.RUN = True

    def run(self):
        while self.RUN:
            c = sys.stdin.read(1)
            if c:
                self.val = c

    def stop(self):
        self.RUN = False

    def read(self):
        if self.val:
            result = self.val
            self.val = None
        else:
            result = ""
        return result

r = None

def startReadingData():
    """Commence à récupérer les entrées clavier"""
    global r
    r = Read()
    r.start()

def stopReadingData():
    """Arrête de récupérer les entrées clavier"""
    global r
    r.stop()

def readData():
    """Retourne la dernière entrée clavier"""
    global r
    return r.read()

def norm(u):
    """Retourne la norme du vecteur u"""
    return sqrt(sum([c**2 for c in u]))

def scal(u, v):
    """Retourne le produit scalaire u.v """
    return sum([u[i]*v[i] for i in range(len(u))])

def clear():
    """Clears the whole screen with the preset color"""
    w("\033[H\033[2J")

def clear_line():
    """Clears the current line with the preset color"""
    w("\033[2K")

def hide_cursor():
    """Hides the cursor"""
    w("\033[?25l")

def show_cursor():
    """Shows the hidden cursor"""
    w("\033[?25h")

def reset_attributes():
    """All attributes off"""
    w("\033[0m")

def bold():
    """Writes next texts in bold"""
    w("\033[1m")

def italic():
    """Writes next texts in italics"""
    w("\033[3m")

def underline():
    """Writes next texts, underlined"""
    w("\033[4m")

def highlight():
    """Writes next texts, highlighted"""
    w("\033[7m")

def darker_font():
    """Writes next texts with a darker font"""
    w("\033[2m")

def invisible_font():
    """Writes next texts with an invisible font"""
    w("\033[8m")

def crossed():
    """Writes next texts, crossed"""
    w("\033[9m")

def home():
    """Sets the cursor at his "home" position.
the default home position is the upper left corner"""
    w("\033[H")

def goto(line, column=None):
    """Sets the cursor to the coordinates (column, line).
The default column value is the current column.
Warning: The origin is (1, 1), not (0, 0)."""
    assert column is None or isinstance(column, int)
    assert isinstance(line, int)
    assert column is not None and column >= 0
    if line < 0:
        raise ValueError("{0} is negative".format(line))
    if not column:
        w("\033[{y}H".format(y=line))
    else:
        w("\033[{y};{x}H".format(x=column, y=line))

def save():
    """Saves the current cursor position.
You can move the cursor to the saved cursor position by using the Restore Cursor
Position sequence."""
    w("\033[s")

def restore():
    """Sets the cursor to the position stored by the Save Cursor Position
sequence."""
    w("\033[u")

def up(n=1):
    """Moves the cursor up by the specified number of lines n without changing
columns.
If the cursor is already on the top line, ANSI.SYS ignores this sequence."""
    w("\033[{0}A".format(n))

def down(n=1):
    """Moves the cursor down by the specified number of lines n without changing
columns.
If the cursor is already on the bottom line, ANSI.SYS ignores this sequence."""
    w("\033[{0}B".format(n))

def right(n=1):
    """Moves the cursor forward by the specified number of columns n without
changing lines.
If the cursor is already in the rightmost column, ANSI.SYS ignores this
sequence."""
    w("\033[{0}C".format(n))

def left(n=1):
    """Moves the cursor back by the specified number of columns without
changing lines.
If the cursor is already in the leftmost column, ANSI.SYS ignores this sequence."""
    w("\033[{0}D".format(n))

def color_seq(fontcolor=None, bgcolor=None):
    """Return the str-sequence which sets the cursor to the specified colors.
The color can be a number between 0 and 255, a (r, g, b) tuple or a str as
"black", "red", "green", "yellow", "blue", "cyan", or "white"."""
    if not (fontcolor is None or isinstance(fontcolor, (str, int, tuple))):
        raise TypeError("type {0} for {1} is not allowed".format(type(fontcolor), fontcolor))
    if not (bgcolor is None or isinstance(bgcolor, (str, int, tuple))):
        raise TypeError("type {0} for {1} is not allowed".format(type(bgcolor), bgcolor))
    transcolor = {"black":0,
                "red":1,
                "green":2,
                "yellow":3,
                "blue":4,
                "purple":5,
                "cyan":6,
                "white":7}
    result = ""
    for color in (fontcolor, bgcolor):
        if color is not None:
            if isinstance(color, str):
                if color not in transcolor.keys():
                    if color[0] == "\\":
                        color = "\\" + color
                    raise ValueError("The str-sequence '{0}' doesn't match to any color".format(color))
                else:
                    color = transcolor[color]
            if isinstance(color, int):
                if color not in range(256):
                    raise ValueError("The int {0} doesn't match to any color".format(color))
                result += "\033[{mode}8;5;{c}m".format(c=color, mode=(3+int(color==bgcolor)))
            elif isinstance(color, tuple):
                if len(color) != 3:
                    raise ValueError("The tuple {0} doesn't have the good length. Expected 3.".format(color))
                else:
                    for c in color:
                        if not c in range(256):
                            raise ValueError("The int {0} doesn't match to any color".format(c))
                result += "\033[{mode}8;2;{r};{g};{b}m".format(mode=(3+int(color==bgcolor)), r=color[0], g=color[1], b=color[2])

    return result

def color(fontcolor=None, bgcolor=None):
    """sets the cursor to the specified colors.
The color can be a number between 0 and 255 or a str as "black", "red", "green",
"yellow", "blue", "cyan", or "white"."""
    w(color_seq(fontcolor, bgcolor))


if __name__ == "__main__":
    ctype = int(str(input("255 colors -> 1, 16M colors -> 2: ")))
    assert ctype in (1, 2)

    if ctype == 1:
        mode = int(str(input("fontcolor -> 1, background -> 2: ")))
        assert mode in (1, 2)
        mode += 2

        reset_attributes(); home(); clear()
        bold(); underline()
        w("Standart colors :")
        reset_attributes()
        goto(1, 25)
        for r in range(0, 8):
            if mode == 3:
                color(fontcolor=r)
            else:
                color(bgcolor=r)
            w(" {r}".format(r=r) + " "*(4-len(str(r))))

        goto(3, 1)
        reset_attributes(); bold(); underline()
        w("high_intensity colors :")
        reset_attributes()
        goto(3, 25)
        for r in range(8, 16):
            if mode == 3:
                color(fontcolor=r)
            else:
                color(bgcolor=r)
            w(" {r}".format(r=r) + " "*(4-len(str(r))))

        goto(5, 1)
        reset_attributes(); bold(); underline()
        w("216 colors :")
        reset_attributes()
        goto(7, 1)
        for r in range(16, 232):
            if mode == 3:
                color(fontcolor=r)
            else:
                color(fontcolor=238, bgcolor=r)
            w(" {r}".format(r=r) + " "*(4-len(str(r))))
            cols = 36
            j = (r-15)//cols+7
            if (r-15)%cols == 0:
                w(u"\u001b[{j};1H".format(j=j))


        goto(j+1, 1)
        reset_attributes(); bold(); underline()
        w("Grayscale colors:")
        reset_attributes()
        goto(j+1, 25)
        if mode == 4:
            w(u"\033[31;5m")
        for r in range(232, 256):
            if mode == 3:
                color(fontcolor=r)
            else:
                color(bgcolor=r)
            w(" {r}".format(r=r) + " "*(4-len(str(r))))

        reset_attributes()
        goto(j+3, 1)
    else:
        r = int(str(input("red: ")))
        assert r in range(256)
        g = int(str(input("green: ")))
        assert r in range(256)
        b = int(str(input("blue: ")))
        assert r in range(256)
        color(None, (r, g, b))
        home(); clear(); reset_attributes()
