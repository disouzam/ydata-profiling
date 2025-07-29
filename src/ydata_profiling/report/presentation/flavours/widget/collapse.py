from ipywidgets import Box, widgets

from ydata_profiling.report.presentation.core import Collapse


class WidgetCollapse(Collapse):
    def render(self) -> widgets.VBox:
        """
    Renders a VBox widget containing a toggle button and an associated item.

    The function checks the anchor ID of the button to determine if the 
    content should display correlation information or variable information.
    Based on this, it defines a toggle function that will manipulate the 
    display properties of the item and its children widgets depending on the 
    button's state.

    If the button's anchor ID is "toggle-correlation-description", the 
    toggle function will control the visibility of children within a grid layout 
    (50% width each) when toggled on or off. If it is any other ID, 
    it will simply show or hide the entire item based on the button state.

    The button observes changes to its value property to invoke the toggle 
    function whenever it is clicked.

    Returns:
        widgets.VBox: A VBox widget containing the toggle button and the item 
        that can be displayed or collapsed based on user interaction.
    """
        if self.content["button"].anchor_id == "toggle-correlation-description":
            collapse = "correlation"
        else:
            collapse = "variable"

        toggle = self.content["button"].render()
        item = self.content["item"].render()

        if collapse == "correlation":

            def toggle_func(widg: dict) -> None:
                if widg["new"]:
                    display = ""
                    grid = "50% 50%"
                else:
                    display = "none"
                    grid = ""

                for c in item.children:
                    if isinstance(c, Box):
                        c.children[1].layout.display = display
                    c.layout.grid_template_columns = grid

        else:

            def toggle_func(widg: dict) -> None:
                if widg["new"]:
                    display = ""
                else:
                    display = "none"
                item.layout.display = display

        toggle_func({"new": False})
        toggle.children[0].observe(toggle_func, names=["value"])

        return widgets.VBox([toggle, item])
