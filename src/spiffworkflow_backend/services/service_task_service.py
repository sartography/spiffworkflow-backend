"""ServiceTask_service."""
import importlib
import inspect
import pkgutil
import sys
import types

# TODO tmp declarations here until airflow provider poetry install is working
operator_module = sys.modules[__name__]

class SlackWebhookOperator:
    def __init__(self, webhook_token="", message="", channel="", **kwargs):
        self.channel = channel
        self.message = message
        self.webhook_token = webhook_token

    def execute(self):
        # TODO log?
        pass

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

def _import_airflow_operators():
    import airflow.providers
    from airflow.models import BaseOperator
    #from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    #import airflow.providers.slack.operators.slack_webhook
    x = list(_classes_of_type_in_pkg(airflow.providers, type(BaseOperator)))
    print(x)
    print(len(x))

class ServiceTaskService:

    @classmethod
    def _available_airflow_operators(cls):
        #try:
        _import_airflow_operators()
        #except:
        #    return['import failed']

        #_submodules_of(airflow.providers)

        x = []
        from airflow.models import BaseOperator
        import airflow.providers.http.operators.http
        print(BaseOperator.__subclasses__())
        
        return x

    @classmethod
    def available_operators(cls):
        # TODO do we define models to add types?

        #available_operators = [
        #    { 
        #        # TODO probably should be class name, description, etc - the more information
        #        # the less chance we can get it all just from reflection though
        #        "name": "SlackWebhookOperator", 
        #        "parameters": [
        #            { "name": "webhook_token", "label": "Webhook Token", "type": "string" },
        #            { "name": "message", "label": "Message", "type": "string" },
        #            { "name": "channel", "label": "Channel", "type": "string" },
        #        ]
        #    },
        #]
        available_operators = cls._available_airflow_operators()

        return available_operators

    @classmethod
    def scripting_additions(cls):
        # TODO add types
        operator_names = [operator['name'] for operator in cls.available_operators()]
        scripting_additions = {name: cls._operator_class_from_name(name) for name in operator_names}

    @classmethod
    def _operator_class_from_name(cls, name):
        # TODO add types
        operator_cls = getattr(operator_module, name)
        return operator_cls

