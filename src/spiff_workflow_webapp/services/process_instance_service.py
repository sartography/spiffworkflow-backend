"""Process_instance_service."""


class ProcessInstanceService():
    """ProcessInstanceService."""

    @staticmethod
    def get_workflow_from_spec(workflow_spec_id, user):
        """Get_workflow_from_spec."""
        workflow_model = WorkflowModel(status=WorkflowStatus.not_started,
                                       study=None,
                                       user_id=user.uid,
                                       workflow_spec_id=workflow_spec_id,
                                       last_updated=datetime.now())
        db.session.add(workflow_model)
        db.session.commit()
        return workflow_model
