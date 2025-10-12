import logging

from markitdown import MarkItDown

from .mixins.document_mixin_service import DocumentMixinService


logger = logging.getLogger(__name__)


class CoreService(DocumentMixinService):
    """Service for handling document conversion operations."""

    def __init__(self):
        logger.info("CoreService initialized with Mixins capabilities.")
        self.markdown_processor = MarkItDown()
