"""ServiceTask_service."""
import json
from typing import Any
from typing import Dict

import requests
from flask import current_app


def connector_proxy_url() -> str:
    """Returns the connector proxy url."""
    return current_app.config["CONNECTOR_PROXY_URL"]


class ServiceTaskDelegate:
    """ServiceTaskDelegate."""

    @staticmethod
    def call_connector(
        name: str, bpmn_params: Any
    ) -> None:  # TODO what is the return/type
        """Calls a connector via the configured proxy."""

        def normalize_value(v: Any):
            value = v["value"]
            secret_prefix = "secret:"  # noqa: S105
            if value.startswith(secret_prefix):
                key = value.removeprefix(secret_prefix)
                # TODO replace with call to secret store
                value = key
            return value

        params = {k: normalize_value(v) for k, v in bpmn_params.items()}
        proxied_response = requests.get(f"{connector_proxy_url()}/v1/do/{name}", params)
        print("From: " + name)
        print(proxied_response.text)


class ServiceTaskService:
    """ServiceTaskService."""

    @staticmethod
    def available_connectors() -> Any:
        """Returns a list of available connectors."""
        try:
            response = requests.get(connector_proxy_url())

            if response.status_code != 200:
                return []

            parsed_response = json.loads(response.text)
            return parsed_response
        except Exception as e:
            print(e)
            return []

    @staticmethod
    def scripting_additions() -> Dict[str, Any]:
        """Allows the ServiceTaskDelegate to be available to script engine instances."""
        return {"ServiceTaskDelegate", ServiceTaskDelegate}
