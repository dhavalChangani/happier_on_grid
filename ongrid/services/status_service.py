"""Verification status service"""

import logging

from typing import Dict, Any, Optional

from ongrid.http_client import HttpClient

logger = logging.getLogger(__name__)


class StatusService:
    """Service for checking verification statuses"""

    def __init__(self, http_client: HttpClient):
        """
        Initialize status service.

        Args:
            http_client: HTTP client instance
        """
        self.http = http_client

    def get_pan_verification_status(
        self, individual_id: int, request_id: int
    ) -> Dict[str, Any]:
        """
        Get PAN verification status for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of PANV request

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
        """
        with self.http.handle_api_exceptions("get PAN verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/panv"

            params = {"requestId": request_id}

            response = self.http.make_request(
                method="GET", endpoint=endpoint, params=params
            )

            logger.info(
                f"PAN verification status retrieved for individual ID {individual_id}, "
                f"request ID: {request_id}, "
                f"state: {response.get('document', {}).get('state')}"
            )
            return response

    def get_education_verification_status(
        self, individual_id: int, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get education verification status for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of EDUV request (optional)

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
        """
        with self.http.handle_api_exceptions("get education verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/eduv"

            params = {}
            if request_id is not None:
                params["requestId"] = request_id

            response = self.http.make_request(
                method="GET", endpoint=endpoint, params=params if params else None
            )

            logger.info(
                f"Education verification status retrieved for individual ID {individual_id}"
                + (f", request ID: {request_id}" if request_id else " (all requests)")
                + (f", state: {response.get('state')}" if request_id else "")
            )
            return response

    def get_employment_verification_status(
        self, individual_id: int, request_id: int
    ) -> Dict[str, Any]:
        """
        Get employment verification status for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of EMPV request

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
        """
        with self.http.handle_api_exceptions("get employment verification status"):
            endpoint = f"/app/v1/individual/{individual_id}/empv"

            params = {"requestId": request_id}

            response = self.http.make_request(
                method="GET", endpoint=endpoint, params=params
            )

            logger.info(
                f"Employment verification status retrieved for individual ID {individual_id}, "
                f"request ID: {request_id}, state: {response.get('state')}"
            )
            return response

    def get_professional_reference_check_status(
        self, individual_id: int, request_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get professional reference check status for an individual.

        Args:
            individual_id: Individual's unique ID at OnGrid
            request_id: ID of PRC request (optional)

        Returns:
            API response dictionary

        Raises:
            OnGridException: If request fails
        """
        with self.http.handle_api_exceptions(
            "get professional reference check status"
        ):
            endpoint = f"/app/v1/individual/{individual_id}/prc"

            params = {}
            if request_id is not None:
                params["requestId"] = request_id

            response = self.http.make_request(
                method="GET", endpoint=endpoint, params=params if params else None
            )

            logger.info(
                f"Professional reference check status retrieved for individual ID {individual_id}"
                + (f", request ID: {request_id}" if request_id else " (all requests)")
                + (f", state: {response.get('state')}" if request_id else "")
            )
            return response
