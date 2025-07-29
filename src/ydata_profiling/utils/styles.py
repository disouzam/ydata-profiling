def get_alert_styles() -> dict:
    """
    Retrieve a dictionary mapping alert categories to their respective styles.

    This function returns a dictionary where keys represent different alert categories
    related to data analysis and model evaluation, and the associated values represent 
    the corresponding alert styles. The styles can be utilized in a user interface
    to convey the severity or importance of each category.

    Returns:
        dict: A dictionary with alert categories as keys and their associated styles 
              as values. The styles are typically used for visual representation in alert 
              messages.

    Example:
        {
            "constant": "warning",
            "duplicate": "secondary",
            "missing": "info",
            ...
        }
    """
    return {
        "constant": "warning",
        "constant_length": "primary",
        "duplicates": "secondary",
        "empty": "info",
        "high_cardinality": "danger",
        "high_correlation": "secondary",
        "infinite": "info",
        "imbalance": "primary",
        "missing": "info",
        "non_stationary": "secondary",
        "rejected": "danger",
        "seasonal": "secondary",
        "skewed": "info",
        "truncated": "info",
        "type_date": "warning",
        "uniform": "danger",
        "unique": "danger",
        "unsupported": "warning",
        "zeros": "info",
    }
