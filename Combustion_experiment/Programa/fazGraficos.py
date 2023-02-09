# Esse arquivo plota todos os gráficos de cada queima, incluindo gráficos de gases combinados.

import pandas as pd
import os
import seaborn
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import scipy.stats as stats
import math
from funcoes.convert_name import *

#-------#
# Cores #
#-------#

red = '#fc6969'
blue = '#3d74f5'
green = '#20872b'
black = '#000000'

#---------#
# FUNÇÕES #
#---------#
def limCalc(value):
    
    og=math.floor(math.log10(value))

    newVal = round(value,1-og)

    factor=10**(og-1)

    if math.floor(newVal/factor) % 2 == 0:
        lim = newVal+2*factor
        
    else:
        lim = newVal+factor

    return lim

def getFigures(number):

    og=math.floor(math.log10(number))
    factor=10**(og-1)
    figures = math.floor(number/factor)

    return figures

"""
Essa é a função usada para plotar gráficos com mais de um elemento. Exemplos no final do código
comboFile: Vetor com os nomes dos arquivos a serem plotados no eixo primário
legendText: Vetor com o texto para legendas do que foi plotado no eixo primário
fileName: Nome do arquivo que será salvo, sem extensão
unity: unidade do eixo y primário

caso deseje usar eixo secundário, deve-se atribuir valor para os parâmetros secundários:
secFiles: Vetor com os nomes dos arquivos a serem plotados no eixo secundário
secLegend: Vetor com o texto para legendas do que foi plotado no eixo secundário
secUnity: unidade do eixo y secundário

"""
def comboPlot(comboFile,legendText,fileName,unity,**secAxisArgs):

    secFiles = secAxisArgs.get('secFiles',None)
    secLegend = secAxisArgs.get('secLegend',None)
    secUnity = secAxisArgs.get('secUnity',unity)


    colors = [black,red,blue,green]
    linestyles = ['-','--','-.',':']
    fig, ax = plt.subplots()

    plots=[]
    maxY1=0
    maxY2=0
    
    for i in range(len(comboFile)):
        data = pd.read_csv(comboFile[i],sep=',',index_col='Tempo')
        
        columns=data.columns.values.tolist()

        x = data.index.values

        if "erro" in columns:            
            err = data["erro"].values

        else:
            err=0

        for column in columns:

            if column == "erro":
                continue

            y=data[column].values

            maxY1_new=max(y+err)
            if maxY1_new>maxY1:
                maxY1=maxY1_new


            plots+=ax.plot(x, y, color=colors[i],linestyle = linestyles[i], label=legendText[i])
            ax.fill_between(x, y - err, y + err, color=colors[i], alpha=0.2,label='_nolegend_')

        axisLabelSize = 15


        text = ''
        substances = len(legendText)

        if secFiles is not None:
            text = ' de '
            for substance in legendText:

                if legendText.index(substance) == substances-2:
                    separador = ' e '
                elif legendText.index(substance) == substances-1:
                    separador = ''
                else:
                    separador=', '

                text += substance+separador

        yLabelText = 'Concentração' + text + ' (' + unity + ')'

        ax.set_xlabel("Tempo (s)", fontsize = axisLabelSize)
        ax.set_ylabel(yLabelText, fontsize = axisLabelSize)


    if secFiles is not None:

        ax2 = ax.twinx()
        for j in range(len(secFiles)):
            data = pd.read_csv(secFiles[j],sep=',',index_col='Tempo')
            
            columns=data.columns.values.tolist()

            x = data.index.values

            if "erro" in columns:            
                err = data["erro"].values

            else:
                err=0

            for column in columns:

                if column == "erro":
                    continue

                y=data[column].values

                maxY2_new=max(y+err)
                if maxY2_new>maxY2:
                    maxY2=maxY2_new

                plots+=ax2.plot(x, y, color = colors[i+j+1], linestyle = linestyles[i+j+1], label=secLegend[j])
                ax2.fill_between(x, y - err, y + err, color=colors[i+j+1], alpha=0.2,label='_nolegend_')

            axisLabelSize = 15

            text = ' de '
            substances = len(secLegend)

            for substance in secLegend:

                if secLegend.index(substance) == substances-2:
                    separador = ' e '
                elif secLegend.index(substance) == substances-1:
                    separador = ''
                else:
                    separador=', '

                text += substance+separador

            yLabelText = 'Concentração' + text + ' (' + secUnity + ')' 
            ax2.set_ylabel(yLabelText, fontsize = axisLabelSize)

        comboFile+=secFiles


