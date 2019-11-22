
class Component:

    def __init__(self):
        self.properties = {}
        self.name = ""
        self.type = ""
        self.position = [0,0]
        # Dictionary which holds terminals as
        # {terminal.index:terminal}
        self.terminals = {}
        self.orientation = 0
        self.parent = None
        self.converted = False

    def __str__(self):
        return f"{self.type} - {self.name}"