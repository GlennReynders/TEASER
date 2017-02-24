# -*- coding: utf-8 -*-
"""
Created on Fri Nov 04 08:35:39 2016

@author: ina
"""

# Created July 2015
# TEASER 4 Development Team

"""This module contains an example how to create an archetype Building, to retrofit
that building and to export that building to internal XML and a Modelica record
"""
import teaser.data.bindings.v_0_3_9

def example_type_building():
    """"First thing we need to do is to import our Project API module"""

    from teaser.project import Project

    """We instantiate the Project class. The parameter load_data = True indicates
    that we load the XML data bases into our Project.
    This can take a few sec."""

    prj = Project(load_data=True,used_data_country="Belgium") #we maken een project aan,
                            # true because data bindings for
                            #type elements and use conditions should be loaded
                            #dus instance of dataclass() wordt aangemaakt
                            #de 3 input XML's worden geladen en de bijhorende scripts aangeroepen
                            #om de nodige waarden te kunnen uitlezen
    prj.name = "ArchetypeBuildings_Ref_ANNEX_bel" #de naam van het project is ...

    """The five functions starting with type_bldg giving us the opportunity to
    create the specific type building (e.g. type_bldg_residential). The function
    automatically calculates all the necessary parameter. If not specified different
    it uses vdi calculation method.
    Dus type_bldg_residential maakt een instance aan van building() en zal vervolgens alles berekenen
    neen!! geen instantie van building() wel van singlefamilydwelling() dit is een specifieker gebouwtype
    """

    prj.type_bldg_residential(name="ResidentialBuilding",
                              year_of_construction=1970,
                              number_of_floors=2,
                              height_of_floors=3.5,
                              net_leased_area=100,
                              construction_type="heavy")

    '''Or we use Annex60 method (e.g with four elements). Which exports one
    Model per zone'''

    prj.used_library_calc = 'Annex60'
    prj.number_of_elements_calc = 4
    prj.merge_windows_calc = False
    prj.calc_all_buildings(raise_errors=True)
    prj.export_annex()

if __name__ == '__main__':
    example_type_building()
    print("That's it! :)")
