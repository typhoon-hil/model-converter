import codecs
import importlib
import os

from model_converter.converter.app.model.terminal import Terminal

from model_converter.converter.app.model.subsystem import Subsystem

from model_converter.converter.app.model.component import Component
from parglare import Grammar, Parser

from model_converter.converter.app.util import get_root_path

from model_converter.converter.parsers.base_parser import BaseParser


class SimulinkParser(BaseParser):

    wrong_orientation_list = []
    default_port_map = {"Gain": [("sp", "in:1"),
                                 ("sp", "out:1")
                                 ]
                        }

    def __init__(self, input_file_path, rule_file_path):
        super().__init__()

        self.user_lib = importlib.import_module('model_converter.'
                                                'user_libs.functions',
                                                'functions')

        self.input_file_path = input_file_path
        self.rule_file_path = rule_file_path

        self.conversion_dict = {"Subsystem": []}

        self.temp_subsystem_dict = {}

        self.component_id_dict = {}
        self.__node_id = 0

        self.path_dict = {}

        self.file_input = None

    def _extract_terminal(self, node):
        """
        Iterates through the list of tokens for a "CNode" XML node,
        returning a Terminal object with its X and Y coordinates,
        node ID and the index of the terminal.

        Args:
            node (list): "CNode" XML node

        Returns:
            Terminal
        """
        terminal_obj_dict = {}
        terminals = node.text.strip("[]").replace(" ", "").split(",")
        if len(terminals) == 1 and terminals[0] == "":
            return terminal_obj_dict
        for i in range(int(terminals[0])):
            sp_in_term = Terminal()
            sp_in_term.index = f"in:{i+1}"
            sp_in_term.name = f"in:{i+1}"
            sp_in_term.kind = "sp"
            terminal_obj_dict[sp_in_term.index] = sp_in_term
        if len(terminals) == 1:
            return terminal_obj_dict
        for i in range(int(terminals[1])):
            sp_out_term = Terminal()
            sp_out_term.index = f"out:{i+1}"
            sp_out_term.name = f"out:{i+1}"
            sp_out_term.kind = "sp"
            terminal_obj_dict[sp_out_term.index] = sp_out_term
        if len(terminals) == 2:
            return terminal_obj_dict
        if len(terminals) >= 6:
            for i in range(int(terminals[5])):
                pe_in_term = Terminal()
                pe_in_term.index = f"lconn:{i+1}"
                pe_in_term.name = f"lconn:{i+1}"
                terminal_obj_dict[pe_in_term.index] = pe_in_term
        if len(terminals) == 7:
            for i in range(int(terminals[6])):
                pe_out_term = Terminal()
                pe_out_term.index = f"rconn:{i+1}"
                pe_out_term.name = f"rconn:{i+1}"
                terminal_obj_dict[pe_out_term.index] = pe_out_term

        return terminal_obj_dict

    def _extract_system(self, node):
        component_dict = {}
        for component in node:
            component_obj = self._create_input_obj_model(component)
            if isinstance(component_obj, Component):
                try:
                    component_dict[component_obj.type].append(component_obj)
                except KeyError:
                    component_dict[component_obj.type] = [component_obj]

            elif isinstance(component_obj, Subsystem):
                try:
                    component_dict["Subsystem"].append(component_obj)
                except KeyError:
                    component_dict["Subsystem"] = [component_obj]

        return component_dict

    def _extract_subsystem(self, node):
        print(1)


    def _add_component_to_dict(self, component_object: (Component, Subsystem)):
        # Removing the "ID" property and adding the
        # component to the id map, which will be used
        # to connect components when parsing the "Line"
        # XML elements
        component_id = component_object.properties.pop("__id__")
        self.component_id_dict[component_id] = component_object

        try:
            self.source_comp_dict_by_type[component_object.type].append(
                component_object)
        except KeyError:
            self.source_comp_dict_by_type[component_object.type] = \
                [component_object]

    def _extract_properties(self, node):
        # Casting into float if the value is a digit,
        # otherwise using the text value
        try:
            text_val = float(node.text)
        except ValueError:
            text_val = node.text
        return {node.attrib.get("Name"): text_val}

    def _extract_component(self, node):

        comp_type = node.attrib.get("BlockType", "SubSystem")
        new_component = Component() if comp_type != "SubSystem" else Subsystem()

        new_component.name = node.attrib.get("Name")
        #
        # Temporarily adding the component's unique ID
        # to the properties dict, which will be used to
        # resolve connections
        #
        new_component.properties["__id__"] = node.attrib.get("SID")

        if comp_type != "Reference":
            if comp_type == "SubSystem":
                comp_type = "Subsystem"
            new_component.type = comp_type

        #
        # Extracting properties of the component.
        #
        for child in node:
            # Setting the Component's type, position, rotation
            if child.tag == "P":
                prop_name = child.attrib.get("Name")
                if prop_name == "SourceBlock":
                    new_component.type = child.text.replace("\n"," ")
                elif prop_name in ("Position", "Location"):
                    position = \
                        child.text.strip("[]").replace(" ", "").split(",")
                    new_component.position[0] = int(position[0])
                    new_component.position[1] = int(position[1])
                elif prop_name == "BlockRotation":
                    pass
                elif prop_name == "Ports":
                    terminals = self._create_input_obj_model(child)
                    for terminal in terminals.values():
                        terminal.parent_component = new_component
                        terminal.position = new_component.position
                    if comp_type == "Subsystem":
                        new_component.terminals = terminals
                    else:
                        new_component.terminals.update(terminals)
            elif child.tag == "System":
                children = self._extract_system(child)
                for child_list in children.values():
                    for child in child_list:
                        child.parent = new_component
                new_component.component_dict = children

                child_ports = children.pop("PMIOPort", [])
                for port in child_ports:
                    # PMIOPorts have a single "terminal" - the actual port
                    term = list(port.terminals.values())[0]
                    new_component.terminals[term.index] = term
                child_ports.clear()
            # Setting the Component's properties
            elif child.tag == "InstanceData":
                for prop in child:
                    ret_val = self._create_input_obj_model(prop)
                    new_component.properties.update(ret_val)
        if new_component.type in SimulinkParser.default_port_map:
            for default_term in \
                    SimulinkParser.default_port_map[new_component.type]:
                index = default_term[1]
                name = default_term[1]
                kind = default_term[0]
                default_term_obj = Terminal(position=new_component.position,
                                            index=index,
                                            kind=kind,
                                            name=name,
                                            parent_component=new_component)
                new_component.terminals[default_term_obj.index] = \
                    default_term_obj

        # Some components are oriented differently
        # in the source netlist (horizontal (ours) vs vertical(theirs))
        #
        if new_component.type in SimulinkParser.wrong_orientation_list:
            if new_component.orientation == 270:
                new_component.orientation = 0
            else:
                new_component.orientation += 90

        orientation = "up"
        if new_component.orientation == 0:
            orientation = "up"
        elif new_component.orientation == 90:
            orientation = "right"
        elif new_component.orientation == 180:
            orientation = "down"
        elif new_component.orientation == 270:
            orientation = "left"
        new_component.orientation = orientation

        self._add_component_to_dict(new_component)
        return new_component

    def _set_terminal_node_id(self, node):
        source = None
        dest = None
        for child in node:
            if child.tag == "P":
                if child.attrib.get("Name") == "Src":
                    source = child.text.split("#")
                elif child.attrib.get("Name") == "Dst":
                    dest = child.text.split("#")
            elif child.tag == "Branch":
                self._set_terminal_node_id(child)

        if source is not None:
            source_comp = self.component_id_dict.get(source[0])
            source_term = source_comp.terminals.get(source[1])
            if source_term is None:
                source_term_kind = source[1].split(":")[0]
                kind = None
                if source_term_kind in ("lconn", "rconn"):
                    kind = "pe"
                elif source_term_kind in ("in", "out"):
                    kind = "sp"
                if kind is None:
                    raise Exception(f"Cannot create terminal of "
                                    f"the {source_term_kind} kind, "
                                    f"for the component {source_comp.type}.")
                missing_term = Terminal(position=source_comp.position,
                                        node_id=self.__node_id,
                                        index=source[1],
                                        parent_component=source_comp,
                                        kind=kind,
                                        name=source[1])
                source_comp.terminals[source[1]] = missing_term
            else:
                source_term.node_id = self.__node_id

        if dest is not None:
            dest_comp = self.component_id_dict.get(dest[0])
            dest_term = dest_comp.terminals.get(dest[1])
            if dest_term is None:
                dest_term_kind = dest[1].split(":")[0]
                kind = None
                if dest_term_kind in ("lconn", "rconn"):
                    kind = "pe"
                elif dest_term_kind in ("in", "out"):
                    kind = "sp"
                if kind is None:
                    raise Exception(f"Cannot create terminal of "
                                    f"the {dest_term_kind} kind, "
                                    f"for the component {dest_comp.type}.")
                missing_term = Terminal(position=dest_comp.position,
                                        node_id=self.__node_id,
                                        index=source[1],
                                        parent_component=dest_comp,
                                        kind=kind,
                                        name=dest[1])
                dest_comp.terminals[source[1]] = missing_term
            else:
                dest_comp.node_id = self.__node_id

    def _create_input_obj_model(self, node):
        """
        Recursively called for each node in the XML netlist.
        Depending on the 2nd item in the node
        (the name of the XML tag), different methods are called.

        CCircuits contain Components or SubCircuits(which are new CCircuits),
        each Component contains CNodes (terminals), Params(properties) and Coord
        which contain positional info (X and Y coords, orientation and flip).

        Args:
            node : XML node

        Returns:
            ret_val (dict):
            {"component_type_name":[component1, component2,...]}
        """
        if node.tag == "Model":
            for child in node:
                if child.tag == "P":
                    continue
                ret_val = self._create_input_obj_model(child)
                if ret_val is not None and type(ret_val) is not dict:
                    return ret_val
        elif node.tag == "System":
            return self._extract_system(node)

        elif node.tag == "Block":
            return self._extract_component(node)

        elif node.tag == "P":
            if node.attrib.get("Name") == "Ports":
                return self._extract_terminal(node)
            return self._extract_properties(node)

        elif node.tag == "Line":
            self._set_terminal_node_id(node)
            self.__node_id += 1
            return


    def read_input(self):
        import xml.etree.ElementTree as ET
        with codecs.open(self.input_file_path, 'r', errors='ignore') as fileData:
            # Creating obj model from the 2nd element
            # since the first one is the XML meta node
            input_data = ET.fromstring(fileData.read())
            for child in input_data:
                self._create_input_obj_model(child)