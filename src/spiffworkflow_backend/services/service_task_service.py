"""ServiceTask_service."""
import ast
import importlib
import inspect
import pkgutil
import sys
from typing import Any, Generator, TypedDict

from spiffworkflow_backend.services.reflection_service import ReflectionService

class OperatorParameter(TypedDict):
    name: str
    type: str
    required: bool

class Operator(TypedDict):
    name: str
    parameters: list[OperatorParameter]

OperatorClass = Any
OperatorClassGenerator = Generator[tuple[str, OperatorClass], None, None]

class ServiceTaskService:

    @staticmethod
    def _available_airflow_operator_classes() -> OperatorClassGenerator:
        """Yields name and class for all airflow operators that are available for use in 
        service tasks."""

        try:
            import airflow.providers
            from airflow.models import BaseOperator
            # TODO filter operators - __subclasses__() check didn't pan out immediately
            yield from ReflectionService.classes_of_type_in_pkg(airflow.providers, type(BaseOperator))
        except:
            pass

    @staticmethod
    def _parse_operator_params(operator_class) -> list[OperatorParameter]:
        """Parses the init of the given operator_class to build a list of OperatorParameters."""

        init_sig = inspect.signature(operator_class.__init__)
        params_to_skip = ['self', 'kwargs']
        params = filter(lambda param: param.name not in params_to_skip, init_sig.parameters.values())
        # TODO remove iterable, take inner type
        # TODO on union form set of types
        params = [{
            "name": param.name, 
            # TODO parsing to better fill out these two fields
            "type": str(param.annotation), 
            "required": True 
        } for param in params]

        return params

    @classmethod
    def available_operator_classes(cls) -> OperatorClassGenerator:
        """Yields name and class for all operators that are available for use in a service task."""

        # TODO maybe premature to have a place to aggregate other operator types?
        yield from cls._available_airflow_operator_classes()

    @classmethod
    def available_operators(cls) -> list[Operator]:
        """Returns a list of all operator names and init parameters that are available for use in 
        a service task."""

        available_operators = [{
            "name": operator_name, 
            "parameters": cls._parse_operator_params(operator_class)
        } for operator_name, operator_class in cls.available_operator_classes()]

        return list(available_operators)

    @classmethod
    def scripting_additions(cls) -> dict[str, OperatorClass]:
        """Returns a dictionary of operator names and classes for loading into a 
        scripting engine instance."""

        operator_classes = list(cls.available_operator_classes())
        scripting_additions = {name: clz for name, clz in operator_classes}
        return scripting_additions
