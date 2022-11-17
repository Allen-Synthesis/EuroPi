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

    def _add_point(self, config_point):
        if config_point["name"] in self.points:
            raise ValueError(f"config point {config_point['name']} is already defined")
        self.points[config_point["name"]] = config_point

    def with_choice(self, name: str, choices: "List", default) -> "ConfigPointsBuilder":

        if default not in choices:
            raise ValueError("default value must be available in given choices")
        self._add_point({"name": name, "type": "choice", "choices": choices, "default": default})
        return self

    def with_int(
        self, name: str, stop: int, default: int, start: int = 0, step: int = 1
    ) -> "ConfigPointsBuilder":
        return self.with_choice(name=name, choices=list(range(start, stop, step)), default=default)

    def build(self) -> ConfigPoints:
        return ConfigPoints(self.points)
