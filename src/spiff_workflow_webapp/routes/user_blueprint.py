"""Main."""
import json
from flask import Blueprint
from flask import Response
from flask import request
from sqlalchemy.exc import IntegrityError

from flask_bpmn.models.db import db
from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.models.user_group_assignment import UserGroupAssignmentModel

user_blueprint = Blueprint("main", __name__)


@user_blueprint.route("/user/<username>", methods=["GET"])
def create_user(username):
    """Create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is not None:
        return Response(json.dumps({"error": f"User already exists: {username}"}), status=409, mimetype='application/json')

    user = UserModel(username=username)
    try:
        db.session.add(user)
    except IntegrityError as exception:
        return Response(json.dumps({"error": repr(exception)}), status=500, mimetype='application/json')

    db.session.commit()
    return Response(json.dumps({"id": user.id}), status=201, mimetype='application/json')


@user_blueprint.route("/user/<username>", methods=["DELETE"])
def delete_user(username):
    """Delete_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        return Response(json.dumps({"error": f"User cannot be found: {username}"}), status=400, mimetype='application/json')

    db.session.delete(user)
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=204, mimetype='application/json')


@user_blueprint.route("/group/<group_name>", methods=["GET"])
def create_group(group_name):
    """Create_group."""
    group = GroupModel.query.filter_by(name=group_name).first()
    if group is not None:
        return Response(json.dumps({"error": f"Group already exists: {group_name}"}), status=409, mimetype='application/json')

    group = GroupModel(name=group_name)
    try:
        db.session.add(group)
    except IntegrityError as exception:
        return Response(json.dumps({"error": repr(exception)}), status=500, mimetype='application/json')
    db.session.commit()

    return Response(json.dumps({"id": group.id}), status=201, mimetype='application/json')


@user_blueprint.route("/group/<group_name>", methods=["DELETE"])
def delete_group(group_name):
    """Delete_group."""
    group = GroupModel.query.filter_by(name=group_name).first()
    if group is None:
        return Response(json.dumps({"error": f"Group cannot be found: {group_name}"}), status=400, mimetype='application/json')

    db.session.delete(group)
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=204, mimetype='application/json')


@user_blueprint.route("/assign_user_to_group", methods=["POST"])
def assign_user_to_group():
    """Assign_user_to_group."""
    content = request.json
    user_id = content.get("user_id")
    group_id = content.get("group_id")

    if user_id is None:
        return Response("{error:'user_id required'}", status=400, mimetype='application/json')

    if group_id is None:
        return Response("{error:'group_id required'}", status=400, mimetype='application/json')

    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        return Response(json.dumps({"error": f"User cannot be found: {user_id}"}), status=400, mimetype='application/json')

    group = GroupModel.query.filter_by(id=group_id).first()
    if group is None:
        return Response(json.dumps({"error": f"Group cannot be found: {group_id}"}), status=400, mimetype='application/json')

    user_group_assignment = UserGroupAssignmentModel.query.filter_by(user_id=user.id, group_id=group.id).first()
    if user_group_assignment is not None:
        return Response(
            json.dumps({"error": f"User ({user.id}) is already in group ({group.id})"}),
            status=409, mimetype='application/json'
        )

    user_group_assignment = UserGroupAssignmentModel(user_id=user.id, group_id=group.id)
    db.session.add(user_group_assignment)
    db.session.commit()

    return Response(json.dumps({"id": user_group_assignment.id}), status=201, mimetype='application/json')
