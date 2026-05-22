from settings import GUI_SCALE


class Cell:
    def __init__(self, nodes, cell_type):
        # cell is initialized by four nodes and a cell type
        # nodes will be a list of lists [[x,y],[x,y],...,...]
        # For now, type will be fuel (yellow), or water (blue)
        # Additional properties will be assigned to the cell based on its type
        self.nodes = nodes
        self.cell_type = cell_type
        if cell_type == "Fuel":
            self.color = "yellow"
        elif cell_type == "Moderator":
            self.color = "blue"
        elif cell_type == "ControlRod":
            self.color = "black"

    def draw(self, canvas):
        x0, y0, x1, y1 = (
            self.nodes[0][0] * GUI_SCALE,
            self.nodes[0][1] * GUI_SCALE,
            self.nodes[3][0] * GUI_SCALE,
            self.nodes[3][1] * GUI_SCALE,
        )
        canvas.create_rectangle(x0, y0, x1, y1, fill=self.color, outline="")
