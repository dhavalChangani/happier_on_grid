"""
Test script for OnGrid document verification using test patterns.

This script demonstrates how to test different verification scenarios
in staging environment using customized field values.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add parent directory to path to import ongrid module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ongrid import OnGridClient
from ongrid.enums import Gender

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VerificationTester:
    """Test harness for document verification scenarios."""

    def __init__(self):
        """Initialize the verification tester."""
        self.client = OnGridClient(
            community_id=os.getenv("ONGRID_COMMUNITY_ID", ""),
            enable_logging=True
        )

    def onboard_test_candidate(
        self,
        name: str = "Test User",
        fathers_name: str = "Test Father",
        email: str = "test@example.com",
        phone: str = "9876543210",
    ) -> Optional[Dict[str, Any]]:
        """
        Onboard a test candidate.

        Args:
            name: Candidate name (customize for PCC testing)
            fathers_name: Father's name (customize for GDC/PVLF/CCRV testing)
            email: Email address
            phone: Phone number

        Returns:
            Onboarding response or None if failed
        """
        candidate_data = {
            "name": name,
            "fathers_name": fathers_name,
            "email": email,
            "phone": phone,
            "gender": Gender.MALE.value,
            "profession_id": 1,
            "city": "Mumbai",
            "has_consent": True,
        }

        logger.info(f"Onboarding candidate: {name}")
        response = self.client.onboard_candidate(candidate_data)

        if response["success"]:
            logger.info(f"✓ Candidate onboarded: ID={response['data']['id']}")
            return response["data"]
        else:
            logger.error(f"✗ Onboarding failed: {response['message']}")
            return None

    def add_pan_document(
        self,
        individual_id: int,
        name_as_per_document: str,
        document_uid: str = "AAAAA1111A",
    ) -> Optional[Dict[str, Any]]:
        """
        Add PAN document for testing.

        Args:
            individual_id: Individual's ID
            name_as_per_document: Name (customize for PANV: CMP::VER::Name)
            document_uid: PAN number (customize for CC: BBBBB2222B for success)

        Returns:
            Document response or None if failed
        """
        logger.info(f"Adding PAN document: {document_uid}")
        
        # Create a dummy file for testing (OnGrid requires file upload)
        # In real scenarios, you would provide actual document file path
        dummy_file_url = "https://example.com/dummy_pan.pdf"
        
        response = self.client.add_pan_document(
            individual_id=individual_id,
            file_path=dummy_file_url,
            document_uid=document_uid,
            name_as_per_document=name_as_per_document,
        )

        if response["success"]:
            logger.info(f"✓ PAN document added: ID={response['data']['id']}")
            return response["data"]
        else:
            logger.error(f"✗ Failed to add PAN: {response['message']}")
            return None

    def add_address(
        self,
        individual_id: int,
        address_line: str,
        address_type: str = "current",
    ) -> Optional[int]:
        """
        Add address for testing.

        Args:
            individual_id: Individual's ID
            address_line: Address (customize for LAV/PAV: CMP::VER::Address)
            address_type: 'current' or 'permanent'

        Returns:
            Address ID or None if failed
        """
        logger.info(f"Adding {address_type} address (simulated)")
        logger.warning(
            f"⚠ Address addition not yet implemented in client. "
            f"Using individual_id={individual_id} as placeholder address_id"
        )
        # Note: The OnGrid client doesn't expose add_address methods yet
        # For testing purposes, we'll use a placeholder
        return individual_id

    def request_pan_verification_test(
        self, individual_id: int, document_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Request PAN verification.

        Args:
            individual_id: Individual's ID
            document_id: Document ID

        Returns:
            Verification response or None if failed
        """
        logger.info(f"Requesting PAN verification")

        response = self.client.request_pan_verification(individual_id, document_id)

        if response["success"]:
            logger.info(f"✓ PAN verification request created: ID={response['data']['id']}")
            return response["data"]
        else:
            logger.error(f"✗ Verification failed: {response['message']}")
            return None

    def check_pan_status(
        self, individual_id: int, request_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Check PAN verification status.

        Args:
            individual_id: Individual's ID
            request_id: Verification request ID

        Returns:
            Status response or None if failed
        """
        logger.info(f"Checking status for PAN verification request {request_id}")
        response = self.client.get_pan_verification_status(individual_id, request_id)

        if response["success"]:
            status = response["data"].get("status", "unknown")
            result = response["data"].get("result", "N/A")
            logger.info(f"✓ Status: {status}, Result: {result}")
            return response["data"]
        else:
            logger.error(f"✗ Status check failed: {response['message']}")
            return None


def test_pan_verification_success():
    """Test PANV with success result using CMP::VER pattern."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: PAN Verification - Success Scenario")
    logger.info("=" * 60)

    tester = VerificationTester()

    # Onboard candidate
    candidate = tester.onboard_test_candidate(
        name="John Doe",
        email="john.doe@test.com",
        phone="9876543210",
    )
    if not candidate:
        return

    # Add PAN with success pattern: CMP::VER::Name
    pan_doc = tester.add_pan_document(
        individual_id=candidate["id"],
        name_as_per_document="CMP::VER::John Doe",
        document_uid="ABCDE1234F",
    )
    if not pan_doc:
        return

    # Request PANV
    verification = tester.request_pan_verification_test(
        individual_id=candidate["id"],
        document_id=pan_doc["id"],
    )
    if not verification:
        return

    # Check status
    tester.check_pan_status(candidate["id"], verification["id"])


