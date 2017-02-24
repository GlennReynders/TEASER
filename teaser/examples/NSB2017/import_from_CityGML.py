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
from teaser.project import Project
import teaser.logic.utilities as utilitis
from mako.template import Template

def example_type_building():
    """"First thing we need to do is to import our Project API module"""

    from teaser.project import Project

    """We instantiate the Project class. The parameter load_data = True indicates
    that we load the XML data bases into our Project.
    This can take a few sec."""

    prj = Project(load_data=True)
    prj.name = "MuisstraatGMLTRY"
  
    """Add here the path to your citygml file, function description: Loads buildings from a citygml file
    calls the function load_gml in data.CityGML we make use of CityGML core and possibly not all kinds of 
    CityGML modelling techniques are supported. If the fucntion of the building is given as Residential 
    (1000) or Office (1120) the importer directly converts the building to archetype buildings. 
    If not only the citygml geometry is imported and you need take care of either the material properties 
    and zoning or you may use the _convert_bldg fucntion in citygml_input module.
        Parameters:	
                path : string
                full path to a CityGML file """
    prj.load_citygml(path="C:\Users\ina\Desktop\MuisstraatGML_FME.gml")
    #we wwant to have the outerwall area for one building of the project
    #print prj.buildings[1].name

    '''We use Annex60 method (e.g with four elements) Which exports one
    Model per zone'''

    #prj.used_library_calc = 'Annex60'
    #prj.number_of_elements_calc = 4
    #prj.merge_windows_calc = False

   # prj.calc_all_buildings(raise_errors=False)


   # We want to print out the outer wall area for each orientation
    # orientation is a float (0: north, 90: est, 180: south, 270: west)

    #prj.export_annex()
   # print prj.buildings[1].get_outer_wall_area(-1) #this works??!! These are TEASER coordinates... Watch out and pluis het uit !!! in citygml_input.py
    #print prj.buildings[1].get_outer_wall_area(-2)
   # print prj.buildings[1].get_outer_wall_area(180.0)
    #print prj.buildings[1].get_outer_wall_area(270.0)
   # prj.save_citygml(path=None)

    prj.used_library_calc = 'AixLib'
    prj.number_of_elements_calc = 2
    prj.merge_windows_calc = False

    prj.calc_all_buildings()

    '''
    Export the Modelica Record. If you have a Dymola License you can  export
    the model with a central AHU (MultizoneEquipped) (only default for office
    and institute buildings)
    '''

    prj.export_aixlib(building_model="MultizoneEquipped",
                      zone_model="ThermalZoneEquipped",
                      corG=True,
                      internal_id=None,
                      path=None)

if __name__ == '__main__':
    example_type_building()
    print("That's it! :)")