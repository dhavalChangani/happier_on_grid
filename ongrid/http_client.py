"""HTTP client for OnGrid API communication"""

import base64
import logging
import os
import requests

from contextlib import contextmanager
from typing import Dict, Any, Optional

from ongrid.exceptions import (
    OnGridException,
    ValidationException,
    APIException,
    AuthenticationException,
    NetworkException,
)

logger = logging.getLogger(__name__)


class HttpClient:
    """
    HTTP client for making requests to OnGrid API.

    Handles authentication, headers, and error handling.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str,
    ):
        """
        Initialize HTTP client.

        Args:
            client_id: OnGrid client ID
            client_secret: OnGrid client secret
            base_url: Base URL for OnGrid API

        Raises:
            OnGridException: If required credentials are missing
        """
        if not client_id or not client_secret:
            raise OnGridException("Client ID and Client Secret are required")
        if not base_url:
            raise OnGridException("Base URL is required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url

    def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        is_multipart: bool = False,
    ) -> Dict[str, Any]:
        """
        Make HTTP request to OnGrid API.

        Args:
            method: HTTP method (POST, PUT, GET, etc.)
            endpoint: API endpoint path
            data: Request data (JSON body or form data)
            files: Dictionary of files to upload
            params: Query parameters
            is_multipart: Force multipart/form-data mode

        Returns:
            API response as dictionary

        Raises:
            OnGridException: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        if files or is_multipart:
            headers = {
                "Authorization": f"Basic {b64_auth_str}",
                "Accept": "application/json",
            }
            request_kwargs = {
                "method": method,
                "url": url,
                "files": files,
                "data": data,
                "params": params,
                "headers": headers,
            }
        else:
            headers = {
                "Authorization": f"Basic {b64_auth_str}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            request_kwargs = {
                "method": method,
                "url": url,
                "json": data,
                "params": params,
                "headers": headers,
            }

        try:
            response = requests.request(**request_kwargs)

            if response.status_code == 401 or response.status_code == 403:
                raise AuthenticationException("Invalid credentials or unauthorized access")
            
            if response.status_code >= 400:
                error_msg = f"OnGrid API error: {response.status_code}"
                response_data = None
                try:
                    response_data = response.json()
                    error_msg = response_data.get("message", error_msg)
                except ValueError:
                    error_msg = response.text or error_msg

                logger.error(f"API error: {error_msg}")
                raise APIException(
                    error_msg,
                    status_code=response.status_code,
                    response_data=response_data,
                )

            return response.json()

        except AuthenticationException:
            raise
        except APIException:
            raise
        except requests.exceptions.ConnectionError as e:
            raise NetworkException("Connection error - Cannot reach OnGrid API") from e
        except requests.exceptions.Timeout as e:
            raise NetworkException("Request timeout - OnGrid API not responding") from e
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Request failed: {str(e)}") from e
        except ValueError as e:
            raise APIException("Invalid JSON response from API") from e

    def build_form_data(
        self, required_fields: Dict[str, Any], optional_fields: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build form data dictionary from required and optional fields.

        Args:
            required_fields: Dictionary of required field name-value pairs
            optional_fields: Dictionary of optional field name-value pairs

        Returns:
            Dictionary with all non-None fields
        """
        form_data = required_fields.copy()

        for key, value in optional_fields.items():
            if value is not None:
                form_data[key] = value

        return form_data

    @contextmanager
    def handle_api_exceptions(self, operation: str):
        """
        Context manager for handling API exceptions consistently.

        Args:
            operation: Name of the operation being performed

        Usage:
            with http_client.handle_api_exceptions("add document"):
                # API call code
        """
        try:
            yield
        except (ValidationException, AuthenticationException, APIException, NetworkException):
            raise
        except OnGridException:
            raise
        except Exception as e:
            logger.exception(f"Unexpected error while {operation}")
            raise OnGridException(f"Failed to {operation}: {str(e)}") from e

    def prepare_multiple_files(
        self, file_paths: Dict[str, Optional[str]]
    ) -> Dict[str, tuple]:
        """
        Prepare multiple files for upload.

        Args:
            file_paths: Dictionary mapping file keys to file paths

        Returns:
            Dictionary with file data ready for requests
        """
        files = {}
        for key, path in file_paths.items():
            if path:
                files[key] = (
                    os.path.basename(path),
                    open(path, "rb"),
                    "application/octet-stream",
                )
        return files

    def close_files(self, files: Dict[str, tuple]) -> None:
        """
        Close all open file handles.

        Args:
            files: Dictionary of file tuples from prepare_multiple_files
        """
        for file_tuple in files.values():
            file_tuple[1].close()
