"""File."""
import enum


class FileType(enum.Enum):
    """FileType."""
    bpmn = "bpmn"
    csv = 'csv'
    dmn = "dmn"
    doc = "doc"
    docx = "docx"
    gif = 'gif'
    jpg = 'jpg'
    md = 'md'
    pdf = 'pdf'
    png = 'png'
    ppt = 'ppt'
    pptx = 'pptx'
    rtf = 'rtf'
    svg = "svg"
    svg_xml = "svg+xml"
    txt = 'txt'
    xls = 'xls'
    xlsx = 'xlsx'
    xml = 'xml'
    zip = 'zip'


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
    "zip": "application/zip"
}


class File(object):
    """File."""

    def __init__(self):
        """__init__."""
        self.content_type = None
        self.name = None
        self.content_type = None
        self.workflow_id = None
        self.irb_doc_code = None
        self.type = None
        self.document = {}
        self.last_modified = None
        self.size = None
        self.data_store = {}
        self.user_uid = None
        self.archived = None

    @classmethod
    def from_file_system(cls, file_name, file_type, content_type,
                         last_modified, file_size):
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
