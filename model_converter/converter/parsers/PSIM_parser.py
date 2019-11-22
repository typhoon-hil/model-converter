import importlib
import os

from parglare import Grammar, Parser

from model_converter.converter.parsers.base_parser import BaseParser
from model_converter.converter.app.model.subsystem import Subsystem
from model_converter.converter.app.model.component import Component
from model_converter.converter.app.model.terminal import Terminal
import codecs

from model_converter.converter.app.util import get_root_path


class PSIMParser(BaseParser):

    #
    # All component type names
    # in this list need to be rotated
    #
    wrong_orientation_list = ["VDC","VDC_CELL","VSIN","VTRI","VSAW",
                              "SWQU","VSTEP","VSTEP_1","VGNL","VGNL_1",
                              "VVCVS","VCCVS","VCCVS_1","VVCVSV","VNONM",
                              "VNOND","VNONSQ","VRAND","VPOWERS","VMATH",
                              "IDC","ISIN","ITRI","ISQU","ISTEP","ISTEP_1",
                              "IGNL","IGNL_1","ICCCS","ICCCS_1","IVCCS",
                              "IVCCSV","INONM","INOND","INONSQ","IRAND",
                              "INONSP_1","INONSP_2"]

    def __init__(self, input_file_path, rule_file_path):
        super().__init__()

        root_path = get_root_path()

        self.user_lib = importlib.import_module('model_converter.'
                                                'user_libs.functions',
                                                'functions')

        self.input_grammar = \
            Grammar.from_file(os.path.join(root_path,
                                           'converter',
                                           'grammars',
                                           'XMLGrammar.pg'))

        self.input_parser = Parser(self.input_grammar)

        self.input_file_path = input_file_path
        self.rule_file_path = rule_file_path

        self.conversion_dict = {"Subsystem": []}

        self.temp_subsystem_dict = {}

        self.path_dict = {}

        self.file_input = None


    def _add_component_to_dict(self, component_object:Component):
        try:
            self.source_comp_dict_by_type[component_object.type].append(
                component_object)
        except KeyError:
            self.source_comp_dict_by_type[component_object.type] = \
                [component_object]

    def _extract_circuit(self, node):
        component_dict = {}
        for component in node[4]:
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

    def _extract_component(self, node):
        """
        Method which extracts information about the component in this
        "Component" XML node, creates a Component object and returns it.

        Also calls self._add_component_to_dict, which
        adds the Component object to the components dict.

        Args:
            node (list):  contains elements which describe the XML node,
                          such as attributes and child elements.

        Returns:
            A new Component object with all properties and attributes set.
        """
        new_component = Component()

        # Extracting type and name of component
        for attribute in node[2]:
            if attribute[0] == "Type":
                new_component.type = attribute[2].strip("\"")
            elif attribute[0] == "Name":
                name = attribute[2].strip("\"").split(".")
                new_component.name = name[-1]

        #
        # Extracting properties of the component.
        #
        for property in node[4]:
            ret_val = self._create_input_obj_model(property)
            #
            # If the return value is a dictionary, it is an actual property
            # of the component - eg. {"Resistance":120}
            #
            if isinstance(ret_val, dict):
                new_component.properties.update(ret_val)
            #
            # If the return value is a Terminal object, it is added to the
            # component's terminal list.
            #
            elif isinstance(ret_val, Terminal):
                ret_val.parent_component = new_component
                new_component.terminals[ret_val.index] = ret_val
            #
            # If the return value is a list, it is a nested list of two lists:
            #    - [x,y] the first one are the coordinates of the component,
            #    - [orientation, flip] properties of the component.
            #
            elif isinstance(ret_val, list):
                new_component.position = ret_val[0]
                new_component.orientation = ret_val[1][0]
                #
                # Some components are oriented differently
                # in the source netlist (horizontal (ours) vs vertical(theirs))
                #
                if new_component.type in PSIMParser.wrong_orientation_list:
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
        x = None
        y = None
        node_id = None
        index = None
        for attribute in node[2]:
            if attribute[0] == "X":
                x = int(attribute[2].strip("\""))
            elif attribute[0] == "Y":
                y = int(attribute[2].strip("\""))
            elif attribute[0] == "NodeId":
                node_id = int(attribute[2].strip("\""))
            elif attribute[0] == "Index":
                index = attribute[2].strip("\"")

        return Terminal(position=[x, y], node_id=node_id,
                        index=index, parent_component=None)

    def _extract_component_position(self, node):
        """
        Iterating through the list of tokens for a "Coord" XML node,
        returning the X and Y coordinates, as well as the rotation
        and flip of the component.

        Args:
            node (list): "Coord" XML node

        Returns:
            [ [X(int), Y(int)], [rotation(int), flip(int)] ]
        """
        x = None
        y = None
        rotation = None
        flip = None
        for attribute in node[2]:
            if attribute[0] == "X":
                x = int(attribute[2].strip("\""))
            elif attribute[0] == "Y":
                y = int(attribute[2].strip("\""))
            elif attribute[0] == "Direction":
                rotation = int(attribute[2].strip("\""))
            elif attribute[0] == "Flip":
                flip = attribute[2].strip("\"")
        return [[x, y], [rotation, flip]]

    def _extract_properties(self, node):
        """
        Iterating through the list of tokens for a "Param" XML node,
        looking for the property name and its value.
        Args:
            node (list): "Param" XML node
        Returns:
            dict {property_name: property_value}
        """
        for attribute in node[2]:
            if attribute[0] == "Name":
                try:
                    return {attribute[2].strip("\""):
                                float(self.si_prefix_remover(node[5]))}
                except ValueError:
                    return {attribute[2].strip("\""): node[5].strip("\"")}

    def _extract_subsystem(self, node):
        """
        Iterating through the list of tokens for a "SubCircuit" XML node,
        recursively calling create_input_obj_model on each child node.
        Depending on the return value of the function, different
        actions are taken:

            - If the return value is an instance of the Terminal class,
              it will be added to the subsystem's terminal list.
            - If the return value is a list, it is a list of X and Y
              coordinates of the "SubCircuit" XML node and its orientation.
            - If the return value is a dict, it is a dictionary of child
              components, and it will be set as the child_dictionary of
              the subsystem object.

        Finally, the subsystem object will be added to the
        source_comp_dict_by_type dictionary.

        Args:
            node (list): "SubCircuit" XML node

        Returns:
            subsystem (Subsystem)
        """
        subsystem = Subsystem()
        for attribute in node[2]:
            if attribute[0] == "Name":
                name = attribute[2].strip("\"")
                subsystem.name = name
        for child in node[4]:
            ret_val = self._create_input_obj_model(child)
            if isinstance(ret_val, Terminal):
                ret_val.parent_component = subsystem
                subsystem.terminals.append(ret_val)
            elif isinstance(ret_val, list):
                subsystem.position = ret_val[0]
                subsystem.orientation = ret_val[1][0]
                #
                # Some components are oriented differently
                # in the source netlist (horizontal (ours) vs vertical(theirs))
                #
                if "SubCircuit" in PSIMParser.wrong_orientation_list:
                    if subsystem.orientation == 270:
                        subsystem.orientation = 0
                    else:
                        subsystem.orientation += 90
            elif isinstance(ret_val, dict):
                for component_list in ret_val.values():
                    for component in component_list:
                        component.parent = subsystem
                subsystem.component_dict = ret_val
        self.source_comp_dict_by_type["Subsystem"].append(subsystem)
        return subsystem

    def _create_input_obj_model(self, node: list):
        """
        Recursively called for each node in the XML netlist.
        Depending on the 2nd item in the node
        (the name of the XML tag), different methods are called.

        CCircuits contain Components or SubCircuits(which are new CCircuits),
        each Component contains CNodes (terminals), Params(properties) and Coord
        which contain positional info (X and Y coords, orientation and flip).

        Args:
            node (list): XML node

        Returns:
            ret_val (dict):
            {"component_type_name":[component1, component2,...]}
        """
        if node[1] == "PsimSchematic":
            for child in node[4]:
                ret_val = self._create_input_obj_model(child)
                if ret_val is not None:
                    return ret_val
        elif node[1] == "CCircuit":
            return self._extract_circuit(node)

        elif node[1] == "Component":
            return self._extract_component(node)

        elif node[1] == "SubCircuit":
            return self._extract_subsystem(node)

        elif node[1] == "CNode":
            return self._extract_terminal(node)

        elif node[1] == "Param":
            return self._extract_properties(node)

        elif node[1] == "Coord":
            return self._extract_component_position(node)

    def read_input(self):
        with codecs.open(self.input_file_path, 'r',
                         'utf-16', errors='ignore') as fileData:
            # Creating obj model from the 2nd element
            # since the first one is the XML meta node
            input_data = self.input_parser.parse(fileData.read())[1]
            self._create_input_obj_model(input_data)


    def si_prefix_remover(self, x):
        dictionary ={
            "T" : "e12",
            "G" : "e9",
            "M" : "e6",
            "k" : "e3",
            "K" : "e3",
            "m" : "e-3",
            "u" : "e-6",
            "n" : "e-9",
            "p" : "e-12"
        }
        if x[-1] in dictionary:
            return x[:-1]+dictionary[x[-1]]
        else:
            return x