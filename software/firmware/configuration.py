"""A collection of classes and functions for dealing with configuration data. There are two main
types of configuration data: the `dict` configuration itself, and the `ConfigSpec`.

The configuration is represented by `Dict(str, Any)`, where the string key represents the config
point's name, pointing to a value that may be of any type.

The `ConfgSpec` is a collection of `ConfigPoints`. Each ConfigPoint consists of a name and description
of the valid values that it may have. There are several different types of COnfigPoints available.
"""

import os
import json
from file_utils import load_file, delete_file, load_json_file
from collections import namedtuple

Validation = namedtuple("Validation", "is_valid message")
"""A class containing configuration validation results.

    :param is_valid: True if the validation was successful, False otherwise.
    :param message: If `is_valid` is false this filed will contain a explanation message.
"""

VALID = Validation(is_valid=True, message="Valid.")
"""The default successful validation."""


class ConfigPoint:
    """Base class for defining `ConfigPoint` types.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param type: The name of this ConfigPoint's type
    :param default: The default value
    """

    def __init__(self, name: str, type: str, default):
        self.name = name
        self.type = type
        self.default = default

    def validate(self, value) -> Validation:
        """Validates the given value with this ConfigPoint. Returns a `Validation` containing the
        validation result, as well as an error message containing the reason for a validation failure.
        """
        raise NotImplementedError


class ChoiceConfigPoint(ConfigPoint):
    """A `ConfigPoint` that requires selection from a limited number of choices. The default value
    must exist in the given choices.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param choices: A List of all of the valid choices for this ConfigPoint
    :param default: The default value
    """

    def __init__(self, name: str, choices: "List", default):
        if default not in choices:
            raise ValueError("default value must be available in given choices")
        super().__init__(name=name, type="choice", default=default)
        self.choices = choices

    def validate(self, value) -> Validation:
        result = value in self.choices
        if not result:
            return Validation(
                is_valid=result,
                message=f"Value '{value}' does not exist in valid choices: [{', '.join(str(c) for c in self.choices)}]",
            )
        return VALID


class IntegerConfigPoint(ChoiceConfigPoint):
    """A `ConfigPoint` that requires selection from a range of integers. The default value must
    exist in the given choices.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param range: The range of valid integers
    :param default: The default value
    """

    def __init__(self, name: str, range: range, default: int):
        super().__init__(name=name, choices=list(range), default=default)


class BooleanConfigPoint(ChoiceConfigPoint):
    """A `ConfigPoint` that allows True/False values.

    :param name: The name of this `ConfigPoint`, will be used by scripts to look up the configured value.
    :param default: The default value
    """

    def __init__(self, name: str, default: bool):
        super().__init__(name=name, choices=[False, True], default=default)


def choice(name: str, choices: "List", default) -> ChoiceConfigPoint:
    """A helper function to simplify the creation of ChoiceConfigPoints. Requires selection from a
    limited number of choices. The default value must exist in the given choices.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param choices: A List of all of the valid choices for this ConfigPoint
    :param default: The default value"""
    return ChoiceConfigPoint(name=name, choices=choices, default=default)


def integer(name: str, range: range, default: int) -> IntegerConfigPoint:
    """A helper function to simplify the creation of IntegerConfigPoints. Requires selection from a
    range of integers. The default value must exist in the given choices.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param range: The range of valid integers
    :param default: The default value
    """
    return IntegerConfigPoint(name=name, range=range, default=default)


def boolean(name: str, default: bool) -> BooleanConfigPoint:
    """A helper function to simplify the creation of BooleanConfigPoints.

    :param name: The name of this `ConfigPoint`, will be used by scripts to lookup the configured value.
    :param default: The default value
    """
    return BooleanConfigPoint(name=name, default=default)


