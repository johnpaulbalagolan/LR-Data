from celery.task import task
from celery.log import get_default_logger
log = get_default_logger()

import importlib

LOADED_FUNCS = {}

def getTaskFunction(config, key):

    if key == 'validate':
        return executeValidateStack
    elif key == 'parse':
        return executeParseStack
    elif key == 'save':
        return executeSaveStack
    else:
        raise Exception("No task configured for '%s'" % key)

def loadFunction(functionName):
    global LOADED_FUNCS
    if functionName not in LOADED_FUNCS:
        (module,func) = functionName.rsplit('.', 1)

        mod = importlib.import_module(module)

        LOADED_FUNCS[functionName] = getattr(mod, func)

    return LOADED_FUNCS[functionName]



@task(queue="validate", ignore_result=True)
def executeValidateStack(envelope, config, enqueueNextTask = True):
    validationResults = {
        'valid': True,
        'data': {}
    }

    if 'validate' in config['tasks']:
        for funcName in config['tasks']['validate']:
            loadFunction(funcName)(envelope, config, validationResults)

            if not validationResults['valid']:
                # print "Failed validation on "+funcName
                break


    # only pass along envelopes that passed validation
    if validationResults['valid']:

        if enqueueNextTask:
            executeParseStack.delay(envelope, config, validationResults)
        else:
            executeParseStack(envelope, config, validationResults, False)

@task(queue="parse", ignore_result=True)
def executeParseStack(envelope, config, validationResults, enqueueNextTask = True):
    parsedDoc = {}

    if 'parse' in config['tasks']:
        for funcName in config['tasks']['parse']:
            loadFunction(funcName)(envelope, config, parsedDoc)

    # apply validationResults data
    parsedDoc.update(validationResults['data'])

    if enqueueNextTask:
        executeSaveStack.delay(envelope, config, parsedDoc)
    else:
        executeSaveStack(envelope, config, parsedDoc, False)


@task(queue="save", ignore_result=True)
def executeSaveStack(envelope, config, parsedDoc, enqueueNextTask = True):
    if 'save' in config['tasks']:
        for funcName in config['tasks']['save']:
            loadFunction(funcName)(envelope, config, parsedDoc)
