"""Script."""
from __future__ import annotations

import importlib
import os
import pkgutil
from abc import abstractmethod
from typing import Any
from typing import Callable

from flask_bpmn.api.api_error import ApiError

from spiffworkflow_backend.models.task import Task


# Generally speaking, having some global in a flask app is TERRIBLE.
# This is here, because after loading the application this will never change under
# any known condition, and it is expensive to calculate it everytime.
SCRIPT_SUB_CLASSES = None


class Script:
    """Provides an abstract class that defines how scripts should work, this must be extended in all Script Tasks."""

    def get_description(self) -> None:
        """Get_description."""
        raise ApiError("invalid_script", "This script does not supply a description.")

    @abstractmethod
    def do_task(
        self, task: Task, workflow_id: int, *args: list[Any], **kwargs: dict[Any, Any]
    ) -> None:
        """Do_task."""
        raise ApiError(
            "invalid_script",
            "This is an internal error. The script you are trying to execute '%s' "
            % self.__class__.__name__
            + "does not properly implement the do_task function.",
        )

    @abstractmethod
    def do_task_validate_only(
        self, task: Task, workflow_id: int, *args: list[Any], **kwargs: dict[Any, Any]
    ) -> None:
        """Do_task_validate_only."""
        raise ApiError(
            "invalid_script",
            "This is an internal error. The script you are trying to execute '%s' "
            % self.__class__.__name__
            + "does must provide a validate_only option that mimics the do_task, "
            + "but does not make external calls or database updates.",
        )

    @staticmethod
    def generate_augmented_list(task: Task, workflow_id: int) -> dict[str, Callable]:
        """This makes a dictionary of lambda functions that are closed over the class instance that they represent.

        This is passed into PythonScriptParser as a list of helper functions that are
        available for running.  In general, they maintain the do_task call structure that they had, but
        they always return a value rather than updating the task data.

        We may be able to remove the task for each of these calls if we are not using it other than potentially
        updating the task data.
        """

        def make_closure(
            subclass: type[Script], task: Task, workflow_id: int
        ) -> Callable:
            """Yes - this is black magic.

            Essentially, we want to build a list of all of the submodules (i.e. email, user_data_get, etc)
            and a function that is assocated with them.
            This basically creates an Instance of the class and returns a function that calls do_task
            on the instance of that class.
            the next for x in range, then grabs the name of the module and associates it with the function
            that we created.
            """
            instance = subclass()
            return lambda *ar, **kw: subclass.do_task(
                instance, task, workflow_id, *ar, **kw
            )

        execlist = {}
        subclasses = Script.get_all_subclasses()
        for x in range(len(subclasses)):
            subclass = subclasses[x]
            execlist[subclass.__module__.split(".")[-1]] = make_closure(
                subclass, task, workflow_id
            )
        return execlist

    @staticmethod
    def generate_augmented_validate_list(
        task: Task, workflow_id: int
    ) -> dict[str, Callable]:
        """This makes a dictionary of lambda functions that are closed over the class instance that they represent.

        This is passed into PythonScriptParser as a list of helper functions that are
        available for running.  In general, they maintain the do_task call structure that they had, but
        they always return a value rather than updating the task data.

        We may be able to remove the task for each of these calls if we are not using it other than potentially
        updating the task data.
        """

        def make_closure_validate(
            subclass: type[Script], task: Task, workflow_id: int
        ) -> Callable:
            """Make_closure_validate."""
            instance = subclass()
            return lambda *a, **b: subclass.do_task_validate_only(
                instance, task, workflow_id, *a, **b
            )

        execlist = {}
        subclasses = Script.get_all_subclasses()
        for x in range(len(subclasses)):
            subclass = subclasses[x]
            execlist[subclass.__module__.split(".")[-1]] = make_closure_validate(
                subclass, task, workflow_id
            )
        return execlist

    @classmethod
    def get_all_subclasses(cls) -> list[type[Script]]:
        """Get_all_subclasses."""
        # This is expensive to generate, never changes after we load up.
        global SCRIPT_SUB_CLASSES
        if not SCRIPT_SUB_CLASSES:
            SCRIPT_SUB_CLASSES = Script._get_all_subclasses(Script)
        return SCRIPT_SUB_CLASSES

    @staticmethod
    def _get_all_subclasses(script_class: Any) -> list[type[Script]]:
        """_get_all_subclasses."""
        # hackish mess to make sure we have all the modules loaded for the scripts
        pkg_dir = os.path.dirname(__file__)
        for (_module_loader, name, _ispkg) in pkgutil.iter_modules([pkg_dir]):
            importlib.import_module("." + name, __package__)

        """Returns a list of all classes that extend this class."""
        all_subclasses = []

        for subclass in script_class.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(Script._get_all_subclasses(subclass))

        return all_subclasses

    def add_data_to_task(self, task: Task, data: Any) -> None:
        """Add_data_to_task."""
        key = self.__class__.__name__

        if task.data is None:
            task.data = {}

        if key in task.data:
            task.data[key].update(data)
        else:
            task.data[key] = data


class ScriptValidationError:
    """ScriptValidationError."""

    def __init__(self, code: str, message: str):
        """__init__."""
        self.code = code
        self.message = message

    @classmethod
    def from_api_error(cls, api_error: ApiError) -> ScriptValidationError:
        """From_api_error."""
        return cls(api_error.code, api_error.message)
