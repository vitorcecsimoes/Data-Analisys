# V 06
from funcoes.time_handlers import *
from funcoes.fuel_handlers import *
import pandas as pd
import math
import json
import os

def main():
    #---------------#
    # Inicialização #
    #---------------#

    print('Buscando pastas para trabalho')
    os.chdir('..')
    dirList = []
    for item in os.scandir('.'):
        if item.is_dir():
               for subitem in os.scandir(item.path):
                       if subitem.is_dir():
                               dirList.append(subitem.path)


    for folder in dirList:
        
        if "Programa" in folder:
            continue
        print(f'Trabalhando em {folder}')

        os.chdir(folder)

        fileList = os.listdir()

        if "Parametros.txt" in fileList:
            os.rename("Parametros.txt","Parameters.txt")
        if "nome.txt" in fileList:
            os.rename("nome.txt","name.txt")
        if "Concentrações" in fileList:
            os.rename("Concentrações","Concentration")

        fileList = os.listdir()

        with open('Parameters.txt','r+',encoding="utf-8") as f:
            data=f.read()
            param=json.loads(data)
            param=renameVariable(param,"tLeito","tBed")
            param=renameVariable(param,"dOrificio","dOrifice")
            param=renameVariable(param,"tcomb","tfuel")
            param=renameVariable(param,"hcomb","hfuel")
            param=renameVariable(param,"tTara","tTare")
            f.seek(0) #retorna o cursor pro inicio (ao ler o cursor vai pro fim)
            f.truncate() #remove valores antigos do arquivo
            json.dump(param,f, ensure_ascii=False, indent=4)
            f.close()
                
        os.chdir('../..')

    print("\nFEITO")



def renameVariable(dictionary,oldName,newName):
    if newName not in dictionary:
        print(f'Translating {oldName}')
        dictionary[newName]=dictionary[oldName]
        del dictionary[oldName]
    else:
        print(f'{newName} OK')
    return dictionary


if __name__ == '__main__':
    main()
