# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 16:09:15 2016

@author: Ina De Jaeger (KU Leuven, EnergyVille)
"""
from teaser.project import Project
import teaser.logic.utilities as utilitis
from mako.template import Template


def example_type_building():
    """"First thing we need to do is to import our Project API module"""

    from teaser.project import Project

    """We instantiate the Project class. The parameter load_data = True indicates
    that we load the XML data bases into our Project.
    This can take a few sec."""

    prj = Project(load_data=True, used_data_country="Belgium")
    prj.name = "TRYMuisstr"
  
    """Add here the path to your citygml file, function description: Loads buildings from a citygml file
    calls the function load_gml in data.CityGML we make use of CityGML core and possibly not all kinds of 
    CityGML modelling techniques are supported. If the fucntion of the building is given as Residential 
    (1000) or Office (1120) the importer directly converts the building to archetype buildings. 
    If not only the citygml geometry is imported and you need take care of either the material properties 
    and zoning or you may use the _convert_bldg fucntion in citygml_input module.
        Parameters:	
                path : string
                full path to a CityGML file """
    prj.load_citygml(path="C:\Users\ina\Documents\GRB\CityGML Example files\MuisstraatGML_FME_232527.gml", lookforneighbours=True)

    prj.used_library_calc = 'IDEAS'
    prj.calc_all_buildings(raise_errors=True)
    prj.export_ideas()

if __name__ == '__main__':
    example_type_building()
    print("That's it! :)")