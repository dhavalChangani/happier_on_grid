"""
Example: How to integrate OnGridClient into happierWork

This file shows how happierWork team can use the OnGridClient class
in their existing codebase for background verification.
"""

from ongrid_client import OnGridClient, OnGridException
import os


# ============================================================================
# SETUP: Initialize the client (do this once in your application)
# ============================================================================

# Option 1: Initialize with API key directly
ongrid_client = OnGridClient(
    api_key=os.getenv("ONGRID_API_KEY"),
    base_url="https://api.ongrid.in"  # Use sandbox URL for testing
)

# Option 2: Initialize in your Django/Flask app
# In settings.py or config.py:
# ONGRID_CLIENT = OnGridClient(api_key=settings.ONGRID_API_KEY)


# ============================================================================
# EXAMPLE 1: Simple Onboarding (Most Common Use Case)
# ============================================================================

def onboard_new_employee(employee):
    """
    Called when a new employee is hired
    This is the simplest way to integrate - just call onboard_candidate()
    """
    try:
        result = ongrid_client.onboard_candidate(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            mobile=employee.mobile,
            date_of_birth=employee.date_of_birth.strftime("%Y-%m-%d"),
            address={
                "line1": employee.address_line1,
                "line2": employee.address_line2,
                "city": employee.city,
                "state": employee.state,
                "pincode": employee.pincode,
                "country": "India"
            },
            verification_types=["identity", "address", "education"],
            reference_id=f"HW-EMP-{employee.id}"
        )
        
        if result['success']:
            # Save verification details to your database
            employee.ongrid_verification_id = result['verification_id']
            employee.ongrid_candidate_id = result['candidate_id']
            employee.bgv_status = 'in_progress'
            employee.save()
            
            print(f"✅ Verification initiated for {employee.email}")
            print(f"   Verification ID: {result['verification_id']}")
            return True
        else:
            print(f"❌ Failed: {result['error']}")
            return False
            
    except OnGridException as e:
        print(f"❌ OnGrid error: {e}")
        return False


# ============================================================================
# EXAMPLE 2: Django Model Integration
# ============================================================================

"""
Add this to your Employee model in models.py:

class Employee(models.Model):
    # Your existing fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    
    # Add these fields for OnGrid integration
    ongrid_candidate_id = models.CharField(max_length=100, null=True, blank=True)
    ongrid_verification_id = models.CharField(max_length=100, null=True, blank=True)
    bgv_status = models.CharField(max_length=50, default='pending')
    bgv_result = models.CharField(max_length=50, null=True, blank=True)
    bgv_report_url = models.URLField(null=True, blank=True)
    bgv_initiated_at = models.DateTimeField(null=True, blank=True)
    bgv_completed_at = models.DateTimeField(null=True, blank=True)
    
    def initiate_background_verification(self):
        '''Initiate background verification for this employee'''
        from django.utils import timezone
        from ongrid_client import OnGridClient
        import os
        
        client = OnGridClient(api_key=os.getenv("ONGRID_API_KEY"))
        
        result = client.onboard_candidate(
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            mobile=self.mobile,
            date_of_birth=self.date_of_birth.strftime("%Y-%m-%d"),
            address={
                "line1": self.address_line1,
                "city": self.city,
                "state": self.state,
                "pincode": self.pincode
            },
            verification_types=["identity", "address"],
            reference_id=f"HW-EMP-{self.id}"
        )
        
        if result['success']:
            self.ongrid_candidate_id = result['candidate_id']
            self.ongrid_verification_id = result['verification_id']
            self.bgv_status = 'in_progress'
            self.bgv_initiated_at = timezone.now()
            self.save()
            return True
        return False
    
    def get_verification_status(self):
        '''Get current verification status'''
        if not self.ongrid_verification_id:
            return None
        
        from ongrid_client import OnGridClient
        import os
        
        client = OnGridClient(api_key=os.getenv("ONGRID_API_KEY"))
        
        try:
            status = client.get_verification_status(self.ongrid_verification_id)
            
            # Update status
            self.bgv_status = status['overall_status']
            
            if status['overall_status'] == 'completed':
                self.bgv_completed_at = timezone.now()
                # Get report
                report = client.get_verification_report(self.ongrid_verification_id)
                self.bgv_result = report.get('overall_result')
                self.bgv_report_url = report.get('report_url')
            
            self.save()
            return status
        except OnGridException as e:
            print(f"Error getting status: {e}")
            return None
"""


