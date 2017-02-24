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


def example_type_building():
    """"First thing we need to do is to import our Project API module"""

    from teaser.project import Project

    """We instantiate the Project class. The parameter load_data = True indicates
    that we load the XML data bases into our Project.
    This can take a few sec."""
    prj = Project(load_data=True,used_data_country = "Belgium")
    prj.name = "NSB_Muisstraat_withoutneighbours"
  
    """Add here the path to your citygml file, function description: Loads buildings from a citygml file
    calls the function load_gml in data.CityGML we make use of CityGML core and possibly not all kinds of 
    CityGML modelling techniques are supported. If the fucntion of the building is given as Residential 
    (1000) or Office (1120) the importer directly converts the building to archetype buildings. 
    If not only the citygml geometry is imported and you need take care of either the material properties 
    and zoning or you may use the _convert_bldg fucntion in citygml_input module.
        Parameters:	
                path : string
                full path to a CityGML file """
    prj.load_citygml(path= "C:\Users\ina\Box Sync\Onderzoek\UNDER CONSTRUCTION\NSB2017\FME\MuisstraatGML_FME.gml", checkforneighbours= False)

    prj.used_library_calc = 'IDEAS'
    prj.calc_all_buildings(raise_errors=True)
    prj.export_ideas()
    prj.export_ideas_loss_area()
    prj.export_ideas_analyse_results(packageDir= None,
                                     outputDir= None) #simulates project and analyses the results

if __name__ == '__main__':
    example_type_building()
    print("That's it! :)")