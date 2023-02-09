# Esse arquivo indica o tempo, local e valor da temperatura máxima obtida durante todas as queimas


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

    data = pd.read_csv("Temperatura.csv",sep=',',index_col='Tempo')

    value = data.max().max()

    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = data.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    columnNames = list(seriesObj[seriesObj == True].index)
    # Iterate over list of columns and fetch the rows indexes where value exists
    for col in columnNames:
        rows = list(result[col][result[col] == True].index)
        for row in rows:
            listOfPos.append((row, col))
    # Return a list of tuples indicating the positions of value in the dataframe

    print(f'\n{folder[3:]}: {listOfPos[0]} {value}')


    os.chdir('../../../..')