# ============================================================================
# EXAMPLE 3: Django View Integration
# ============================================================================

"""
Add this to your views.py:

from django.http import JsonResponse
from django.views import View
from ongrid_client import OnGridClient
import os

class InitiateVerificationView(View):
    '''API endpoint to initiate verification'''
    
    def post(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            
            # Check if already initiated
            if employee.ongrid_verification_id:
                return JsonResponse({
                    'success': False,
                    'message': 'Verification already initiated'
                }, status=400)
            
            # Initiate verification
            if employee.initiate_background_verification():
                return JsonResponse({
                    'success': True,
                    'message': 'Verification initiated successfully',
                    'verification_id': employee.ongrid_verification_id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to initiate verification'
                }, status=500)
                
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Employee not found'
            }, status=404)


class VerificationStatusView(View):
    '''API endpoint to get verification status'''
    
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            
            if not employee.ongrid_verification_id:
                return JsonResponse({
                    'success': False,
                    'message': 'No verification initiated'
                }, status=404)
            
            status = employee.get_verification_status()
            
            if status:
                return JsonResponse({
                    'success': True,
                    'data': {
                        'verification_id': employee.ongrid_verification_id,
                        'status': employee.bgv_status,
                        'result': employee.bgv_result,
                        'progress': status.get('progress', 0),
                        'report_url': employee.bgv_report_url
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Failed to get status'
                }, status=500)
                
        except Employee.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Employee not found'
            }, status=404)
"""


# ============================================================================
# EXAMPLE 4: Webhook Handler (Receive status updates from OnGrid)
# ============================================================================

"""
Add this webhook handler to receive automatic updates:

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def ongrid_webhook(request):
    '''Handle webhook callbacks from OnGrid'''
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Extract information
        event_type = data.get('event')
        verification_id = data.get('verification_id')
        reference_id = data.get('reference_id')
        status = data.get('status')
        result = data.get('result')
        
        # Find employee by reference_id
        if reference_id and reference_id.startswith('HW-EMP-'):
            employee_id = int(reference_id.replace('HW-EMP-', ''))
            employee = Employee.objects.get(id=employee_id)
            
            # Update employee record
            employee.bgv_status = status
            
            if status == 'completed':
                employee.bgv_result = result
                employee.bgv_completed_at = timezone.now()
                
                # Notify HR team
                send_verification_completed_email(employee)
            
            employee.save()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
"""


# ============================================================================
# EXAMPLE 5: Bulk Processing
# ============================================================================

def bulk_initiate_verifications(employee_ids):
    """
    Initiate verifications for multiple employees
    """
    results = {
        'success': [],
        'failed': []
    }
    
    for emp_id in employee_ids:
        try:
            employee = get_employee(emp_id)  # Your function to get employee
            
            result = ongrid_client.onboard_candidate(
                first_name=employee.first_name,
                last_name=employee.last_name,
                email=employee.email,
                mobile=employee.mobile,
                date_of_birth=employee.date_of_birth.strftime("%Y-%m-%d"),
                address={
                    "line1": employee.address_line1,
                    "city": employee.city,
                    "state": employee.state,
                    "pincode": employee.pincode
                },
                verification_types=["identity", "address"],
                reference_id=f"HW-EMP-{employee.id}"
            )
            
            if result['success']:
                results['success'].append({
                    'employee_id': emp_id,
                    'verification_id': result['verification_id']
                })
            else:
                results['failed'].append({
                    'employee_id': emp_id,
                    'error': result.get('error')
                })
                
        except Exception as e:
            results['failed'].append({
                'employee_id': emp_id,
                'error': str(e)
            })
    
    return results


# ============================================================================
# EXAMPLE 6: Check Verification Status
# ============================================================================

