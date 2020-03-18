
class Pattern:
    """
    This class is used for N:M conversions.
    """

    def __init__(self, name=""):
        """
        Patterns are described by the components which make up the pattern
        and the connections between those components.
        """
        #
        # Pattern name is used in the conversion rules
        #
        # Example: *Boost => Boost
        #          pattern name => Typhoon component type
        self.name = name.strip()

        # Components dict holds the type names of the
        # components which will be converted, under a
        # key which the user defines. This key is to be
        # used later on in the conversion to reference
        # exactly that one component which is being
        # consumed for this pattern conversion.

        # Example:
        # {"M":"MOSFET",
        #  "D":"DIODE"}
        self.components = {}

        # Connections list holds the connections
        # between components which must exist in order
        # for the components to be matched with this pattern
        self.connections = []

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()


class Rule:
    """
    This class defines the conversion rules.
    """
    def __init__(self,
                 source_type: str = "",
                 typhoon_type: str = "",
                 pattern_match: bool = False):
        self.source_type = source_type.strip()
        self.typhoon_type = typhoon_type.strip()
        self.pattern_match = pattern_match
        self.properties = []

        # components = {"handle":{"type":"type_name1".
        #                           "properties":["name":"value"],
        #                           "}
        #              "connections":[{"start_handle":"terminal", "end_handle":"terminal"},
        #                             {"start_handle":"terminal", "end_handle":"terminal"}],
        #              "ports":}
        self.components = {}
        self.connections = []
        self.ports = {}
        self.terminals = {}
        self.predicates = []

    def __str__(self):
        return f"{self.source_type} -> {self.typhoon_type}"

    def __repr__(self):
        return self.__str__()


class Connection:
    """
    This class is used to describe the connections
    between components in pattern matches
    """

    def __init__(self,
                 start_handle: str,
                 start_terminal: str,
                 end_handle: str,
                 end_terminal: str):
        """
        Connection objects contain start and end terminals,
        described by dicts. The keys are the user defined
        names of component types in the pattern, and the values
        are terminal keys of the matched component objects.

        If both start and end terminals are in the same node,
        the parent components of these terminals are matched
        to the pattern.

        Args:
            start_handle (str): handle of the component -
                                the user defined name of
                                the component type
                                defined in the pattern

            start_terminal (str): actual terminal key of
                                  the component object's
                                  terminal

            end_handle (str): handle of the component -
                              the user defined name of
                              the component type defined
                              in the pattern

            end_terminal (str): actual terminal key of
                                the component object's terminal
        """
        self.start_handle = start_handle
        self.start_terminal = start_terminal
        self.end_handle = end_handle
        self.end_terminal = end_terminal

    def __str__(self):
        return f"{self.start_handle}:{self.start_terminal} -> " \
               f"{self.end_handle}:{self.end_terminal}"

    def __repr__(self):
        return self.__str__()


class Property:
    """
    This class is used for describing properties within conversion rules.

    These are the valid use cases:
        1.) The property is a string value
        2.) The property is a numeric value
        3.) The property is a reference to another Component's property
        4.) The property is the return value of a user defined function
    """
    def __init__(self, prop_type="str", name="", value=None):
        """
        Args:
            type (str): type of the property - str/float/ref/func
            name (str): name of the property of the Typhoon component
            value: value of the property - either a string or a float
        """
        self.name = name.strip()
        self.prop_type = prop_type
        self.value = value
        self.params = {}

    def __str__(self):
        return f"{self.name} ({self.prop_type}) = {self.value} ({self.params})"

    def __repr__(self):
        return self.__str__()


class Predicate:
    """
    This class is used to describe additional conditions
    of component conversion, and is instantiated when
    a conversion rule is annotated in the rule file.

    A comparison of the component's property (property_name)
    is done with the condition value, via the operator
    (greater, lesser, equal, and their combinations).
    """
    def __init__(self,
                 property_name: str,
                 operator: str,
                 condition_value: (str, float, int)):
        self.property_name = property_name.strip()
        condition_value = condition_value.strip()
        if operator == ">":
            self.operator = "gt"
        elif operator == "<":
            self.operator = "lt"
        elif operator == "==":
            self.operator = "eq"
        elif operator == ">=":
            self.operator = "gteq"
        elif operator == "<=":
            self.operator = "lteq"
        else:
            raise Exception("Predicate operators must be "
                            "either >, <, ==, >= or <= .")
        try:
            self.condition_value = float(condition_value)
        except ValueError:
            if self.operator == "eq":
                self.condition_value = condition_value.strip("\"")
            else:
                raise Exception("Predicate operator must be '==' "
                                "for correct string comparison.")


    def evaluate(self, component):
        if component is None:
            raise Exception("Cannot evaluate predicate on None type object.")
        component_property_value = component.properties.get(self.property_name,
                                                            None)
        if component_property_value is None:
            return False
        try:
            if self.operator == "gt":
                return component_property_value > self.condition_value
            elif self.operator == "lt":
                return component_property_value < self.condition_value
            elif self.operator == "eq":
                return component_property_value == self.condition_value
            elif self.operator == "gteq":
                return component_property_value >= self.condition_value
            elif self.operator == "ltgt":
                return component_property_value <= self.condition_value
        except TypeError as e:
            return False

