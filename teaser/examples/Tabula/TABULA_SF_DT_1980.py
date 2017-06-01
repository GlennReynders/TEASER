#Created July 2015
#TEASER 4 Development Team
"""
This scripts shows how to create a building from scratch (or arbitrary sources)
calculate parameters for a Modelica model and save this example building in a
XML based format. The used classes are imported one after another. Of course
you can import all the classes at the beginning.
"""

'''
First we need to import the classes we want to use
'''

from teaser.logic.buildingobjects.boundaryconditions.boundaryconditions \
    import BoundaryConditions
from teaser.logic.buildingobjects.building import Building
from teaser.logic.buildingobjects.buildingphysics.groundfloor import\
    GroundFloor
from teaser.logic.buildingobjects.buildingphysics.innerwall import InnerWall
from teaser.logic.buildingobjects.buildingphysics.ceiling import Ceiling
from teaser.logic.buildingobjects.buildingphysics.floor import Floor
from teaser.logic.buildingobjects.buildingphysics.layer import Layer
from teaser.logic.buildingobjects.buildingphysics.material import Material
from teaser.logic.buildingobjects.buildingphysics.outerwall import OuterWall
from teaser.logic.buildingobjects.buildingphysics.rooftop import Rooftop
from teaser.logic.buildingobjects.buildingphysics.window import Window
from teaser.logic.buildingobjects.thermalzone import ThermalZone
from teaser.project import Project

def example_create_building():
    '''
    Instantiate a Project class (with load_data set to true), instantiate a
    Building class, with the project as a parent. This automatically adds the
    specific building and all its future changes to the project.
    '''
    prj = Project(load_data=True)
    prj.name = "NSB_TABULA_DT"
    bldg = Building(parent=prj)

    '''Set some building parameters'''
    bldg.name = "TABULA_SF_DT_1980"
    bldg.street_name = "Awesome Avenue 42"
    bldg.city = "46325 Fantastic Town"
    bldg.year_of_construction = 1980
    bldg.number_of_floors = 2
    bldg.height_of_floors = 2.75

    '''Instantiate a ThermalZone class, with building as parent and set  some
    parameters of the thermal zone'''

    tz = ThermalZone(parent=bldg)
    tz.name = "Living Room"
    tz.area = 146.4
    tz.volume = 655.7
    tz.infiltration_rate = 5 #ADD old tabula: 14.3

    '''Instantiate UseConditions18599 class with thermal zone as parent,
    and load the use conditions for the usage 'Living' '''

    tz.use_conditions = BoundaryConditions(parent=tz)
    tz.use_conditions.load_use_conditions("Living")

    '''Define one element for the roof'''

    roof = Rooftop(parent=tz)
    roof.name = "Rooftop"
    roof.load_type_element(year=bldg.number_of_floors,
                           construction='heavy')
    roof.area = 170
    roof.orientation = -1
    roof.tilt = 0


    '''We save information of the Outer and Inner walls as well as Windows
    in dicts, the key is the name, while the value is a list (if applicable)
    [year of construciton,
     construction type,
     area,
     tilt,
     orientation]
     Orientation: TEASER: 0 = North, IDEAS: 0 = South, dus IDEAS>TEASER = -180
     TEASER: (0 : north, 90: est, 180: south, 270: west)
     '''

    out_wall_dict = {"Outer Wall 1": [bldg.year_of_construction, 'heavy',
                                      50.2975+9.5, 90.0, 0.0],
                     "Outer Wall 2": [bldg.year_of_construction, 'heavy',
                                      41.1525, 90.0, 90.0],
                     "Outer Wall 3": [bldg.year_of_construction, 'heavy',
                                      50.2975, 90.0, 180.0],
                     "Outer Wall 4": [bldg.year_of_construction, 'heavy',
                                      41.1525, 90.0, 270.0]}

    in_wall_dict = {"Inner Wall 1": [bldg.year_of_construction, 'heavy',
                                     182.9, 90.0, 0.0]}

    win_dict = {"Window 1": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             8.6, 90.0, 0.0],
                "Window 2": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             9.4, 90.0, 90.0],
                "Window 3": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             11.9, 90.0, 180.0],
                "Window 4": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             10.2, 90.0, 270.0]}

    for key, value in out_wall_dict.items():
        '''instantiate OuterWall class'''
        out_wall = OuterWall(parent = tz)
        out_wall.name = key
        '''load typical construction, based on year of construction and
        construction type'''
        out_wall.load_type_element(year=value[0],
                                   construction=value[1])
        out_wall.area = value[2]
        out_wall.tilt = value[3]
        out_wall.orientation = value[4]

    for key, value in in_wall_dict.items():
        '''instantiate InnerWall class'''
        in_wall = InnerWall(parent = tz)
        in_wall.name = key
        '''load typical construction, based on year of construction and
        construction type'''
        in_wall.load_type_element(year=value[0],
                                  construction=value[1])
        in_wall.area = value[2]
        in_wall.tilt = value[3]
        in_wall.orientation = value[4]

    for key, value in win_dict.items():
        '''instantiate Window class'''
        win = Window(parent = tz)
        win.name = key
        '''load typical construction, based on year of construction and
                construction type'''
        win.load_type_element(year= value[0],
                              construction= value[1])
        win.area = value[2]
        win.tilt = value[3]
        win.orientation = value[4]

    '''For a GroundFloor we are using the load_type_element function,
    which needs the year of construction and the construction type ('heavy'
    or 'light')
    '''
    ground = GroundFloor(parent=tz)
    ground.name = "Ground floor"
    ground.load_type_element(bldg.year_of_construction, 'heavy')
    ground.area = 146.4
    ground.orientation = -2
    ground.tilt = 0

    '''We need to create also a floor and a ceiling
    '''
    floor = Floor(parent=tz)
    floor.name = "Floor"
    floor.load_type_element(bldg.year_of_construction, 'heavy')
    floor.area = 92.0
    floor.orientation = -2
    floor.tilt = 0

    ceiling = Ceiling(parent=tz)
    ceiling.name = "Ceiling"
    ceiling.load_type_element(bldg.year_of_construction, 'heavy')
    ceiling.area = 92.0
    ceiling.orientation = -1
    ceiling.tilt = 0

    '''
    We need to set the projects calculation method. The library we want to
    use is AixLib, we are using a two element model and want an extra resistance
    for the windows. To export the parameters to a Modelica record, we use
    the export_aixlib function. path = None indicates, that we want to store
    the records in TEASER'S Output folder
    '''
    '''Or we use Annex60 method (e.g with four elements). Which exports one
    Model per zone'''

    prj.used_library_calc = 'IDEAS'
    prj.calc_all_buildings(raise_errors=True)
    prj.export_ideas()

if __name__ == '__main__':
    example_create_building()
    print("That's it :)")