def check_employee_verification_status(employee_id):
    """
    Check and update verification status for an employee
    """
    employee = get_employee(employee_id)
    
    if not employee.ongrid_verification_id:
        return {'error': 'No verification initiated'}
    
    try:
        status = ongrid_client.get_verification_status(
            employee.ongrid_verification_id
        )
        
        # Update employee record
        employee.bgv_status = status['overall_status']
        employee.save()
        
        # If completed, get the report
        if status['overall_status'] == 'completed':
            report = ongrid_client.get_verification_report(
                employee.ongrid_verification_id
            )
            
            employee.bgv_result = report['overall_result']
            employee.bgv_report_url = report['report_url']
            employee.save()
            
            return {
                'status': 'completed',
                'result': report['overall_result'],
                'report_url': report['report_url']
            }
        
        return {
            'status': status['overall_status'],
            'progress': status.get('progress', 0)
        }
        
    except OnGridException as e:
        return {'error': str(e)}


# ============================================================================
# EXAMPLE 7: Celery Task (Async Processing)
# ============================================================================

"""
If you use Celery for async tasks:

from celery import shared_task
from ongrid_client import OnGridClient
import os

@shared_task
def initiate_verification_task(employee_id):
    '''Async task to initiate verification'''
    try:
        employee = Employee.objects.get(id=employee_id)
        
        client = OnGridClient(api_key=os.getenv("ONGRID_API_KEY"))
        
        result = client.onboard_candidate(
            first_name=employee.first_name,
            last_name=employee.last_name,
            email=employee.email,
            mobile=employee.mobile,
            date_of_birth=employee.date_of_birth.strftime("%Y-%m-%d"),
            address={
                "line1": employee.address_line1,
                "city": employee.city,
                "state": employee.state,
                "pincode": employee.pincode
            },
            verification_types=["identity", "address"],
            reference_id=f"HW-EMP-{employee.id}"
        )
        
        if result['success']:
            employee.ongrid_verification_id = result['verification_id']
            employee.bgv_status = 'in_progress'
            employee.save()
            return {'success': True, 'verification_id': result['verification_id']}
        else:
            return {'success': False, 'error': result['error']}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}


# Usage:
# initiate_verification_task.delay(employee_id=123)
"""


# ============================================================================
# EXAMPLE 8: Management Command
# ============================================================================

"""
Create a Django management command:
File: management/commands/initiate_bgv.py

from django.core.management.base import BaseCommand
from ongrid_client import OnGridClient
import os

class Command(BaseCommand):
    help = 'Initiate background verification for employees'
    
    def add_arguments(self, parser):
        parser.add_argument('employee_ids', nargs='+', type=int)
    
    def handle(self, *args, **options):
        client = OnGridClient(api_key=os.getenv("ONGRID_API_KEY"))
        
        for emp_id in options['employee_ids']:
            try:
                employee = Employee.objects.get(id=emp_id)
                
                result = client.onboard_candidate(
                    first_name=employee.first_name,
                    last_name=employee.last_name,
                    email=employee.email,
                    mobile=employee.mobile,
                    date_of_birth=employee.date_of_birth.strftime("%Y-%m-%d"),
                    address={
                        "line1": employee.address_line1,
                        "city": employee.city,
                        "state": employee.state,
                        "pincode": employee.pincode
                    },
                    verification_types=["identity", "address"],
                    reference_id=f"HW-EMP-{emp_id}"
                )
                
                if result['success']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Verification initiated for employee {emp_id}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ Failed for employee {emp_id}: {result["error"]}'
                        )
                    )
                    
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Employee {emp_id} not found')
                )

# Usage:
# python manage.py initiate_bgv 123 456 789
"""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_employee(employee_id):
    """Dummy function - replace with your actual implementation"""
    # This would be your actual employee retrieval logic
    # e.g., return Employee.objects.get(id=employee_id)
    pass


def send_verification_completed_email(employee):
    """Dummy function - replace with your actual implementation"""
    # Send email to HR when verification is complete
    pass


if __name__ == "__main__":
    print("This file contains examples. Import and use in your application.")
