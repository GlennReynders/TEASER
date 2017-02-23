# Created November 2016
# Ina De Jaeger (KU Leuven, EnergyVille)

"""ideas_output

This module contains function to call Templates for IDEAS model generation
"""
import os
import teaser.logic.utilities as utilities
from mako.template import Template

def export_ideas(buildings,
                         prj,
                         path=None,
                         building_model="One-zone"):
    """Exports models for IDEAS library

        Exports a building for detailed IDEAS Building model (currently
        only one-zone models are supported, two-zone models will be added soon).
        This function uses Mako Templates specified in
        data.output.modelicatemplates.ideas

        Parameters
        ----------

        buildings : list of instances of Building
            list of TEASER instances of a Building that is exported to IDEAS
             models. If you want to export a single building,
            please pass it over as a list containing only that building.
        prj : instance of Project
            Instance of TEASER Project object to access Project related
            information, e.g. name or version of used libraries
        path : string
            if the Files should not be stored in default output path of TEASER,
            an alternative path can be specified as a full path
        building_model : string
            Currently, only export to one-zone models is supported. Two-zone models
            will be added soon

        Attributes
        ----------

        lookup : TemplateLookup object
            Instance of mako.TemplateLookup to store general functions for templates
        zone_template_1 : Template object
            Template for ThermalZoneRecord using 1 element model
        zone_template_2 : Template object
            Template for ThermalZoneRecord using 2 element model
        zone_template_3 : Template object
            Template for ThermalZoneRecord using 3 element model
        zone_template_4 : Template object
            Template for ThermalZoneRecord using 4 element model
        model_template : Template object
            Template for MultiZone model
        """

    # check the arguments
    # in case there are other export options added, then add here the option
    # default is detailed
    assert building_model in ["One-zone"]

    #software versions that should be used when opening the Modelica files
    uses = [
        'Modelica(version="' + prj.modelica_info.version + '")',
        'IDEAS(version="' + prj.buildings[-1].library_attr.version + '")']

    # CREATION OF PACKAGE.MO AND PACKAGE.ORDER (project level)
    _help_package(path, prj.name, uses, within=None)
    _help_package_order(path, buildings, extra_list=[prj.name + "_Project"])
    #create project.mo file
    _help_project(path, prj, buildings)

    #for now, the only option is detailed
    if building_model == "One-zone":
        print("Exporting to one-zone IDEAS building models")
        #project.mo file
        for bldg in buildings:
            #PATH VARIABLES
            bldg_path = os.path.join(path,bldg.name) + "/"
            occupant_path = bldg_path + "Occupant/"
            structure_path = bldg_path + "Structure/"
            data_path = structure_path + "Data/"
            materials_path = data_path + "Materials/"
            constructions_path = data_path + "Constructions/"

            #FOLDER CREATION
            _help_foldercreation(bldg_path, structure_path, materials_path, constructions_path)

            # CREATION OF PACKAGE.MO AND PACKAGE.ORDER
            # building level
            _help_package(bldg_path, bldg.name, within=prj.name)
            _help_package_order(bldg_path, [bldg], "_Building",
                                ["Structure", "HeatingSystem", \
                                 "VentilationSystem", "ElectricalSystem", \
                                 "Occupant"], [bldg])
            # structure
            _help_package(structure_path, "Structure",
                          within=prj.name + "." + bldg.name,
                          packagedescription=
                          "Package of the particular building structure")
            _help_package_order(structure_path, [bldg], "_Structure", ["Data"], [])
            # data
            _help_package(data_path, "Data",
                          within=prj.name + "." + bldg.name + ".Structure",
                          kindofpackage="MaterialProperties",
                          packagedescription=
                          "Data for transient thermal building simulation")
            _help_package_order(data_path, [], None, ["Materials", "Constructions"], [])

            #occupant
            _help_package(occupant_path, "Occupant",
                          within=prj.name + "." + bldg.name,
                          packagedescription=
                          "Package of the particular building occupant")
            _help_package_order(occupant_path, [], "", ["ISO13790"], [])

            #CREATION OF MODELICA MODELS
                # we create the building.mo file
            _help_building(bldg_path, prj= prj, bldg= bldg)

                #we create the occupant.mo file
            _help_occupant(occupant_path, prj, bldg)
                # we start creating the structure.mo file
                #(here initialisation, then addition of zones & components)
            structure_filepath = utilities.get_full_path(
                                    structure_path + bldg.name
                                    + "_Structure.mo")
            _help_structure(structure_filepath, bldg, prj)

                #we create a help file for the connections in structure.mo
            help_file = open(utilities.get_full_path(structure_path +
                                                    "help_file.txt"), 'w')
            help_file.close()

            # we need all material names and construction names for this building
            # required for the package.order file
            bldg_materials = []
            bldg_constructions = []
            for zoneindex, zone in enumerate(bldg.thermal_zones, start = 1):
                #loop all building elements of this zone
                buildingelements = zone.outer_walls + zone.inner_walls + zone.windows
                count_windows = 0
                count_outerwalls = 0
                count_rooftops = 0
                count_groundfloors = 0
                count_innerwalls = 0
                count_ceilings = 0
                count_floors = 0
                count_elementsinzone = 0
                for elementindex, buildingelement in enumerate(buildingelements, start = 1):
                    #elementindex is required for annotation placement
                    #create lists with all building elements for this zone
                    #create materials.mo and constructions.mo
                    construction_mats = ""
                    construction_resistance = 0
                    for layerelement in buildingelement.layer:
                        material = layerelement.material
                        # add the material to the construction outputstring
                        # required for the construction.mo file
                        # required dataformat: Materials.BrickMe(d=0.08), ...
                        modelicapathtomaterial = "Data.Materials." + \
                                            material.name.replace(" ", "")
                        construction_mats = construction_mats + \
                                            modelicapathtomaterial + \
                                            "(d=" + \
                                            str(layerelement.thickness) + "),"
                        # required for glazing.mo
                        construction_resistance = construction_resistance + \
                                            (layerelement.thickness / \
                                             material.thermal_conduc)
                        if material.name.replace(" ", "") in bldg_materials:
                            pass #material is already created for this building
                        else:
                            #create material.mo
                            _help_records(recordTemplate="Material", recordPath=materials_path, prj = prj, bldg = bldg, material= material)
                            # add material name to the bldg_materials list
                            bldg_materials.append(material.name.replace(" ", ""))



                    if type(buildingelement).__name__ == "Window":
                        count_windows += 1
                        count_elementsinzone += 1
                        # rename element, required for citygml import
                        if buildingelement.name == "None":
                            buildingelement.name = "Window_" + str(count_windows)
                        else:
                            buildingelement.name = buildingelement.name + "_" + str(count_windows)


                        # add this window to the structure.mo file + create its glazing and its frame
                        _help_window(structure_path=structure_path, prj= prj, bldg=bldg, zone= zone, buildingelement=buildingelement, zoneindex=zoneindex, elementindex = elementindex,
                                     count_elementsinzone=count_elementsinzone,constructions_path= constructions_path)
                        # add construction name to the bldg_constructions list (both glazing and frame)
                        bldg_constructions.append(buildingelement.name.replace(" ", "")
                                                  + "_Glazing")
                        bldg_constructions.append(buildingelement.name.replace(" ", "")
                                                  + "_Frame")

                    else: #if no window, then opaque for sure
                        #add this buildingelement to the structure.mo file
                        if type(buildingelement).__name__ == "OuterWall":
                            count_outerwalls += 1
                            count_elementsinzone +=1
                            if buildingelement.name == "None":
                                buildingelement.name = "OuterWall_" + str(count_outerwalls)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_outerwalls)

                            #add this outerwall to the structure.mo file
                            _help_buildingelement(ideasTemplate="OuterWall", structurefile_path =structure_filepath, prj = prj, bldg = bldg, zone = zone,
                                            buildingelement= buildingelement, zoneindex=zoneindex, elementindex=elementindex, count_elementsinzone=count_elementsinzone,
                                            inc = "incWall",
                                            azi = (buildingelement.orientation-180)/180, #TEASER orientation vs IDEAS orientation
                                            structure_path= structure_path,
                                            path = constructions_path)

                        elif type(buildingelement).__name__ == "Rooftop":
                            count_rooftops += 1
                            count_elementsinzone +=1
                            if buildingelement.name == "None":
                                buildingelement.name = "Rooftop_" + str(count_rooftops)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_rooftops)

                            if buildingelement.orientation == -1:
                                inc = "incCeil"
                            else:
                                inc = buildingelement.tilt
                            #add this rooftop to the structure.mo file
                            _help_buildingelement(ideasTemplate="OuterWall", structurefile_path=structure_filepath,
                                                  prj=prj, bldg=bldg, zone = zone,
                                                  buildingelement=buildingelement, zoneindex=zoneindex, elementindex=elementindex, count_elementsinzone=count_elementsinzone,
                                                  inc= inc, structure_path= structure_path, path = constructions_path)


                        elif type(buildingelement).__name__ == "GroundFloor":
                            count_groundfloors += 1
                            count_elementsinzone += 1
                            if buildingelement.name == "None":
                                buildingelement.name = "Groundfloor_" + str(count_groundfloors)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_groundfloors)

                            #add this groundfloor to the structure.mo file
                            _help_buildingelement(ideasTemplate="SlabOnGround", structurefile_path=structure_filepath, prj=prj, bldg=bldg, zone = zone,
                                                  buildingelement=buildingelement, zoneindex=zoneindex, elementindex=elementindex, count_elementsinzone=count_elementsinzone,
                                                  inc="incFloor",
                                                  structure_path= structure_path,
                                                  path = constructions_path)

                        elif type(buildingelement).__name__ == "InnerWall":
                            count_innerwalls +=1
                            count_elementsinzone +=2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            if buildingelement.name == "None":
                                buildingelement.name = "InnerWall_" + str(count_innerwalls)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_innerwalls)
                            # add this innerwall to the structure.mo file
                            _help_buildingelement(ideasTemplate="InnerWall", structurefile_path=structure_filepath, prj = prj, bldg = bldg, zone = zone,
                                            buildingelement=buildingelement, zoneindex=zoneindex, elementindex=elementindex, count_elementsinzone=count_elementsinzone,
                                            inc="incWall" ,
                                            azi= (buildingelement.orientation-180)/180, #TEASER orientation vs IDEAS orientation
                                            structure_path= structure_path,
                                            path= constructions_path)

                        elif type(buildingelement).__name__ == "Ceiling":
                            count_ceilings += 1
                            count_elementsinzone += 2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            if buildingelement.name == "None":
                                buildingelement.name = "Ceiling_" + str(count_ceilings)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_ceilings)

                            #add this ceiling to the structure.mo file
                            _help_buildingelement(ideasTemplate="InnerWall", structurefile_path=structure_filepath, prj = prj,
                                                  bldg = bldg, zone = zone, buildingelement=buildingelement, elementindex=elementindex, zoneindex=zoneindex,
                                                  count_elementsinzone=count_elementsinzone,inc = "incCeil",
                                                  structure_path= structure_path,
                                                  path = constructions_path)

                        elif type(buildingelement).__name__ == "Floor":
                            count_floors += 1
                            count_elementsinzone += 2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            if buildingelement.name == "None":
                                buildingelement.name = "Floor_" + str(count_floors)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(count_floors)

                            #add this floor to the structure.mo file
                            _help_buildingelement(ideasTemplate="InnerWall", structurefile_path=structure_filepath,
                                                prj=prj, bldg=bldg, zone= zone, buildingelement=buildingelement,
                                                zoneindex=zoneindex, elementindex=elementindex, count_elementsinzone=count_elementsinzone,
                                                inc = "incFloor", structure_path= structure_path, path = constructions_path)

                        else:
                            print("This building element, named " + buildingelement.name +
                                  " \n is neither a Window(), nor an OuterWall(), nor a Rooftop(), " +
                                  " \n nor a Groundfloor(), nor an InnerWall(), nor a Ceiling(), " +
                                  " \n nor a Floor() and was therefore not exported")
                        # add construction name to the bldg_constructions list
                        bldg_constructions.append(buildingelement.name.replace(" ", ""))
                        # add element to constructions.mo
                        _help_records(recordTemplate="Construction", recordPath=constructions_path, prj=prj, bldg=bldg,
                                  buildingelement=buildingelement, construction_mats=construction_mats)

                # add this zone to the structure.mo file and add connections to help_file
                _help_zone(structure_path, bldg, prj, zone, zoneindex, count_elementsinzone)

            # add connections from help_file to the structure.mo file
            out_file = open(utilities.get_full_path(structure_path +
                                         bldg.name + "_Structure.mo"), 'a')
            out_file.write("equation\n")
            help_file = open(utilities.get_full_path(structure_path +
                                                    "help_file.txt"), 'r')
            out_file.write(help_file.read())
            help_file.close()
            # add last sentence to the structure.mo file
            out_file.write("end "+ bldg.name + "_Structure;")
            out_file.close()
            # delete the help_file.txt
            os.remove(structure_path + "help_file.txt")

            # CREATION OF PACKAGE.MO AND PACKAGE.ORDER
            # constructions(kindofpackage=same as IDEAS.BUILDING.DATA)
            _help_package(constructions_path, "Constructions",
                          within=prj.name + "." + bldg.name + \
                                 ".Structure.Data",
                          kindofpackage="MaterialProperties",
                          packagedescription=
                          "Library of building envelope constructions")
            _help_package_order(constructions_path, [], None, bldg_constructions, [])
                # materials (kindofpackage is same as in IDEAS.BUILDING.DATA)
            _help_package(materials_path, "Materials",
                          within=prj.name + "." + bldg.name + \
                                 ".Structure.Data",
                          kindofpackage="MaterialProperties",
                          packagedescription=
                          "Library of construction materials")
            _help_package_order(materials_path, [], None, bldg_materials, [])

    else:
        #export is not detailed, so is not supported
        print("Please indicate a supported mode for export \
        (for now only: Detailed), for this reason nothing has been exported")



    print("Exports can be found here:")
    print(path)

