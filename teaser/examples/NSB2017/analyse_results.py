# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 16:33:20 2016

@author: ina
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 16:09:15 2016

@author: ina
"""
import os
import time
from multiprocessing import Pool
import buildingspy.simulate.Simulator as si
from modelicares import SimRes, util
import pandas
import numpy
import matplotlib.pyplot as plt


def analyseSimResults():
    outputDir = "C:\Users\ina\TEASEROutput"
    buildingsmatlist = []  # list with building.mat strings
    for file in os.listdir(outputDir):
        if file.endswith(".mat"):
            buildingsmatlist.append(file)

    results_csv = open(outputDir + "/results_csv.csv", 'w')
    results_csv.write(
        "Name of building;Peak power[W];Total energy use[J];Overheating[Ks];\n")
    results_csv.close()

    resultsdict = dict()
    districtpeakpower = list()

    for buildingindex, building in enumerate(buildingsmatlist):
        sim = SimRes(outputDir + "/" + building)  # path to .mat file
        buildingname = building[:-4]
        aliases = {'sim.Te': "Outside temperature",
                   buildingname + '_Building.heatingSystem.QHeaSys': "Q heating system",
                   buildingname + '_Building.building.TSensor[1]': "TSensor of zone"}  # name of Dymola variable : name of header of column
        dfwithalltimes = sim.to_pandas(list(aliases), aliases)
        df = dfwithalltimes.loc[lambda df: df.index > 0, :]  # dataframe, starting with time = 0 (more or less)
        # pandas.DataFrame.to_csv(df, path_or_buf=resultspath+ "/" +buildingname+".csv", sep= ";")

        # calculate peak power of all buildings to csv file
        maxvariables = pandas.DataFrame.max(df)  # method for peak power, return pandas series

        # calculate energy use for space heating
        timearray = df.index.values
        qarray = df['Q heating system / W'].values
        energyuse = numpy.trapz(y=qarray, x=timearray)

        # calculate overheating = K.h boven 25°C
        temparray = df["TSensor of zone / K"].values
        overheatingarray = [(temp - 298.15) for temp in temparray]  # this array contains all temp - 25°C, if negative, set to 0, then integrate
        for index, temp in enumerate(overheatingarray):
            if temp < 0.0:
                overheatingarray[index] = 0.0
        overheating = numpy.trapz(y=overheatingarray, x=timearray)

        # add all powers of all buildings, in order to get the peak power
        if buildingindex == 0:
            # create list for the first time
            for element in qarray:
                districtpeakpower.append(element)
        else:
            # list exists, make the sum of each element respectively
            for index, element in enumerate(qarray):
                districtpeakpower[index] += element

        # print all results of this building
        results_csv = open(outputDir + "/results_csv.csv", 'a')
        results_csv.write(
            buildingname + ";" + str(maxvariables.loc['Q heating system / W']) + ";" + str(energyuse) + ";" + str(
                overheating) + ";\n")
        results_csv.close()

        # resultsdict[buildingname] = df #add to dict, key = buildingname, values = dataframe with results"""
    results_csv = open(outputDir + "/results_csv.csv", 'a')
    results_csv.write("\n \n \n District peak power;" + str(max(districtpeakpower)))
    results_csv.close()














    # print resultsdict

    # tSensor = sim[buildingname + "_Building.building.TSensor[1]"]
    # plot = sim.plot(ynames1='Muisstraat7_Building.building.TSensor[1]', ylabel1="TSensor of zone")
    # plot.save(formats='pdf')#doesn't appear?
    # print(resultsTSensor)
    # print(tSensor)
    # calculate hours of overheating and days of overheating
    """overheating = df[df["TSensor of zone / K"] >= 298.15].index.tolist()
    overheatinghours = list()
    overheatingdays = list()
    for time in overheating:
        time = time // 3600
        if time not in overheatinghours:
            overheatinghours.append(time)
        day = time // 24
        if day not in overheatingdays:
            overheatingdays.append(day)"""

    """
    buildingsmatlist = []  # list with building.mat strings
    for file in os.listdir(matpath):
        if file.endswith(".mat"):
            buildingsmatlist.append(file)

    results_csv = open(matpath + "/results_csv.csv", 'w')
    results_csv.write("Name of building;Peak power;Hours of overheating;Days of overheating;Total energy use;\n")
    results_csv.close()

    resultspath = matpath + "/Results"
    #os.makedirs(resultspath)

    resultsdict = dict()
    districtpeakpower = list()

    for buildingindex, building in enumerate(buildingsmatlist):
        sim = SimRes(matpath+"/"+building) #path to .mat file
        buildingname = building[:-4]
        aliases = {'sim.Te':"Outside temperature", buildingname+'_Building.heatingSystem.QHeaSys':"Q heating system", buildingname+'_Building.building.TSensor[1]':"TSensor of zone"} #name of Dymola variable : name of header of column
        dfwithalltimes = sim.to_pandas(list(aliases), aliases)
        df = dfwithalltimes.loc[lambda df: df.index > 0,:] #dataframe, starting with time = 0 (more or less)
        #pandas.DataFrame.to_csv(df, path_or_buf=resultspath+ "/" +buildingname+".csv", sep= ";")

        #calculate peak power of all buildings to csv file
        maxvariables = pandas.DataFrame.max(df) #method for peak power, return pandas series

        #calculate hours of overheating and days of overheating
        overheating = df[df["TSensor of zone / K"] >=  298.15].index.tolist()
        overheatinghours = list()
        overheatingdays = list()
        for time in overheating:
            time = time//3600
            if time not in overheatinghours:
                overheatinghours.append(time)
            day = time//24
            if day not in overheatingdays:
                overheatingdays.append(day)

        #calculate energy use for space heating
        timearray = df.index.values
        qarray = df['Q heating system / W'].values
        energyuse = numpy.trapz(y=qarray, x=timearray)

        print (buildingname)
        print (len(qarray))

        # add all powers of all buildings, in order to get the peak power
        if buildingindex == 0:
            #create list for the first time
            for element in qarray:
                districtpeakpower.append(element)
        else:
            #list exists, make the sum of each element respectively
            for index, element in enumerate(qarray):
                districtpeakpower[index] += element
        print (districtpeakpower)
        print("Max peak power on district level: " + str(max(districtpeakpower)))

        #print all results of this building
        results_csv = open(matpath + "/results_csv.csv", 'a')
        results_csv.write(buildingname +";"+ str(maxvariables.loc['Q heating system / W']) +";"+ str(len(overheatinghours)) +";"+ str(len(overheatingdays)) +";"+ str(energyuse) + ";\n")
        results_csv.close()

        #resultsdict[buildingname] = df #add to dict, key = buildingname, values = dataframe with results

    print (max(districtpeakpower))
    #print resultsdict

    #tSensor = sim[buildingname + "_Building.building.TSensor[1]"]
    #plot = sim.plot(ynames1='Muisstraat7_Building.building.TSensor[1]', ylabel1="TSensor of zone")
    #plot.save(formats='pdf')#doesn't appear?
    #print(resultsTSensor)
    #print(tSensor)"""

if __name__ == '__main__':
    analyseSimResults()
    print("That's it! :)")