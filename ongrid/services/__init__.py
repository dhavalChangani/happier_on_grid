"""OnGrid service modules"""

from ongrid.services.candidate_service import CandidateService
from ongrid.services.document_service import DocumentService
from ongrid.services.verification_service import VerificationService
from ongrid.services.status_service import StatusService

__all__ = [
    "CandidateService",
    "DocumentService",
    "VerificationService",
    "StatusService",
]
