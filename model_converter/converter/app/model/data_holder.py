
class DataHolder:
    """
    DataHolder objects are POPO (Plain Ol' Python Object) objects which
    will be used when calling the TyphoonHIL API
    to create components and set their properties
    """

    def __init__(self):
        self.typhoon_type = ""
        self.source_type = ""
        self.orientation = "up"
        self.name = ""
        self.properties = {}
        self.terminals = []
        self.variable = None
        self.position = []
        self.parent = None

    def __str__(self):
        return f"{self.typhoon_type}: {self.name}"

class SubsystemDataHolder:
    """
    SubsystemDataHolder objects are POPO (Plain Ol' Python Object)
    objects which will be used when calling the TyphoonHIL API
    to create components and set their properties.

    These differ from regular DataHolders by having child components,
    a connections list which defines the connections between
    child components and a list of ports (Port objects).
    """
    def __init__(self):
        self.components = {}
        self.connections = []
        self.ports = []
        self.name = ""
        self.typhoon_type = "core/Empty Subsystem"
        self.position = [50, 50]
        self.parent = None
        self.orientation = "up"