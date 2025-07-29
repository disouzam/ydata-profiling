from ydata_profiling.report.presentation.core.container import Container
from ydata_profiling.report.presentation.flavours.html import templates


class HTMLContainer(Container):
    def render(self) -> str:
        """
    Renders the appropriate HTML template based on the specified sequence type.

    The method checks the value of `self.sequence_type` and renders one 
    of several predefined templates accordingly. The data required for 
    rendering these templates is retrieved from `self.content`.

    The following sequence types are supported:

    - "list": Renders the `list.html` template, using `anchor_id` and `items` from `self.content`.
    - "accordion": Renders the `list.html` template, using `anchor_id` and `items` from `self.content`.
    - "named_list": Renders the `named_list.html` template, using `anchor_id` and `items` from `self.content`.
    - "tabs": Renders the `tabs.html` template, using `tabs`, `anchor_id`, and `nested` from `self.content`.
    - "select": Renders the `select.html` template, using `tabs`, `anchor_id`, and `nested` from `self.content`.
    - "sections": Renders the `sections.html` template, using `sections` and `full_width` from `self.content`.
    - "grid": Renders the `grid.html` template, using `items` from `self.content`.
    - "batch_grid": Renders the `batch_grid.html` template, using `items`, `batch_size`, `titles`, and `subtitles` from `self.content`.

    Raises:
        ValueError: If the `sequence_type` is not recognized.

    Returns:
        str: The rendered HTML string of the template.
    """
        if self.sequence_type in ["list", "accordion"]:
            return templates.template("sequence/list.html").render(
                anchor_id=self.content["anchor_id"], items=self.content["items"]
            )
        elif self.sequence_type == "named_list":
            return templates.template("sequence/named_list.html").render(
                anchor_id=self.content["anchor_id"], items=self.content["items"]
            )
        elif self.sequence_type == "tabs":
            return templates.template("sequence/tabs.html").render(
                tabs=self.content["items"],
                anchor_id=self.content["anchor_id"],
                nested=self.content["nested"],
            )
        elif self.sequence_type == "select":
            return templates.template("sequence/select.html").render(
                tabs=self.content["items"],
                anchor_id=self.content["anchor_id"],
                nested=self.content["nested"],
            )
        elif self.sequence_type == "sections":
            return templates.template("sequence/sections.html").render(
                sections=self.content["items"],
                full_width=self.content["full_width"],
            )
        elif self.sequence_type == "grid":
            return templates.template("sequence/grid.html").render(
                items=self.content["items"]
            )
        elif self.sequence_type == "batch_grid":
            return templates.template("sequence/batch_grid.html").render(
                items=self.content["items"],
                batch_size=self.content["batch_size"],
                titles=self.content.get("titles", True),
                subtitles=self.content.get("subtitles", False),
            )
        else:
            raise ValueError("Template not understood", self.sequence_type)
