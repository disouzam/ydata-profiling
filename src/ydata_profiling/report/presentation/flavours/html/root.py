from ydata_profiling.report.presentation.core.root import Root
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLRoot(Root):
    def render(self, **kwargs) -> str:
        """
    Renders an HTML report by populating a template with content and navigation items.

    This method extracts navigation items from the 'body' of the content, which includes
    section names and their corresponding anchor IDs. It then uses these items along with
    other content provided in the instance and any additional keyword arguments to render
    the specified template.

    Args:
        **kwargs: Additional keyword arguments that will be passed to the template.

    Returns:
        str: The rendered HTML report as a string.
    """
    nav_items = [
        (section.name, section.anchor_id)
        for section in self.content["body"].content["items"]
    ]

    return templates.template("report.html").render(
        **self.content, nav_items=nav_items, **kwargs
    )"""
        nav_items = [
            (section.name, section.anchor_id)
            for section in self.content["body"].content["items"]
        ]

        return templates.template("report.html").render(
            **self.content, nav_items=nav_items, **kwargs
        )
