# -*- coding: utf-8 -*-
import sys
import os
import time
import tty
import termios
import traceback

import Menu
import Game
from Tools import *

old_settings = termios.tcgetattr(sys.stdin)
game = None
main_menu = None
ROWS = 31
COLS = 51

def init():
	global game, main_menu, ROWS, COLS
	game = Game.create(ROWS, COLS)
	main_menu = Menu.create([[("Nouvelle\npartie", lambda: Game.restart(game))],
				 [("Reprendre\nla\npartie", lambda: Game.setRunning(game, True))],
				 [("Quitter", lambda: Game.setRunning(game, False))]],
				 COLS-25//2, ROWS//2-10//2, 25, 5, dy=3, framing=False, auto_clear="all")
	tty.setcbreak(sys.stdin.fileno())
	startReadingData()
	reset_attributes(); clear(); hide_cursor()

def run():
	global RUN, game, main_menu

	try:
		Menu.run(main_menu)
		if Game.isRunning(game):
			Game.display(game)
			sys.stdout.flush()
		while Game.isRunning(game):
			key = readData()
			if key:
				int1 = interact(game, key, (("UP", "LEFT", "DOWN", "RIGHT"), Game.move), EXE=Game.exe)
				int2 = interact(main_menu, key, ESC=Menu.run)
				interaction = int1 or int2
				if interaction: # On affiche que si quelque chose a changé
					Game.display(game)
					reset_attributes()
					sys.stdout.flush()
			time.sleep(0.05)
	except:
		exception()

def exception():
	w("\033[37;40m\033[H\033[2J\033[32;40m" + traceback.format_exc(), file=sys.stderr)
	quit()

def quit():
	global old_settings
	stopReadingData()
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
	show_cursor(); reset_attributes(); home(); clear()
	os.kill(os.getpid(), 9) # Méthode plus violente que sys.exit() pour quitter le programme.
							# Je l'utilise ici pour être sûr que les processus liés au Thread soit tués.


if __name__ == "__main__":
	init()
	run()
	quit()
