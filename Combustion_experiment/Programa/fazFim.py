# Esse código remove os dados após o final do experimento.
# Para ele funcionar é preciso criar um arquivo chamado "tBalança.csv" com 3 colunas, uma com o nome do exmperimento, uma com o tempo de início e outra com o tempo de fim

import pandas as pd
import math
import json
import os
import shutil
import scipy.stats as stats


#---------------#
# Inicialização #
#---------------#

print('Carregando configurações')
iniFim = pd.read_csv('tBalanca.csv',sep=',',index_col='Experimento')

print('Buscando pastas para trabalho')
os.chdir('..')
dirList = []
for item in os.scandir('.'):
    if item.is_dir():
           for subitem in os.scandir(item.path):
                   if subitem.is_dir():
                           dirList.append(subitem.path)

zeros = [0 for i in range(len(iniFim.index))]

linRegMassa =pd.DataFrame({'a':zeros,'b':zeros,'r':zeros})

linRegMassa.index=iniFim.index

for folder in dirList:
    
    if "Programa" in folder:
        continue

    os.chdir(folder)

    experiment = os.path.basename(os.getcwd())

    fileList = os.listdir()

    #verifica se existe a pasta com CSVs, se não ele não trabalha nela
    if "CSV" not in fileList:
        os.chdir('../..')
        continue

    print(f'\nTrabalhando em {folder}')

    #criação de pasta se não existir
    outFolder = os.getcwd() + '\\CSV\\Tratado'
    exists = os.path.exists(outFolder)

    if not exists:
        os.makedirs(outFolder)
        print("Pasta criada")

    csvFolder = 'CSV/T13 - 2'
    os.chdir(csvFolder)

    fileList = os.listdir()

    #Leitura do arquivo da balança para fazer regressão linear

    balanca = pd.read_csv('Balanca.csv',sep=',',index_col='Tempo')

    ini = iniFim.loc[experiment,"ini"]
    fim = iniFim.loc[experiment,"fim"]

    x = balanca.iloc[ini:fim].index.values
    y = balanca.iloc[ini:fim,0].values

    #regressão linear da balança
    slope, intercept, r, p, std_err = stats.linregress(x, y)

    linRegMassa.loc[experiment,['a','b','r']]=[slope,intercept,r]

    linY = slope * x + intercept

    #tempo do final do experimento
    expEnd = -intercept/slope+60

    if expEnd>balanca.index[-1]:
        expEnd= balanca.index[-1]
    elif expEnd < fim:
        expEnd = fim + 20

    print(expEnd)

#--------------------#
# Ajustando arquivos #
#--------------------#

    for file in fileList:

        if file=='tempoChama.csv':
            data = pd.read_csv(file,sep=',',index_col='z')

            saveFile = outFolder + '\\' + file

            data.to_csv(saveFile,index='z')

            continue


        print(file)
        data = pd.read_csv(file,sep=',',index_col='Tempo')

        if file == 'Pressao.csv':
            data.drop(['P10', 'P12'], inplace=True,axis=1)

        #removendo final

        data=data[data.index<expEnd]

        saveFile = outFolder + '\\' + file

        data.to_csv(saveFile,index_label="Tempo")

    os.chdir('../../../..')

linRegMassa.to_csv('dados_massa.csv',index_label="Experimento")

with open("dados_massa.txt", "w") as text_file:
    for experiment in linRegMassa.index:
        a = linRegMassa.loc[experiment,'a']*1000
        a = float('%.3g' % a)
        r=linRegMassa.loc[experiment,'r']**2
        r = float('%.3g' % r)
        text_file.write(f'\n{experiment}&{a} R$^2$ = {r}\\\\')