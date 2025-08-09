import requests
import sys
import os
from datetime import datetime

class PDFFormFillerAPITester:
    def __init__(self, base_url="https://a3470659-73f8-45a3-9f38-48507dd91610.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    # For file uploads, don't set Content-Type header
                    response = requests.post(url, data=data, files=files)
                else:
                    headers['Content-Type'] = 'application/json'
                    response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        print(f"Response: {response.json()}")
                    except:
                        print("Response: Non-JSON content")
                else:
                    print(f"Response Content-Type: {response.headers.get('content-type', 'Unknown')}")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Error Response: {response.text}")
                except:
                    print("Could not read error response")

            return success, response

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_parse_data(self):
        """Test data parsing endpoint"""
        test_data = {
            "raw_data": """Last Name: ALSQOUR
First Name: NAEL OMAR MOHAMMAD
Middle Name: [Leave Blank]
Current Address: 3100 Van Buren Blvd Apt 611, Riverside, CA 92503
Mobile Phone: +1 (832) 757-3013
Position Applying For: Driver
Salary Desired: $20/hour"""
        }
        
        success, response = self.run_test(
            "Parse Personal Data",
            "POST",
            "parse-data",
            200,
            data=test_data
        )
        return success

    def test_fill_form(self):
        """Test PDF form filling with actual file"""
        pdf_path = "/app/content.pdf"
        
        if not os.path.exists(pdf_path):
            print(f"❌ PDF file not found at {pdf_path}")
            return False
            
        personal_data = """Last Name: ALSQOUR
First Name: NAEL OMAR MOHAMMAD
Middle Name: [Leave Blank]
Other Names Used: [Leave Blank]
Current Address: 3100 Van Buren Blvd Apt 611, Riverside, CA 92503
Home Phone: [Leave Blank]
Mobile Phone: +1 (832) 757-3013
Email: [Leave Blank]
Driver's License #: W9493684
How did you hear about us?: Friend referral
Worked at company before?: No
Relatives working here?: No
Proof of right to work in U.S.: Yes
Are you 18 or older?: Yes
Terminated before?: No
Can work any shift?: Yes
Can work overtime/weekends?: Yes
Position Applying For: Driver
Salary Desired: $20/hour
Special Skills/Training: College educated in Jordan; fluent in Arabic & English; proficient in Word; experienced with Uber, Lyft, DoorDash, student transportation apps
College: University in Jordan
Field of Study: Business/General
Degree: Bachelor's
Year Received: 2008
Other Skills: Transportation apps, navigation, rideshare & delivery platforms
Languages Speak: Arabic, English
Languages Read: Arabic, English
Languages Write: Arabic, English
License Type: Driver License
License Number: W9493684
State: CA
Expiration: 11/20/2028
CPR/BLS Certified: No
Employer #1: Upland Furniture LLC, 735 S Cactus Ave, Upland, CA 91786 — From 09/01/2024 to 09/30/2024 — Full-Time — May Contact: Yes — Supervisor: N/A — Position: Delivery Driver — Reason: Left for higher pay in apps
Employer #2: Self-Employed – Uber, Lyft, DoorDash, Student Transportation — From 10/2024 to Present — Full-Time — Position: Passenger transport, rideshare, deliveries — Reason: Current"""

        try:
            with open(pdf_path, 'rb') as pdf_file:
                files = {'file': ('content.pdf', pdf_file, 'application/pdf')}
                data = {'data': personal_data}
                
                success, response = self.run_test(
                    "Fill PDF Form",
                    "POST",
                    "fill-form",
                    200,
                    data=data,
                    files=files
                )
                
                if success and response:
                    # Check if we got a PDF response
                    content_type = response.headers.get('content-type', '')
                    if 'application/pdf' in content_type:
                        print(f"✅ Received PDF response ({len(response.content)} bytes)")
                        return True
                    else:
                        print(f"❌ Expected PDF, got {content_type}")
                        return False
                        
        except Exception as e:
            print(f"❌ Error reading PDF file: {str(e)}")
            return False
            
        return success

    def test_send_email_validation(self):
        """Test email endpoint validation (without actual sending)"""
        # Test with missing email configuration (should fail gracefully)
        email_data = {
            "recipient_email": "test@example.com",
            "subject": "Test Form",
            "message": "Test message",
            "session_id": "invalid-session-id"
        }
        
        success, response = self.run_test(
            "Send Email Validation",
            "POST",
            "send-email",
            400,  # Expecting 400 due to missing email config
            data=email_data
        )
        return success

def main():
    print("🚀 Starting PDF Form Filler API Tests")
    print("=" * 50)
    
    # Setup
    tester = PDFFormFillerAPITester()
    
    # Run tests in order
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Parse Data", tester.test_parse_data),
        ("Fill Form", tester.test_fill_form),
        ("Email Validation", tester.test_send_email_validation),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {str(e)}")
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check backend implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())