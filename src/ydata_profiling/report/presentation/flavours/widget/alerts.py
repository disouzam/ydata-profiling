from typing import List

from ipywidgets import HTML, Button, widgets

from ydata_profiling.report.presentation.core import Alerts
from ydata_profiling.report.presentation.flavours.html import templates
from ydata_profiling.utils.styles import get_alert_styles


def get_row(items: List[widgets.Widget]) -> widgets.GridBox:
    """
    Create a grid layout containing a row of widgets.

    This function takes a list of Jupyter widgets and arranges them in a
    single-row grid layout, with specified column widths.

    Parameters:
        items (List[widgets.Widget]): A list of Jupyter widget objects to be
        displayed in the grid.

    Returns:
        widgets.GridBox: A GridBox containing the provided widgets arranged
        in a single row with a layout that has two columns, where the first
        column takes up 75% of the width and the second column takes up 25%.
    """
    layout = widgets.Layout(width="100%", grid_template_columns="75% 25%")
    return widgets.GridBox(items, layout=layout)


class WidgetAlerts(Alerts):
    def render(self) -> widgets.GridBox:
        """
    Renders a grid of alert items based on the provided alert content.

    The function iterates over alerts in the content dictionary, skipping any alerts 
    that are of type "rejected". For each alert, it generates an HTML representation 
    using the corresponding template and creates a disabled button with an appropriate 
    style based on the alert type.

    Returns:
        widgets.GridBox: A grid box containing the rendered alert items and 
        associated buttons.

    Raises:
        KeyError: If the alert type does not have a corresponding style.
    """
    styles = get_alert_styles()

    items = []
    for alert in self.content["alerts"]:
        type_name = alert.alert_type.name.lower()
        if type_name == "rejected":
            continue

        items.append(
            HTML(
                templates.template(f"alerts/alert_{type_name}.html").render(
                    alert=alert
                )
            )
        )

        style_name = styles[type_name]
        if style_name not in ("primary", "success", "info", "warning", "danger"):
            style_name = ""

        items.append(
            Button(
                description=type_name.replace("_", " ").capitalize(),
                button_style=style_name,
                disabled=True,
            )
        )

    return get_row(items)"""
        styles = get_alert_styles()

        items = []
        for alert in self.content["alerts"]:
            type_name = alert.alert_type.name.lower()
            if type_name == "rejected":
                continue

            items.append(
                HTML(
                    templates.template(f"alerts/alert_{type_name}.html").render(
                        alert=alert
                    )
                )
            )

            style_name = styles[type_name]
            if style_name not in ("primary", "success", "info", "warning", "danger"):
                style_name = ""

            items.append(
                Button(
                    description=type_name.replace("_", " ").capitalize(),
                    button_style=style_name,
                    disabled=True,
                )
            )

        return get_row(items)
