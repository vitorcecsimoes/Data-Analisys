import json
import os


def importFuels():
    os.chdir('combustiveis')
    fileList = os.listdir()
    comb={}
    for file in fileList:
        combName =file[:-5]
        with open(file) as f:
                data=f.read()
                comb[combName]=json.loads(data)
    os.chdir('..')
    return comb