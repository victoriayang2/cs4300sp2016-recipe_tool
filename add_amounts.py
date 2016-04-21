import json
import glob

path = 'jsons\chunk*.json'   
files=glob.glob(path)
for file in files:
    ings = []
    recipes = []
    with open(file) as f:
        for line in f:
            ings.append(json.loads(line)['ing'])
    filename = file.split(".")
    tag = filename[0].split("chunk")[1]
    parsed = 'jsons\parsed' + tag + "." + filename[1]
    with open(parsed) as f:
        for line in f:
            recipes.append(json.loads(line))
    for i,r in enumerate(recipes):
        r['amounts'] = ings[i]
    output = open(parsed, 'w')
    for r in recipes:
        line = json.dumps(r) + "\n"
        output.write(line)
    output.close()