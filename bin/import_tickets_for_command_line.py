"""Grabs tickets from csv and makes process instances."""
import os
from flask_bpmn.models.db import db

from spiffworkflow_backend.models.process_instance import ProcessInstanceModel

import csv

from spiffworkflow_backend import create_app
from spiffworkflow_backend.models.user import UserModel
from spiffworkflow_backend.services.process_instance_processor import ProcessInstanceProcessor
from spiffworkflow_backend.services.process_instance_service import ProcessInstanceService
from flask import current_app

from spiffworkflow_backend.services.process_model_service import ProcessModelService


def print_process_instance_count(process_model_identifier_ticket: str):
    """Print process instance count."""
    process_instances = ProcessInstanceModel.query.filter_by(process_model_identifier=process_model_identifier_ticket).all()
    process_instance_count = len(process_instances)
    print(f"process_instance_count: {process_instance_count}")


def main():
    """Main."""
    os.environ["FLASK_ENV"] = "development"
    os.environ["FLASK_SESSION_SECRET_KEY"] = "whatevs"
    app = create_app()
    process_model_identifier_ticket = "ticket"
    with app.app_context():

        bpmn_spec_dir = current_app.config["BPMN_SPEC_ABSOLUTE_DIR"]
        print(f"bpmn_spec_dir: {bpmn_spec_dir}")
        db.session.query(ProcessInstanceModel).filter(ProcessInstanceModel.process_model_identifier == process_model_identifier_ticket).delete()
        db.session.commit()
        print_process_instance_count(process_model_identifier_ticket)
        process_model = ProcessModelService().get_process_model(process_model_identifier_ticket)
        columns_to_data_key_mappings = {"Month": "month", "MS": "milestone", "ID": "req_id", "Dev Days": "dev_days"}
        columns_to_header_index_mappings = {}

        user = UserModel.query.filter_by(username='test_user1').first()

        with open("tickets.csv") as infile:
            reader = csv.reader(infile, delimiter=",")
            header = next(reader)
            for column_name in columns_to_data_key_mappings:
                columns_to_header_index_mappings[column_name] = header.index(column_name)
            id_index = header.index("ID")
            priority_index = header.index("Priority")
            print(f"header: {header}")
            for row in reader:
                ticket_identifier = row[id_index]
                priority = row[priority_index]
                print(f"ticket_identifier: {ticket_identifier}")
                print(f"priority: {priority}")

                process_instance = ProcessInstanceService.create_process_instance(
                    process_model_identifier_ticket, user
                )
                processor = ProcessInstanceProcessor(process_instance)

                processor.do_engine_steps()
                processor.save()

                for column_name, desired_data_key in columns_to_data_key_mappings.items():
                    appropriate_index = columns_to_header_index_mappings[column_name]
                    print(f"appropriate_index: {appropriate_index}")
                    processor.bpmn_process_instance.data[desired_data_key] = row[appropriate_index]
                processor.save()

                process_instance_data = processor.get_data()
                print(f"process_instance_data: {process_instance_data}")

        print(f"columns_to_header_index_mappings: {columns_to_header_index_mappings}")
        print_process_instance_count(process_model_identifier_ticket)


# if __name__ == "__main__":
main()
