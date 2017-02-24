# Created November 2016
# Ina De Jaeger (KU Leuven, EnergyVille)

"""ideas_output

This module contains function to call Templates for IDEAS model generation
"""
import teaser.data.output.aixlib_output as aixlib_output
import os
import teaser.logic.utilities as utilitis
from mako.template import Template
from sympy import Point3D, Plane
from sympy.abc import x
from sympy.geometry import Line3D, Segment3D
import teaser.data.input.citygml_input as citygml_in


def export_loss_area(prj,
                   building_model="Detailed",
                   merge_windows=False,
                   internal_id=None,
                   exportpath=None):
    """Exports values to a record file for IDEAS simulation

    The Export function for creating a IDEAS example model

    Parameters
    ----------
    building_model : str
        setter of the used IDEAS building model
        (Currently only detailed is supported)
    merge_windows : bool
            True for merging the windows into the outer walls, False for
            separate resistance for window, default is False
    internal_id : float
        setter of the used building which will be exported, if None then
        all buildings will be exported
    exportpath : string
        if the Files should not be stored in OutputData, an alternative
        path can be specified as a full and absolute path

    """

    #file for all buildings
    help_file_loss_areas = open(utilitis.get_full_path(exportpath +
                                                       "/TEASER_geometry.csv"), 'w')
    help_file_loss_areas.write(
        "Name of building;Number of neighbours; Number of floors; Volume of the zone;\
        Area of the zone;Groundfloor area; Outerwalls area;Window area;\
        Deleted wall area;Innerwall area;Floor area;Total loss area (walls+windows+roof+groundfloor);Total loss area (every house is detached);\n")
    help_file_loss_areas.close()

    #if: internal_id is given, then we look for the buildings in our project,
        # for which the internal_id matches
    #(this could be more than 1 building), only these buildings are exported
    if internal_id is not None:
        exported_list_of_buildings = [bldg for bldg in
                                      prj.buildings if
                                      bldg.internal_id == internal_id]
    else:   #else: no internal_id is given, so all buildings are exported
        exported_list_of_buildings = prj.buildings

    #for now, the only option is detailed
    if building_model == "Detailed":
        print("Printing all buildings, zones and buildingelements")
        for bldgindex, bldg in enumerate(exported_list_of_buildings):
            for zoneindex, zone in enumerate(bldg.thermal_zones, start = 1):
                help_file_loss_areas = open(utilitis.get_full_path(exportpath +
                                                                   "/TEASER_geometry.csv"), 'a')
                help_file_loss_areas.write(str(bldg.name) +";" + str(len(bldg.list_of_neighbours)) +";"+ str(bldg.number_of_floors) +";" + str(zone.volume) + ";" +
                                           str(zone.area) +";")
                help_file_loss_areas.close()

                #loop all building elements of this zone
                buildingelements = zone.outer_walls + zone.inner_walls + zone.windows
                count_outerwalls_area = 0
                count_rooftops_area = 0
                count_groundfloors_area = 0
                count_innerwalls_area = 0
                count_ceilings_area = 0
                count_floors_area = 0
                count_windows_area = 0
                for elementindex, buildingelement in enumerate(buildingelements, start = 1):
                    if type(buildingelement).__name__ == "OuterWall":
                        count_outerwalls_area += buildingelement.area

                    elif type(buildingelement).__name__ == "Rooftop":
                        count_rooftops_area += buildingelement.area

                    elif type(buildingelement).__name__ == "GroundFloor":
                        count_groundfloors_area += buildingelement.area

                    elif type(buildingelement).__name__ == "InnerWall":
                        count_innerwalls_area += buildingelement.area

                    elif type(buildingelement).__name__ == "Ceiling":
                        count_ceilings_area += buildingelement.area

                    elif type(buildingelement).__name__ == "Floor":
                        count_floors_area += buildingelement.area

                    elif type(buildingelement).__name__ == "Window":
                        count_windows_area += buildingelement.area

                help_file_loss_areas = open(utilitis.get_full_path(exportpath +
                                                             "/TEASER_geometry.csv"), 'a')
                help_file_loss_areas.write(str(count_groundfloors_area) + ";" + str(count_outerwalls_area) + ";" +
                                           str(count_windows_area) + ";" + str(bldg.deleted_surfaces_area) + ";" +
                                           str(count_innerwalls_area) + ";" + str(count_floors_area) + ";" +
                                           str(count_outerwalls_area+count_windows_area+2*count_groundfloors_area) + ";" +
                                           str(count_outerwalls_area+count_windows_area+2*count_groundfloors_area+bldg.deleted_surfaces_area) +
                                           "\n")
                help_file_loss_areas.close()
    print("All buildings, zones and buildingelements are listed")