from flask_bpmn.models.db import db
from flask_bpmn.models.group import FlaskBpmnGroupModel
from sqlalchemy.orm import relationship


class GroupModel(FlaskBpmnGroupModel):
    __tablename__ = "group"
    __table_args__ = {'extend_existing': True}
    new_name_two = db.Column(db.String(255))
    user_group_assignments = relationship("UserGroupAssignmentModel", cascade="all, delete")
    users = relationship("UserModel", secondary="user_group_assignment")
