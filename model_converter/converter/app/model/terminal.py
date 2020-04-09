from model_converter.converter.app.model.component import Component


class Terminal:

    def __init__(self, position:list=None, node_id:int=None,
                 index:(int,str)=None, parent_component:Component=None,
                 name:str=None, kind:str="pe", direction:str="in",
                 side:str="left"):
        self.position = position
        self.node_id = node_id
        self.direction = direction
        self.index = index
        self.parent_component = parent_component
        self.kind = kind
        self.name = name
        self.side = side

    def clone(self):
        terminal = Terminal()
        terminal.name = self.name
        terminal.kind = self.kind
        terminal.parent_component = self.parent_component
        terminal.node_id = self.node_id
        terminal.position = [coord for coord in self.position]
        terminal.direction = self.direction
        terminal.index = self.index
        terminal.side = self.side
        return terminal

    def copy_from(self, other: "Terminal"):
        self.name = other.name
        self.kind = other.kind
        self.node_id = other.node_id
        self.index = other.index
        self.direction = other.direction
        self.position = [coord for coord in other.position]
        self.parent_component = other.parent_component
        self.side = other.side


class Port(Terminal):
    pass
