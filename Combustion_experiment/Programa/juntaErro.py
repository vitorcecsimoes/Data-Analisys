# Esse código junta o valor dos gases com seus erros em um mesmo arquivo CSV

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

    print(f'\nTrabalhando em {folder}')

    os.chdir('CSV/T13 - 2')

    fileList = os.listdir()

    for file in fileList:
        errorFile = file[:-4] + " stde.csv"
        if errorFile not in fileList:
            continue

        print(file)
        data = pd.read_csv(file,sep=',',index_col='Tempo')
        errorData = pd.read_csv(errorFile,sep=',',index_col='Tempo')

        data=pd.merge(data,errorData, how="left", left_index=True, right_index=True)
        
        data.columns = ['valor_orig', 'erro_orig']

        data[['valor','erro']]=data[['valor_orig','erro_orig']]

        #ajuste para valor negativo onde existe possibilidade de valor positivo dentro da margem de erro
        data['valor'][data['valor_orig'] < 0] = (data['valor_orig']+data['erro_orig'])/2
        data['erro'][data['valor_orig'] < 0] = (data['valor_orig']+data['erro_orig'])/2

        #ajuste do valor e margem de erro que permite valor negativo
        data['valor'][data['valor_orig']-data['erro_orig'] < 0] = data['valor_orig']+(data['erro_orig']-data['valor_orig'])/2
        data['erro'][data['valor_orig']-data['erro_orig'] < 0] = data['erro_orig']-(data['erro_orig']-data['valor_orig'])/2

        #ajuste de valor e margem de erro que continuam negativos após todas as correções
        data['valor'][data['valor'] < 0] = 0
        data['erro'][data['erro'] < 0] = 0

        #remove os dados originais para ficar só com os corrigidos
        data.drop('valor_orig',inplace=True,axis=1)
        data.drop('erro_orig',inplace=True,axis=1)


        data.to_csv(file,index_label="Tempo")

        os.remove(errorFile)


    os.chdir('../../../..')