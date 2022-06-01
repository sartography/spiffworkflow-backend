"""File."""
import enum

from flask_bpmn.models.db import db
from marshmallow import INCLUDE
from marshmallow import Schema
from sqlalchemy import func
from sqlalchemy.orm import deferred  # type: ignore
from sqlalchemy.orm import relationship

from spiffworkflow_backend.models.data_store import DataStoreModel


class FileModel(db.Model):
    """FileModel."""

    __tablename__ = "file"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    process_instance_id = db.Column(
        db.Integer, db.ForeignKey("process_instance.id"), nullable=True
    )
    task_spec = db.Column(db.String(50), nullable=True)
    irb_doc_code = db.Column(
        db.String(50), nullable=False
    )  # Code reference to the documents.xlsx reference file.
    data_stores = relationship(DataStoreModel, cascade="all,delete", backref="file")
    md5_hash = db.Column(db.String(50), unique=False, nullable=False)
    data = deferred(db.Column(db.LargeBinary))  # Don't load it unless you have to.
    size = db.Column(db.Integer, default=0)
    date_modified = db.Column(db.DateTime(timezone=True), onupdate=func.now())
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    user_uid = db.Column(db.String(50), db.ForeignKey("user.uid"), nullable=True)
    archived = db.Column(db.Boolean, default=False)


class FileType(enum.Enum):
    """FileType."""

    bpmn = "bpmn"
    csv = "csv"
    dmn = "dmn"
    doc = "doc"
    docx = "docx"
    gif = "gif"
    jpg = "jpg"
    md = "md"
    pdf = "pdf"
    png = "png"
    ppt = "ppt"
    pptx = "pptx"
    rtf = "rtf"
    svg = "svg"
    svg_xml = "svg+xml"
    txt = "txt"
    xls = "xls"
    xlsx = "xlsx"
    xml = "xml"
    zip = "zip"


CONTENT_TYPES = {
    "bpmn": "text/xml",
    "csv": "text/csv",
    "dmn": "text/xml",
    "doc": "application/msword",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "gif": "image/gif",
    "jpg": "image/jpeg",
    "md": "text/plain",
    "pdf": "application/pdf",
    "png": "image/png",
    "ppt": "application/vnd.ms-powerpoint",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "rtf": "application/rtf",
    "svg": "image/svg+xml",
    "svg_xml": "image/svg+xml",
    "txt": "text/plain",
    "xls": "application/vnd.ms-excel",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xml": "application/xml",
    "zip": "application/zip",
}


class File:
    """File."""

    def __init__(self):
        """__init__."""
        self.content_type = None
        self.name = None
        self.content_type = None
        self.process_instance_id = None
        self.irb_doc_code = None
        self.type = None
        self.document = {}
        self.last_modified = None
        self.size = None
        self.data_store = {}
        self.user_uid = None
        self.archived = None

    @classmethod
    def from_file_system(
        cls, file_name, file_type, content_type, last_modified, file_size
    ):
        """From_file_system."""
        instance = cls()
        instance.name = file_name
        instance.content_type = content_type
        instance.type = file_type.value
        instance.document = {}
        instance.last_modified = last_modified
        instance.size = file_size
        # fixme:  How to track the user id?
        instance.data_store = {}
        return instance


class FileSchema(Schema):
    """FileSchema."""

    class Meta:
        """Meta."""

        model = File
        fields = [
            "id",
            "name",
            "content_type",
            "process_instance_id",
            "irb_doc_code",
            "last_modified",
            "type",
            "archived",
            "size",
            "data_store",
            "document",
            "user_uid",
            "url",
        ]
        unknown = INCLUDE

    # url = Method("get_url")
    #
    # def get_url(self, obj):
    #     token = 'not_available'
    #     if hasattr(obj, 'id') and obj.id is not None:
    #         file_url = url_for("/v1_0.crc_api_file_get_file_data_link", file_id=obj.id, _external=True)
    #         if hasattr(flask.g, 'user'):
    #             token = flask.g.user.encode_auth_token()
    #         url = file_url + '?auth_token=' + urllib.parse.quote_plus(token)
    #         return url
    #     else:
    #         return ""
    #