def _help_foldercreation (bldg_path, structure_path, materials_path, constructions_path):
    # we create a folder for each building
    utilities.create_path(utilities.get_full_path(bldg_path))
    # folder for the heating system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "HeatingSystem"))
    # folder for the ventilation system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "VentilationSystem"))
    # folder for the electrical system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "ElectricalSystem"))
    # folder for the occupant
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "Occupant"))
    # folder for the structure, materials and constructions
    utilities.create_path(utilities.get_full_path(structure_path))
    utilities.create_path(utilities.get_full_path(materials_path))
    utilities.create_path(utilities.get_full_path(constructions_path))



def _help_package(path, name, uses=None, within=None,
                  kindofpackage=None, packagedescription=None):
    '''creates a package.mo file
    Parameters
    ----------
    path : string
        path of where the package.mo should be placed
    name : string
        name of the Modelica package
    within : string
        path of Modelica package containing this package
    '''
    package_template = Template(filename=utilities.get_full_path
    ("data/output/modelicatemplate/ideas/package"))
    out_file = open(
        utilities.get_full_path(path + "/" + "package" + ".mo"), 'w')
    out_file.write(package_template.render_unicode(
                                name=name,
                                within=within,
                                uses=uses,
                                kindofpackage = kindofpackage,
                                packagedescription=packagedescription))

