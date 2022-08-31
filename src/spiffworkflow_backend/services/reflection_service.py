"""Reflection_service."""
import importlib
import inspect
import pkgutil
import types
from typing import get_args, get_origin, Any, Callable, Generator, TypedDict

DiscoveredClass = Any
DiscoveredModule = Any
DiscoveredClassGenerator = Generator[tuple[str, DiscoveredClass], None, None]
DiscoveredModuleGenerator = Generator[tuple[str, DiscoveredModule], None, None]

class ParameterDescription(TypedDict):
    id: str
    type: str
    required: bool

class ReflectionService:
    """Utilities to aid in reflection."""
    
    @staticmethod
    def modules_in_pkg(pkg) -> DiscoveredModuleGenerator:
        """Recursively yields a (name, module) for each module in the given pkg."""

        for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
            if ispkg:
                # TODO couldn't get this to work with exec_module
                sub_pkg = finder.find_module(name).load_module(name)
                yield from ReflectionService.modules_in_pkg(sub_pkg)
                continue
            try:
                spec = finder.find_spec(name)
                module = types.ModuleType(spec.name)
                spec.loader.exec_module(module)
                yield name, module
            except:
                pass

    @staticmethod
    def classes_in_pkg(pkg) -> DiscoveredClassGenerator:
        """Recursively yields a (name, class) for each class in each module in the given pkg."""

        for module_name, module in ReflectionService.modules_in_pkg(pkg):
            for clz_name, clz in inspect.getmembers(module, inspect.isclass):
                if clz.__module__ == module_name:
                    yield clz_name, clz

    @staticmethod
    def classes_of_type_in_pkg(pkg, clz_type) -> DiscoveredClassGenerator:
        """Recursively yields a (name, class) for each class in each module in the given pkg 
        that isinstance of the given clz_type."""

        for clz_name, clz in ReflectionService.classes_in_pkg(pkg):
            if isinstance(clz, clz_type):
                yield clz_name, clz

    @staticmethod
    def _param_annotation_desc(param: inspect.Parameter) -> ParameterDescription:
        """Parses a callable parameter's type annotation, if any, to form a ParameterDescription."""

        param_id = param.name
        param_type_desc = "any"

        none_type = type(None)
        supported_types = {str, int, bool, none_type}
        unsupported_type_marker = object

        assert unsupported_type_marker not in supported_types

        annotation = param.annotation

        if annotation in supported_types:
            annotation_types = {annotation}
        else:
            # an annotation can have more than one type in the case of a union
            # get_args normalizes Union[str, dict] to (str, dict)
            # get_args normalizes Optional[str] to (str, none)
            # all unsupported types are marked so (str, dict) -> (str, unsupported)
            # the absense of a type annotation results in an empty set
            annotation_types = set(map(lambda t: t if t in supported_types else unsupported_type_marker, 
                get_args(annotation)))

        # a parameter is required if it has no default value and none is not in its type set
        param_req = param.default is param.empty and none_type not in annotation_types

        # the none type from a union is used for requiredness, but needs to be discarded 
        # to single out the optional type
        annotation_types.discard(none_type)

        # if we have a single supported type use that, else any is the default
        if len(annotation_types) == 1:
            annotation_type = annotation_types.pop()
            if annotation_type in supported_types:
                param_type_desc = annotation_type.__name__

        return { "id": param_id, "type": param_type_desc, "required": param_req }

    @staticmethod
    def callable_params_desc(c: Callable) -> list[ParameterDescription]:
        """Parses the signature of a callable and returns a description of each parameter."""

        sig = inspect.signature(c)
        params_to_skip = ['self', 'kwargs']
        params = filter(lambda param: param.name not in params_to_skip, sig.parameters.values())
        params = [ReflectionService._param_annotation_desc(param) for param in params]

        return params
