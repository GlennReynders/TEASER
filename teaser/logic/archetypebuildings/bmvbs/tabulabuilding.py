# created June 2015
# by TEASER4 Development Team
from teaser.logic.archetypebuildings.residential \
    import Residential
from teaser.logic.buildingobjects.boundaryconditions.boundaryconditions \
    import BoundaryConditions as UseCond
from teaser.logic.buildingobjects.buildingphysics.ceiling import Ceiling
from teaser.logic.buildingobjects.buildingphysics.floor import Floor
from teaser.logic.buildingobjects.buildingphysics.groundfloor \
    import GroundFloor
from teaser.logic.buildingobjects.buildingphysics.innerwall import InnerWall
from teaser.logic.buildingobjects.buildingphysics.outerwall import OuterWall
from teaser.logic.buildingobjects.buildingphysics.rooftop import Rooftop
from teaser.logic.buildingobjects.buildingphysics.window import Window
from teaser.logic.buildingobjects.thermalzone import ThermalZone
from teaser.logic.buildingobjects.buildingphysics.layer import Layer
from teaser.logic.buildingobjects.buildingphysics.material import Material
from teaser.project import Project


class TabulaBuilding(Residential):
    """Archetype Residential Building according

    Subclass from Residential archetpye class to represent
    TabulaBuilding

    The SingleFamilyDwelling module contains a singlezone building. It has 4
    outer walls, 4 windows, a flat roof and a ground floor. Depending on (
    typical length and width) the interior wall areas are assigned. It makes
    number_of_floors and height_of_floors mandatory parameters.
    Additional information can be passed
    to the archetype (e.g. floor layout and number of neighbors).

    Default values are given according to IWU.

    In detail the net leased area is divided into the following thermal zone
    area:

    #. Single dwelling (100% of net leased area)

    Parameters
    ----------

    parent: Project()
        The parent class of this object, the Project the Building belongs to.
        Allows for better control of hierarchical structures. If not None it
        adds this Building instance to Project.buildings.
        (default: None)
    name : str
        Individual name
    year_of_construction : int
        Year of first construction
    construction_period: list[str]
        Construction period of Building
    height_of_floors : float [m]
        Average height of the buildings' floors
    number_of_floors : int
        Number of building's floors above ground
    net_leased_area : float [m2]
        Total net leased area of building. This is area is NOT the footprint
        of a building
    with_ahu : Boolean
        If set to True, an empty instance of BuildingAHU is instantiated and
        assigned to attribute central_ahu. This instance holds information for
        central Air Handling units. Default is False.
    residential_layout : int
        Structure of floor plan (default = 0)
            0: compact
            1: elongated/complex
    attic : int
        Design of the attic. CAUTION: this will not change the orientation or
        tilt of the roof instances, but just adapt the roof area(!) (default
        = 0)
            0: flat roof
            1: non heated attic
            2: partly heated attic
            3: heated attic
    cellar : int
        Design of the of cellar CAUTION: this will not change the
        orientation, tilt of GroundFloor instances, nor the number or area of
        ThermalZones, but will change GroundFloor area(!) (default = 0)
            0: no cellar
            1: non heated cellar
            2: partly heated cellar
            3: heated cellar
    dormer : str
        Is a dormer attached to the roof? CAUTION: this will not
        change roof or window orientation or tilt, but just adapt the roof
        area(!) (default = 0)
            0: no dormer
            1: dormer
    construction_type : str
        Construction type of used wall constructions default is "heavy")
            heavy: heavy construction
            light: light construction

    Note
    ----------
    The listed attributes are just the ones that are set by the user
    calculated values are not included in this list. Changing these values is
    expert mode.


    Attributes
    ----------

    zone_area_factors : dict
        This dictionary contains the name of the zone (str), the
        zone area factor (float) and the zone usage from BoundaryConditions XML
        (str). (Default see doc string above)
    outer_wall_names : dict
        This dictionary contains a random name for the outer walls,
        their orientation and tilt. Default is a building in north-south
        orientation)
    roof_names : dict
        This dictionary contains the name of the roofs, their orientation
        and tilt. Default is one flat roof.
    ground_floor_names : dict
        This dictionary contains the name of the ground floors, their
        orientation and tilt. Default is one ground floor.
    window_names : dict
        This dictionary contains the name of the window, their
        orientation and tilt. Default is a building in north-south
        orientation)
    inner_wall_names : dict
        This dictionary contains the name of the inner walls, their
        orientation and tilt. Default is one cumulated inner wall.
    ceiling_names : dict
        This dictionary contains the name of the ceilings, their
        orientation and tilt. Default is one cumulated ceiling.
    floor_names : dict
        This dictionary contains the name of the floors, their
        orientation and tilt. Default is one cumulated floor.
    est_living_area_factor : float
        Estimation factor for calculation of number of heated floors
    est_bottom_building_closure : float
        Estimation factor to calculate ground floor area
    est_upper_building_closure : float
        Estimation factor to calculate attic area
    est_factor_win_area : float
        Estimation factor to calculate window area
    est_factor_cellar_area : float
        Estimation factor to calculate heated cellar area
    """

    def __init__(
            self,
            parent,
            name=None,
            year_of_construction=None,
            construction_period=None,
            number_of_floors=None,
            height_of_floors=None,
            net_leased_area=None,
            with_ahu=False,
            residential_layout=None,
            neighbour_buildings=None,
            attic=None,
            cellar=None,
            dormer=None,
            construction_type=None):

        """Constructor of SingleFamilyDwelling
        """

        super(TabulaBuilding, self).__init__(
            parent,
            name,
            year_of_construction,
            net_leased_area,
            with_ahu)

        self.construction_period = construction_period
        self.residential_layout = residential_layout
        self.neighbour_buildings = neighbour_buildings
        self.attic = attic
        self.cellar = cellar
        self.dormer = dormer
        self.construction_type = construction_type
        self.number_of_floors = number_of_floors
        self.height_of_floors = height_of_floors

        # Parameters are default values for current calculation following IWU

        # [area factor, usage type(has to be set)]
        self.zone_area_factors = {"SingleDwelling": [1, "Living"]}

        self.est_living_area_factor = 0.75  # fW
        self.est_bottom_building_closure = 1.33  # p_FB
        self.est_upper_building_closure = 1.0
        self.est_factor_win_area = 0.2
        self.est_factor_cellar_area = 0.5

        self.nr_of_orientation = 1

        # estimated intermediate calculated values
        self._living_area_per_floor = 0
        self._number_of_heated_floors = 0
        self._est_factor_heated_cellar = 0
        self._est_factor_heated_attic = 0
        self._est_roof_area = 0
        self._est_ground_floor_area = 0.0
        self._est_win_area = 0
        self._est_outer_wall_area = 0.0
        self._est_cellar_wall_area = 0
        self._est_factor_volume = 0.0

        self.est_factor_neighbour = 0.0  # n_Nachbar
        self.est_extra_floor_area = 0.0  # q_Fa

        if self.neighbour_buildings == 0:
            self._est_factor_neighbour = 0.0
            self._est_extra_floor_area = 50.0
        elif self.neighbour_buildings == 1:
            self._est_factor_neighbour = 1.0
            self._est_extra_floor_area = 30.0
        elif self.neighbour_buildings == 2:
            self._est_factor_neighbour = 2.0
            self._est_extra_floor_area = 10.0

        self._est_facade_to_floor_area = 0.0  # p_Fa

        if self.residential_layout == 0:
            self._est_facade_to_floor_area = 0.66
        elif self.residential_layout == 1:
            self._est_facade_to_floor_area = 0.8

        self._est_factor_heated_attic = 0.0  # f_TB_DG
        self._est_area_per_floor = 0.0  # p_DA
        self._est_area_per_roof = 0.0  # p_OG

        if self.attic == 0:
            self._est_factor_heated_attic = 0.0
            self._est_area_per_floor = 1.33
            self._est_area_per_roof = 0.0
        elif self.attic == 1:
            self._est_factor_heated_attic = 0.0
            self._est_area_per_floor = 0.0
            self._est_area_per_roof = 1.33
        elif self.attic == 2:
            self._est_factor_heated_attic = 0.5
            self._est_area_per_floor = 0.75
            self._est_area_per_roof = 0.67
        elif self.attic == 3:
            self._est_factor_heated_attic = 1.0
            self._est_area_per_floor = 1.5
            self._est_area_per_roof = 0.0

        self._est_factor_heated_cellar = 0.0  # f_TB_KG

        if self.cellar == 0:
            self._est_factor_heated_cellar = 0.0
        elif self.cellar == 1:
            self._est_factor_heated_cellar = 0.0
        elif self.cellar == 2:
            self._est_factor_heated_cellar = 0.5
        elif self.cellar == 3:
            self._est_factor_heated_cellar = 1.0

        self._est_factor_dormer = 0.0

        if self.dormer == 0:
            self._est_factor_dormer = 1.0
        elif self.dormer == 1:
            self._est_factor_dormer = 1.3

        if self.with_ahu is True:
            self.central_ahu.profile_temperature = (7 * [293.15] +
                                                    12 * [295.15] +
                                                    6 * [293.15])
            self.central_ahu.profile_min_relative_humidity = (25 * [0.45])
            self.central_ahu.profile_max_relative_humidity = (25 * [0.55])
            self.central_ahu.profile_v_flow = (
                7 * [0.0] + 12 * [1.0] + 6 * [0.0])

    def get_elements_from_file(self, zone):
        '''
        Get a all elements from a XML file and set it to a thermalzone
        '''

        for outerwall in self.parent.data.element_bind.OuterWall:
            if outerwall.building_age_group == self.construction_period:
                wall = OuterWall(zone)
                wall.name = "OuterWall"
                wall.construction_type = outerwall.construction_type
                wall.year_of_construction = \
                    outerwall.year_of_construction
                wall.building_age_group = outerwall.building_age_group
                wall.inner_convection = outerwall.inner_convection
                wall.inner_radiation = outerwall.inner_radiation
                wall.outer_convection = outerwall.outer_convection
                wall.outer_radiation = outerwall.outer_radiation
                wall.orientation = 0
                for layer_bind in outerwall.Layers.layer:
                    layer = Layer(wall)
                    layer.id = layer_bind.id - 1
                    layer.thickness = layer_bind.thickness
                    for mat in self.parent.data.material_bind.Material:
                        if mat.material_id == layer_bind.material.material_id:
                            material = Material(layer)
                            material.name = mat.name
                            material.density = mat.density
                            material.thermal_conduc = mat.thermal_conduc
                            material.heat_capac = mat.heat_capac

        for rooftop in self.parent.data.element_bind.Rooftop:
                wall = Rooftop(zone)
                wall.name = "Rooftop"
                wall.construction_type = rooftop.construction_type
                wall.year_of_construction = \
                    rooftop.year_of_construction
                wall.building_age_group = rooftop.building_age_group
                wall.inner_convection = rooftop.inner_convection
                wall.inner_radiation = rooftop.inner_radiation
                wall.outer_convection = rooftop.outer_convection
                wall.outer_radiation = rooftop.outer_radiation
                for layer_bind in rooftop.Layers.layer:
                    layer = Layer(wall)
                    layer.id = layer_bind.id - 1
                    layer.thickness = layer_bind.thickness
                    for mat in self.parent.data.material_bind.Material:
                        if mat.material_id == layer_bind.material.material_id:
                            material = Material(layer)
                            material.name = mat.name
                            material.density = mat.density
                            material.thermal_conduc = mat.thermal_conduc
                            material.heat_capac = mat.heat_capac

        for groundfloor in self.parent.data.element_bind.GroundFloor:
                wall = GroundFloor(zone)
                wall.name = "GroundFloor"
                wall.construction_type = groundfloor.construction_type
                wall.year_of_construction = \
                    groundfloor.year_of_construction
                wall.building_age_group = groundfloor.building_age_group
                wall.inner_convection = groundfloor.inner_convection
                wall.inner_radiation = groundfloor.inner_radiation
                for layer_bind in groundfloor.Layers.layer:
                    layer = Layer(wall)
                    layer.id = layer_bind.id - 1
                    layer.thickness = layer_bind.thickness
                    for mat in self.parent.data.material_bind.Material:
                        if mat.material_id == layer_bind.material.material_id:
                            material = Material(layer)
                            material.name = mat.name
                            material.density = mat.density
                            material.thermal_conduc = mat.thermal_conduc
                            material.heat_capac = mat.heat_capac

        for window in self.parent.data.element_bind.Window:
                wall = Window(zone)
                wall.name = "Window"
                wall.construction_type = window.construction_type
                wall.year_of_construction = \
                    window.year_of_construction
                wall.building_age_group = window.building_age_group
                wall.inner_convection = window.inner_convection
                wall.inner_radiation = window.inner_radiation
                wall.outer_convection = window.outer_convection
                wall.outer_radiation = window.outer_radiation
                for layer_bind in window.Layers.layer:
                    layer = Layer(wall)
                    layer.id = layer_bind.id - 1
                    layer.thickness = layer_bind.thickness
                    for mat in self.parent.data.material_bind.Material:
                        if mat.material_id == layer_bind.material.material_id:
                            material = Material(layer)
                            material.name = mat.name
                            material.density = mat.density
                            material.thermal_conduc = mat.thermal_conduc
                            material.heat_capac = mat.heat_capac

        self.number_of_floors = 0
        for floor in self.parent.data.element_bind.Floor:
            if floor.building_age_group == self.construction_period:
                self.number_of_floors += 1
                wall = Floor(zone)
                wall.name = "Floor"
                wall.construction_type = floor.construction_type
                wall.year_of_construction = \
                    floor.year_of_construction
                wall.building_age_group = floor.building_age_group
                wall.inner_convection = floor.inner_convection
                wall.inner_radiation = floor.inner_radiation
                for layer_bind in floor.Layers.layer:
                    layer = Layer(wall)
                    layer.id = layer_bind.id - 1
                    layer.thickness = layer_bind.thickness
                    for mat in self.parent.data.material_bind.Material:
                        if mat.material_id == layer_bind.material.material_id:
                            material = Material(layer)
                            material.name = mat.name
                            material.density = mat.density
                            material.thermal_conduc = mat.thermal_conduc
                            material.heat_capac = mat.heat_capac

    def generate_archetype(self):
        """Generates a SingleFamilyDwelling building for Tabula.

        With given values, this class generates a archetype building for
        single family dwellings according to TEASER requirements
        """
        # help area for the correct building area setting while using typeBldgs
        type_bldg_area = self.net_leased_area
        self.net_leased_area = 0.0
        type_bldg_area = 100

        for key, value in self.zone_area_factors.items():
            zone = ThermalZone(self)
            zone.name = key
            zone.area = type_bldg_area * value[0]
            use_cond = UseCond(zone)
            use_cond.load_use_conditions(value[1],
                                         data_class=self.parent.data)

            zone.use_conditions = use_cond

        for zone in self.thermal_zones:
                self.get_elements_from_file(zone)

        self._number_of_heated_floors = self._est_factor_heated_cellar + \
            self.number_of_floors + self.est_living_area_factor \
            * self._est_factor_heated_attic

        self._living_area_per_floor = type_bldg_area / \
            self._number_of_heated_floors

        self._est_ground_floor_area = self.est_bottom_building_closure * \
            self._living_area_per_floor

        self._est_roof_area = self.est_upper_building_closure * \
            self._est_factor_dormer * self._est_area_per_floor * \
            self._living_area_per_floor

        self._top_floor_area = self._est_area_per_roof * \
            self._living_area_per_floor

        if self._est_roof_area == 0:
            self._est_roof_area = self._top_floor_area

        self._est_facade_area = self._est_facade_to_floor_area * \
            self._living_area_per_floor + self._est_extra_floor_area

        self._est_win_area = self.est_factor_win_area * type_bldg_area

        self._est_cellar_wall_area = self.est_factor_cellar_area * \
            self._est_factor_heated_cellar * self._est_facade_area

        self._est_outer_wall_area = (self._number_of_heated_floors *
                                     self._est_facade_area) - \
            self._est_cellar_wall_area - \
            self._est_win_area

        # self._est_factor_volume = type_bldg_area * 2.5

        orientation = 0
        self.outer_area[orientation] = self._est_outer_wall_area / \
                                             self.nr_of_orientation

        self.window_area[orientation] = self._est_win_area / \
                                             self.nr_of_orientation

        ground_floor_orienatation = -2
        self.outer_area[ground_floor_orienatation] = self._est_ground_floor_area

        for key, value in self.outer_area.items():
            self.set_outer_wall_area(value, key)
        for key, value in self.window_area.items():
            self.set_window_area(value, key)

    def generate_from_gml(self):
        """Enriches lod1 or lod2 data from CityGML

        Adds Zones, BoundaryConditions, Material settings for walls and
        windows to the geometric representation of CityGML
        """

        type_bldg_area = self.net_leased_area
        self.net_leased_area = 0.0
        # create zones with their corresponding area, name and usage
        for key, value in self.zone_area_factors.items():
            zone = ThermalZone(self)
            zone.area = type_bldg_area * value[0]
            zone.name = key
            use_cond = UseCond(zone)
            use_cond.load_use_conditions(value[1],
                                         data_class=self.parent.data)
            zone.use_conditions = use_cond
            zone.use_conditions.with_ahu = False
            zone.use_conditions.persons *= zone.area * 0.01
            zone.use_conditions.machines *= zone.area * 0.01

            for surface in self.gml_surfaces:
                if surface.surface_tilt is not None:
                    if surface.surface_tilt == 90:
                        outer_wall = OuterWall(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self.construction_type,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

                        window = Window(zone)
                        window.load_type_element(self.year_of_construction,
                                                 "Kunststofffenster, "
                                                 "Isolierverglasung",
                                                 data_class=self.parent.data)
                        window.name = "asd" + str(surface.surface_tilt)
                        window.tilt = surface.surface_tilt
                        window.orientation = surface.surface_orientation

                    elif surface.surface_tilt == 0 and \
                        surface.surface_orientation == \
                            -2:
                        outer_wall = GroundFloor(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self.construction_type,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

                    else:
                        outer_wall = Rooftop(zone)
                        outer_wall.load_type_element(
                            year=self.year_of_construction,
                            construction=self.construction_type,
                            data_class=self.parent.data)
                        outer_wall.name = surface.name
                        outer_wall.tilt = surface.surface_tilt
                        outer_wall.orientation = surface.surface_orientation

            for key, value in self.inner_wall_names.items():

                for zone in self.thermal_zones:
                    inner_wall = InnerWall(zone)
                    inner_wall.load_type_element(
                        year=self.year_of_construction,
                        construction=self.construction_type,
                        data_class=self.parent.data)
                    inner_wall.name = key
                    inner_wall.tilt = value[0]
                    inner_wall.orientation = value[1]

            if self.number_of_floors > 1:

                for key, value in self.ceiling_names.items():

                    for zone in self.thermal_zones:
                        ceiling = Ceiling(zone)
                        ceiling.load_type_element(
                            year=self.year_of_construction,
                            construction=self.construction_type,
                            data_class=self.parent.data)
                        ceiling.name = key
                        ceiling.tilt = value[0]
                        ceiling.orientation = value[1]

                for key, value in self.floor_names.items():

                    for zone in self.thermal_zones:
                        floor = Floor(zone)
                        floor.load_type_element(
                            year=self.year_of_construction,
                            construction=self.construction_type,
                            data_class=self.parent.data)
                        floor.name = key
                        floor.tilt = value[0]
                        floor.orientation = value[1]
            else:
                pass

        for surface in self.gml_surfaces:
            if surface.surface_tilt is not None:
                if surface.surface_tilt != 0 and surface.surface_orientation\
                        != -2 and surface.surface_orientation != -1:
                    self.set_outer_wall_area(surface.surface_area *
                                             (1 - self.est_factor_win_area),
                                             surface.surface_orientation)
                else:
                    self.set_outer_wall_area(surface.surface_area,
                                             surface.surface_orientation)
        for surface in self.gml_surfaces:

            if surface.surface_tilt != 0 and surface.surface_orientation != \
                    -2 and surface.surface_orientation != -1:
                self.set_window_area(surface.surface_area *
                                     self.est_factor_win_area,
                                     surface.surface_orientation)

        for zone in self.thermal_zones:
            zone.set_inner_wall_area()
            zone.set_volume_zone()

    @property
    def outer_wall_list(self):
        return self.outer_wall_list

    @outer_wall_list.setter
    def add_outer_wall(self, wall):
        self.outer_wall_list.append(wall)

    @property
    def rooftop_list(self):
        return self.rooftop_list

    @rooftop_list.setter
    def add_rooftop_list(self, wall):
        self.rooftop_list.append(wall)

    @property
    def ground_floor_list(self):
        return self.ground_floor_list

    @ground_floor_list.setter
    def add_ground_floor(self, wall):
        self.ground_floor_list.append(wall)

    @property
    def window_list(self):
        return self.window_list

    @window_list.setter
    def add_window(self, wall):
        self.window_list.append(wall)

    @property
    def door_list(self):
        return self.door_list

    @door_list.setter
    def add_door(self, wall):
        self.door_list.append(wall)

    @property
    def residential_layout(self):
        return self._residential_layout

    @residential_layout.setter
    def residential_layout(self, value):
        if value is not None:
            self._residential_layout = value
        else:
            self._residential_layout = 0

    @property
    def neighbour_buildings(self):
        return self._neighbour_buildings

    @neighbour_buildings.setter
    def neighbour_buildings(self, value):
        if value is not None:
            self._neighbour_buildings = value
        else:
            self._neighbour_buildings = 0

    @property
    def attic(self):
        return self._attic

    @attic.setter
    def attic(self, value):
        if value is not None:
            self._attic = value
        else:
            self._attic = 0

    @property
    def cellar(self):
        return self._cellar

    @cellar.setter
    def cellar(self, value):
        if value is not None:
            self._cellar = value
        else:
            self._cellar = 0

    @property
    def dormer(self):
        return self._dormer

    @dormer.setter
    def dormer(self, value):
        if value is not None:
            self._dormer = value
        else:
            self._dormer = 0

    @property
    def construction_type(self):
        return self._construction_type

    @construction_type.setter
    def construction_type(self, value):
        if value is not None:
            if value == "heavy" or value == "light":
                self._construction_type = value
            else:
                raise ValueError("Construction_type has to be light or heavy")
        else:
            self._construction_type = "heavy"

if __name__ == '__main__':
    from teaser.data.dataclass import DataClass
    import teaser.logic.utilities as utils
    prj = Project()
    data = DataClass()
    """  data.path_tb = utils.get_full_path(
            "data/input/inputdata/TypeBuildingElements.xml")
    data.path_mat = utils.get_full_path(
            "data/input/inputdata/MaterialTemplates2.xml")
    data.load_tb_binding()
    data.load_mat_binding()"""
    prj.data = data
    bld = TabulaBuilding(prj, construction_period= [1969, 1978])
    bld.generate_archetype()
