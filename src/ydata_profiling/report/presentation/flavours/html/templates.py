"""Contains all templates used for generating the HTML profile report"""
import shutil
from pathlib import Path

import jinja2

from ydata_profiling.config import Settings
from ydata_profiling.report.formatters import fmt, fmt_badge, fmt_numeric, fmt_percent

# Initializing Jinja
package_loader = jinja2.PackageLoader(
    "ydata_profiling", "report/presentation/flavours/html/templates"
)
jinja2_env = jinja2.Environment(
    lstrip_blocks=True, trim_blocks=True, loader=package_loader
)
jinja2_env.filters["is_list"] = lambda x: isinstance(x, list)
jinja2_env.filters["fmt_badge"] = fmt_badge
jinja2_env.filters["fmt_percent"] = fmt_percent
jinja2_env.filters["fmt_numeric"] = fmt_numeric
jinja2_env.filters["fmt"] = fmt


def template(template_name: str) -> jinja2.Template:
    """Get the template object given the name.

    Args:
      template_name: The name of the template file (.html)

    Returns:
      The jinja2 environment.

    """
    return jinja2_env.get_template(template_name)


def create_html_assets(config: Settings, output_file: Path) -> None:
    """
    Generate and write HTML assets to the specified output directory.

    This function creates the necessary directories and files for 
    CSS and JavaScript assets based on the provided configuration. 
    It removes any existing directory defined by the `assets_prefix` 
    in the configuration and recreates it with updated assets.

    Parameters:
        config (Settings): The configuration object containing settings 
                           for HTML assets, including the style theme 
                           and localization options.
        output_file (Path): The path to the output directory where 
                            the HTML assets will be stored.

    Returns:
        None: This function does not return a value. It directly 
              modifies the file system by creating directories and files.

    Notes:
        - If `use_local_assets` is true, the function will include 
          local theme-specific CSS and JS files based on the 
          `theme` specified in the configuration.
        - Default CSS and JS files are also included regardless 
          of the theme.
        - The generated files will be populated with rendered 
          templates, incorporating primary colors and navbar settings 
          from the configuration.
    """
    theme = config.html.style.theme

    path = output_file.with_name(str(config.html.assets_prefix))
    if path.is_dir():
        shutil.rmtree(path)

    path.joinpath("images").mkdir(parents=True, exist_ok=True)

    css = []
    js = []

    if config.html.use_local_assets:
        if theme is not None:
            css.append(f"wrapper/assets/{theme.value}.bootstrap.min.css")
        else:
            css.append("wrapper/assets/bootstrap.min.css")

        js.append("wrapper/assets/bootstrap.bundle.min.js")

    css.append("wrapper/assets/style.css")
    js.append("wrapper/assets/script.js")

    css_dir = path / "css"
    if not css_dir.exists():
        css_dir.mkdir()
        for css_file in css:
            (css_dir / Path(css_file).name).write_text(
                template(css_file).render(
                    primary_colors=config.html.style.primary_colors,
                    nav=config.html.navbar_show,
                    style=config.html.style,
                )
            )

    js_dir = path / "js"
    if not js_dir.exists():
        js_dir.mkdir()
        for js_file in js:
            (js_dir / Path(js_file).name).write_text(template(js_file).render())
