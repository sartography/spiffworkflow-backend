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
def _submodules_of(pkg):
    for finder, name, ispkg in pkgutil.iter_modules(pkg.__path__):
        if not ispkg:
            print('** ' + name)
            try:
                spec = finder.find_spec(name)
                mod = types.ModuleType(spec.name)
                spec.loader.exec_module(mod)
                for n, o in inspect.getmembers(mod):
                    if inspect.isclass(o):
                        print('$$ ' + n)
            except:
                pass
            continue
        submodule = finder.find_module(name).load_module(name)
        yield from _submodules_of(submodule)
        yield submodule, name

def _import_submodules_of(pkg):
    for submodule, name in _submodules_of(pkg):
        print(name)
        #x = __import__(name)
        #x = importlib.import_module(name)
        #print(submodule)
        #print(x)
        for n, o in inspect.getmembers(submodule):
            if inspect.isclass(o):
                print('** ' + n)
                continue
            #print('$ ' + submodule['__path__'])
    print('hi')

def _classes_in(pkg):
    for submodule, name in _submodules_of(pkg):
        pass
        #print(name)
        #print(dir(submodule))
        #print(submodule.__dict__)
        #for k, v in submodule.__dict__.items():
        #    print(k)

def _import_airflow_operators():
    import airflow.providers
    #from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
    #import airflow.providers.slack.operators.slack_webhook
    _classes_in(airflow.providers)

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

