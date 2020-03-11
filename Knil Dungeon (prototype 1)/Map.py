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



build = {"roads":lambda grid, r, *values: grid_append_road(grid, r, *values),
         "trees":lambda grid, t, *values: grid_append_tree(grid, t, *values),
         "houses":lambda grid, h, *values: grid_append_house(grid, h, *values),
         "areas":lambda grid, r, *values: grid_append_area(grid, r, *values)}

def create(xml_file_path):
    global build
    assert isinstance(xml_file_path, str)

    root = ET.parse(xml_file_path).getroot()
    buildings = ["areas", "roads", "trees", "houses"]

    dim = xpath(root, "/map/dimension")
    dimension = (int(dim.find('line').text), int(dim.find('column').text))
    val = case_to_dict(xpath(root, "/map/case"))
    grid = [[dict(val) for _ in range(dimension[1])] for _ in range(dimension[0])]
    del dim, dimension

    for building in buildings:
        b = xpath(root, building)
        values = b.find('values')
        for elt in b:
            if elt is not values:
                grid = build[b.tag](grid, elt, values)

    return grid



def case_to_dict(c):
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
    return grid[y][x]

def setCase(grid, x, y, case_value, force=False):
    if not force:
        case = getCase(grid, x, y)
        if not case["crossable"]:
            case_value["crossable"] = 0
    grid[y][x] = case_value
    return grid

# def isWall(g):
#     if type(g)==tuple:
#         if g[2] in range(2,12) or g[3] in range(2,12):
#             return True
#         else :
#             return False
#     else:
#         return False

def grid_append_road(grid, r, values):
    """Ajoute une route a grid"""
    origin = str_to_tuple(r.find("origin").text)
    size = str_to_tuple(r.find("size").text)
    walls = str_to_tuple(r.find("walls").text)
    normal_case = case_to_dict(values.find('normal_case'))
    wall_case = case_to_dict(values.find('wall_case'))
    grid = grid_append_rect(grid, origin, size, walls, normal_case, wall_case, force_normal_value=True)
    return grid

def grid_append_house(grid, h, *args):
    vals = h.find("values")
    abs_origin = str_to_tuple(h.find('origin').text)
    nc = case_to_dict(vals.find("normal_case"))
    wc = case_to_dict(vals.find("wall_case"))
    rooms = [subelement for subelement in h if subelement.tag == 'room']
    for room in rooms:
        grid = grid_append_room(grid, room, abs_origin, nc, wc)
    return grid

def grid_append_room(grid, room, origin, nc, wc):
    x0, y0 = origin
    if room.find('values'):
        values = room.find('values')
        if values.find('normal_case'):
            normal_case = case_to_dict(values.find('normal_case'))
        else:
            normal_case = nc
        if values.find('wall_case'):
            wall_case = case_to_dict(values.find('wall_case'))
        else:
            wall_case = wc
    else:
        normal_case, wall_case = nc, wc
    x1, y1 = str_to_tuple(room.find('origin').text)
    abs_origin = x0+x1, y0+y1
    size = str_to_tuple(room.find('size').text)
    walls = str_to_tuple(room.find('walls').text)
    grid = grid_append_rect(grid, abs_origin, size, walls, normal_case, wall_case, True, False)
    dx, dy = str_to_tuple(room.find('door_location').text)
    dx, dy = x0+x1+dx, y0+y1+dy
    grid = setCase(grid, dx, dy, normal_case, True)
    if room.find('room'):
        for subroom in [subelement for subelement in room if subelement.tag=='room']:
            grid_append_room(grid, subroom, abs_origin, normal_case, wall_case)
    return grid

def grid_append_tree(grid, t, values):
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

def grid_append_area(grid, a, *values):
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

if __name__ == "__main__":
    print_grid(create("data.xml"))
