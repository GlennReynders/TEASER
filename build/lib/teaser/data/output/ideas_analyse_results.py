# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 16:09:15 2016

@author: ina
"""
import os
import time
import teaser.logic.utilities as utilitis
import pandas
import numpy
from multiprocessing import Pool
import buildingspy.simulate.Simulator as si
from modelicares import SimRes

def simulate_project(prj, outputDir, packageDir):
    """
    This function simulates a project with buildings.

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    packageDir : string
        complete output directory where the exported models are (top level package.mo and package.order files)
    """
    #timer
    starttime = time.time()

    utilitis.create_path(utilitis.get_full_path(outputDir))

    #simulation list for buildingspy
    li = []
    for bld in prj.buildings:
        # this is necessary for the correct names in the simulation script
        name = prj.name + "." + bld.name + "." + bld.name  # path to runable building.mo files
        s = si.Simulator(name, "dymola", outputDir, packageDir)
        li.append(s)

    po = Pool(processes=3)
    po.map(simulateCase, li)

    #timer
    endtime = time.time()
    print('Simulation lasted ' + str((endtime - starttime) / 60) + ' minutes.')

def simulateCase(s):
    ''' This is a helper function for simulate_project. Sets common parameters and run a simulation.
    :param s: A simulator object.
    '''

    s.showGUI(show=False)
    s.setStartTime(-2592000)  # simulate one month, before the actual simulations
    s.setStopTime(3.1536e7)  # simulate one year
    s.setSolver("Dassl")
    s.showProgressBar(show=True)
    s.printModelAndTime()
    s.setNumberOfIntervals(56880)  # per 10 min: 56880, per hour: 9480
    s.getParameters()
    s.simulate()

def analyse_results(outputDir):
    ''' This function analyses the results and exports them

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    '''

    buildingsmatlist = []  # list with building.mat strings
    for file in os.listdir(outputDir):
        if file.endswith(".mat"):
            buildingsmatlist.append(file)

    results_csv = open(outputDir + "/TEASER_simulations.csv", 'w')
    results_csv.write(
        "Name of building;Peak power[W];Total energy use[J];Overheating[Ks];\n")
    results_csv.close()

    districtpeakpower = list() #list that sums the peak power of the individual buildings

    for buildingindex, building in enumerate(buildingsmatlist):
        sim = SimRes(outputDir + "/" + building)  # path to .mat file
        buildingname = building[:-4] #buildingname.mat to buildingname
        aliases = {'sim.Te': "Outside temperature",
                   buildingname + '_Building.heatingSystem.QHeaSys': "Q heating system",
                   buildingname + '_Building.building.TSensor[1]': "TSensor of zone"}  # name of Dymola variable : name of header of column
        dfwithalltimes = sim.to_pandas(list(aliases), aliases)
        df = dfwithalltimes.loc[lambda df: df.index > 0, :]  # dataframe, starting with time = 0 (more or less)
        pandas.DataFrame.to_csv(df, path_or_buf=outputDir+ "/" +buildingname+".csv", sep= ";")

        # calculate peak power of all buildings to csv file
        maxvariables = pandas.DataFrame.max(df)  # method for peak power, return a pandas series

        # calculate energy use for space heating
        timearray = df.index.values
        qarray = df['Q heating system / W'].values
        energyuse = numpy.trapz(y=qarray, x=timearray)

        # calculate overheating = K.h (over 25°C = 298.15 K)
        temparray = df["TSensor of zone / K"].values
        overheatingarray = [(temp - 298.15) for temp in temparray]  # this array contains all temp - 25°C, if negative, set to 0, then integrate
        for index, temp in enumerate(overheatingarray):
            if temp < 0.0:
                overheatingarray[index] = 0.0
        overheating = numpy.trapz(y=overheatingarray, x=timearray)

        # add all powers of all buildings, in order to get the peak power of the district
        # assumes that all timesteps of all buildings are equal (!!! not through if different user behaviour)
        # TODO: create a dataframe with timesteps of 10 minutes (not 10 min AND each event)
        if buildingindex == 0:
            # create list for the first time
            for element in qarray:
                districtpeakpower.append(element)
        else:
            # list exists, make the sum of each element respectively
            for index, element in enumerate(qarray):
                districtpeakpower[index] += element

        # print all results of this building
        results_csv = open(outputDir + "/TEASER_simulations.csv", 'a')
        results_csv.write(
            buildingname + ";" + str(maxvariables.loc['Q heating system / W']) + ";" + str(energyuse) + ";" + str(
                overheating) + ";\n")
        results_csv.close()

    #print district peak power at the end
    results_csv = open(outputDir + "/TEASER_simulations.csv", 'a')
    results_csv.write("\n \n \n District peak power;" + str(max(districtpeakpower)))
    results_csv.close()

if __name__ == '__main__':
    analyse_results()
    print("That's it! :)")