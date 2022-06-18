from appdirs import AppDirs

from os.path import join, exists
from os import makedirs


DIRS = AppDirs('lanku', 'LANNOCC')

if not exists(DIRS.user_data_dir):
    makedirs(DIRS.user_data_dir)

def load_win_config(name):
    config = join(DIRS.user_data_dir, name)
    if not exists(config):
        return None

    with open(config, 'r') as config:
        return [ int(x) for x in config.readline().strip().split(',') ]

def save_win_config(name, x, y, w, h):
    config = join(DIRS.user_data_dir, name)

    with open(config, 'w') as config:
        #print(f'{x},{y},{w},{h}')
        config.write(f'{x},{y},{w},{h}')

