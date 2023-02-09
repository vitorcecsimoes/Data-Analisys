# Esse script plota os gráficos combinando as queimas em pares.

import pandas as pd
import os
import seaborn
import matplotlib.pyplot as plt
import scipy.stats as stats
from funcoes.convert_name import *

#-------#
# Cores #
#-------#

red = '#fc6969'
blue = '#3d74f5'
green = '#20872b'
black = '#000000'
    

#---------------#
# Inicialização #
#---------------#

# Vetor com os arquivos que serão plotados

toPlot = ['Acetileno.csv','Ammonia.csv','Carbon Dioxide.csv','Carbon Monoxide.csv',
            'Etileno.csv','Methane.csv','Nitric Oxide.csv','Balanca.csv']

csvDir='.\\CSV\\Tratado'


print('Fazendo gráficos combinados')
os.chdir('..')
dirList = []
for item in os.scandir('.'):
    if item.is_dir():
        dirList.append(item.path)

seaborn.set_theme(style='whitegrid', rc = {'figure.figsize':(12,8)}, font_scale = 1.25)

for folder in dirList:
    if "Programa" in folder:
        continue

    print(f'\n\n{folder}')
    os.chdir(folder)

    # Verifica se já tem pasta para arquivar os graficos gerados
    grafFolder = os.getcwd() + '\\Graficos combinados'
    exists = os.path.exists(grafFolder)

    # Cria pasta para os CSVs se não existir
    if not exists :
        os.makedirs(grafFolder)
        print("Pasta criada")

    subDirList =[]
    for subitem in os.scandir('.'):
        if subitem.is_dir():
            subDirList.append(subitem.path)

    subDirList.remove('.\\Graficos combinados')

    for i in range(len(subDirList)):

        os.chdir(subDirList[i])

        name_file = open("nome.txt", "r",encoding='utf-8')
        nameI = name_file.read()
        name_file.close()

        os.chdir(csvDir)

        fileList = os.listdir() 
        fileList = [file for file in fileList if file.endswith('.csv')]

        for file in fileList:

            if file not in toPlot:
                continue

            data1 = pd.read_csv(file,sep=',',index_col='Tempo')

            columns=data1.columns.values.tolist()

            if "valor" not in columns:
                data1.rename(columns={ data1.columns[0]: "valor" }, inplace = True)

            
            print(file[:-4])

            x1 = data1.index.values
            y1 = data1["valor"].values
            
            if "erro" in columns:
                err1 = data1["erro"].values
            else:
                err1=0



            

            name = convertName(file[:-4])

            if name!= 'Massa':
                title = 'Comparação da emissão de ' + name
                
                if 'Ammonia' in file or 'Nitric' in file:
                    unity = 'ppmv'
                else:
                    unity = '%v'

                yLabel = 'Concentração (' + unity + ')'

            else:
                title = 'Comparação da perda de massa'
                yLabel = 'Massa (kg)'

            os.chdir('../../..')

            for j in range(i+1,len(subDirList)):
                fileName = file[:-4] + ' ' + subDirList[i][2:5] + subDirList[i][-10:] +' + '+ subDirList[j][2:5] + subDirList[j][-10:]

                os.chdir(subDirList[j])

                name_file = open("nome.txt", "r",encoding='utf-8')
                nameJ = name_file.read()
                name_file.close()

                os.chdir(csvDir)

                data2 = pd.read_csv(file,sep=',',index_col='Tempo')

                fig, ax = plt.subplots()

                if "valor" not in columns:
                    data2.rename(columns={ data2.columns[0]: "valor" }, inplace = True)

                x2 = data2.index.values
                y2 = data2["valor"].values

                if "erro" in columns:
                    err2 = data2["erro"].values
                else:
                    err2=0

                ax.plot(x1, y1, color=black,linestyle = '-', label=nameI)
                ax.fill_between(x1, y1 - err1, y1 + err1, color=black, alpha=0.2)

                ax.plot(x2, y2, color=red, linestyle = '--', label=nameJ)
                ax.fill_between(x2, y2 - err2, y2 + err2, color=red, alpha=0.2)

                

                axisLabelSize = 15

                ax.set_xlabel("Tempo (s)", fontsize = axisLabelSize)
                ax.set_ylabel(yLabel, fontsize = axisLabelSize)

                ax.set_ylim(0, None)
                ax.set_xlim(0, None)

                ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=True, shadow=True, ncol=2)
                fig.subplots_adjust(bottom=0.20)

                # fig.suptitle(title, fontsize=20)

                

                saveFile = grafFolder+'\\'+fileName+'.png'
                print(fileName)

                plt.savefig(saveFile,bbox_inches='tight')
                plt.close()
                # plt.show()
                # break

                os.chdir('../../..')

            os.chdir(subDirList[i])
            os.chdir(csvDir)

        os.chdir('../../..')


    os.chdir('..')