# Ajuste dos limite de escala dos gráficos para alinhar os dois eixos

    limY1 = limCalc(maxY1)
    num1 = getFigures(limY1)
    factor1 = 10**(math.floor(math.log10(limY1))-1)

    minTicks = 6
    maxTicks = 12
    ticks = minTicks
    
    if secFiles is None:
        
        while num1 % ticks !=0:
            ticks +=1
            
            if ticks > maxTicks:
                limY1+=factor1
                num1+=1
                ticks=minTicks

    
    else:

        limY2 = limCalc(maxY2)
        num2 = getFigures(limY2)
        factor2 = 10**(math.floor(math.log10(limY2))-1)

        

        ticksOk = False

        #print(f'{num1}; {num2}; {num1%num2}')

        if num1 > num2:
            flag = True
            large = num1
            small = num2
        else:
            flag = False
            large = num2
            small = num1

        while large % small !=0:

            while large % small !=0:

                if large % small > small/2:
                    large += 1
                else:
                    small += 1

            if flag:
                limY1=large*factor1
                limY2=small*factor2
            else:
                limY1=small*factor1
                limY2=large*factor2


            num1 = getFigures(limY1)
            num2 = getFigures(limY2)

            #print(f'{num1}; {num2}; {large%small}')
            # print(f'{limY1}; {limY2}; {large%small}')
            # input()

            while num1 % ticks !=0:
                ticks +=1
                
                if ticks > maxTicks:
                    limY1+=factor1
                    num1+=1
                    ticks=minTicks

            if num1 > num2:
                flag = True
                large = num1
                small = num2
            else:
                flag = False
                large = num2
                small = num1

        
        ax2.yaxis.set_major_locator(mtick.LinearLocator(ticks+1))
        ax2.set_ylim(0, limY2)


    ax.yaxis.set_major_locator(mtick.LinearLocator(ticks+1))
    ax.set_ylim(0, limY1)
    ax.set_xlim(0, None)


    labels = [l.get_label() for l in plots]

    ax.legend(plots, labels ,loc='upper center', bbox_to_anchor=(0.5, -0.12), fancybox=True, shadow=True, ncol=len(labels))
    fig.subplots_adjust(bottom=0.20)
    
    title = ''
    files = len(comboFile)
    for file in comboFile:

        if comboFile.index(file) == files-2:
            separador = ' e '
        elif comboFile.index(file) == files-1:
            separador = ''
        else:
            separador=', '

        title += convertName(file[:-4])+separador


    #fig.suptitle(title, fontsize=20)

    saveFile = grafFolder+'\\'+fileName+'.png'
    print(fileName)
    plt.savefig(saveFile,bbox_inches='tight')
    #plt.show()
    plt.close()

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

    # Verifica se já tem pasta para arquivar os graficos gerados
    grafFolder = os.getcwd() + '\\graf'
    exists = os.path.exists(grafFolder)

    # Cria pasta para os CSVs se não existir
    if not exists :
        os.makedirs(grafFolder)
        print("Pasta criada")

    #vai para a pasta de trabalho
    os.chdir('CSV/Tratado')

    #lista os arquivos para fazer loop neles, selecionando só os .csv
    fileList = os.listdir() 
    fileList = [file for file in fileList if file.endswith('.csv')]

    seaborn.set_theme(style='whitegrid',
            rc = {'figure.figsize':(12,8)},
            font_scale = 1.25)

    for file in fileList:

        if file=="tempoChama.csv":

            data = pd.read_csv(file,sep=',',index_col=False)

            fig, ax = plt.subplots()

            data.drop(data.index[0],inplace=True)

            tTemp = data[["z","tTemp"]].copy()
            tPress =data[["z","tPress"]].copy()

            tPress.drop(tPress.index[[0,2]],inplace=True)

            if "Mandioca Muito Ar 2" in folder:
                tPress.drop(tPress.index[-1],inplace=True)

            x = tTemp["tTemp"].values
            y = tTemp["z"].values

            slope, intercept, r, p, std_err = stats.linregress(x, y)

            linY= slope * x + intercept
            a = float('%.3g' % slope)
            b = float('%.3g' % intercept)
            linLabel= f'{a}x + {b}'

            ax.scatter(x, y, color = red, label="Temperatura")
            ax.plot(x, linY, color = red, linestyle='--', label=linLabel)

            x = tPress["tPress"].values
            y = tPress["z"].values
            
            slope, intercept, r, p, std_err = stats.linregress(x, y)

            linY= slope * x + intercept
            a = float('%.3g' % slope)
            b = float('%.3g' % intercept)
            linLabel= f'{a}x + {b}'

            plt.scatter(x, y, color = black, label="Pressão")
            plt.plot(x, linY, color = black, linestyle='--', label=linLabel)

            axisLabelSize = 15

            ax.set_xlabel('Tempo (s)', fontsize = axisLabelSize)
            ax.set_ylabel('Altura (mm)', fontsize = axisLabelSize)

            ax.set_xlim(0, None)
            ax.set_ylim(0, None)

            ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', borderaxespad=0)
            fig.subplots_adjust(right=0.80)

            
            fileName = "velocidade"
            saveFile = grafFolder+'\\'+fileName+'.png'
            print(fileName)
            plt.savefig(saveFile,bbox_inches='tight')
            plt.close()

            continue

        data = pd.read_csv(file,sep=',',index_col='Tempo')

        columns=data.columns.values.tolist()

        fig, ax = plt.subplots()


        #diferencia gás do resto dos dados
        if "erro" in columns:

            x = data.index.values
            y = data["valor"].values
            err = data["erro"].values
            

            ax.plot(x, y, color=black, label=file[:-4])
            ax.fill_between(x, y - err, y + err, color=black, alpha=0.2)


        else:
            seaborn.lineplot(data=data,dashes=False)

            if len(columns)>1:
                ax.legend(bbox_to_anchor=(1.02, 0.5), loc='center left', borderaxespad=0)
                fig.subplots_adjust(right=0.83)
            else:
                ax.legend([],[], frameon=False)

        axisLabelSize = 15

        unity = getUnity(file[:-4])

        if unity == '%v' or unity == 'ppmv':
            yLabelText = 'Concentração (' + unity + ')'
        elif unity == '':
            yLabelText = convertName(file[:-4])
        else:
            yLabelText = convertName(file[:-4]) + ' (' + unity +')'


        ax.set_xlabel("Tempo (s)", fontsize = axisLabelSize)
        ax.set_ylabel(yLabelText, fontsize = axisLabelSize)

        ax.set_ylim(0, None)
        ax.set_xlim(0, None)
    
        fileName = file[:-4]
        saveFile = grafFolder+'\\'+fileName+'.png'
        print(fileName)
        plt.savefig(saveFile,bbox_inches='tight')
        plt.close()

    
    # Essas são as chamadas para plotagem de gráficos com múltiplos elementos

    # Uso apenas do eixo primário
    comboPlot(['Nitric Oxide.csv','Ammonia.csv'],['NO','NH$_3$'],'NO_NH3','ppmv')
    comboPlot(['Carbon Monoxide.csv', 'Carbon Dioxide.csv'],['CO','CO$_2$'],'CO_CO2','%v')
    comboPlot(['Methane.csv', 'Etileno.csv', 'Acetileno.csv'],['CH$_4$','C$_2$H$_2$','C$_2$H$_4$'],'CH4_C2H2_C2H4','%v')

    # Uso de eixo primário e secundário
    comboPlot(['Nitric Oxide.csv','Ammonia.csv'],['NO','NH$_3$'],'NO_NH3_CO','ppmv',secFiles = ['Carbon Monoxide.csv'], secLegend = ['CO'], secUnity = '%v')
    comboPlot(['Nitric Oxide.csv','Ammonia.csv'],['NO','NH$_3$'],'NO_NH3_O2','ppmv',secFiles = ['O2.csv'], secLegend = ['O$_2$'], secUnity = '%v')
    comboPlot(['Carbon Monoxide.csv'],['CO'],'CO_CH4','%v',secFiles = ['Methane.csv'], secLegend = ['CH$_4$'], secUnity = '%v')
    comboPlot(['Ammonia.csv'],['NH$_3$'],'CO_NH3','ppmv',secFiles = ['Carbon Monoxide.csv'], secLegend = ['CO'], secUnity = '%v')
    comboPlot(['Ammonia.csv'],['NH$_3$'],'O2_NH3','ppmv',secFiles = ['O2.csv'], secLegend = ['O$_2$'], secUnity = '%v')
    comboPlot(['Nitric Oxide.csv'],['NO'],'O2_NO','ppmv',secFiles = ['O2.csv'], secLegend = ['O$_2$'], secUnity = '%v')
    comboPlot(['Carbon Monoxide.csv'],['CO'],'O2_CO','%v',secFiles = ['O2.csv'], secLegend = ['O$_2$'], secUnity = '%v')


    



    os.chdir('../../../..')