def _help_package_order(path, package_list_with_addition, addition=None, extra_list=[], package_list_without=[]):
    '''creates a package.order file
    Parameters
    ----------
    path : string
        path of where the package.order should be placed
    package_list : [string]
        name of all models or packages contained in the package
    addition : string
        if there should be a suffix in front of package_list.string it can
        be specified
    extra : [string]
        an extra package or model not contained in package_list can be
        specified, necessary in IDEAS for the folders Structure,
        HeatingSystem, ...
    '''
    order_template = Template(filename=utilities.get_full_path
    ("data/output/modelicatemplate/ideas/package_order"))

    out_file = open(
        utilities.get_full_path(path + "/" + "package" + ".order"), 'w')
    out_file.write(order_template.render_unicode
                   (list_with_add=package_list_with_addition,
                    addition=addition,
                    list_without_add=package_list_without,
                    extra=extra_list))
    out_file.close()

def _help_records(recordTemplate, recordPath, prj, bldg, buildingelement = None, material = None, construction_mats = "", nameofglazinginIDEAS = "", frame_uvalue=0):
     #make sure that path = constructions_path when recordTemplate = Construction, Glazing or Frame"
     #make sure that path = materials_path when recordTemplate = Material

     #recordTemplate, recordPath, prj and bldg are always required, rest is additional and checked

    assert recordTemplate in ["Construction", "Glazing", "Frame", "Material"]

    filepath = utilities.get_full_path("data/output/modelicatemplate/ideas/")
    window_uvalue = 0

    if recordTemplate == "Construction":
        template = Template(filename=filepath + "ideas_ConstructionRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "") + ".mo"
        assert buildingelement is not None
        assert construction_mats is not ""

    elif recordTemplate == "Glazing":
        template = Template(filename=filepath + "ideas_GlazingRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "")\
                                + "_Glazing.mo"
        assert buildingelement is not None
        assert nameofglazinginIDEAS is not ""

    elif recordTemplate == "Frame": #not yet in use
        template = Template(filename=filepath + "ideas_FrameRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "")\
                                + "_Frame.mo"
        assert buildingelement is not None
        assert frame_uvalue is not 0

    elif recordTemplate == "Material":
        template = Template(filename=filepath+"ideas_MaterialRecord")
        recordname = recordPath + material.name.replace(" ", "") + ".mo"
        assert material is not None

    else:
        print("I'm sorry, I cannot find an IDEAS recordtemplate for this record")

    #create record.mo
    out_file = open(utilities.get_full_path(recordname), 'w')
    out_file.write(template.render_unicode(
        mod_prj=prj.name,
        bldg=bldg,
        #only required for construction, glazing and frame
        buildingelement=buildingelement,
        #only required for construction
        construction_mats=construction_mats[:-1],  # delete last comma
        #only required for glazing
        nameofglazinginIDEAS = nameofglazinginIDEAS,
        #only required for frame
        frame_uvalue = frame_uvalue,
        #only required for materials
        mat=material))
    out_file.close()

def _help_buildingelement(ideasTemplate, structurefile_path, prj, bldg, zone,
                        buildingelement, zoneindex,  elementindex,count_elementsinzone,
                        inc, structure_path, path, azi = "aziSouth", construction_mats="",
                        construction_resistance=0, material = None, ):
    assert ideasTemplate in ["OuterWall", "SlabOnGround", "InnerWall", "Window", "BoundaryWall"]

    filepath = utilities.get_full_path(
        "data/output/modelicatemplate/ideas/")
    if ideasTemplate == "OuterWall":
        template = Template(filename=filepath + "ideas_OuterWall")
    elif ideasTemplate == "SlabOnGround":
        template = Template(filename=filepath + "ideas_SlabOnGround")
    elif ideasTemplate == "InnerWall":
        template = Template(filename=filepath + "ideas_InnerWall")
    elif ideasTemplate == "Window":
        template = Template(filename=filepath + "ideas_Window")
    elif ideasTemplate == "BoundaryWall": #currently not in use
        template = Template(filename=filepath + "ideas_BoundaryWall")
    else:
        print("I'm sorry, I cannot find an IDEAS template for this BuildingElement()")

    out_file = open(structurefile_path, 'a')
    out_file.write(
        template.render_unicode(
            bldg=bldg,
            mod_prj=prj.name,
            buildingelement=buildingelement,
            zoneindex=zoneindex,
            elementindex=elementindex,
            inc=inc,
            azi=azi))
    out_file.close()
#todo/ kijk naar alle helpfuncties en predeclare de variabelen die je kan, zodat je enkel hoogstnodige moet geven indien je functie aanroept, dan kan je hier contruction record laten aanmaken per buildingelement, daarna kijken of window er ook nog bij kan
    # create construction.mo for this building element
        # is currently done above, should be moved here

    # add connections for this buildingelement to help_file
    _help_connectcomponents(structure_path, buildingelement, zone, count_elementsinzone, ideasTemplate = ideasTemplate)

def _help_window (structure_path, prj, bldg, zone, buildingelement, zoneindex, elementindex, count_elementsinzone, constructions_path):
    #this should be deleted, for now okay, because teaser input is not able to go as detailed as now
    if bldg.year_of_construction <= 1945:
        nameofglazinginIDEAS = "EpcSingle"
        frame_uvalue = 2.6
    elif bldg.year_of_construction >= 1946 and bldg.year_of_construction <= 1970:
        nameofglazinginIDEAS = "EpcSingle"
        frame_uvalue = 2.6
    elif bldg.year_of_construction >= 1971 and bldg.year_of_construction <= 1990:
        nameofglazinginIDEAS = "EpcDouble"
        frame_uvalue = 4.55
    elif bldg.year_of_construction >= 1991 and bldg.year_of_construction <= 2005:
        nameofglazinginIDEAS = "EpcDouble"
        frame_uvalue = 4.6
    elif bldg.year_of_construction >= 2006 and bldg.year_of_construction <= 2011:
        nameofglazinginIDEAS = "Ins2Ar"
        frame_uvalue = 3
    elif bldg.year_of_construction >= 2012 and bldg.year_of_construction <= 2016:
        nameofglazinginIDEAS = "Ins2Ar"
        frame_uvalue = 3 #self defined, for this moment, same as 2006-2011 > Change this

    # add window to structure.mo
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    window_template = Template(
        filename=filepath + "ideas_Window")
    out_file = open(utilities.get_full_path(
        structure_path + bldg.name
        + "_Structure.mo"), 'a')
    out_file.write(window_template.render_unicode(
        bldg=bldg,
        mod_prj=prj.name,
        buildingelement=buildingelement,
        zoneindex=zoneindex,
        elementindex = elementindex,
        count_elementsinzone= count_elementsinzone))
    out_file.close()

    # create glazing.mo
    _help_records(recordTemplate="Glazing", recordPath=constructions_path, prj = prj, bldg = bldg, buildingelement=buildingelement,
                  nameofglazinginIDEAS= nameofglazinginIDEAS)

    # create frame.mo (not yet in use)
    _help_records(recordTemplate="Frame", recordPath=constructions_path, prj= prj, bldg = bldg, buildingelement=buildingelement,
                  frame_uvalue= frame_uvalue)

    #connect components
    _help_connectcomponents(structure_path, buildingelement, zone, count_elementsinzone)

def _help_zone (structure_path, bldg, prj, zone, zoneindex, count_elementsinzone):
    #add zone to structure.mo file
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    zone_template = Template(
        filename=filepath + "ideas_Zone")
    out_file = open(utilities.get_full_path(structure_path +
                                           bldg.name + "_Structure.mo"), 'a')
    out_file.write(zone_template.render_unicode(bldg=bldg,
                                                mod_prj=prj.name,
                                                zone=zone,
                                                zoneindex=zoneindex,
                                                count_elementsinzone = count_elementsinzone))
    out_file.close()

    # add zone connections
    _help_connectzones(structure_path, zone, zoneindex)

def _help_connectcomponents (structure_path, buildingelement, zone, count_elementsinzone, ideasTemplate= ""):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    connectcomponents_template = Template(
        filename=filepath + "ideas_ConnectComponents")
    help_file = open(utilities.get_full_path(structure_path +
                                            "help_file.txt"), 'a')
    help_file.write(connectcomponents_template.render_unicode(
        buildingelement=buildingelement,
        zone=zone,
        index=count_elementsinzone,
        ideasTemplate = ideasTemplate))
    help_file.close()

def _help_connectzones (structure_path, zone, zoneindex):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    connectzones_templates = Template(
        filename=filepath + "ideas_ConnectZones")
    help_file = open(utilities.get_full_path(structure_path +
                                            "help_file.txt"), 'a')
    help_file.write(connectzones_templates.render_unicode(
                                        zone=zone,
                                        index=zoneindex))
    help_file.close()

def _help_structure (structure_filepath, bldg, prj):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    structure_template = Template(
        filename=filepath + "ideas_Structure")
    out_file = open(structure_filepath, 'w')
    out_file.write(structure_template.render_unicode(bldg=bldg,
                                                     mod_prj=prj.name))
    out_file.close()

def _help_heatingsystem (path, name, ):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    heatingsystem_template = Template(
        filename=filepath + "ideas_HeatingSystem")

def _help_ventilationsystem (path, name, ):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    ventilationsystem_template = Template(
        filename=filepath + "ideas_VentilationSystem")

def _help_electricalsystem (path, name, ):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    electricalsystem_template = Template(
        filename=filepath + "ideas_ElectricalSystem")

def _help_occupant (occupant_path, prj, bldg):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    occupant_template = Template(
        filename=filepath + "ideas_Occupant")
    out_file = open(utilities.get_full_path(occupant_path + "ISO13790.mo"), 'w')
    out_file.write(occupant_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

def _help_building (bldg_path, prj, bldg):
    #Building.mo model
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    building_template = Template(
        filename=filepath + "ideas_Building")
    out_file = open(utilities.get_full_path(bldg_path +
                                           bldg.name + "_Building.mo"), 'w')
    out_file.write(building_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

    #this building with an inner sim > runable file on building level
    building_runable_template = Template(
        filename = filepath + "ideas_Building_runable")
    out_file = open(utilities.get_full_path(bldg_path +
                                           bldg.name + ".mo"), 'w')
    out_file.write(building_runable_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

def _help_project(path, prj, buildings):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    template = Template(
        filename=filepath + "ideas_Project")
    out_file = open(utilities.get_full_path(path +"/" +
                                           prj.name + "_Project.mo"), 'w')
    out_file.write(template.render_unicode(prj_name=prj.name,
                    buildings = buildings))
    out_file.close()