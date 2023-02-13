# Data-Analisys
This software was developed as a part of master's thesis for mechanical engineering at Universidade Estadual de Campinas (UNICAMP)

The software operate as follows:

## Introduction

This script synchronizes data collected using three different programs that were running on two different computers. After that, it performs data correction, denoising and different types of calculations. All the results are later exported to both an excel file and multiple .csv files locate in a new folder within the experiments results folder.

### Synchronization

The script performs two different corrections regarding the synchronization of the data set: one regarding the response delay between sensors and the other regarding the computer and the software that were used.
For the first case, the physical apparatus can be divided between 3 distinct zones: the fixed bed sensors, the FTIR and the O2 sensor. There is a delay of 2.2 s between the fixed bed and the FTIR and of 6.9 s between the fixed bed and the O2 sensor.
Regarding the software, each of them uses a different form of indexing. For the fixed bed and the O2 sensor the data was indexed by the time and date from one of the computers. The FTIR data is indexed by the time spent after the “start” button is pressed on the software used to collect the gas samples. Finally, the FTIR internal pressure and temperature data is indexed by the time and date of the second computer.
To sumarize, the script developed is capable of synchronizing and adjusting the indexing taking into consideration different types of indexing, different sensor delays and different time frames, since the exact time on the computers used for the collection were out of sync.

### Processing

#### Zeroing
Regarding the processing and corrections, the first correction made is zeroing the sensor values. Some of them indicated non zero values when they were supposed to do so, therefore the script detects and does this correction when needed.

### Fuel density
Using the fuel height and its mass, the software evaluates the fuel total volume and its bulk density.

#### Denoising

A second correction is the denoise of the data provided by the scale. This is done using two methods: the first one is the removal of repeated values, since the scale has a resolution of 0.02 kg which is not refined enough to measure the mass loss in an 1 s interval. The script also evaluates if there is any drastic change of the indicated value, this might happens if there is any external interference during the experiment (such as someone touching the scale mid experiment). After that the software performs a linear interpolation between every 2 remaining points. The other method is applied after the interpolation is done, and consists on re-evaluating the data value by taking the average of its neighboring datapoints, this way eliminating any inflection and reducing overall data noise.
#### Concentration
The gases concentration values must be adjusted using the temperature and pressure data of the FTIR collected. This is done by appliyng the following formula to all concentration data points:

Y_real = y_collected * P_std * T_real / (P_real * T_std)

#### Pressure data

All the pressure data collected must also be adjusted, since the data indicates the value between its point and P10 instead of indicating the value between tis point and P13. This is done by adding or subtracting the P13 value according to the sensor position.

#### Air flow

Using the data from the pressure drop at the orifice plate it is possible to attain the value of the air flow inside the fixed bed. This can only be done using an iterative method.

#### Stoichiometry

Using the mass loss data, the air flow, and the fuel ultimate analysis the scripts evaluates the relationship between the real air flow and the theoretical stoichiometry value of oxygen needed for the combustion to occur.
