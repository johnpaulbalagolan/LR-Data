import importlib

LOADED_FUNCS = {}


def getTaskFunction(config, key):
    global LOADED_FUNCS
    if key in config['tasks']:
        g = globals()

        if key not in LOADED_FUNCS:
            (module,func) = config['tasks'][key].rsplit('.', 1)

            mod = importlib.import_module(module)

            LOADED_FUNCS[key] = getattr(mod, func)

        return LOADED_FUNCS[key]

    else:
        raise Exception("No task configured for '%s'" % key)

