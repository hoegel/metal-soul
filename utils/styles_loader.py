from PySide6.QtWidgets import QWidget
from resources.colors import (
    CHOSEN_WEAPON_COLOR,
    NOT_CHOSEN_WEAPON_COLOR,
    GOOD_HP_BAR
)


def load_stylesheet_with_variables(paths: list[str], variables: dict[str, str]) -> str:
    full_style = ""
    for path in paths:
        with open(path, "r") as f:
            template = f.read()
            styled = template.format(**variables)
            full_style += styled + "\n"
    return full_style


def get_all_styles() -> str:
    variables = {
        "CHOSEN_WEAPON_COLOR": CHOSEN_WEAPON_COLOR,
        "NOT_CHOSEN_WEAPON_COLOR": NOT_CHOSEN_WEAPON_COLOR,
        "GOOD_HP_BAR": GOOD_HP_BAR,
    }

    style_paths = [
        "resources/styles/hud.qss",
    ]

    return load_stylesheet_with_variables(style_paths, variables)


def apply_app_styles(app):
    app.setStyleSheet(get_all_styles())


def update_style_property(widget: QWidget, property_name: str, new_value: str) -> None:
    """Обновляет конкретное свойство стиля, сохраняя остальные."""
    # Получаем текущий стиль
    current_style = widget.styleSheet()
    
    # Парсим текущий стиль в словарь (свойство: значение)
    styles = {}
    for rule in current_style.split(';'):
        rule = rule.strip()
        if not rule:
            continue
        if ':' in rule:
            prop, val = rule.split(':', 1)
            styles[prop.strip()] = val.strip()

    styles[property_name] = new_value
    
    new_style = '; '.join(f"{k}: {v}" for k, v in styles.items() if v) + ';'
    widget.setStyleSheet(new_style)