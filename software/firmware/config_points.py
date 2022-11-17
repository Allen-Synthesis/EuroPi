class ConfigPoints:
    def __init__(self, points) -> None:
        self.points = points

    def __len__(self):
        return len(self.points)

    def default_config(self):
        return {name: details["default"] for name, details in self.points.items()}


class ConfigPointsBuilder:
    def __init__(self) -> None:
        self.points = {}

    def with_choice(self, name: str, choices: "List", default) -> "ConfigPointsBuilder":
        self.points[name] = {"name": name, "type": "choice", "choices": choices, "default": default}
        return self

    def build(self) -> ConfigPoints:
        return ConfigPoints(self.points)
