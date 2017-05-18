# Created January 2017
# TEASER Development Team

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""

import teaser.logic.utilities as utilities
import os


def example_save():
    """"This function demonstrates different loading options of TEASER"""

    # In example e4_save we saved two TEASER projects using *.teaserXML and
    # Python package pickle. This example shows how to import these
    # information into your python environment again.

    # To load data from *.teaserXML we can use a simple API function. So
    # first we need to instantiate our API (similar to example
    # e1_generate_archetype). The XML file is called
    # `ArchetypeExample.teaserXML` and saved in the default path. You need to
    #  run e4 first before you can load this example file.

    from teaser.project import Project

    # The last option to import data into TEASER is using a CityGML file. The
    # import of CityGML underlies some limitations e.g. concerning data
    # given in the file and the way the buildings are modeled.

    prj_gml = Project(load_data=True)
    prj_gml.name = "CityGMLSample_Genk_round2_3"

    load_gml = utilities.get_full_path(os.path.join(
        'examples',
        'examplefiles',
        'CityGMLSample.gml'))

    prj_gml.load_citygml(path="C:\Users\ina\Box Sync\Onderzoek\UNDER CONSTRUCTION/4DH2017\FME\Real model build up\Waterschei_works.gml",
                         checkadjacantbuildings=True)
    prj_gml.used_library_calc = 'IDEAS'
    #prj_gml.calc_all_buildings(raise_errors=True)
    prj_gml.export_ideas()

    # After you imported your teaser project one or another way into you
    # python environment you can access variables and functions.

    # if: internal_id is given, then we look for the buildings in our project,
    # for which the internal_id matches
    # (this could be more than 1 building), only these buildings are exported

    exported_list_of_buildings = prj_gml.buildings

    # for now, the only option is detailed
    print("Printing all buildings, zones and buildingelements")
    for bldgindex, bldg in enumerate(exported_list_of_buildings):
        for zoneindex, zone in enumerate(bldg.thermal_zones, start=1):
            print("Building name: " + bldg.name)
            print("Zone name: " + str(zone.name) + " " + str(zone.internal_id))
            print("Building number of floors: " + str(bldg.number_of_floors))
            # loop all building elements of this zone
            buildingelements = zone.outer_walls + zone.inner_walls + zone.windows + zone.rooftops + zone.ground_floors + zone.ceilings + zone.floors
            count_outerwalls_area = 0
            count_rooftops_area = 0
            count_groundfloors_area = 0
            count_innerwalls_area = 0
            count_ceilings_area = 0
            count_floors_area = 0
            count_windows_area = 0
            for elementindex, buildingelement in enumerate(buildingelements, start=1):
                print(buildingelement.name + " has a tilt of " + str(buildingelement.tilt))


if __name__ == '__main__':
    example_save()

    print("Example 9: That's it! :)")
