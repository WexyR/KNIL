# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from Tools import *
import random

from copy import copy
def print_grid(grid):
    for row in grid:
        line = ""
        for elt in row:
            line += str(elt[0]).ljust(4)
        print(line)


#Dictionnaire qui associe aux mots-clefs de construction leur fonction respective
build = {"roads":lambda grid, r, *values: grid_append_road(grid, r, *values),
         "dungeon_roads":lambda grid, r, *values: grid_append_road(grid, r, *values),
         "trees":lambda grid, t, *values: grid_append_tree(grid, t, *values),
         "houses":lambda grid, h, *values: grid_append_house(grid, h),
         "dungeon_houses":lambda grid, h, *values: grid_append_house(grid, h),
         "areas":lambda grid, r, *values: grid_append_area(grid, r),
         "interactive_cases":lambda grid, i, *values: grid_append_int_cases(grid, i)}

def create(xml_file_path):
    """construction d'une grille à partir d'un fichier de données"""

    global build
    assert isinstance(xml_file_path, str)

    root = ET.parse(xml_file_path).getroot()
    # Ordre de construction
    buildings = ["areas", "roads", "trees", "houses", "dungeon_roads", "dungeon_houses", "interactive_cases"]

    # Grille par défaut
    dim = xpath(root, "/map/dimension")
    dimension = (int(dim.find('line').text), int(dim.find('column').text))
    val = case_to_dict(xpath(root, "/map/case"))
    grid = [[dict(val) for _ in range(dimension[1])] for _ in range(dimension[0])]
    del dim, dimension

    # Modification de la grille, étape par étape
    for building in buildings:
        b = xpath(root, building) # Récupère l'élément parent de construction
        if b is not None:
            values = b.find('values') # Valeurs communes des enfants (certains n'en n'ont pas besoin)
            for elt in b:
                if elt is not values:
                    grid = build[b.tag](grid, elt, values) # On ajoute à la grille la construction de chaque enfants
    return grid



def case_to_dict(c):
    """Construit une case à partir d'un element d'un arbre xml qui possède les
arguments attendus, en tenant compte des cases qui contiennent d'autres cases
(appel récursif) et des cases qui sont aléatoires"""

    case = dict()
    for feature in c:
        if feature.tag == "special_case":
            case[feature.tag] = case_to_dict(feature)
            break
        elif "randomize" in feature.attrib.keys():
            heredity = bool([child for child in feature])
            if heredity:
                vals = [str_to_tuple(child.text, 1) for child in feature]
            else:
                vals = str_to_tuple(feature.text, 1)
            if feature.attrib["equal"] == "True":
                vals = list(random.choice(vals) for _ in range(int(feature.attrib["randomize"])))
            else:
                random.shuffle(vals)
                vals = vals[:int(feature.attrib["randomize"])]
            vals = tuple(vals)
            if len(vals) == 1:
                vals = vals[0]
        else:
            vals = str_to_tuple(feature.text, 1)
        case[feature.tag] = vals
    if c.attrib:
        case["attrib"] = c.attrib
    return case

def getCase(grid, x, y):
    """Retourne la case de la grille aux coordonnées (x, y)"""

    return grid[y][x]

def setCase(grid, x, y, case_value, force=False):
    """Change la case de la grille aux coordonnées (x, y), en tenant compte du
caractère 'traversable' de la case si besoin"""

    if not force:
        case = getCase(grid, x, y)
        if not case["crossable"]:
            case_value["crossable"] = 0
    grid[y][x] = dict(case_value)
    return grid

def grid_append_road(grid, r, values):
    """Ajoute une route à la grille"""

    origin = str_to_tuple(r.find("origin").text)
    size = str_to_tuple(r.find("size").text)
    if r.find('walls') is not None:
        walls = str_to_tuple(r.find("walls").text)
    else:
        walls = (0, 0, 0, 0)
    normal_case = case_to_dict(values.find('normal_case'))
    wall_case = case_to_dict(values.find('wall_case'))
    grid = grid_append_rect(grid, origin, size, walls, normal_case, wall_case, force_normal_value=True, force_wall_value=True)
    return grid

def grid_append_house(grid, h):
    """Ajoute une maison à la grille"""

    vals = h.find("values")
    abs_origin = str_to_tuple(h.find('origin').text)
    nc = case_to_dict(vals.find("normal_case"))
    wc = vals.find("wall_case")
    if wc is not None:
        wc = case_to_dict(wc)
    else:
        wc = nc
    rooms = [subelement for subelement in h if subelement.tag == 'room']
    for room in rooms:
        grid = grid_append_room(grid, room, abs_origin, nc, wc)
    return grid

