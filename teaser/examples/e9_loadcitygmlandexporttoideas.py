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
    prj_gml.name = "CityGMLSample"

    load_gml = utilities.get_full_path(os.path.join(
        'examples',
        'examplefiles',
        'CityGMLSample.gml'))

    prj_gml.load_citygml(path=load_gml)
    prj_gml.used_library_calc = 'IDEAS'
    #prj_gml.calc_all_buildings(raise_errors=True)
    prj_gml.export_ideas()

    # After you imported your teaser project one or another way into you
    # python environment you can access variables and functions.


if __name__ == '__main__':
    example_save()

    print("Example 9: That's it! :)")
