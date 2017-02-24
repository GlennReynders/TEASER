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
    prj = Project(load_data=True, used_data_country = "Belgium")
    prj.name = "NSB_TABULA_TER" #ADD
    bldg = Building(parent=prj)

    '''Set some building parameters'''
    bldg.name = "TABULA_SF_TER_1980" #ADD
    bldg.street_name = "Awesome Avenue 42"
    bldg.city = "46325 Fantastic Town"
    bldg.year_of_construction = 1980 #ADD
    bldg.number_of_floors = 2
    bldg.height_of_floors = 2.75

    '''Instantiate a ThermalZone class, with building as parent and set  some
    parameters of the thermal zone'''

    tz = ThermalZone(parent=bldg)
    tz.name = "Living Room"
    tz.area = 168.3 #ADD
    tz.volume = 462.8 #ADD
    tz.infiltration_rate = 5 #ADD old tabula: 7.82

    '''Instantiate UseConditions18599 class with thermal zone as parent,
    and load the use conditions for the usage 'Living' '''

    tz.use_conditions = BoundaryConditions(parent=tz)
    tz.use_conditions.load_use_conditions("Living") #same as CityGML import

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
                                      41.3+9.5, 90.0, 0.0], # ADD
                     #"Outer Wall 2": [bldg.year_of_construction, 'heavy',
                                      #0.0, 90.0, 270.0], #ADD
                     "Outer Wall 3": [bldg.year_of_construction, 'heavy',
                                      41.3, 90.0, 180.0]} #ADD
                     #"Outer Wall 4": [bldg.year_of_construction, 'heavy',
                                      #0.0, 90.0, 90.0]} #ADD

    win_dict = {"Window 1": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             5.7, 90.0, 0.0], #ADD
                "Window 2": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             6.3, 90.0, 90.0], #ADD
                "Window 3": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             5.9, 90.0, 180.0], #ADD
                "Window 4": [bldg.year_of_construction, 'Kunststofffenster, Isolierverglasung',
                             6.4, 90.0, 270.0]} #ADD

    in_wall_dict = {"Inner Wall 1": [bldg.year_of_construction, 'heavy',
                                     82.6, 90.0, 0.0]} #ADD

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

    '''We need to create also a floor and a ceiling
    '''
    floor = Floor(parent=tz)
    floor.name = "Floor"
    floor.load_type_element(bldg.year_of_construction, 'heavy')
    floor.area = 106.3 #ADD
    floor.orientation = -2
    floor.tilt = 0

    ceiling = Ceiling(parent=tz)
    ceiling.name = "Ceiling"
    ceiling.load_type_element(bldg.year_of_construction, 'heavy')
    ceiling.area = 106.3 #ADD
    ceiling.orientation = -1
    ceiling.tilt = 0

    '''For a GroundFloor we are using the load_type_element function,
    which needs the year of construction and the construction type ('heavy'
    or 'light')
    '''
    ground = GroundFloor(parent=tz)
    ground.name = "Ground floor"
    ground.load_type_element(bldg.year_of_construction, 'heavy')
    ground.area = 62.0 #ADD
    ground.orientation = -2
    ground.tilt = 0

    '''Define one element for the roof'''
    roof = Rooftop(parent=tz)
    roof.name = "Rooftop"
    roof.load_type_element(year=bldg.number_of_floors,
                           construction='heavy')
    roof.area = 78.6 #ADD
    roof.orientation = -1
    roof.tilt = 0

    prj.used_library_calc = 'IDEAS'
    prj.calc_all_buildings(raise_errors=True)
    prj.export_ideas()
    prj.export_ideas_loss_area()
    prj.export_ideas_analyse_results(packageDir=None,
                                     outputDir=None)  # simulates project and analyses the results

if __name__ == '__main__':
    example_create_building()
    print("That's it :)")
