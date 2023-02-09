#  Esse código calcula a velocidade do avanço da frente de chama, considerando a temperatura e a pressão

import pandas as pd
import numpy as np
import math
import json
import os

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


results={'z':[420,360,300,270,240,210,180,150,120,90,60,30]}

for folder in dirList:
    
    if "Programa" in folder:
        continue

    os.chdir(folder)

    fileList = os.listdir()

    #verifica se a pasta contem o arquivo de parâmetros, se não ele não trabalha nela
    if "Parametros.txt" not in fileList:
        os.chdir('../..')
        continue


    print(f'\nTrabalhando em {folder}')

    time = pd.read_excel('tempo_chama.xlsx')


    experiment = os.path.basename(os.getcwd())

    

    for key in time.columns:

        if key=='z':
            continue

        columnID = experiment +' '+ key[1:]
        
        to_dict=[0 for i in range(12)]

        k=0
        for i in time.index:
            to_dict[k]= time.loc[i,key]
            k+=1

        results[columnID]=to_dict

    os.chdir('../..')

    resultsDF = pd.DataFrame(results)

print('Salvando...')

saida = pd.ExcelWriter('velocidade_chama.xlsx')
resultsDF.to_excel(saida,"tempo", index = None)

saida.save()

print('Feito')
