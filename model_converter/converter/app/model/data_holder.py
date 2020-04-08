
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
        self.comp_grid_dimensions = [[None, None], [None, None]]
        
    def calculate_grid_dimensions(self):
        """
        Iterating through the components and stretching
        the grid depending on their positions.

        Returns:
            None
        """

        for components_list_by_type in self.components.values():
            for component in components_list_by_type:
                grid_x_min = self.comp_grid_dimensions[0][0]
                grid_x_max = self.comp_grid_dimensions[0][1]
                grid_y_min = self.comp_grid_dimensions[1][0]
                grid_y_max = self.comp_grid_dimensions[1][0]
                if grid_x_min is None or component.position[0] < grid_x_min:
                    # New grid X min
                    self.comp_grid_dimensions[0][0] = component.position[0]
                if grid_x_max is None or component.position[0] > grid_x_max:
                    # New grid X max
                    self.comp_grid_dimensions[0][1] = component.position[0]
                if grid_y_min is None or component.position[1] < grid_y_min:
                    # New grid Y min
                    self.comp_grid_dimensions[1][0] = component.position[1]
                if grid_y_max is None or component.position[1] > grid_y_max:
                    # New grid Y max
                    self.comp_grid_dimensions[1][1] = component.position[1]
    
        #
        # Stretching the grid out so the ports
        # don't get placed on top of the components
        #
        self.comp_grid_dimensions[0][0] -= 100
        self.comp_grid_dimensions[0][1] += 100
        self.comp_grid_dimensions[1][0] -= 100
        self.comp_grid_dimensions[1][1] += 100

