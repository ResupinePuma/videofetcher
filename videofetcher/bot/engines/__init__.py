import sys, logging
from os import listdir
from os.path import realpath, dirname, splitext, join
from imp import load_source

engine_dir = dirname(realpath(__file__))
engines = {}
engine_shortcuts = {}


def get_engine_files():
    return [name for name in listdir(engine_dir) if "_engine.py" in name]


def load_module(filename, module_dir):
    modname = splitext(filename)[0]
    if modname in sys.modules:
        del sys.modules[modname]
    filepath = join(module_dir, filename)
    module = load_source(modname, filepath)
    module.name = modname
    return module

def load_engine(engine_module):
    try:
        engine = load_module(engine_module, engine_dir)
    except:
        logging.exception('Cannot load engine "{}"'.format(engine_module))
        return None
    return engine

def load_engines(engine_list: list = [] ):
    global engines
    engines.clear()
    engine_list.extend(get_engine_files())
    for engine_data in engine_list:
        pos = int(engine_data.split("_")[0])
        engine = load_engine(engine_data)
        if engine is not None:
            engines[pos] = engine
    return engines