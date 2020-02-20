import codecs
import importlib
import os

from model_converter.converter.app.model.terminal import Terminal, Port

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

        self.port_map = {}

        self.component_id_dict = {}
        self.__node_id = 0

        self.path_dict = {}

        self.file_input = None

    def _extract_terminal(self, node):
        """
        In Simulink netlists, terminals are defined as lists of integers.
        Each integer is the number of specific terminal types.
        1st and 2nd elements are the signal processing terminals IN and OUT.
        The 6th and 7th elements are the power electronics
        terminals LConn and RConn.

        Args:
            node (str): string which represents the component's terminals.
                        For example: '[1, 1, 0, 0, 0, 2, 2]'

        Returns:
            terminal_obj_dict (dict): {Terminal.index:Terminal object,...}
        """
        terminal_obj_dict = {}
        terminals = node.text.strip("[]").replace(" ", "").split(",")
        # Component has no terminals
        if len(terminals) == 1 and terminals[0] == "":
            return terminal_obj_dict
        # Component has SP-In terminals
        for i in range(int(terminals[0])):
            sp_in_term = Terminal()
            sp_in_term.index = f"in:{i+1}"
            sp_in_term.name = None
            sp_in_term.kind = "sp"
            terminal_obj_dict[sp_in_term.index] = sp_in_term
        if len(terminals) == 1:
            return terminal_obj_dict
        # Component has SP-Out terminals
        for i in range(int(terminals[1])):
            sp_out_term = Terminal()
            sp_out_term.index = f"out:{i+1}"
            sp_out_term.name = None
            sp_out_term.kind = "sp"
            terminal_obj_dict[sp_out_term.index] = sp_out_term
        if len(terminals) == 2:
            return terminal_obj_dict
        # Component has PE terminals (lconn)
        if len(terminals) >= 6:
            for i in range(int(terminals[5])):
                pe_in_term = Terminal()
                pe_in_term.index = f"lconn:{i+1}"
                pe_in_term.name = None
                terminal_obj_dict[pe_in_term.index] = pe_in_term
        # Component has PE terminals (rconn)
        if len(terminals) == 7:
            for i in range(int(terminals[6])):
                pe_out_term = Terminal()
                pe_out_term.index = f"rconn:{i+1}"
                pe_out_term.name = None
                terminal_obj_dict[pe_out_term.index] = pe_out_term

        return terminal_obj_dict

    def _extract_system(self, node, skip_connections:bool=False):
        """
        Systems are composite elements - they hold other components
        (defined by "Block" elements) and "Line" elements, which describe
        all elements of a single node.

        Args:
            node: "System" XML element
            skip_connections (bool): flag for skipping "Line" parsing.

        Returns:
            component_dict (dict): {"Subsystem":[Subsystem_object1,...],
                                    "Component Type A":[Component_object1,
                                                        Component_object2],
                                    ...}
        """
        component_dict = {"Subsystem":[]}
        for component in node:
            component_obj = self._create_input_obj_model(component,
                                                         skip_connections)
            if isinstance(component_obj, Component):
                try:
                    component_dict[component_obj.type].append(component_obj)
                except KeyError:
                    component_dict[component_obj.type] = [component_obj]

            elif isinstance(component_obj, Subsystem):
                component_dict["Subsystem"].append(component_obj)

        return component_dict

    def _add_component_to_dicts(self, component_object: (Component, Subsystem)):
        """
        Adds the component or subsystem to the list
        of components of the same type.

        Args:
            component_object (Component,
                             Subsystem): component which is getting
                                         added to the list

        Returns:
            None
        """
        component_id = component_object.properties.get("__id__")
        if component_id in self.component_id_dict:
            return
        self.component_id_dict[component_id] = component_object

        if component_object.type not in self.source_comp_dict_by_type:
            self.source_comp_dict_by_type[component_object.type] = []
        self.source_comp_dict_by_type[component_object.type].append(
            component_object)


    def _extract_properties(self, node):
        """
        This method is called whenever a Property node is parsed.
        Returns a dictionary with the name of the property and the value

        Args:
            node: "P" tagged XML node

        Returns:
            dict {property_name:property_value}
        """
        # Casting into float if the value is a digit,
        # otherwise using the text value
        try:
            text_val = float(node.text)
        except ValueError:
            text_val = node.text
        return {node.attrib.get("Name"): text_val}

    def _extract_component(self, node):
        """
        This method is called whenever a "Block" tagged XML node is parsed.
        Creates a Component or Subsystem object, sets its properties and
        terminals, adds it to the component dicts (ID and type dicts),
        and finally, returns the newly created object.

        Args:
            node: "Block" tagged XML node

        Returns:
            new_component (Component,Subsystem)
        """

        comp_type = node.attrib.get("BlockType", "SubSystem")
        new_component = Component() if comp_type != "SubSystem" else Subsystem()

        new_component.name = node.attrib.get("Name")
        #
        # Temporarily adding the component's unique ID
        # to the properties dict, which will be used to
        # resolve connections
        #
        new_component.properties["__id__"] = node.attrib.get("SID")

        #
        # Temporarily adding a counter for LConn, RConn, In and Oout
        # terminals, which will be used to create missing terminals
        # of each connection if needed
        #
        if comp_type not in ("PMIOPort", "Inport", "Outport"):
            new_component.properties["__lconn__"] = 1
            new_component.properties["__rconn__"] = 1
            new_component.properties["__in__"] = 1
            new_component.properties["__out__"] = 1

        if comp_type != "Reference":
            # Matching case since the BaseParser checks
            # for "Subsystem" instead of "SubSystem"
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
                    # Subsystem ports are defined
                    # by the child block's "PMIOPort"/"Inport"/"Outport"
                    if comp_type == "Subsystem":
                        continue
                    terminals = self._create_input_obj_model(child)
                    for terminal in terminals.values():
                        terminal.parent_component = new_component
                        terminal.position = new_component.position
                    else:
                        new_component.terminals.update(terminals)
                elif prop_name == "Side":
                    term_side = self._create_input_obj_model(child)
                    new_component.properties.update(term_side)
            #
            # The block is a subsystem element
            #
            elif child.tag == "System":
                children = self._create_input_obj_model(child,
                                                        skip_connections=False)
                for child_list in children.values():
                    for subsys_child in child_list:
                        subsys_child.parent = new_component
                new_component.component_dict = children

                port_types = {ports:children.pop(ports, []) for ports in
                              ("PMIOPort", "Inport", "Outport")}

                for port_type, ports in port_types.items():
                    for port in ports:
                        term_index = None
                        if port_type == "PMIOPort":
                            side = port.properties["Side"]
                            term_side = "lconn" if side == "Left" else "rconn"
                            key = f"__{term_side}__"
                            term_index = \
                                f"{term_side}:{port.parent.properties[key]}"
                            port.parent.properties[key] += 1
                        elif port_type == "Inport":
                            key = "__out__"
                            term_index = f"out:{port.parent.properties[key]}"
                            port.parent.properties[key] += 1
                        elif port_type == "Outport":
                            key = "__in__"
                            term_index = f"in:{port.parent.properties[key]}"
                            port.parent.properties[key] += 1
                        # Ports always have a single "terminal"
                        term = list(port.terminals.values())[0]
                        # Keeping the original port name
                        term.name = port.name
                        term.index = term_index
                        term.parent_component = new_component
                        self.component_id_dict[port.properties["__id__"]] = term
                        if term not in self.port_map:
                            self.port_map[term] = []
                        new_component.terminals.append(term)
                #
                # Parsing Line tagged XML elements,
                # this sets all terminal node IDs.
                #
                for line in child:
                    if line.tag == "Line":
                        self._create_input_obj_model(line)
            #
            # Setting the Component's properties
            #
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

        self._add_component_to_dicts(new_component)
        return new_component

    def __get_component_terminal(self, data):
        if data is not None:
            component = self.component_id_dict.get(data[0])
            # Subsystem terminals replace their
            # PMIOPort components in the id_dict
            if type(component) is Terminal:
                terminal = component
            else:
                terminal = None
                if type(component) is Subsystem:
                    # Subsystem terminals attribute is a list
                    for term in component.terminals:
                        if term.index == data[1]:
                            terminal = term
                            break
                # Getting an actual component's terminal
                else:
                    terminal = component.terminals.get(data[1],
                                                       None)
            return terminal


    def _set_terminal_node_id(self, node,
                              increment_id:bool=True):
        start = None
        end = None
        terminals_in_node = []
        #
        # Extracting the component ID and terminal name
        # for the connection start and end points
        #
        for child in node:
            if child.tag == "P":
                if child.attrib.get("Name") == "Src":
                    start = child.text.split("#")
                elif child.attrib.get("Name") == "Dst":
                    end = child.text.split("#")
            # The connection contains more than 2 components
            # if the "Line" element contains a child element called "Branch"
            elif child.tag == "Branch":
                # Not incrementing node_id since all branches
                # and their root element are in the same node

                # Unpacking the return value of this recursive call
                # and appending it into the list of all terminals in this node
                terminals_in_node.extend(
                    self._set_terminal_node_id(child, increment_id=False))

        for data in (start, end):
            if data is None:
                continue
            # The component reference is used to set the missing
            # terminal's parent, and also to add terminals to its
            # terminal collection
            component = self.component_id_dict.get(data[0])

            terminal = self.__get_component_terminal(data)

            if terminal is None:
                term_kind = data[1].split(":")[0]
                kind = None
                if term_kind in ("lconn", "rconn"):
                    kind = "pe"
                elif term_kind in ("in", "out"):
                    kind = "sp"
                if kind is None:
                    raise Exception(f"Cannot create terminal of "
                                    f"the {term_kind} kind, "
                                    f"for the component {component.type}.")
                index = data[1]
                # "Side" properties are present in PE terminals/ports,
                # it describes the name of the terminal. This is important
                # because Line XML elements describe connections using
                # component ID's and terminal names
                # (example: SRC - 4#lconn:1, DST - 7#rconn:3)
                if "Side" in component.properties:
                    index = "lconn" if component.properties["Side"] == "Left" \
                        else "rconn"
                    index += f":{component.properties['Port']}" \
                        if "Port" in component.properties else ":1"
                terminal = Terminal(position=component.position,
                                    node_id=self.__node_id,
                                    index=index,
                                    parent_component=component,
                                    kind=kind,
                                    name=index)
                if kind == "sp":
                    # term_kind holds the direction,
                    # extracted from the terminal name
                    terminal.direction = term_kind
                # Subsystem terminals are contained in lists, since
                # their "index" is not a unique value - example:
                # multiple lconn:1 terminals for each PMIOPort
                if type(component) is Subsystem:
                    component.terminals.append(terminal)
                    self.port_map[terminal] = []
                # All other components terminals are contained in dicts
                else:
                    component.terminals[data[1]] = terminal
            else:
                if terminal.node_id is None:
                    terminal.node_id = self.__node_id
            terminals_in_node.append(terminal)
        # If increment_id is set to False, the method was called recursively,
        # and the setting of node IDs should be left to the original
        # call of the method (initial parse of the Line element)
        if increment_id is False:
            return terminals_in_node

        self.__node_id += 1
        #
        # The following code sets all terminals' node ID
        # to the node ID of the ports of the same node
        #
        ports_in_node = []
        for terminal in terminals_in_node:
            if terminal.parent_component.type in ["PMIOPort",
                                                  "Inport",
                                                  "Outport"] \
                    or type(terminal.parent_component) is Subsystem:
                ports_in_node.append(terminal)

        if ports_in_node:
            for port in ports_in_node:
                if port not in self.port_map:
                    self.port_map[port] = []
                for terminal in terminals_in_node:
                    if terminal is port:
                        continue
                    self.port_map[port].append(terminal)
                    terminal.node_id = port.node_id
                    if type(terminal.parent_component) is Subsystem:
                        self._set_port_node_ids(terminal)


    def _set_port_node_ids(self, port:Port):
        """
        Iterates through all the terminals and ports in a node.
        Sets the terminals' node ID to their port node ID,
        and sets any other port's node ID to the first port's ID.
        If there was a port present in the node (besides the first port)
        the method is called recursively, and all the terminals in that
        other port's node get their node IDs set to the previously set value.

        Args:
            port (Port): port object which is used to retrieve
                         all terminals in the node

        Returns:
            None
        """
        for terminal in self.port_map[port]:
            if terminal.node_id == port.node_id:
                continue
            terminal.node_id = port.node_id
            # Checking if the current terminal is actually a port
            if type(terminal.parent_component) is Subsystem:
                self._set_port_node_ids(terminal)

    def _create_input_obj_model(self, node, skip_connections:bool=False):
        """
        Creates the object model from the passed XML netlist.
        Depending on the tag of the XML node, different methods
        are called.

        Elements can be:
            Model - this is the root element
            System - this element is a container for other elements,
                     and it describes an entire hierarchical level
                     of a netlist
            Block - this element describes actual components
                    (can also be a Subsystem)
            P - this element is a Property element
            Line - this element describes a connection between components
                    (can contain Branch elements, which means there are
                    more than 2 components connected by this line)

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
                ret_val = self._create_input_obj_model(child, skip_connections)
                if ret_val is not None:
                    return ret_val

        elif node.tag == "System":
            return self._extract_system(node, skip_connections)

        elif node.tag == "Block":
            return self._extract_component(node)

        elif node.tag == "P":
            if node.attrib.get("Name") == "Ports":
                return self._extract_terminal(node)
            return self._extract_properties(node)

        elif node.tag == "Line" and not skip_connections:
            return self._set_terminal_node_id(node)

    def read_input(self):
        import xml.etree.ElementTree as ET
        with codecs.open(self.input_file_path,
                         'r', errors='ignore') as fileData:
            # Parsing XML with the ElementTree library
            input_data = ET.fromstring(fileData.read())
            for child in input_data:
                self._create_input_obj_model(child, skip_connections=False)
