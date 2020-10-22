import discord
import json
import os

with open('./modules.json', 'r') as f:
    modules = json.loads(f.read())

def keys_exists(element, *keys):
    for key in keys:
        try:
            element = element[key]
        except KeyError:
            return False
    return True

def nest_create(element, key):
    try:
        element[key]
    except KeyError:
        element[key] = {}

for filename in os.listdir('./modules'):
    if os.path.isdir(f'./modules/{filename}'):
        for module in os.listdir(f'./modules/{filename}'):
            if module.endswith('.py'):
                module = module[:-3]
                if keys_exists(modules, filename, module) == True:
                    if modules[filename][module] != False:
                        modules[filename][module] = True
                        with open ('./modules.json', 'w') as f:
                            f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':')))
                else:
                    nest_create(modules, filename)
                    if filename == 'minecraft':
                        modules[filename][module] = True
                    else:
                        modules[filename][module] = False
                    with open ('./modules.json', 'w') as f:
                        f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':')))

for key in list(modules):
    if key not in os.listdir('./modules'):
        modules.pop(key)
        with open ('./modules.json', 'w') as f:
            f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':')))


for filename in os.listdir('./modules'):
    if os.path.isdir(f'./modules/{filename}'):
        for key in modules[filename]:
            if (f'{key}.py') not in os.listdir(f'./modules/{filename}'):
                modules.pop(key)
                with open ('./modules.json', 'w') as f:
                    f.write(json.dumps(modules, sort_keys=True, indent=4, separators=(',', ':'))) 