def grid_append_room(grid, room, origin, nc, wc):
    """Ajoute une salle dans une maison de la grille"""

    x0, y0 = origin
    if room.find('values'):
        values = room.find('values')
        if values.find('normal_case') is not None:
            normal_case = case_to_dict(values.find('normal_case'))
        else:
            normal_case = nc
        if values.find('wall_case') is not None:
            wall_case = case_to_dict(values.find('wall_case'))
        else:
            wall_case = wc
    else:
        normal_case, wall_case = nc, wc
    x1, y1 = str_to_tuple(room.find('origin').text)
    abs_origin = x0+x1, y0+y1
    size = str_to_tuple(room.find('size').text)
    if room.find('walls') is not None:
        walls = str_to_tuple(room.find("walls").text)
    else:
        walls = (0, 0, 0, 0)
    grid = grid_append_rect(grid, abs_origin, size, walls, normal_case, wall_case, True, False)
    if room.find('door') is not None:
        for d in room.findall('door'):
            dx, dy = str_to_tuple(d.find('door_location').text)
            dx, dy = x0+x1+dx, y0+y1+dy
            normal_case_cross = dict(normal_case)

            if d.find('door_cross') is not None:
                normal_case_cross["crossable"] = int(d.find('door_cross').text)
            normal_case_cross['special_type'] = 'door'
            if d.find('doorID') is not None:
                normal_case_cross["doorID"] = d.find('doorID').text
            grid = setCase(grid, dx, dy, normal_case_cross, True)
    if room.find('room') is not None:
        for subroom in [subelement for subelement in room if subelement.tag=='room']:
            grid_append_room(grid, subroom, abs_origin, normal_case, wall_case)
    return grid

def grid_append_tree(grid, t, values):
    """Ajoute un arbre à la grille"""

    x0, y0= str_to_tuple(t.find('origin').text)
    radius= str_to_tuple(t.find('radius').text)
    for j in range(y0-radius, y0+radius+1):
        for i in range(x0-radius, x0+radius+1):
            if i >= 0 and j >= 0 and i < len(grid[0]) and j < len(grid):
                v = (i-x0, j-y0)
                if norm(v) <= radius:
                    grid = setCase(grid, i, j, case_to_dict(values.find('leaf_case')))
    if x0 >= 0 and y0 >= 0 and x0 < len(grid[0]) and y0 < len(grid):
        grid = setCase(grid, x0, y0, case_to_dict(values.find('trunk_case')))
    return grid

def grid_append_area(grid, a):
    """Ajoute une zone à la grille"""

    origin = str_to_tuple(a.find("origin").text)
    size = str_to_tuple(a.find("size").text)
    x0, y0 = origin
    line, column = size
    for j in range(y0, y0+line):
        for i in range(x0, x0+column):
            if i >= 0 and j >= 0 and i < len(grid[0]) and j < len(grid):
                normal_case = case_to_dict(a.find("normal_case"))
                grid = setCase(grid, i, j, normal_case, True)
    return grid

def grid_append_rect(grid, origin, size, walls, normal_case, wall_case=None, force_normal_value=False, force_wall_value=False):
    """Ajoute une rectangle à la grille, en tenant compte des contours si besoin"""

    x0, y0 = origin
    line, column = size
    for j in range(y0, y0+line):
        for i in range(x0, x0+column):
            if i >= 0 and j >= 0 and i < len(grid[0]) and j < len(grid):
                if walls != (0, 0, 0, 0):
                    if wall_case:
                        if j == y0 and walls[0]:
                            grid = setCase(grid, i, j, wall_case, force_wall_value)
                        elif i == x0+column-1 and walls[1]:
                            grid = setCase(grid, i, j, wall_case, force_wall_value)
                        elif j == y0+line-1 and walls[2]:
                            grid = setCase(grid, i, j, wall_case, force_wall_value)
                        elif i == x0 and walls[3]:
                            grid = setCase(grid, i, j, wall_case, force_wall_value)
                        else:
                            grid = setCase(grid, i, j, normal_case, force_normal_value)
                    else:
                        raise ValueError("No value for walls.")
                else:
                    grid = setCase(grid, i, j, normal_case, force_normal_value)
    return grid

def grid_append_int_cases(grid, i):
    """Ajoute une case interactive à la grille"""

    for cpt, case in enumerate(i.findall('case')):
        x, y = str_to_tuple(case.find('origin').text)
        case_value = dict(grid[y][x])
        if i.find('values') is not None:
            for elt in i.find('values'):
                case_value[elt.tag] = str_to_tuple(elt.text, 1)
        if case.find('executions') is not None:
            exec_list = [execution.text for execution in case.find('executions').findall('execution')]
            case_value['executions'] = exec_list
        if case.find('events') is not None:
            event_list = [event.text for event in case.find('events').findall('event')]
            case_value['events'] = event_list
        setCase(grid, x, y, case_value, True)
    return grid

if __name__ == "__main__":
    print_grid(create("data.xml"))
