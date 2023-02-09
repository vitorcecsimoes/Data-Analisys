# Esse programa todos os experimentos em um mesmo gráfico

import pandas as pd
import os
import seaborn
import matplotlib.pyplot as plt
import scipy.stats as stats
from funcoes.convert_name import *

#-------#
# Cores #
#-------#

red = '#e62020'
lightBlue = '#4d91f0'
green = '#20872b'
black = '#000000'
orange = '#f5742a'
darkBlue = '#2611d9'
pink = '#f05bdc'
purple = '#6c07b0'
lime = '#56e37b'

    

#---------------#
# Inicialização #
#---------------#

# Vetor com os arquivos que serão plotados

toPlot = ['Ammonia.csv']

csvDir='./CSV/Tratado'

# Caso plote mais do que 8 experimentos juntos será preciso aumentar o número de cores.

colors=[purple,pink,green,lime,darkBlue,lightBlue,red,orange]

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
    grafFolder = os.getcwd() + '/Graficos combinados'
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

    fig, ax = plt.subplots()
    
    for i in range(len(subDirList)):

        print(subDirList[i])

        os.chdir(subDirList[i])

        name_file = open("nome.txt", "r",encoding='utf-8')
        runName = name_file.read()
        name_file.close()

        os.chdir(csvDir)

        fileList = os.listdir() 
        fileList = [file for file in fileList if file.endswith('.csv')]

        for file in fileList:

            if file not in toPlot:
                continue

            data = pd.read_csv(file,sep=',',index_col='Tempo')

            columns=data.columns.values.tolist()

            if "valor" not in columns:
                data1.rename(columns={ data1.columns[0]: "valor" }, inplace = True)
            
            print(file[:-4])

            x = data.index.values
            y = data["valor"].values
            
            if "erro" in columns:
                err = data["erro"].values
            else:
                err=0

            name = convertName(file[:-4])

            if name!= 'Massa':
                title = 'Comparação da emissão de ' + name
                
                if 'Ammonia' in file or 'Nitric' in file:
                    unity = 'ppm'
                else:
                    unity = '%'

                yLabel = 'Concentração (' + unity + ')'

            else:
                title = 'Comparação da perda de massa'
                yLabel = 'Massa (kg)'

            ax.plot(x, y, color=colors[i], label=runName)
            ax.fill_between(x, y - err, y + err, color=colors[i], alpha=0.2)

            os.chdir('../../..')

    axisLabelSize = 15

    ax.set_xlabel("Tempo (s)", fontsize = axisLabelSize)
    ax.set_ylabel(yLabel, fontsize = axisLabelSize)

    ax.set_ylim(0, None)
    ax.set_xlim(0, None)

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=True, shadow=True, ncol=2)
    fig.subplots_adjust(bottom=0.23)

    fig.suptitle(title, fontsize=20)

    

    saveFile = grafFolder+'/NH3_all.png'
    
    plt.savefig(saveFile,bbox_inches='tight')
    plt.close()
    #plt.show()
    
    os.chdir('../../..')
