import re

from ipywidgets import widgets

from ydata_profiling.config import ImageType
from ydata_profiling.report.presentation.core.image import Image


class WidgetImage(Image):
    def render(self) -> widgets.Widget:
        """
    Renders an HTML widget containing an image, with optional caption support.

    This method processes the image and its format specified in the `self.content` dictionary. 
    If the image format is SVG, it adjusts the styling to ensure the image does not exceed 
    the maximum width of its container, while also removing height attributes. 
    For other image formats, it wraps the image in an HTML `<img>` tag and includes an alt text.

    If a caption is provided in the `self.content` dictionary, it creates an HTML paragraph 
    element styled with gray color and italicized text to display below the image.

    Returns:
        widgets.Widget: An HTML widget containing the rendered image, and an optional caption 
        wrapped in a VBox if the caption is present.

    Attributes:
        self.content (dict): A dictionary containing information about the image, its format, 
        alt text, and optional caption. 
        - 'image': The source of the image.
        - 'image_format': The format of the image (e.g., SVG).
        - 'alt': Alt text for the image.
        - 'caption': Optional caption text to be displayed below the image.

    Raises:
        KeyError: If required keys are not present in the self.content dictionary.
    """
    image = self.content["image"]
    if self.content["image_format"] == ImageType.svg:
        image = image.replace("svg ", 'svg style="max-width: 100%" ')
        image = re.sub('height="[\\d]+pt"', "", image)
    else:
        alt = self.content["alt"]
        image = f'<img src="{image}" alt="{alt}" />'

    widget = widgets.HTML(image)
    if "caption" in self.content and self.content["caption"] is not None:
        caption = self.content["caption"]
        caption = widgets.HTML(f'<p style="color: #999"><em>{caption}</em></p>')
        return widgets.VBox([widget, caption])
    else:
        return widget"""
        image = self.content["image"]
        if self.content["image_format"] == ImageType.svg:
            image = image.replace("svg ", 'svg style="max-width: 100%" ')

            image = re.sub('height="[\\d]+pt"', "", image)
        else:
            alt = self.content["alt"]
            image = f'<img src="{image}" alt="{alt}" />'

        widget = widgets.HTML(image)
        if "caption" in self.content and self.content["caption"] is not None:
            caption = self.content["caption"]
            caption = widgets.HTML(f'<p style="color: #999"><em>{caption}</em></p>')
            return widgets.VBox([widget, caption])
        else:
            return widget
