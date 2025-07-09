def load_stylesheet(paths: list[str]) -> str:
    styles = []
    for path in paths:
        with open(path, "r") as f:
            styles.append(f.read())
    return "\n".join(styles)


stylesheet = load_stylesheet([
    "resources/styles/hud.qss",
])