def test_pan_verification_invalid():
    """Test PANV with invalid result using CMP::INV pattern."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: PAN Verification - Invalid Scenario")
    logger.info("=" * 60)

    tester = VerificationTester()

    candidate = tester.onboard_test_candidate(
        name="Jane Smith",
        email="jane.smith@test.com",
        phone="9876543211",
    )
    if not candidate:
        return

    # Add PAN with invalid pattern: CMP::INV::Name
    pan_doc = tester.add_pan_document(
        individual_id=candidate["id"],
        name_as_per_document="CMP::INV::Jane Smith",
        document_uid="XXXXX9999X",
    )
    if not pan_doc:
        return

    verification = tester.request_pan_verification_test(
        individual_id=candidate["id"],
        document_id=pan_doc["id"],
    )
    if not verification:
        return

    tester.check_pan_status(candidate["id"], verification["id"])


def test_address_verification_success():
    """Test LAV with verified result using CMP::VER pattern (placeholder)."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Local Address Verification - Success Scenario (Skipped)")
    logger.info("=" * 60)

    logger.warning("⚠ Address verification test skipped - not yet implemented in client")
    logger.info("To test address verification, use the Testing.md guide to customize:")
    logger.info("  - currentAddress field with pattern: CMP::VER::Address")
    logger.info("  - Then request LAV/LADV/LAPV verification via API")


def test_insufficiency_scenario():
    """Test insufficiency scenario using INSUF pattern."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST: PAN Verification - Insufficiency Scenario")
    logger.info("=" * 60)

    tester = VerificationTester()

    candidate = tester.onboard_test_candidate(
        name="Sarah Williams",
        email="sarah.williams@test.com",
        phone="9876543213",
    )
    if not candidate:
        return

    # Add PAN with insufficiency pattern: INSUF::132::15::Name
    pan_doc = tester.add_pan_document(
        individual_id=candidate["id"],
        name_as_per_document="INSUF::132::15::Sarah Williams",
        document_uid="SSSSS5555S",
    )
    if not pan_doc:
        return

    verification = tester.request_pan_verification_test(
        individual_id=candidate["id"],
        document_id=pan_doc["id"],
    )
    if not verification:
        return

    tester.check_pan_status(candidate["id"], verification["id"])


def main():
    """Run all test scenarios."""
    logger.info("\n" + "🚀 " * 30)
    logger.info("STARTING ONGRID VERIFICATION TESTING")
    logger.info("Environment: STAGING ONLY")
    logger.info("🚀 " * 30)

    try:
        # Run test scenarios
        test_pan_verification_success()
        test_pan_verification_invalid()
        test_address_verification_success()
        test_insufficiency_scenario()

        logger.info("\n" + "✅ " * 30)
        logger.info("ALL TESTS COMPLETED")
        logger.info("✅ " * 30 + "\n")

    except Exception as e:
        logger.error(f"\n❌ Test execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
