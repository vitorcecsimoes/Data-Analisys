import pandas as pd
import numpy as np
import math
import json
import os

def convertToFloat(dataFrame,exceptionList=[]):
	for col in dataFrame:
		if col not in exceptionList:
			print (f'    {col}: Converting values to float')

			# converting from string to float

			dataFrame[col]=dataFrame[col].apply(lambda x: x.replace(",","."))
			dataFrame[col]=pd.to_numeric(dataFrame[col])

	return dataFrame

def zeroSensors(dataFrame,tareTime,specificExceptionList=[],partialExceptionList=[]):
	for col in dataFrame:

		partialException = any([char in col for char in partialExceptionList])
		if col not in specificExceptionList and not partialException:

			# evaluating average value of the first [interval] seconds
			interval=60
			zero=0
			for i in range(interval):
				zero += dataFrame.loc[tareTime+i,col]
			zero/=interval

			if abs(zero) > 1e-3 :
				if "P" in col:
					zero = round(zero)

				elif col == "Dp Orificio" and zero > 3:
					zero = 0.54

			print (f'    {col}: Adjusting {zero} as zero')

			#subtracting average from all entries
			for i in dataFrame.index:
				dataFrame.loc[i,col]-=zero
				if dataFrame.loc[i,col] <0:
					dataFrame.loc[i,col]=0

	return dataFrame

