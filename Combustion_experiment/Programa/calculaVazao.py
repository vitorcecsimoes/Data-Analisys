# Esse código calcula a vazão de Ar/A


from funcoes.time_handlers import *
from funcoes.fuel_handlers import *
import pandas as pd
import math
import json
import os
import shutil


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

    os.chdir(folder)

    fileList = os.listdir()

    #verifica se existe a pasta com CSVs, se não ele não trabalha nela
    if "CSV" not in fileList:
        os.chdir('../..')
        continue

    
    os.chdir('CSV/Tratado')

    fileList = os.listdir()

    data = pd.read_csv("vazao_ar_area.csv",sep=',',index_col='Tempo')
    data.drop(index=data.index[:250],inplace=True)
    mean=data["mp/A"].mean()
    error=data["mp/A"].sem()
    print(f'\n{folder[3:]}: {mean} kg/sm2 ({error})')


    os.chdir('../../../..')