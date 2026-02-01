# Database clients (Supabase)

from app.infrastructure.db.analysis_repository import (
    delete_analysis,
    get_analysis,
    list_analyses,
    save_analysis,
)
from app.infrastructure.db.conversation_repository import (
    get_conversation,
    save_conversation,
)
from app.infrastructure.db.faq_repository import (
    create_document as create_faq_document,
)
from app.infrastructure.db.faq_repository import (
    delete_document as delete_faq_document,
)
from app.infrastructure.db.faq_repository import (
    list_documents as list_faq_documents,
)
from app.infrastructure.db.faq_repository import (
    update_document_active_status as update_faq_document_active_status,
)
from app.infrastructure.db.faq_repository import (
    update_document_content as update_faq_document_content,
)

__all__ = [
    # Analysis
    "delete_analysis",
    "get_analysis",
    "list_analyses",
    "save_analysis",
    # Conversation
    "get_conversation",
    "save_conversation",
    # FAQ
    "create_faq_document",
    "delete_faq_document",
    "list_faq_documents",
    "update_faq_document_content",
    "update_faq_document_active_status",
]
