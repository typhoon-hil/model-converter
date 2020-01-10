
class Subsystem:

    def __init__(self):
        self.name = ""
        self.position = [0,0]
        self.orientation = 0
        self.terminals = []
        self.properties = {}
        #
        # Dictionary which holds all components and subsystems
        #
        # {"component type":[component1, component2, ...]}
        # {"subsystem":{"component type":[component3, component4, ...]}
        #
        self.component_dict = {}
        self.parent = None

    def __str__(self):
        return self.name