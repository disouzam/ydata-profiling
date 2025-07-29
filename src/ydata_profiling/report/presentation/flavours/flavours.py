from typing import Callable, Dict, Type

from ydata_profiling.report.presentation.core import Root
from ydata_profiling.report.presentation.core.renderable import Renderable


def apply_renderable_mapping(
    mapping: Dict[Type[Renderable], Type[Renderable]],
    structure: Renderable,
    flavour: Callable,
) -> None:
    """```python
def apply_renderable_mapping(
    mapping: Dict[Type[Renderable], Type[Renderable]],
    structure: Renderable,
    flavour: Callable,
) -> None:
    """
    Applies a mapping of Renderable types to convert a given Renderable structure 
    using a specified flavour function.

    This function retrieves the appropriate conversion class from the mapping 
    based on the type of the provided structure and calls the convert_to_class 
    method to perform the conversion.

    Args:
        mapping (Dict[Type[Renderable], Type[Renderable]]): A dictionary where keys 
            are types of Renderable and values are the corresponding conversion 
            classes.
        structure (Renderable): An instance of a Renderable that needs to be converted.
        flavour (Callable): A function that provides additional processing or 
            configuration for the conversion.

    Returns:
        None: This function modifies the structure in place and does not return 
        any value.
    """
    mapping[type(structure)].convert_to_class(structure, flavour)


def get_html_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]:
    """Workaround variable type annotations not being supported in Python 3.5

    Returns:
        type annotated mapping dict
    """
    from ydata_profiling.report.presentation.core import (
        HTML,
        Alerts,
        Collapse,
        Container,
        CorrelationTable,
        Dropdown,
        Duplicate,
        FrequencyTable,
        FrequencyTableSmall,
        Image,
        Root,
        Sample,
        Table,
        ToggleButton,
        Variable,
        VariableInfo,
    )
    from ydata_profiling.report.presentation.flavours.html import (
        HTMLHTML,
        HTMLAlerts,
        HTMLCollapse,
        HTMLContainer,
        HTMLCorrelationTable,
        HTMLDropdown,
        HTMLDuplicate,
        HTMLFrequencyTable,
        HTMLFrequencyTableSmall,
        HTMLImage,
        HTMLRoot,
        HTMLSample,
        HTMLTable,
        HTMLToggleButton,
        HTMLVariable,
        HTMLVariableInfo,
    )

    return {
        Container: HTMLContainer,
        Variable: HTMLVariable,
        VariableInfo: HTMLVariableInfo,
        Table: HTMLTable,
        HTML: HTMLHTML,
        Root: HTMLRoot,
        Image: HTMLImage,
        FrequencyTable: HTMLFrequencyTable,
        FrequencyTableSmall: HTMLFrequencyTableSmall,
        Alerts: HTMLAlerts,
        Duplicate: HTMLDuplicate,
        Dropdown: HTMLDropdown,
        Sample: HTMLSample,
        ToggleButton: HTMLToggleButton,
        Collapse: HTMLCollapse,
        CorrelationTable: HTMLCorrelationTable,
    }


def HTMLReport(structure: Root) -> Root:
    """Adds HTML flavour to Renderable

    Args:
        structure:

    Returns:

    """
    mapping = get_html_renderable_mapping()
    apply_renderable_mapping(mapping, structure, flavour=HTMLReport)
    return structure


def get_widget_renderable_mapping() -> Dict[Type[Renderable], Type[Renderable]]:
    """
    Generates a mapping between renderable components and their corresponding widget classes.

    This function returns a dictionary where the keys are types of renderable components
    defined in the ydata_profiling.report.presentation.core module and the values are 
    corresponding widget classes from the ydata_profiling.report.presentation.flavours.widget module.

    Returns:
        Dict[Type[Renderable], Type[Renderable]]: A dictionary mapping renderable component types 
        to their respective widget types. The mapping includes various components such as
        Container, Variable, Table, Alerts, Dropdown, and others, each linked to its widget equivalent.

    Example:
        mapping = get_widget_renderable_mapping()
        widget = mapping[Container]

    This function is useful in the context of generating visual representations of the profiling report's 
    components.
    """
    from ydata_profiling.report.presentation.core import (
        HTML,
        Alerts,
        Collapse,
        Container,
        CorrelationTable,
        Dropdown,
        Duplicate,
        FrequencyTable,
        FrequencyTableSmall,
        Image,
        Root,
        Sample,
        Table,
        ToggleButton,
        Variable,
        VariableInfo,
    )
    from ydata_profiling.report.presentation.flavours.widget import (
        WidgetAlerts,
        WidgetCollapse,
        WidgetContainer,
        WidgetCorrelationTable,
        WidgetDropdown,
        WidgetDuplicate,
        WidgetFrequencyTable,
        WidgetFrequencyTableSmall,
        WidgetHTML,
        WidgetImage,
        WidgetRoot,
        WidgetSample,
        WidgetTable,
        WidgetToggleButton,
        WidgetVariable,
        WidgetVariableInfo,
    )

    return {
        Container: WidgetContainer,
        Variable: WidgetVariable,
        VariableInfo: WidgetVariableInfo,
        Table: WidgetTable,
        HTML: WidgetHTML,
        Root: WidgetRoot,
        Image: WidgetImage,
        FrequencyTable: WidgetFrequencyTable,
        FrequencyTableSmall: WidgetFrequencyTableSmall,
        Alerts: WidgetAlerts,
        Duplicate: WidgetDuplicate,
        Dropdown: WidgetDropdown,
        Sample: WidgetSample,
        ToggleButton: WidgetToggleButton,
        Collapse: WidgetCollapse,
        CorrelationTable: WidgetCorrelationTable,
    }


def WidgetReport(structure: Root) -> Root:
    """
    Generates a report for a given widget structure by applying a renderable mapping.

    This function retrieves the current widget renderable mapping and applies it 
    to the provided structure, potentially modifying it to fit the desired output format.

    Parameters:
    structure (Root): The root structure representing the widget hierarchy that 
                      needs to be reported on.

    Returns:
    Root: The modified structure after applying the renderable mapping.
    """
    mapping = get_widget_renderable_mapping()
    apply_renderable_mapping(mapping, structure, flavour=WidgetReport)
    return structure"""
    mapping = get_widget_renderable_mapping()
    apply_renderable_mapping(mapping, structure, flavour=WidgetReport)
    return structure
