"""Main."""
import json

from flask import Blueprint
from flask import request
from flask import Response
from flask_bpmn.models.db import db
from sqlalchemy.exc import IntegrityError

from spiff_workflow_webapp.models.group import GroupModel
from spiff_workflow_webapp.models.user import UserModel
from spiff_workflow_webapp.models.user_group_assignment import UserGroupAssignmentModel
import flask.wrappers

user_blueprint = Blueprint("main", __name__)


@user_blueprint.route("/user/<username>", methods=["GET"])
def create_user(username: str) -> flask.wrappers.Response:
    """Create_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is not None:
        return Response(
            json.dumps({"error": f"User already exists: {username}"}),
            status=409,
            mimetype="application/json",
        )

    user = UserModel(username=username)
    try:
        db.session.add(user)
    except IntegrityError as exception:
        return Response(
            json.dumps({"error": repr(exception)}),
            status=500,
            mimetype="application/json",
        )

    db.session.commit()
    return Response(
        json.dumps({"id": user.id}), status=201, mimetype="application/json"
    )


@user_blueprint.route("/user/<username>", methods=["DELETE"])
def delete_user(username: str) -> flask.wrappers.Response:
    """Delete_user."""
    user = UserModel.query.filter_by(username=username).first()
    if user is None:
        return Response(
            json.dumps({"error": f"User cannot be found: {username}"}),
            status=400,
            mimetype="application/json",
        )

    db.session.delete(user)
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=204, mimetype="application/json")


@user_blueprint.route("/group/<group_name>", methods=["GET"])
def create_group(group_name: str) -> flask.wrappers.Response:
    """Create_group."""
    group = GroupModel.query.filter_by(name=group_name).first()
    if group is not None:
        return Response(
            json.dumps({"error": f"Group already exists: {group_name}"}),
            status=409,
            mimetype="application/json",
        )

    group = GroupModel(name=group_name)
    try:
        db.session.add(group)
    except IntegrityError as exception:
        return Response(
            json.dumps({"error": repr(exception)}),
            status=500,
            mimetype="application/json",
        )
    db.session.commit()

    return Response(
        json.dumps({"id": group.id}), status=201, mimetype="application/json"
    )


@user_blueprint.route("/group/<group_name>", methods=["DELETE"])
def delete_group(group_name: str) -> flask.wrappers.Response:
    """Delete_group."""
    group = GroupModel.query.filter_by(name=group_name).first()
    if group is None:
        return Response(
            json.dumps({"error": f"Group cannot be found: {group_name}"}),
            status=400,
            mimetype="application/json",
        )

    db.session.delete(group)
    db.session.commit()

    return Response(json.dumps({"ok": True}), status=204, mimetype="application/json")


@user_blueprint.route("/assign_user_to_group", methods=["POST"])
def assign_user_to_group() -> flask.wrappers.Response:
    """Assign_user_to_group."""
    user = get_user_from_request()
    group = get_group_from_request()

    user_group_assignment = UserGroupAssignmentModel.query.filter_by(
        user_id=user.id, group_id=group.id
    ).first()
    if user_group_assignment is not None:
        return Response(
            json.dumps({"error": f"User ({user.id}) is already in group ({group.id})"}),
            status=409,
            mimetype="application/json",
        )

    user_group_assignment = UserGroupAssignmentModel(user_id=user.id, group_id=group.id)
    db.session.add(user_group_assignment)
    db.session.commit()

    return Response(
        json.dumps({"id": user_group_assignment.id}),
        status=201,
        mimetype="application/json",
    )


@user_blueprint.route("/remove_user_from_group", methods=["POST"])
def remove_user_from_group() -> flask.wrappers.Response:
    """Remove_user_from_group."""
    user = get_user_from_request()
    group = get_group_from_request()

    user_group_assignment = UserGroupAssignmentModel.query.filter_by(
        user_id=user.id, group_id=group.id
    ).first()
    if user_group_assignment is None:
        return Response(
            json.dumps({"error": f"User ({user.id}) is not in group ({group.id})"}),
            status=400,
            mimetype="application/json",
        )

    db.session.delete(user_group_assignment)
    db.session.commit()

    return Response(
        json.dumps({"ok": True}),
        status=204,
        mimetype="application/json",
    )


def get_user_from_request() -> UserModel:
    """Get_user_from_request."""
    user_id = request.json.get("user_id")

    if user_id is None:
        return Response(
            "{error:'user_id required'}", status=400, mimetype="application/json"
        )

    user = UserModel.query.filter_by(id=user_id).first()
    if user is None:
        return Response(
            json.dumps({"error": f"User cannot be found: {user_id}"}),
            status=400,
            mimetype="application/json",
        )
    return user


def get_group_from_request() -> GroupModel:
    """Get_group_from_request."""
    group_id = request.json.get("group_id")

    if group_id is None:
        return Response(
            "{error:'group_id required'}", status=400, mimetype="application/json"
        )

    group = GroupModel.query.filter_by(id=group_id).first()
    if group is None:
        return Response(
            json.dumps({"error": f"Group cannot be found: {group_id}"}),
            status=400,
            mimetype="application/json",
        )
    return group
