from ipywidgets import widgets

from ydata_profiling.report.presentation.core import Dropdown


class WidgetDropdown(Dropdown):
    def render(self) -> widgets.VBox:
        """
    Renders a VBox widget containing a Dropdown and the corresponding item view.

    The Dropdown is populated with items from the `self.content` dictionary, which
    includes a list of options and a description. When the selected value of the 
    Dropdown changes, a callback function updates the selected index of the item view.
    
    The function checks if there are any items to display. If items are present, it 
    returns a VBox containing both the Dropdown and the item view. If no items are 
    available, it returns a VBox with just the Dropdown.

    Returns:
        widgets.VBox: A VBox widget containing the Dropdown and item view, or just 
        the Dropdown if no items are present.
    """
        dropdown = widgets.Dropdown(
            options=self.content["items"], description=self.content["name"]
        )
        titles = []
        item = self.content["item"].content["items"]
        for i in item:
            titles.append(i.name)
        item = self.content["item"].render()

        def change_view(widg: dict) -> None:
            if dropdown.value == "":
                item.selected_index = None
            else:
                for i in range(len(titles)):
                    if titles[i] == dropdown.value:
                        item.selected_index = i
                        break

        dropdown.observe(change_view, names=["value"])

        if self.content["item"] is not None:
            return widgets.VBox([dropdown, item])
        else:
            return widgets.Vbox([dropdown])
