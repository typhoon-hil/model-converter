from model_converter.converter.app.model.component import Component


class Terminal:

    def __init__(self, position:list=None, node_id:int=None,
                 index:(int,str)=None, parent_component:Component=None,
                 name:str=None, kind:str="pe"):
        self.position = position
        self.node_id = node_id
        self.index = index
        self.parent_component = parent_component
        self.kind = kind
        self.name = name

    def clone(self):
        terminal = Terminal()
        terminal.name = self.name
        terminal.kind = self.kind
        terminal.parent_component = self.parent_component
        terminal.node_id = self.node_id
        terminal.position = [self.position[0],self.position[1]]
        terminal.index = self.index
        return terminal

    def copy_from(self, other: "Terminal"):
        self.name = other.name
        self.kind = other.kind
        self.node_id = other.node_id
        self.index = other.index
        self.position = [x for x in other.position]
        self.parent_component = other.parent_component


class Port(Terminal):
    pass
