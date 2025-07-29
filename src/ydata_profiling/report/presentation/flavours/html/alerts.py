from ydata_profiling.report.presentation.core.alerts import Alerts
from ydata_profiling.report.presentation.flavours.html import templates
from ydata_profiling.utils.styles import get_alert_styles


class HTMLAlerts(Alerts):
    def render(self) -> str:
        """```python
def render(self) -> str:
    """
    Renders the alert template with the provided content and styles.

    This method retrieves the necessary styles for the alerts and then 
    renders the HTML template using the content of the current instance. 
    The result is an HTML string representing the alerts.

    Returns:
        str: The rendered HTML string of the alerts.
    """
        styles = get_alert_styles()

        return templates.template("alerts.html").render(**self.content, styles=styles)
