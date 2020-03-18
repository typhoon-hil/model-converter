import codecs
import os

from jinja2 import Template
from parglare import Grammar, Parser

from model_converter.converter.app.model.rule import Rule, Property, \
    Connection, Pattern, Predicate
from model_converter.converter.app.model.subsystem import Subsystem
from model_converter.converter.app.model.terminal import Terminal, Port
from model_converter.converter.app.model.data_holder import DataHolder, \
    SubsystemDataHolder
import logging

from model_converter.converter.app.util import get_root_path


class BaseParser:

    def __init__(self):
        from typhoon.api.schematic_editor import model as mdl
        self.mdl = mdl

        self.rule_file_path = None
        self.input_file_path = None
        self.user_lib = None

        root_path = get_root_path()
        logging.basicConfig(filename=os.path.join(root_path,"conversion.log"),
                            filemode="w", level=logging.WARNING)
        self.rule_grammar = \
            Grammar.from_file(os.path.join(root_path,
                                           'converter',
                                           'grammars',
                                           'TyphoonRuleGrammar.pg'))

        self.rule_parser = Parser(self.rule_grammar)
        #
        # Should be set by child classes
        #
        self.input_parser = None
        self.match_rules = None
        self.patterns = {}
        #
        # Hierarchy of converted components (DataHolders),
        # used to connect components at the end of the conversion.
        # node_dict = {subsystem_handle(str):{node_id(str/int):
        #                                   [terminal_handle1(str),
        #                                   terminal_handle2(str),...]
        #                                   }
        #             }
        # Added None as the root level.
        #
        self.node_dict = {None:{}}
        self.conversion_dict = {}

        #
        # Dictionary which holds all subsystems
        # converted from the netlist, used to place
        # components into their parent subsystems
        #
        self.temp_subsystem_dict = {}

        #
        # Dictionary which holds all source components,
        # in TYPE:[INSTANCE1, INSTANCE2...] pairs
        #
        self.source_comp_dict_by_type = {"Subsystem": []}

        self.compiled = False

    def read_rules(self):
        with codecs.open(self.rule_file_path, 'r', errors='ignore') \
                as fileData:
            rules = self.rule_parser.parse(fileData.read())

            self.match_rules = self._create_rule_obj_model(rules)

    def read_input(self):
        raise NotImplementedError("Reimplement this method in a child class.")

    def _create_rule_obj_model(self, rule_list):
        """
        Creates a Rule object model from the parsed
        rule file.

        Also creates patterns if defined,
        and adds them to the self.patterns dict under
        the pattern names.

        Args:
            rule_list (list): list of rules, each of which is essentially
                              a nested list (list of lists)

        Returns:
            rules (list): Rule objects
        """
        rules = []

        if len(rule_list) == 2:
            #
            for pattern in rule_list[0]:
                pattern_obj = self._create_pattern_rule(pattern)
                self.patterns[pattern_obj.name] = pattern_obj
            for rule in rule_list[1]:
                if rule[1][0] == "*":
                    if rule[1][3] == "{":
                        rules.append(self._create_n_to_m_rule(rule))
                    else:
                        rules.append(self._create_n_to_one_rule(rule))
                else:
                    if rule[1][2] == "{":
                        rules.append(self._create_n_to_m_rule(rule))
                    else:
                        rules.append(self._create_n_to_one_rule(rule))
        return rules

    def _create_predicate_obj(self, predicate_node):
        property_name = None
        condition = "=="
        property_value = None
        if len(predicate_node.split(">=")) == 2:
            condition = ">="
        elif len(predicate_node.split("=<")) == 2:
            condition = "<="
        elif len(predicate_node.split(">")) == 2:
            condition = ">"
        elif len(predicate_node.split("<")) == 2:
            condition = "<"
        property_name, property_value = predicate_node.split(condition)

        return Predicate(property_name, condition, property_value)

    def _create_property_obj(self, prop_node):
        """
        Creates a Property object from the parsed property rule.

        Args:
            prop_node (list): nested list containing
                              all the parsed (DSL) terminal values

        Returns:
            prop_obj (Property)
        """
        prop_obj = Property(name=prop_node[0])
        #
        # Str property
        #
        if "\"" == prop_node[2][0] and "\"" == prop_node[2][-1] \
                or "'" == prop_node[2][0] and "'" == prop_node[2][-1]:
            prop_obj.prop_type = "str"
            prop_obj.value = prop_node[2].strip("\"").strip("'")
        #
        # Num property
        #
        elif prop_node[2].isdigit():
            prop_obj.prop_type = "num"
            prop_obj.value = float(prop_node[2])
        #
        # Checking if property value is a function call or
        # just a property with parentheses in its name
        #
        elif "(" in prop_node[2]:
            prop_split = prop_node[2].split("(", 1)
            func_name = prop_split[0]
            function = getattr(self.user_lib, func_name, None)
            # Checking if there is a user defined function with this name
            if function:
                prop_obj.prop_type = "func"
                prop_obj.value = func_name
                params = prop_split[1].strip(")")
                if params:
                    param_list = params.split(",")
                    for parameter in param_list:
                        key, value = parameter.split("=")
                        if "(" in value and ")" not in value:
                            value += ")"
                        prop_obj.params[key.strip(" ")] = value.strip(" ")
            # Property value is a reference to a source component property
            else:
                prop_obj.prop_type = "ref"
                prop_obj.value = prop_node[2]
        #
        # Reference property
        #
        else:
            prop_obj.prop_type = "ref"
            prop_obj.value = prop_node[2]

        return prop_obj

    def _create_n_to_m_rule(self, rule_node):
        """

        Args:
            rule_node:

        Returns:

        """
        #
        # Checking if the "source type" is a pattern.
        # If it is a pattern, all indices are moved by 1,
        # and the pattern first must be found before
        # converting by this rule.
        #
        predicates = rule_node[0]
        rule_node = rule_node[1]
        is_pattern_match = rule_node[0] == "*"

        source_type = rule_node[1] if is_pattern_match else rule_node[0]
        typhoon_type = rule_node[3] if is_pattern_match \
                                       and rule_node[3] != "{" else "N-to-M"

        rule_obj = Rule(source_type=source_type,
                        typhoon_type=typhoon_type,
                        pattern_match=is_pattern_match)

        for predicate in predicates:
            rule_obj.predicates.append(self._create_predicate_obj(predicate[1]))

        #
        # List containing all components which will
        # be created in this new subsystem
        #
        component_list = rule_node[4] if is_pattern_match else rule_node[3]
        for component in component_list:
            comp_rule_obj = Rule(typhoon_type=component[2])
            #
            # Setting property mapping
            #
            for prop in component[4]:
                comp_rule_obj.properties.append(self._create_property_obj(prop))
            rule_obj.components[component[0]] = comp_rule_obj
        #
        # List containing connections between the
        # newly created components inside the subsystem
        #
        connection_list = rule_node[7] if is_pattern_match else rule_node[6]

        for connection in connection_list:
            conn_obj = Connection(start_handle=connection[0],
                                  start_terminal=connection[2],
                                  end_handle=connection[4],
                                  end_terminal=connection[6])
            rule_obj.connections.append(conn_obj)

        port_list = rule_node[11] if is_pattern_match else rule_node[10]
        for port in port_list:
            comp_handle = port[0]
            comp_term = port[2]
            term_type = port[4]
            if is_pattern_match:
                pattern_handle = port[7]
                term_node = port[9]
            else:
                # 1:N conversion, there is no
                # pattern component handle
                # example: just '0' instead of 'MyComponent.0'
                pattern_handle = None
                term_node = port[7]
            rule_obj.ports[pattern_handle, term_node] = (term_type, comp_handle, comp_term)
        return rule_obj

    def _create_one_to_one_rule(self, rule_node):
        """
        Creates a Rule object from the parsed 1:1 rule.

        Args:
            rule_node (list): nested list containing
            all the parsed (DSL) terminal values

        Returns:
            rule_obj (Rule)
        """
        rule_obj = Rule(source_type=rule_node[0], typhoon_type=rule_node[2])

        #
        # Setting property mapping
        #
        for prop in rule_node[4]:
            rule_obj.properties.append(self._create_property_obj(prop))

        #
        # Setting terminal node mapping
        #

        for terminal in rule_node[7]:
            term_name = terminal[0]
            term_type = terminal[2]
            term_node = terminal[5]
            rule_obj.terminals[term_node] = (term_type, term_name)

        return rule_obj

    def _create_pattern_rule(self, pattern_node):
        """
        Creates pattern objects which are used in conversion rules.

        Example of a conversion rule with pattern matching:
            *Buck => Buck
            (pattern name => Typhoon component type)

        Args:
            pattern_node (list): nested list of lists containing
                                 components and their connections

        Returns:
            pattern_obj (Pattern)
        """
        pattern_obj = Pattern(pattern_node[0].strip())
        #
        # Mapping user defined handles to their component types
        #
        for component in pattern_node[4]:
            pattern_obj.components[component[0]] = component[2]
        #
        # Mapping the connections between pattern components
        #
        for connection in pattern_node[8]:
            start_handle = connection[0]
            start_terminal = connection[2]
            end_handle = connection[4]
            end_terminal = connection[6]
            connection_obj = Connection(start_handle=start_handle,
                                        start_terminal=start_terminal,
                                        end_handle=end_handle,
                                        end_terminal=end_terminal)
            pattern_obj.connections.append(connection_obj)

        return pattern_obj

    def _create_n_to_one_rule(self, rule_node):
        """
        Creates a Rule object from the parsed N:1 rule.

        Args:
            rule_node (list): nested list of lists containing
                              components and their connections

        Returns:
            rule_obj (Rule)
        """
        predicates = rule_node[0]
        rule_node = rule_node[1]
        is_pattern_match = rule_node[0] == "*"

        source_type = rule_node[1] if is_pattern_match else rule_node[0]
        typhoon_type = rule_node[3] if is_pattern_match else rule_node[2]
        rule_obj = Rule(source_type=source_type,
                        typhoon_type=typhoon_type,
                        pattern_match=is_pattern_match)

        rule_list = rule_node[5] if is_pattern_match else rule_node[4]
        for prop in rule_list:
            rule_obj.properties.append(self._create_property_obj(prop))

        for predicate in predicates:
            rule_obj.predicates.append(self._create_predicate_obj(predicate[1]))

        terminal_list = rule_node[8] if is_pattern_match else rule_node[7]
        for terminal in terminal_list:
            term_name = terminal[0]
            term_kind = terminal[2]
            if is_pattern_match:
                term_parent = terminal[5]
                term_node = terminal[7]
            else:
                term_parent = None
                term_node = terminal[5]
            rule_obj.terminals[term_parent, term_node] = (term_kind,
                                                          term_parent,
                                                          term_name)

        return rule_obj

    def _pattern_match(self, start_collection, end_collection, connection):
        matched = {}
        for start_comp in start_collection:
            if start_comp.converted:
                continue
            for end_comp in end_collection:
                if start_comp is end_comp:
                    continue
                if end_comp.converted:
                    continue
                start_terminal = \
                    start_comp.terminals[connection.start_terminal]
                end_terminal = end_comp.terminals[connection.end_terminal]
                if start_terminal.node_id == end_terminal.node_id:
                    if connection.start_handle not in matched:
                        matched[connection.start_handle] = start_terminal
                    if connection.end_handle not in matched:
                        matched[connection.end_handle] = end_terminal
                    return matched

    def _create_conversion_subsystems(self,
                                      component_parent: (Subsystem, None),
                                      current_sub: Subsystem = None):

        if component_parent is None:
            return None

        subsystem = \
            self.temp_subsystem_dict.get(component_parent.name, None)
        if subsystem is None:
            subsystem = SubsystemDataHolder()
            subsystem.name = component_parent.name.split(".")[-1]
            subsystem.components["Subsystem"] = []
            subsystem.ports = [port.clone() for port
                               in component_parent.terminals]

            self.temp_subsystem_dict[component_parent.name] = subsystem

        if current_sub is not None:
            subsystem.components["Subsystem"].append(current_sub)
        if component_parent.parent is None:
            if subsystem not in self.conversion_dict["Subsystem"]:
                self.conversion_dict["Subsystem"].append(subsystem)
            return subsystem


        parent = self._create_conversion_subsystems(component_parent.parent,
                                                    subsystem)
        subsystem.parent = parent
        return subsystem



    def get_original_file_name(self, file_name:str):
        """
        Returns the file TSE file name
        Args:
            file_name: (str) input file's filename

        Returns:
            tse file name (str)
        """
        path = ""
        path = os.path.join(path, *file_name)
        return path+".tse"


    def get_available_file_name(self, file_name:str):
        """
        Checks if the input file's filename is available as the output file's
        filename. If the name is already taken, appends an index (or increments
         it if there is already an index present) to the output file's filename.
        Args:
            file_name: (str) input file's filename

        Returns:
            new file name (str)
        """
        index = 0
        path = ""
        path = os.path.join(path, *file_name)
        while True:
            if os.path.isfile(path+".tse"):
                index+=1
            else:
                return path+".tse"
            if not os.path.isfile(path+"("+str(index)+").tse"):
                return path+"("+str(index)+").tse"


    def _save_single_component(self, component, parent=None):
        from typhoon.api.schematic_editor.exception import SchApiException
        component.parent = parent
        component_handle = \
            self.mdl.create_component(
                        component.typhoon_type,
                        parent=parent,
                        name=component.name,
                        rotation=component.orientation,
                        position=component.position)

        for key, value in component.properties.items():
            try:
                self.mdl.set_property_value(
                    self.mdl.prop(component_handle, key), value)
            except SchApiException:
                logging.warning(f"(Property setting error) "
                                f"{component.name}- error setting"
                                f" property \"{key}\" to "
                                f"\"{value}\".")
        self.mdl.set_position(component_handle, component.position)

        for term in component.terminals:
            try:
                #
                # !! NOTE !!
                # This may raise the SchApiException if the component
                # does not have a terminal with the passed name
                #
                terminal_handle = self.mdl.term(component_handle, term.name)

                subsystem_dict = self.node_dict.get(parent, None)
                # If the parent key is not present, create a new dict
                # and set the reference to it so it can be populated
                # with node id's and the corresponding terminal handles
                if subsystem_dict is None:
                    new_subsystem = {}
                    self.node_dict[parent] = new_subsystem
                    subsystem_dict = new_subsystem
                connectables = subsystem_dict.get(term.node_id, None)
                if connectables is None:
                    subsystem_dict[term.node_id] = []
                subsystem_dict[term.node_id].append(
                    [False, terminal_handle, component])
            except SchApiException:
                logging.warning(f"[Terminal connection error] Cannot retrieve "
                                f"terminal \"{term.name}\" of the "
                                f"\"{component_handle.fqn}\""
                                f"({component.typhoon_type}) component.")
        return component_handle

    def save_component(self, component, parent=None):
        from typhoon.api.schematic_editor.exception import SchApiException
        if isinstance(component, SubsystemDataHolder):
            component_handle = \
                self.mdl.create_component(component.typhoon_type,
                                          parent=parent,
                                          name=component.name,
                                          position=component.position,
                                          rotation=component.orientation)
            temp_handle_dict = {}
            #
            # Creating child components inside the subsystem
            #
            for handle, child_comp_list in component.components.items():
                for child_comp in child_comp_list:
                    child_comp.parent = component_handle
                    if isinstance(child_comp, SubsystemDataHolder):
                        self.save_component(child_comp, component_handle)
                    else:
                        child_handle = \
                            self._save_single_component(child_comp,
                                                        component_handle)

                        temp_handle_dict[handle] = child_handle

            #
            # Creating inner component connections
            #
            for connection in component.connections:
                start_handle = temp_handle_dict[connection.start_handle]
                start_term = connection.start_terminal

                #
                # Creating logging strings, used in except blocks below
                #
                child_handles = "("
                for handle in component.components.keys():
                    child_handles += handle + ", "
                child_handles = child_handles.strip().strip(",") + ")"

                # Retrieving start terminal
                try:
                    start_terminal = self.mdl.term(start_handle, start_term)
                except SchApiException:
                    typhoon_type = \
                        component.components[start_handle].typhoon_type
                    logging.warning(f"[N -> M conversion error - "
                                    f"{child_handles}] Cannot retrieve terminal"
                                    f" {start_term} of component {start_handle}"
                                    f" ({typhoon_type}).")
                    continue
                end_handle = temp_handle_dict[connection.end_handle]
                end_term = connection.end_terminal
                # Retrieving end terminal
                try:
                    end_terminal = self.mdl.term(end_handle, end_term)
                except SchApiException:
                    typhoon_type = \
                        component.components[end_handle].typhoon_type
                    logging.warning(f"[N -> M conversion error - "
                                    f"{child_handles}] Cannot retrieve terminal"
                                    f" {end_term} of component {end_handle}"
                                    f" ({typhoon_type}).")
                    continue
                # Connecting child component terminals
                try:
                    self.mdl.create_connection(start_terminal, end_terminal)
                except SchApiException:
                    logging.warning(f"[N -> M conversion error - "
                                    f"{child_handles}] Cannot connect terminals"
                                    f"{start_terminal} with {end_terminal}.")
            # Counter for unique port names.
            UID = 0
            init_pos = [15, 50]
            for port in component.ports:
                # If the parent_component of a port is a string,
                # the conversion was 1:Sub. This means the port_name
                # should contain the parent_component name to avoid
                # port name duplication
                if isinstance(port.parent_component, str):
                    port_name = f"{port.parent_component} {port.name}"
                else:
                    port_name = "Port" + str(UID) if port.name is None \
                        else port.name
                if port.kind == "sp":
                    port_handle = self.mdl.create_port(parent=component_handle,
                                                       kind=port.kind,
                                                       direction=port.direction,
                                                       name=port_name,
                                                       position=init_pos)
                else:
                    port_handle = self.mdl.create_port(parent=component_handle,
                                                       kind=port.kind,
                                                       name=port_name,
                                                       position=init_pos)
                #
                # Checking if the parent_component of this port is
                # a string value. If it is, the Subsystem was not
                # present in the original netlist, and this port
                # should be connected to the component which set
                # its node ID.
                #
                if isinstance(port.parent_component, str):
                    source_term = \
                        self.mdl.term(temp_handle_dict[port.parent_component],
                                      port.name)
                    self.mdl.create_connection(port_handle, source_term)

                init_pos = [i for i in init_pos]
                init_pos[1] += 50

                UID += 1  # Incrementation of the unique ID number.
                level = self.node_dict.get(component_handle, None)
                if level is None:
                    self.node_dict[component_handle] = \
                        {port.node_id: [
                            [False, port_handle, component]]}
                else:
                    connectables = level.get(port.node_id, None)
                    if connectables is None:
                        level[port.node_id] = []

                    level[port.node_id].append(
                        [False, port_handle, component])

                parent_level = self.node_dict.get(
                    parent, None)
                if parent_level is None:
                    self.node_dict[parent] = {
                        port.node_id: [
                            [False, self.mdl.term(component_handle, port_name),
                             component]]}
                else:
                    parent_connectables = parent_level.get(port.node_id,
                                                           None)
                    if parent_connectables is None:
                        parent_level[port.node_id] = []

                    parent_level[port.node_id].append(
                        [False, self.mdl.term(component_handle, port_name),
                         component])

        else:
            self._save_single_component(component, parent)


    def save_subsystem(self, subsystem, parent_subsystem_handle):
        sub = self.mdl.create_component("core/Empty Subsystem",
                                        parent=parent_subsystem_handle,
                                        name=subsystem.name.split(".")[-1],
                                        position=subsystem.position)

        # Counter for unique port names.
        UID = 0
        for port in subsystem.ports:
            port_name = "Port" + str(UID)
            port_handle = self.mdl.create_port(parent=sub,
                                               kind=port.kind,
                                               name=port_name,
                                               position=port.position)

            UID += 1  # Incrementation of the unique ID number.
            level = self.node_dict.get(sub, None)
            if level is None:
                self.node_dict[sub] = \
                    {port.node_id:[[False,port_handle, subsystem]]}
            else:
                connectables = level.get(port.node_id, None)
                if connectables is None:
                    level[port.node_id] = [[False,port_handle, subsystem]]
                else:
                    level[port.node_id].append([False,port_handle, subsystem])
            parent_level = self.node_dict.get(parent_subsystem_handle, None)
            if not parent_level:
                self.node_dict[parent_subsystem_handle] = {port.node_id:[[False,self.mdl.term(sub,port_name), subsystem]]}
            else:
                parent_connectables = parent_level.get(port.node_id, None)
                if parent_connectables is None:
                    parent_level[port.node_id] = [[False, self.mdl.term(sub,port_name), subsystem]]
                else:
                    parent_level[port.node_id].append([False, self.mdl.term(sub,port_name), subsystem])

        for type, component in subsystem.components.items():
            component.parent = sub
            if type == "Subsystem":
                self.save_subsystem(component, sub)
            else:
                self.save_component(component, sub)


    def save_schematic(self, device_id, config_id, compile_model=False):
        """
        Instantiates a Schematic API client, creates a new model and configures
        it, and saves each converted component.

        Also connects terminals in each node for each level in the hierarchy.

        Depending on the compile_model flag, the model will be
        compiled after saving and connecting all components.

        Args:
            device_id (str): device identifier - example: "HIL604"
            config_id (str): configuration identifier - example: "1"
            compile_model (bool): compilation flag

        Returns:
            None
        """

        self.mdl.create_new_model()
        #
        # !! Setting HIL model !!
        #
        self.mdl.set_model_property_value("hil_device", device_id)
        self.mdl.set_model_property_value("hil_configuration_id", config_id)

        # API calls for component creation, property setting,
        # child element creation etc...
        for type, components in self.conversion_dict.items():
            for component in components:
                self.save_component(component, component.parent)
        #
        # API calls for terminal connection
        #
        for connectable_dict in self.node_dict.values():
            for key, connectable_list in connectable_dict.items():
                # Terminals might not be connected,
                # in this case their Node ID is None.
                # node_id:[terminal list]
                if key is None:
                    continue
                self._connect(connectable_list)
        path = self.input_file_path.split(os.path.sep)
        path[0] += os.path.sep
        path[-1] = path[-1].replace(".xml", "")
        self.save_path = self.get_original_file_name(path)
        self.mdl.save_as(self.save_path)
        if compile_model:
            self.compiled = self.mdl.compile()
        self.mdl.close_model()

    def _connect(self, connectable_list:list):
        """
        Connecting terminal handles from the same node,
        contained in the connectable_list.

        If there are more than two terminals in a node,
        a junction will be created and used to connect
        all terminals together.

        Args:
            connectable_list (list): terminal handle list,
                                     all of which are in
                                     the same node.

        Returns:
            None
        """
        from typhoon.api.schematic_editor.exception import SchApiException
        junction = None
        # Checking if a junction should be used to connect
        # terminals from this node list
        if len(connectable_list) > 2 and junction is None:
            kind = "sp" if [term for term in connectable_list
                            if self.mdl.get_connectable_kind(term[1]) == "sp"] \
                else "pe"
            position = [0, 0]
            for connectable in connectable_list:
                position[0] += connectable[2].position[0]
                position[1] += connectable[2].position[1]
            position[0] = int(position[0]/len(connectable_list))
            position[1] = int(position[1]/len(connectable_list))
            connectable_parent = connectable_list[0][2].parent

            junction = \
                self.mdl.create_junction(parent=connectable_parent,
                                         position=position,
                                         kind=kind)
        #
        # Connecting all terminals from the same
        # node with the newly created junction
        #
        if junction:
            for connectable in connectable_list:
                try:
                    self.mdl.create_connection(junction,
                                               connectable[1])
                except SchApiException:
                    logging.warning(f"[Connecting Schematic components] Unable "
                                    f"to connect {junction} with "
                                    f"{connectable[1].fqn}.")
        #
        # Connecting terminals directly with each other
        #
        else:
            for connectable_A in connectable_list:
                for connectable_B in connectable_list:
                    if connectable_A is connectable_B:
                        continue
                    if connectable_A[0] or connectable_B[0]:
                        continue
                    #
                    # !! Note !!
                    #
                    # Uncomment this to prevent the connecting of
                    # two or more terminals of the same component
                    # with each other

                    # if connectable_A[2] is connectable_B[2]:
                    #     continue

                    try:
                        self.mdl.create_connection(connectable_A[1],
                                                   connectable_B[1])
                        connectable_B[0] = True
                    except SchApiException:
                        logging.warning(f"[Connecting Schematic components] "
                                        f"Unable to connect "
                                        f"{connectable_A[1].fqn} with "
                                        f"{connectable_B[1].fqn}.")

    def _convert_one_to_sub(self, rule, component, parent_subsystem):
        """
        Converts the component into a Subsystem.
        All child components defined by the rule
        are also created and added to the components
        dictionary.

        Args:
            rule (Rule): Rule object which defines the new Subsystem
            component (Component): netlist Component object
            parent_subsystem (Subsystem): the component's parent
                                          (None if this is on the root level)

        Returns:
            sub (SubsystemDataHolder)
        """
        sub = SubsystemDataHolder()
        sub.position = [i * 2 for i in component.position]
        sub.name = component.name

        for handle, child_comp_rule in rule.components.items():
            dh = self._convert_one_to_one(child_comp_rule,
                                          component,
                                          None)
            dh.name = handle
            sub.components[handle] = [dh]

        sub.connections = rule.connections

        try:
            for i, items in enumerate(rule.ports.items()):
                key = items[0][1]
                values = items[1]
                node_id = component.terminals[key].node_id
                port = Port()
                port.node_id = node_id
                port.kind = values[0]
                port.parent_component = values[1]
                port.name = values[2]
                sub.ports.append(port)
        except KeyError:
            logging.warning(f"[1:M - {rule.source_type} ({component.name}) -> "
                            f"core/Subsystem] Port mapping #{i} is incorrect, "
                            f"missing terminal with the ID \"{key}\" in the "
                            f"source component.")
            return None

        sub.parent = parent_subsystem
        return sub

    def _convert_one_to_n(self, rule):
        """
        Iterates through all source components of
        the specified source type - defined in the rule object,
        and converts them into either a single new component (DataHolder)
        or a whole subsystem with child components (SubsystemDataHolder).

        Args:
            rule (Rule): Rule object

        Returns:
            ret_val (list): list of DataHolders or SubsystemDataHolders
        """
        if rule.source_type not in self.source_comp_dict_by_type:
            return
        ret_val = []
        for component in self.source_comp_dict_by_type.get(rule.source_type,[]):
            if component.converted is True:
                continue
            #
            # Predicate check. If all conditions are not met,
            # the current component will be skipped
            # (and not marked as converted)
            #
            conditions_fulfilled = True
            for predicate in rule.predicates:
                if predicate.evaluate(component) is False:
                    conditions_fulfilled = False
                    break
            if conditions_fulfilled is False:
                continue
            dh = None
            parent_subsystem = None
            #
            # Creating hierarchy for the component if needed
            # (if the component is in a subsystem)
            #
            if component.parent is not None and \
                    component.parent.name in self.temp_subsystem_dict:
                parent_subsystem = \
                    self.temp_subsystem_dict[component.parent.name]
            else:
                parent_subsystem = \
                    self._create_conversion_subsystems(component.parent)

            if parent_subsystem is not None:
                parent_subsystem.position = [coord for coord in
                                             component.parent.position]
            if rule.components:
                dh = self._convert_one_to_sub(rule, component, parent_subsystem)
                if dh is None:
                    continue
            else:
                dh = self._convert_one_to_one(rule, component, parent_subsystem)


            #
            # !! Important part !!
            #
            # Adds the DataHolder of this component to
            # the conversion_dict if it is found on the root level
            #
            if parent_subsystem is None:
                if dh.typhoon_type not in self.conversion_dict:
                    self.conversion_dict[dh.typhoon_type] = [dh]
                else:
                    self.conversion_dict[dh.typhoon_type].append(dh)
                ret_val.append(dh)
            #
            # If the component is not on the root level,
            # the parent subsystem's component dict will be
            # updated with the newly converted component, and
            # since the parent subsystem has already been added
            # to the conversion dict no other action is required
            #
            else:
                if dh.typhoon_type not in parent_subsystem.components:
                    parent_subsystem.components[dh.typhoon_type] = [dh]
                else:
                    parent_subsystem.components[dh.typhoon_type].append(dh)
        if ret_val:
            return ret_val

    def _find_pattern(self, rule):
        """
        This method finds the pattern (collection of components
        which are interconnected) by retrieving lists of candidate
        components and iterating through the connections list of the
        pattern to check if the candidate components are linked in the
        specified way.

        If a pattern is found, the components are marked as converted.

        Args:
            rule (Rule): Rule object with the candidate types
                         and their connections

        Returns:
            SubsystemDataHolder
        """
        pattern = self.patterns.get(rule.source_type)
        pattern_candidates = \
            {handle: self.source_comp_dict_by_type.get(comp_type, [])
             for handle, comp_type in pattern.components.items()}
        matched = {}
        for connection in pattern.connections:
            #
            # Connection start elements
            #
            if connection.start_handle in matched:
                start_collection = \
                    [matched[connection.start_handle].parent_component]
            else:
                start_collection = \
                    pattern_candidates.get(connection.start_handle, [])
            #
            # Connection end elements
            #
            if connection.end_handle in matched:
                end_collection = \
                    [matched[connection.end_handle].parent_component]
            else:
                end_collection = \
                    pattern_candidates.get(connection.end_handle, [])

            #
            # Returns a dictionary with the start
            # and end handles and their terminals,
            # or an empty dictionary if nothing was
            # matched
            #
            matched_terminals = self._pattern_match(start_collection,
                                                    end_collection,
                                                    connection)
            #
            # If connected terminals were found,
            # adding the entries to the matched dictionary
            #
            if matched_terminals:
                matched.update(matched_terminals)
            #
            # If any part of the pattern connection
            # was not found, returning None
            #
            else:
                return None

        # Checking if the number of matched
        # terminals is the same as the number
        # of components defined in the pattern rule
        if len(matched) == len(pattern.components):
            for terminal in matched.values():
                terminal.parent_component.converted = True
            # Converting the matched terminals' parents
            return self._convert_pattern(matched, rule)
        else:
            return None

    def _convert_one_to_one(self, rule, component, parent_subsystem=None):
        """
        Converts a component into a single DataHolder,
        sets its properties and maps its terminals.

        Args:
            rule (Rule): Rule object which defines the conversion
            component (Component): Component object created from the netlist
            parent_subsystem (Subsystem): parent subsystem of the component

        Returns:
            dh (DataHolder)
        """
        #
        # DataHolder objects are POPO objects which
        # will be used when calling the TyphoonHIL API
        # to create components and set their properties
        #
        dh = DataHolder()
        dh.typhoon_type = rule.typhoon_type
        dh.source_type = rule.source_type
        dh.name = component.name
        dh.orientation = component.orientation
        dh.position = [i * 2 for i in component.position]

        if parent_subsystem is not None:
            dh.parent = parent_subsystem

        # Setting properties
        for prop in rule.properties:
            # Property is a reference to a component property
            if prop.prop_type == "ref":
                if prop.value in component.properties:
                    dh.properties[prop.name] = \
                        component.properties[prop.value]
                else:
                    logging.warning(f"[1:1 - {rule.source_type} "
                                    f"({component.name}) -> "
                                    f"{rule.typhoon_type}] Missing property"
                                    f" \"{prop.value}\" in "
                                    f"source component, unable to set "
                                    f"\"{prop.name}\".")
            # Property is a String or number
            elif prop.prop_type in {"str", "num"}:
                dh.properties[prop.name] = prop.value
            # Property is the return value of a function call
            else:
                params = {}
                call_func = True
                for name, value in prop.params.items():
                    if value.isdigit():
                        params[name] = float(value)
                    elif "\"" == value[0] and "\"" == value[-1] or \
                            "'" == value[0] and "'" == value[-1]:
                        params[name] = value
                    else:
                        if value in component.properties:
                            params[name] = component.properties[value]
                        else:
                            logging.warning(f"[1:1 - {rule.source_type} "
                                            f"({component.name}) -> "
                                            f"{rule.typhoon_type}] Missing"
                                            f" property \"{value}\" for "
                                            f"function call "
                                            f"\"{prop.value}\" - kwarg "
                                            f"\"{name}\", unable to set "
                                            f"\"{prop.name}\".")
                            call_func = False
                if call_func:
                    dh.properties[prop.name] = \
                        getattr(self.user_lib, prop.value)(**params)

        for i, items in enumerate(rule.terminals.items()):
            key = items[0][1]
            values = items[1]
            terminal_obj = Terminal()
            try:
                orig_terminal = component.terminals[key]
            except KeyError:
                logging.warning(f"[1:1 - {rule.source_type} "
                                f"({component.name}) -> "
                                f"{rule.typhoon_type}] Terminal mapping #{i} is"
                                f" incorrect, missing terminal \"{key}\" in the"
                                f" source component.")
                continue
            terminal_obj.node_id = orig_terminal.node_id
            terminal_obj.index = orig_terminal.index
            terminal_obj.kind = values[0]
            terminal_obj.name = values[2]
            terminal_obj.position = [i * 2 for i in orig_terminal.position]
            terminal_obj.parent_component = dh
            dh.terminals.append(terminal_obj)

        component.converted = True
        return dh

    def _convert_sub_to_sub(self, matched_terminals, rule):
        """
        Converts a matched pattern into a Subsystem.
        Args:
            matched_terminals (dict): passed by the _find_pattern method
            rule (Rule): Rule object which defines the conversion

        Returns:
            sub (SubsystemDataHolder)
        """
        sub = SubsystemDataHolder()
        components = {}
        # Initial position
        init_position = [50, 50]

        name = "|"
        #
        # Concatenating each component's
        # name with the initial name of this new Subsystem
        #
        for match in matched_terminals.values():
            name += match.parent_component.name+"|"

        sub.name = name

        for handle, child_comp_rule in rule.components.items():
            dh = DataHolder()
            dh.typhoon_type = child_comp_rule.typhoon_type
            dh.source_type = ""
            dh.name = handle
            dh.orientation = "up"
            dh.position = [i * 2 for i in init_position]
            init_position = dh.position

            dh.parent = sub
            #
            # Setting properties
            #
            for prop in child_comp_rule.properties:
                # Property is a reference to a component property
                if prop.prop_type == "ref":
                    prop_value_split = prop.value.split(".")
                    comp_handle = None
                    comp_prop = None
                    component = None
                    if len(prop_value_split) == 2:
                        comp_handle, comp_prop = prop_value_split
                        if comp_handle not in matched_terminals:
                            logging.warning(f"[N:M - {rule.source_type} -> "
                                            f"core/Subsystem] Error in "
                                            f"property mapping "
                                            f"\"{prop.name}\", the entered "
                                            f"pattern component handle "
                                            f"\"{comp_handle}\" is "
                                            f"not present in the pattern. "
                                            f"Unable to set it to the "
                                            f"value of the pattern "
                                            f"component's property.")
                            continue
                        component = \
                            matched_terminals[comp_handle].parent_component
                    else:
                        logging.warning(f"[N:M - {rule.source_type} -> "
                                        f"core/Subsystem] Error in property"
                                        f" mapping \"{prop.name}\", missing"
                                        f" pattern component handle. "
                                        f"Unable to set it to the value of "
                                        f"the pattern component's "
                                        f"property.")
                        continue
                    if comp_prop in component.properties:
                        dh.properties[prop.name] = \
                            component.properties[comp_prop]
                    else:
                        logging.warning(f"[N:M - {rule.source_type} "
                                        f" -> core/Subsystem] Missing "
                                        f"property \"{comp_prop}\" in "
                                        f"source component "
                                        f"\"{component.type}\", unable to"
                                        f" set \"{prop.name}\".")
                # Property is a String or number
                elif prop.prop_type in {"str", "num"}:
                    dh.properties[prop.name] = prop.value
                # Property is the return value of a function call
                else:
                    params = {}
                    call_func = True
                    for name, value in prop.params.items():
                        if not call_func:
                            break
                        # Arg is digit
                        if value.isdigit():
                            params[name] = float(value)
                        # Arg is string
                        elif "\"" == value[0] and "\"" == value[-1] or \
                                "'" == value[0] and "'" == value[-1]:
                            params[name] = value
                        # Arg is reference to component value
                        else:
                            arg_value_split = value.split(".")
                            comp_handle = None
                            comp_prop = None
                            component = None
                            if len(arg_value_split) == 2:
                                comp_handle, comp_prop = arg_value_split
                                if comp_handle not in matched_terminals:
                                    logging.warning(f"[N:M - "
                                                    f"{rule.source_type} ->"
                                                    f" core/Subsystem] "
                                                    f"Error in property "
                                                    f"mapping "
                                                    f"\"{prop.name}\", the "
                                                    f"entered pattern "
                                                    f"component handle "
                                                    f"\"{comp_handle}\" is "
                                                    f"not present in the "
                                                    f"pattern. Unable to "
                                                    f"set its property "
                                                    f"\"{comp_prop}\" as "
                                                    f"the kwarg "
                                                    f"\"{name}\".")
                                    call_func = False
                                    continue
                                component = \
                                    matched_terminals[
                                        comp_handle].parent_component
                            else:
                                logging.warning(
                                    f"[N:M - {rule.source_type} -> "
                                    f"core/Subsystem] Error in property"
                                    f" mapping \"{prop.name}\", missing"
                                    f" pattern component handle. "
                                    f"Unable to set it to the value of "
                                    f"the pattern component's "
                                    f"property.")
                                call_func = False
                                continue
                            if comp_prop in component.properties:
                                params[name] = \
                                    component.properties[comp_prop]
                            else:
                                logging.warning(f"[N:M - "
                                                f"{rule.source_type} ->"
                                                f" core/Subsystem] "
                                                f"Error in property "
                                                f"mapping "
                                                f"\"{prop.name}\", the "
                                                f"property \"{comp_prop}\""
                                                f"was not found in the "
                                                f"component "
                                                f"\"{component.name}\" - "
                                                f"handle \"{comp_handle}\"."
                                                f"Unable to set it as "
                                                f"the kwarg "
                                                f"\"{name}\".")
                                call_func = False
                    if call_func:
                        dh.properties[prop.name] = \
                            getattr(self.user_lib, prop.value)(**params)
            # DataHolders are to be added to lists
            # since the parent is a SubsystemDataHolder,
            # and its components will be iterated through
            # upon creation via API
            components[handle] = [dh]
        sub.components = components
        sub.connections = rule.connections
        try:
            for i, items in enumerate(rule.ports.items()):
                component = matched_terminals[items[0][0]].parent_component
                key = items[0][1]
                values = items[1]
                node_id = component.terminals[key].node_id
                port = Port()
                port.node_id = node_id
                port.kind = values[0]
                port.parent_component = values[1]
                port.name = values[2]

                sub.ports.append(port)
        except KeyError:
            logging.warning(
                f"[N:M - {rule.source_type} ({component.name}) -> "
                f"core/Subsystem] Port mapping #{i} is incorrect, "
                f"missing terminal with the ID \"{key}\" in the "
                f"source component.")
            return None


        # sub.parent = parent_subsystem

        self.conversion_dict["Subsystem"].append(sub)
        return sub

    def _convert_sub_to_one(self, matched_terminals, rule):
        """
        Converts a matched pattern into a single DataHolder.

        Args:
            matched_terminals (dict): passed by the _find_pattern method
            rule (Rule): Rule object which defines the conversion

        Returns:
            dh (DataHolder)
        """
        dh = DataHolder()
        dh.source_type = rule.source_type
        dh.typhoon_type = rule.typhoon_type
        name = "|"
        position = [0, 0]
        for term in matched_terminals.values():
            name += term.parent_component.name + "|"
            position[0] += term.parent_component.position[0] * 2
            position[1] += term.parent_component.position[1] * 2
        position[0] = int(position[0] / len(matched_terminals))
        position[1] = int(position[1] / len(matched_terminals))

        dh.position = position
        dh.name = name

        for prop in rule.properties:
            if prop.prop_type == "ref":
                # User defined handle in the pattern.
                comp_ref = prop.value[0]
                # Property name of the matched component
                comp_prop_name = prop.value[1]
                component = matched_terminals(comp_ref, None)
                if component is None:
                    logging.warning(f"[N:1 - {rule.source_type} -> "
                                    f"{rule.typhoon_type}] Error in property "
                                    f"mapping \"{prop.name}\", "
                                    f"\"{comp_ref}\" handle was not found "
                                    f"in the defined pattern.")
                    continue

                component_property = \
                    component.properties.get(comp_prop_name, None)
                if component_property is None:
                    logging.warning(f"[N:1 - {rule.source_type} -> "
                                    f"{rule.typhoon_type}] Error in property "
                                    f"mapping \"{prop.name}\", "
                                    f"\"{comp_prop_name}\" property was not "
                                    f"found in the pattern matched "
                                    f"\"{comp_ref}\" component.")
                    continue
                dh.properties[prop.name] = component_property
            elif prop.prop_type in {"str", "num"}:
                dh.properties[prop.name] = prop.value
            else:
                # Function value
                func_name = prop.value
                func_params = {arg: matched_terminals[handle].parent_component
                               for arg, handle in prop.params.items()}
                func_ret_val = \
                    getattr(self.user_lib, func_name)(**func_params)
                dh.properties[prop.name] = func_ret_val

            for term_name, term_props in rule.terminals.items():
                orig_terminal = matched_terminals.get(term_props[1], None)
                if orig_terminal is None:
                    logging.warning(f"[N:1 - {rule.source_type} -> "
                                    f"{rule.typhoon_type}] Error in terminal "
                                    f"mapping, \"{term_props[1]}\" terminal "
                                    f"was not found.")

                    continue
                terminal_obj = Terminal()
                terminal_obj.node_id = \
                    orig_terminal.parent_component.terminals[
                        term_name[1]].node_id
                terminal_obj.index = orig_terminal.index
                terminal_obj.kind = term_props[0]
                terminal_obj.name = term_props[2]
                terminal_obj.position = [i * 2 for i in
                                         orig_terminal.position]
                dh.terminals.append(terminal_obj)

        if dh.typhoon_type not in self.conversion_dict:
            self.conversion_dict[dh.typhoon_type] = []

        self.conversion_dict[dh.typhoon_type].append(dh)

        return dh

    def _convert_pattern(self, matched_terminals, rule):
        #
        # Subsystem pattern
        #
        if len(rule.components) > 0:
            return self._convert_sub_to_sub(matched_terminals, rule)
        #
        # N:1 conversion
        #
        else:
            return self._convert_sub_to_one(matched_terminals, rule)


    def convert(self):
        """
        Converts all components in the netlist.

        Returns:
            converted_components (list): list of (Subsystem)DataHolders
        """
        converted_components = []
        for rule in self.match_rules:
            if rule.pattern_match is True:
                components = []
                component = self._find_pattern(rule)
                while component:
                    components.append(component)
                    component = self._find_pattern(rule)
                if components:
                    converted_components.append(components)
            elif rule.pattern_match is False:
                component = self._convert_one_to_n(rule)
                if component is not None:
                    converted_components.append(component)
        return converted_components

    def convert_schema(self, device_id, config_id, compile_model=False):
        self.report_path = None
        self.save_path = None
        self.converted = self.convert()
        self.save_schematic(device_id,
                            config_id,
                            compile_model)

        report_path = self.generate_report()
        return self.save_path, self.compiled, report_path

    def generate_report(self):
        """
        Generates a conversion report file at the source file location.
        """
        input_components = self.source_comp_dict_by_type.values()
        converted = []
        unconverted = []
        for component_list in input_components:
            for component in component_list:
                # Not reporting subsystem conversion
                if isinstance(component, Subsystem):
                    break
                whitespace = 20 - len(component.name)
                if whitespace < 0:
                    whitespace = 0
                component.whitespace = whitespace
                if component.converted:
                    converted.append(component)
                else:
                    unconverted.append(component)
        template_path = os.path.join(get_root_path(),
                                     "converter",
                                     "app",
                                     "resources",
                                     "report_template.txt")
        with open(template_path) as file_:
            template = Template(file_.read())

        save_path = self.input_file_path.split(os.path.sep)
        save_path[-1] = "report.txt"
        save_path[0] += os.path.sep
        save_path = os.path.join(*save_path)
        converted.sort(key=lambda x: x.type)
        unconverted.sort(key=lambda x: x.type)
        count = len(converted) + len(unconverted)
        with open(save_path, "w") as report_file:
            report_file.write(
                template.render(path_to_source=self.input_file_path,
                                source_component_count=count,
                                successful_conversions=converted,
                                unsuccessful_conversions=unconverted,
                                save_path=self.save_path))

        return save_path
