"""ServiceTask_service."""
import importlib
import inspect
import pkgutil
import sys
import types

# TODO these could be moved to a more generic location
def _modules_in_pkg(pkg):
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        if ispkg:
            # TODO couldn't get this to work with exec_module
            sub_pkg = finder.find_module(name).load_module(name)
            yield from _modules_in_pkg(sub_pkg)
            continue
        try:
            spec = finder.find_spec(name)
            module = types.ModuleType(spec.name)
            spec.loader.exec_module(module)
            yield name, module
        except:
            pass

def _classes_in_pkg(pkg):
    for module_name, module in _modules_in_pkg(pkg):
        for clz_name, clz in inspect.getmembers(module, inspect.isclass):
            if clz.__module__ == module_name:
                yield clz_name, clz

def _classes_of_type_in_pkg(pkg, clz_type):
    for clz_name, clz in _classes_in_pkg(pkg):
        if isinstance(clz, clz_type):
            yield clz_name, clz


class ServiceTaskService:

    @staticmethod
    def _available_airflow_operator_classes():
        try:
            import airflow.providers
            from airflow.models import BaseOperator
            # TODO filter only operators with no subclasses
            yield from _classes_of_type_in_pkg(airflow.providers, type(BaseOperator))
        except:
            pass

    @staticmethod
    def _infer_operator_params(operator_class):
        init_sig = inspect.signature(operator_class.__init__)
        params_to_skip = ['self', 'kwargs']
        params = filter(lambda param: param.name not in params_to_skip, init_sig.parameters.values())
        # TODO add new attrib to tell if type is optional
        # TODO remove iterable, take inner type
        # TODO on union form set of types
        params = [{"name": param.name, "type": str(param.annotation) } for param in params]
        return params

    @classmethod
    def available_operator_classes(cls):
        # TODO maybe premature to have a place to aggregate other operator types?
        yield from cls._available_airflow_operator_classes()

    # TODO wtf is the syntax here?
    #type OperatorParm = Dict[k in [name, parameter], str]

    @classmethod
    def available_operators(cls):
        # TODO do we define models to add types?
        available_operators = [{
            "name": name, 
            "parameters": cls._infer_operator_params(clz)
        } for name, clz in cls.available_operator_classes()]

        return list(available_operators)

    @classmethod
    def scripting_additions(cls):
        # TODO add types
        operator_classes = list(cls.available_operator_classes())
        scripting_additions = {name: clz for name, clz in operator_classes}
        return scripting_additions
