"""Test Api Blueprint."""
import json
from typing import Union

from flask.testing import FlaskClient
from flask_bpmn.models.db import db

from spiff_workflow_webapp.models.process_instance import ProcessInstanceModel


def test_user_can_be_created_and_deleted(client: FlaskClient) -> None:
    process_instance = ProcessInstanceModel.query.filter().first()
    if process_instance is not None:
        db.session.delete(process_instance)
        db.session.commit()

    last_response = None
    tasks = [
        {"task_identifier": "1", "answer": {"Product Name": "G", "Quantity": "2"}},
        {"task_identifier": "1", "answer": {"Sleeve Type": "Short"}},
        {"task_identifier": "1", "answer": {"Continue shopping?": "N"}},
        {"task_identifier": "1", "answer": {"Shipping Method": "Overnight"}},
        {"task_identifier": "1", "answer": {"Shipping Address": "Somewhere"}},
        {"task_identifier": "1", "answer": {"Place Order": "Y"}},
        {"task_identifier": "1", "answer": {"Card Number": "MY_CARD"}},
        {"task_identifier": "2", "answer": {"Was the customer charged?": "Y"}},
        {"task_identifier": "1", "answer": {"Was the product available?": "Y"}},
        {"task_identifier": "1", "answer": {"Was the order shipped?": "Y"}},
    ]
    for task in tasks:
        run_task(client, task, last_response)

    process_instance = ProcessInstanceModel.query.filter().first()
    if process_instance is not None:
        db.session.delete(process_instance)
        db.session.commit()


def run_task(
    client: FlaskClient, request_body: dict, last_response: Union[None, str]
) -> None:
    """Run_task."""
    response = client.post(
        "/run_process",
        content_type="application/json",
        data=json.dumps(request_body),
    )
    assert response.status_code == 200
