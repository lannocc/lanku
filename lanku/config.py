from appdirs import AppDirs

from os.path import join, exists
from os import makedirs


DIRS = AppDirs('lanku', 'LANNOCC')

if not exists(DIRS.user_data_dir):
    makedirs(DIRS.user_data_dir)

HOME = join(DIRS.user_data_dir, 'home')

def load_home_config():
    if not exists(HOME):
        return None

    with open(HOME, 'r') as home:
        return [ int(x) for x in home.readline().strip().split(',') ]

def save_home_config(x, y, w, h):
    with open(HOME, 'w') as home:
        print(f'{x},{y},{w},{h}')
        home.write(f'{x},{y},{w},{h}')