class ConfigSpec:
    """
    A container for `ConfigPoints` representing the set of configuration options for a specific
    script.
    """

    def __init__(self, config_points: "List[ConfigPoint]") -> None:
        self.points = {}
        for point in config_points:
            if point.name in self.points:
                raise ValueError(f"config point {point.name} is already defined")
            self.points[point.name] = point

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points.values())

    def default_config(self) -> "dict(str, any)":
        """Returns the default configuration for this spec."""
        return {point.name: point.default for point in self.points.values()}

    def validate(self, configuration) -> Validation:
        """Validates the given configuration with this spec. Returns a `Validation` containing the
        validation result, as well as an error message containing the reason for a validation failure.
        """
        for name, value in configuration.items():
            if name not in self.points:
                return Validation(is_valid=False, message=f"ConfigPoint '{name}' is not defined.")

            validation = self.points[name].validate(value)
            if not validation.is_valid:
                return validation

        return VALID


class ConfigFile:
    """A class containing functions for dealing with configuration files."""

    @staticmethod
    def config_filename(cls):
        """Returns the filename for the config file for the given class."""
        return f"config/{cls.__qualname__}.json"

    @staticmethod
    def save_config(cls, data: dict):
        """Take config as a dict and save to this class's config file.

        .. note::
            Be mindful of how often `_save_config()` is called because
            writing to disk too often can slow down the performance of your
            script. Only call save state when state has changed and consider
            adding a time since last save check to reduce save frequency.
        """
        json_str = json.dumps(data)
        try:
            os.mkdir("config")
        except OSError:
            pass
        with open(ConfigFile.config_filename(cls), "w") as file:
            file.write(json_str)

    @staticmethod
    def load_config(cls, config_spec: ConfigSpec):
        """If this class has config points, this method validates and returns the ConfigSettings object
        representing the class's config file.  Otherwise an empty ConfigSettings object is returned.
        """
        if len(config_spec):
            saved_config = load_json_file(ConfigFile.config_filename(cls))
            config = config_spec.default_config()

            validation = config_spec.validate(saved_config)

            if not validation.is_valid:
                raise ValueError(validation.message)

            config.update(saved_config)
            return ConfigSettings(config)
        else:
            return ConfigSettings({})

    @staticmethod
    def delete_config(cls):
        """Deletes the config file, effectively resetting to defaults."""
        delete_file(ConfigFile.config_filename(cls))


class ConfigSettings:
    """Collects the configuration settings into an object with attributes instead of a dict with keys

    Dict keys are converted to upper-case strings with underscores
    """

    def __init__(self, d):
        """Constructor

        @param d  The raw dict loaded from the configuration file
        """
        self.__dict__ = {}  # required for getattr & setattr

        for k in d.keys():
            cname = self.to_attr_name(k)
            setattr(self, cname, d[k])

    def to_attr_name(self, key):
        """Converts a dict key string to its equivalent attribute name

        @param key  The string to convert
        @return     The same string, converted to upper-case, preserving underscores

        @exception  ValueError if the key contains invalid characters; only letters, numbers, hyphens, and underscores
                    are permitted. They key cannot be length 0, nor can it begin with a number
        """
        key = key.strip()
        s = ""
        for ch in key:
            if ch.isalpha() or ch.isdigit() or ch == "_":
                s += ch.upper()
            else:
                raise ValueError(
                    f"Invalid attribute name: {key}. Keys cannot contain the character {ch}"
                )

        if len(s) == 0:
            raise ValueError("Invalid attribute name: key cannot be empty")
        elif s[0].isdigit():
            raise ValueError("Invalid attribute name: key cannot start with a number")
        return s

    def __eq__(self, that):
        """Allows comparing the config object directly to either another config object or a dict

        @param that  The object we're comparing to, either a dict or another ConfigSettings object

        @return True if the two objects are equivalent, otherwise False
        """
        if type(that) is dict:
            try:
                that = ConfigSettings(that)
                return self == that
            except ValueError:
                return False
        elif type(that) is ConfigSettings:
            # Make sure every key self exists and is equal to the equivalent in that
            for k in self.__dict__.keys():
                if not k in that.__dict__ or self.__dict__[k] != that.__dict__[k]:
                    return False

            # Make sure every key in that exists and is equal to its equivalent in self
            for k in that.__dict__.keys():
                if not k in self.__dict__ or self.__dict__[k] != that.__dict__[k]:
                    return False

            return True
