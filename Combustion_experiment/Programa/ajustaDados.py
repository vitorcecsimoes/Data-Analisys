# V 09.18
# Author: Vitor Cecconi Simões
print('Carregando bibliotecas')

from funcoes.time_handlers import *
from funcoes.fuel_handlers import *
from funcoes.data_functions import *
import pandas as pd
import numpy as np
import math
import json
import os

def main():
    #-----------#
    # Constants #
    #-----------#

    # Standard temperature and pressure of the gas cell
    Tstd = 170 #oC
    Pstd = 750 #mmHg

    # Time that takes for the gas to reach FTIR and O2 analiser
    FTIRDelay = 2 #s
    O2SensorDelay = 6 #s


    #---------#
    # Startup #
    #---------#

    print('Loading configurations from file')
    with open('config.txt') as f:
            data=f.read()
            config=json.loads(data)

    print('Loading fuel properties')

    propComb=importFuels()

    print('Indexing work folders')
    os.chdir('..')
    dirList = []
    for item in os.scandir('.'):
        if item.is_dir():
               for subitem in os.scandir(item.path):
                       if subitem.is_dir():
                               dirList.append(subitem.path)


    for folder in dirList:
        
        if "Program" in folder:
            continue

        os.chdir(folder)

        fileList = os.listdir()

        #check if the folder has the parameters file, if it doesn't it will be skipped
        if "Parameters.txt" not in fileList:
            os.chdir('../..')
            continue


        print(f'\nWorking in {folder}')

    #--------------#
    # Reading data #
    #--------------#

        print('Reading data')

        with open('Parameters.txt',encoding="utf-8") as f:
            data=f.read()
            param=json.loads(data)

    # Concentration

        os.chdir('Concentration')

        fileList = os.listdir()

        blank={'Time':[]}

        gasData=pd.DataFrame(blank)

        for file in fileList:
            print (file)
            component = file[9:-4]
            data = pd.read_csv(file,names=["Time", component])
            data["Time"]=data["Time"].apply(np.floor) #round time values down (an error lower than 1 s is ok)
            gasData = pd.merge(gasData, data, on="Time", how="outer")

        gasData=gasData.sort_values("Time") #make sure that all time values are ordered from smallest to largest (the time order might be disrupeted when the datas were merged)
        gasData=gasData.reset_index(drop=True)


    # TP and Fixes Bed data

        os.chdir('..')

        fileList = os.listdir()

        fileList = [file for file in fileList if file.endswith('.csv')]

        for file in fileList:
            print (file)
            if "TP" in file:
                tpData = pd.read_csv(file,sep=',')
            else:
                bedData = pd.read_csv(file,sep=';')
                


    #-----------------------#
    # First data adjustment #
    #-----------------------#

        print('Processing values')

    # Concentration time adjustment

        print('Adjusting time')

        seconds_tBed= timeToSeconds(param["tBed"],":")
        seconds_tFTIR = timeToSeconds(param["tFTIR"],":")

        print('    FTIR syncing')
     
        gasData["Time"]=gasData["Time"]+seconds_tBed+FTIRDelay

        start = int(gasData["Time"].iloc[0])
        finish = int(gasData["Time"].iloc[-1])

        timeTemplate=pd.DataFrame({'Time':list(range(start,finish))})

        gasData = pd.merge(timeTemplate, gasData, on="Time", how="left")

        gasData=gasData.interpolate()

        gasData=gasData.set_index("Time")

        gasData.sort_index(axis=1, inplace=True)



    # Adjusting TP columns

        tpData.drop('Comments',inplace=True,axis=1)

        colNames=tpData.columns

        if tpData.loc[1,colNames[1]] > 400:
            tpData.columns = ['Time', 'P', 'T']
        else:
            tpData.columns = ['Time', 'T', 'P']

        

    # Ajusting TP time
        
        print('     TP syncing')

        timeAdjust = seconds_tBed-seconds_tFTIR

        tpData = tpData.iloc[60: , :] # remove the first 60 lines from TP
        tpData.reset_index(drop=True) # resting index

        tpData["Time"]=tpData["Time"].apply(timeToSeconds,args=(" "))+timeAdjust

        for i in tpData.index[:-2]:
            if tpData.loc[i,"Time"]-tpData.loc[i+1,"Time"]==0:
                tpData=tpData.drop(labels=i,axis=0) # remove duplicated time entries

        start = int(tpData["Time"].iloc[0])
        finish = int(tpData["Time"].iloc[-1])

        timeTemplate=pd.DataFrame({'Time':list(range(start,finish))})

        tpData = pd.merge(timeTemplate, tpData, on="Time", how="left")

        tpData=tpData.interpolate()

        gasTPData=pd.merge(gasData, tpData, on="Time", how="left")

        gasTPData["Time"]=pd.to_numeric(gasTPData["Time"])

        gasTPData=gasTPData.set_index("Time")

        

    # Fixed bed time adjustment
        
        print('    Syncing fixed bed data')

        bedData=bedData.rename({'TIME': 'Time'}, axis=1)
        zero_time = timeToSeconds(param["tTare"],":")

        for i in range(len(bedData.index)):  
            bedData.loc[i,"Time"]=int(timeToSeconds(bedData.loc[i,"Time"],":"))

        bedData["Time"]=pd.to_numeric(bedData["Time"])

        print('    Removendo excesso de tempo')
        
        bedData=bedData[bedData.Time>=zero_time] #remove all data before tTare

        bedData=bedData.set_index("Time")



    #-----------------#
    # Zeroing sensors #
    #-----------------#

        print ('Converting data from string to float and zeroing sensor values')

        bedData = convertToFloat(bedData,["Time","DATE","index"])

        bedData = zeroSensors(bedData,zero_time,["Time","DATE","index"],["O2","T","R6"])


    #-----------------------#
    # Adjusting scale value #
    #-----------------------#

        #This piece of code adjust the scale values after the time value after a pre-defined ignition point.

        print('Suavizando a curva da scale')

        scaleBotton=bedData["Balanca"].copy()
        scaleTop=bedData["Balanca"].copy()
        scale = pd.DataFrame(index=bedData.index.copy())

        sensor = "T13" # sensor to be used as reference to determine the ignition point
        limValue = 100 # threshold value of the sensor (the ignition point will be when the sensor indicate this or a higher value)
        stopPoint=0

        # loop to find the exact ignition point
        local=0
        for i in bedData.index:
           val=bedData.loc[i,sensor]
           local+=1
           if val >= limValue:
               stopPoint=i
               break

        scaleBotton=scaleBotton[scaleBotton.index>=stopPoint] #removes all data before the stopPoint
        scaleTop=scaleTop[scaleTop.index<stopPoint] #removes all data after the stopPoint

        scaleBotton.drop_duplicates(keep = 'first', inplace = True)
        auxBalacaBotton = scaleBotton.copy()

        for i in range(1,len(auxBalacaBotton.index)-2):
            if auxBalacaBotton.index[i]-auxBalacaBotton.index[i-1]<3 or auxBalacaBotton.iloc[i-1]-auxBalacaBotton.iloc[i]>0.1:
                scaleBotton.drop(index=auxBalacaBotton.index[i],inplace=True)


        scaleTop=pd.concat([scaleTop,scaleBotton])
        scale=pd.merge(scale,scaleTop, how="left", left_index=True, right_index=True)
        scale=scale.interpolate()

        scale["aux"]=scale["Balanca"]
        halfInterval=3
        check=local-halfInterval
        for i in scale.index[local-halfInterval:-halfInterval-1]:
            if scale.index[check+halfInterval]-scale.index[check-halfInterval]!=halfInterval*2:
                continue
            check+=1
            med=0
            for j in range(-halfInterval,halfInterval):
                med+=scale.loc[i+j,"aux"]/(halfInterval*2)
            scale.loc[i,"Balanca"] = med

        scale.drop('aux',inplace=True,axis=1)

        bedData.drop('Balanca',inplace=True,axis=1)
        bedData=bedData.join(scale)


    #------------#
    # O2 syncing #
    #------------#

        print('Sincronizando O2')

        concO2=bedData["O2"]
        concO2.index=bedData.index-O2SensorDelay
        #concO2=concO2.shift(periods=O2SensorDelay)
        
        bedData.drop('O2',inplace=True,axis=1)
        
        bedData=bedData.join(concO2)



    #----------#
    # Air flow #
    #----------#

        # Evaluation of mp and mp/A using the orifice plate
        print ('Calculando fluxo de ar')
        
        # Fixed bed dimensions
        dTubo = 0.034 #m
        dLeito = 0.220 #m
        hBed = 1300 #mm

        dOrifice = param["dOrifice"]/1000 #m
        AOrificio = (math.pi*dOrifice**2)/4
        ALeito = (math.pi*dLeito**2)/4
        beta = dOrifice/dTubo

        #air properties
        mu = 1.8444e-5 #kg/m.s
        R = 287 #J/kg.K
        Tamb=param["Tamb"]+273.14 #K
        rho = param["Pamb"]*100/(R*Tamb) #kg/m3

        #seting inicial values
        ReD = 10000.0
        bedData["mp"]=pd.NaT
        bedData["mp_dryAir"]=pd.NaT
        bedData["mp/A"]=pd.NaT

        #Antoine's equation values from: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185&Mask=4#Thermo-Phase
        if Tamb<304:
            A=5.40221
            B=1838.675
            C=-31.737
        else:
            A=5.20389
            B=1733.926
            C=-39.485
        
        pg = 10**(A-B/(Tamb+C))
        umAbs=0.622*param["ur"]*pg/(param["Pamb"]-param["ur"]*pg)

        for i in bedData.index:  
            DPorif = bedData.loc[i,"Dp Orificio"]*9.81
            dif = 2
            if DPorif < 20:
                mp=0
            else:
                while (dif>1):
                    A = 1900*beta/ReD
                    Cd = 0.5961 + 0.0261*beta**2-0.216*beta**8+0.000521*(10**6*beta/ReD)**0.7 + (0.0188+0.0063*A)*beta**3.5*(10**6/ReD)**0.3 + 0.011*(0.75-beta)*(2.8-dTubo/0.0254)
                    mp = Cd*AOrificio*(2*DPorif*rho/(1-beta**4))**0.5
                    ReD_new = 4*mp/(math.pi*dTubo*mu)
                    dif = abs(ReD-ReD_new)
                    ReD=ReD_new

            bedData.loc[i,"mp"]=mp
            bedData.loc[i,"mp/A"]=mp/ALeito
            bedData.loc[i,"mp_dryAir"] = (1 - umAbs)*bedData.loc[i,"mp"]
            

    #-----------------------------#
    # Estequiometry and mass loss #
    #-----------------------------#
     
        print('Evaluating mass loss and combustion estequiometry')

        cinzas = 0
        mC=0
        mH=0
        mO=0
        mN=0
        mS=0
        mCl=0
        umidade = 0
        composicaoTotal = 0
        i = 0

        for proporcao in param["comb"]["prop"]:
            composicaoTotal += proporcao

        composicaoTotal *=100 #multipling fuel composition by 100 to adjust fuel dataset

        for comb in param["comb"]["tipo"]:
            cinzas += param["comb"]["prop"][i]*propComb[comb]["imediata"]["cinzas"]/composicaoTotal
            mC += param["comb"]["prop"][i]*propComb[comb]["elementar"]["C"]/composicaoTotal
            mH += param["comb"]["prop"][i]*propComb[comb]["elementar"]["H"]/composicaoTotal
            mO += param["comb"]["prop"][i]*propComb[comb]["elementar"]["O"]/composicaoTotal
            mN += param["comb"]["prop"][i]*propComb[comb]["elementar"]["N"]/composicaoTotal
            mS += param["comb"]["prop"][i]*propComb[comb]["elementar"]["S"]/composicaoTotal
            mCl += param["comb"]["prop"][i]*propComb[comb]["elementar"]["Cl"]/composicaoTotal
            umidade += param["comb"]["prop"][i]*propComb[comb]["imediata"]["umidade"]/composicaoTotal
            i+=1

        #molar mass
        mMolC=12 #kg/kmol
        mMolH=1 #kg/kmol
        mMolN=14 #kg/kmol
        mMolS=32 #kg/kmol
        mMolO=16 #kg/kmol
        
        bedData["mp_comb aux"]=0
        bedData["mp_comb"]=0
        bedData["Ar/Ar Esteq aux"]=0
        bedData["Ar/Ar Esteq"]=0
        
        check=0
        for i in bedData.index[:-2]:
            if bedData.index[check+1]-bedData.index[check]!=1:
                print(f'faltando tempo {secondsToTime(i+1)}')
                continue
            check+=1
            bedData.loc[i,"mp_comb aux"]=bedData.loc[i+1,"Balanca"]-bedData.loc[i,"Balanca"]
        
        #to reduce input noise, an average of the 2*[halfInterval] values is used
        halfInterval=15
        check=halfInterval
        for i in bedData.index[halfInterval+1:-halfInterval-1]:
            if bedData.index[check+halfInterval]-bedData.index[check-halfInterval]!=halfInterval*2:
                continue
            check+=1
            for j in range(-halfInterval,halfInterval):
               bedData.loc[i,"mp_comb"]+=bedData.loc[i+j,"mp_comb aux"]/(2*halfInterval)
            
            if bedData.loc[i,"mp_comb"] < 0:

                #If the plenum temperature is high enough, the fuel is considered to be 100% dry.
                if bedData.loc[i,"T01"]>=100:
                    umidade = 0

                mpCombSeco = (1-umidade)*bedData.loc[i,"mp_comb"]

                nC=mC*(-mpCombSeco)/mMolC
                nH=mH*(-mpCombSeco)/mMolH
                nN=mN*(-mpCombSeco)/mMolN
                nS=mS*(-mpCombSeco)/mMolS
                nO=mO*(-mpCombSeco)/mMolO
                
                nCO2=nC
                nH2O=nH/2
                nNO=nN
                nSO2=nS
                
                nO2=nCO2+nH2O/2+nNO/2+nSO2-nO/2
                nN2=nO2*0.79/0.21
                
                mArEsteq=(2*mMolO*nO2+2*mMolN*nN2) #kg/s
                
                bedData.loc[i,"Ar/Ar Esteq aux"] = bedData.loc[i,"mp_dryAir"]/mArEsteq
              
        #An average is calculated to reduce noise
        check=halfInterval
        for i in bedData.index[halfInterval+1:-halfInterval-1]:
            if bedData.index[check+halfInterval]-bedData.index[check-halfInterval]!=halfInterval*2:
                continue
            check+=1
            med=0
            for j in range(-halfInterval,halfInterval):
                med+=bedData.loc[i+j,"Ar/Ar Esteq aux"]/(halfInterval*2)
            bedData.loc[i,"Ar/Ar Esteq"] = med

        bedData.drop('mp_comb aux',inplace=True,axis=1)
        bedData.drop('Ar/Ar Esteq aux',inplace=True,axis=1)



    #-------------------------#
    # Adjusting pressure data #
    #-------------------------#

        print ('Adjusting pressure data')

        for j in range(2,14):
            sensor = "P{}".format(j)
            print (f'    {sensor}')
            if j < 10:
                for i in bedData.index:  
                    bedData.loc[i,sensor]+= bedData.loc[i,"P13"]
            else:
                for i in bedData.index:  
                    bedData.loc[i,sensor]= bedData.loc[i,"P13"] - bedData.loc[i,sensor]



    #-----------------------------------#
    # Correcting gas concentration data #
    #-----------------------------------#

        print('Correcting gas concentration data')

        gasDataCorrigido=gasTPData.copy()

        gases=gasData.columns

        for gas in gases:
            print(f'    {gas}')
            gasDataCorrigido[gas]=gasDataCorrigido[gas]*Pstd*gasDataCorrigido["T"]/(gasDataCorrigido["P"]*Tstd)

        
        gasDataCorrigido.sort_index(axis=1, inplace=True)




    #--------------------#
    # Combining all data #
    #--------------------#
        print('Combining data')
        

        fullRun=pd.merge(gasDataCorrigido,bedData, left_index=True, right_index=True)

        #Removing extra columns
        fullRun.drop('T',inplace=True,axis=1)
        fullRun.drop('P',inplace=True,axis=1)
        fullRun.drop('DATE',inplace=True,axis=1)
        fullRun.drop('R6_0',inplace=True,axis=1)
        fullRun.drop('R6_1',inplace=True,axis=1)
        fullRun.drop('R6_2',inplace=True,axis=1)
        fullRun.drop('R6_3',inplace=True,axis=1)
        fullRun.drop('T14',inplace=True,axis=1)
        fullRun.drop('T15',inplace=True,axis=1)
        fullRun.drop('T16',inplace=True,axis=1)
        fullRun.drop('O2 ok',inplace=True,axis=1)


        #Defining experiment start point
        print('Seting start point')

        partialFullRun=fullRun.copy()

        sensor = "T13" # Sensor to be used as start point
        limValue = 2 # Threshold value of the sensor
        tag = sensor + ' - ' + str(limValue) # identificantion tag for folder management and excel spreadshet
        stopPoint=0
        for i in partialFullRun.index[2:-2]:
           val=(partialFullRun.loc[i+1,sensor]-partialFullRun.loc[i-1,sensor])/2
           if val >= limValue:
               stopPoint=i
               break

        partialFullRun=partialFullRun[partialFullRun.index>=stopPoint] #removing all data before the start point
        partialFullRun=partialFullRun.reset_index(drop=True)


    #-------------#
    # Flame speed #
    #-------------#
        
        print('Evaluating flame speed')

        top = 13
        bottom = 2
        sensorsID=range(2,top+1)

        flameTime = pd.DataFrame({
            'z':[420,360,300,270,240,210,180,150,120,90,60,30],
            'tTemp':[0 for i in sensorsID],
            'tPress':[0 for i in sensorsID]
            })

        for j in sensorsID:
            sensorP = "P{}".format(j)
            if j<10:
                sensorT = "T0{}".format(j)
            else:
                sensorT = "T{}".format(j)
        
            limValue = 2
            stopPointT=0
            for i in partialFullRun.index[2:-2]:
                
                if partialFullRun.loc[i,"Dp Orificio"] <2: #airflow check
                    continue

                val=(partialFullRun.loc[i+1,sensorT]-partialFullRun.loc[i-1,sensorT])/2
                if val >= limValue:
                    stopPointT=i
                    break

            limValue = 0
            stopPointP=0
            for i in partialFullRun.index:

                if partialFullRun.loc[i,"Dp Orificio"] <2: #airflow check
                    continue

                val=partialFullRun.loc[i,sensorP]
                if val <= limValue:
                    stopPointP=i
                    break

            flameTime.loc[top-j,'tTemp']=stopPointT
            flameTime.loc[top-j,'tPress']=stopPointP

        print('Salvando...')
        
        output = pd.ExcelWriter('tempo_chama.xlsx')
        flameTime.to_excel(output,"tempos", index = None)

        output.save()

        print('Feito')

    #-------#
    # EXCEL #
    #-------#

        print('Saving to EXCEL')

        output = pd.ExcelWriter('dados.xlsx')

        bedData.to_excel(output,"Dados do Leito")
        gasTPData.to_excel(output,"Concentrações")
        fullRun.to_excel(output,"Completo")
        partialFullRun.to_excel(output,tag)

        print('Salvando...')

        output.save()

        print('Feito')


    #-----#
    # CSV #
    #-----#
        
        print('Saving to CSV')


        for criteria in [tag1,tag2]:

            if criteria == tag1:
                csvData=partialFullRun1
            else:
                csvData=partialFullRun

            # Check if the folder is available
            folder = os.getcwd() + '\\CSV\\'+ criteria
            exists = os.path.exists(folder)

            # Create a new folder if necessary
            if not exists :
                os.makedirs(folder)
                print("Pasta CSV criada")

            gases=gasDataCorrigido.columns.values.tolist()

            gases.remove('T')
            gases.remove('P')

            for gas in gases:

                filePath = folder + '\\' + gas + '.csv'

                csvData.to_csv(filePath,columns=[gas],index_label="Time")

            filePath = folder + '\\Temperatura.csv'
            csvData.to_csv(filePath,columns=["T02","T03","T04","T05","T06","T07","T08","T09","T10","T11","T12","T13"],index_label="Time")

            filePath = folder + '\\Temperatura_no_pleno.csv'
            csvData.to_csv(filePath,columns=["T01"],index_label="Time")

            filePath = folder + '\\Pressao.csv'
            csvData.to_csv(filePath,columns=["P2","P3","P4","P5","P6","P7","P8","P9","P10","P11","P12","P13"],index_label="Time")

            filePath = folder + '\\Balanca.csv'
            csvData.to_csv(filePath,columns=["Balanca"],index_label="Time")

            filePath = folder + '\\O2.csv'
            csvData.to_csv(filePath,columns=["O2"],index_label="Time")

            filePath = folder + '\\vazao_ar.csv'
            csvData.to_csv(filePath,columns=["mp_dryAir"],index_label="Time")

            filePath = folder + '\\vazao_ar_area.csv'
            csvData.to_csv(filePath,columns=["mp/A"],index_label="Time")

            filePath = folder + '\\relacao_ar_esteq.csv'
            csvData.to_csv(filePath,columns=["Ar/Ar Esteq"],index_label="Time")

            filePath = folder + '\\flameTime.csv'
            flameTime.to_csv(filePath,columns=['z','tTemp','tPress'],index=False)

        print('Done')



    #--------------#
    # Fuel density #
    #--------------#

        print ('\nEvaluating fuel density')


        hComb=0
        hBed=1300#cm

        for h in param["hfuel"]:
            hComb+=(hBed-h*10)/len(param["hfuel"])

        volComb=ALeito*hComb/1000 #m3

        tMassa=timeToSeconds(param["tcomb"],":")
        massa=0
        for i in range(60):
            massa+=bedData.loc[tMassa+i,"Balanca"]/60

        densidade=massa/volComb

        # Ajustando tudo para 4 algarismos significativos

        massa=float('%.4g' % massa)
        hComb=float('%.4g' % hComb)
        volComb=float('%.4g' % volComb)
        densidade=float('%.4g' % densidade)
        

        #salvando em arquivo .txt
        output=open("densidade.txt","w")

        output.write(f'Massa de combustível: {massa} kg')
        output.write(f'\nAltura do combustível: {hComb} mm ({volComb} m³)')
        output.write(f'\nDensidade bulk: {densidade} kg/m³')

        output.close()

        print('Done')

if __name__=='__main__':
    main()