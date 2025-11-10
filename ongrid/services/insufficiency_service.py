"""Insufficiency service"""

import logging

from typing import Dict, Any, List, Optional

from ongrid.exceptions import ValidationException
from ongrid.http_client import HttpClient
from ongrid import validators

logger = logging.getLogger(__name__)


class InsufficientService:
    """Service for managing insufficiencies"""

    def __init__(self, http_client: HttpClient):
        """
        Initialize insufficiency service.

        Args:
            http_client: HTTP client instance
        """
        self.http = http_client

    def get_insufficiencies(
        self,
        community_id: int,
        individual_id: Optional[int] = None,
        request_id: Optional[int] = None,
        page_no: int = 0,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get list of insufficiencies based on criteria.

        Args:
            community_id: Community ID
            individual_id: Individual ID (optional)
            request_id: Request ID (optional)
            page_no: Page number (default: 0)
            page_size: Size of each page, range 1-500 (default: 100)

        Returns:
            Dict containing:
                - pageNo: Page number
                - pageSize: Page size
                - totalCount: Total count of insufficiencies
                - communityInsufficiencyDTO: List of insufficiency objects

        Raises:
            ValidationException: If validation fails
            OnGridException: If request fails
        """
        validation_errors = []
        validation_errors.extend(
            validators.validate_positive_integer(community_id, "community_id")
        )

        if individual_id is not None:
            validation_errors.extend(
                validators.validate_positive_integer(individual_id, "individual_id")
            )

        if request_id is not None:
            validation_errors.extend(
                validators.validate_positive_integer(request_id, "request_id")
            )

        if page_size < 1 or page_size > 500:
            validation_errors.append("page_size must be between 1 and 500")

        if page_no < 0:
            validation_errors.append("page_no must be non-negative")

        if validation_errors:
            raise ValidationException(f"Validation failed: {'; '.join(validation_errors)}")

        with self.http.handle_api_exceptions("get insufficiencies"):
            endpoint = f"/app/v1/community/{community_id}/insufficiency"

            params = {
                "pageNo": page_no,
                "pageSize": page_size,
            }

            if individual_id is not None:
                params["individualId"] = individual_id

            if request_id is not None:
                params["requestId"] = request_id

            logger.info(
                f"Fetching insufficiencies for community {community_id} with params: {params}"
            )

            response = self.http.make_request(
                method="GET", endpoint=endpoint, params=params
            )

            logger.info(
                f"Retrieved {response.get('totalCount', 0)} insufficiencies "
                f"(page {page_no}, size {page_size})"
            )

            return response
