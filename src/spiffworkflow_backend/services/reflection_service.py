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
        param_id = param.name
        param_type_desc = "any"
        # TODO this check is working so far but appears wrong
        param_req = param.default is param.empty
        annotation = param.annotation

        if annotation == param.empty:
            pass
        elif type(annotation) == type:
            # TODO handle non builtin types
            param_type_desc = annotation.__name__
        else:

            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin is None or args == ():
                param_type_desc = 'any'
            else:
                none_type_set = {type(None)}
                args = set(filter(lambda t: type(t) == type, args))
                if param_req and args & none_type_set:
                    param_req = False
                args -= none_type_set
                if len(args) == 1:
                    param_type = args.pop()
                    if type(param_type) == type:
                        param_type_desc = param_type.__name__

        return { "id": param_id, "type": param_type_desc, "required": param_req }

    @staticmethod
    def callable_params_desc(c: Callable) -> list[ParameterDescription]:
        """Parses the signature of a callable and returns a description of each parameter."""

        sig = inspect.signature(c)
        params_to_skip = ['self', 'kwargs']
        params = filter(lambda param: param.name not in params_to_skip, sig.parameters.values())
        # TODO remove iterable, take inner type
        # TODO on union form set of types
        params = [ReflectionService._param_annotation_desc(param) for param in params]

        return params
