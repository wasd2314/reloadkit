import requests
import sys
import json
from datetime import datetime

class SoftwareHubAPITester:
    def __init__(self, base_url="https://one-click-apps.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, description=""):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        if description:
            print(f"   Description: {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_data": None,
                "error": None
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    result["error"] = error_data
                    print(f"   Error: {error_data}")
                except:
                    result["error"] = response.text
                    print(f"   Error: {response.text}")

            self.test_results.append(result)
            return success, result["response_data"] if success else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            result = {
                "test_name": name,
                "method": method,
                "endpoint": endpoint,
                "expected_status": expected_status,
                "actual_status": None,
                "success": False,
                "response_data": None,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200,
            description="Check if API is accessible"
        )

    def test_get_apps(self):
        """Test getting all apps"""
        success, response = self.run_test(
            "Get All Apps",
            "GET",
            "apps",
            200,
            description="Fetch all seeded apps"
        )
        
        if success and isinstance(response, list):
            print(f"   Found {len(response)} apps")
            if len(response) >= 10:
                print("   ✅ Expected 10 apps found")
            else:
                print(f"   ⚠️  Expected 10 apps, found {len(response)}")
        
        return success, response

    def test_get_stats(self):
        """Test getting statistics"""
        success, response = self.run_test(
            "Get Statistics",
            "GET",
            "stats",
            200,
            description="Check total apps and downloads count"
        )
        
        if success:
            print(f"   Total Apps: {response.get('total_apps', 'N/A')}")
            print(f"   Total Downloads: {response.get('total_downloads', 'N/A')}")
        
        return success, response

    def test_create_app(self):
        """Test creating a new app"""
        test_app = {
            "name": "Test App",
            "category": "Other",
            "icon_name": "FaTest",
            "description": "A test application for API testing",
            "url": "https://example.com/download"
        }
        
        success, response = self.run_test(
            "Create New App",
            "POST",
            "apps",
            200,
            data=test_app,
            description="Create a test app"
        )
        
        if success:
            print(f"   Created app with ID: {response.get('id', 'N/A')}")
            return success, response.get('id')
        
        return success, None

    def test_download_increment(self, app_id):
        """Test incrementing download count"""
        if not app_id:
            print("❌ Skipping download test - no app ID provided")
            return False, {}
            
        success, response = self.run_test(
            "Increment Download Count",
            "POST",
            f"apps/{app_id}/download",
            200,
            description=f"Increment download count for app {app_id}"
        )
        
        if success:
            print(f"   New download count: {response.get('download_count', 'N/A')}")
        
        return success, response

    def test_update_app(self, app_id):
        """Test updating an app"""
        if not app_id:
            print("❌ Skipping update test - no app ID provided")
            return False, {}
            
        update_data = {
            "description": "Updated test application description"
        }
        
        success, response = self.run_test(
            "Update App",
            "PUT",
            f"apps/{app_id}",
            200,
            data=update_data,
            description=f"Update app {app_id}"
        )
        
        return success, response

    def test_delete_app(self, app_id):
        """Test deleting an app"""
        if not app_id:
            print("❌ Skipping delete test - no app ID provided")
            return False, {}
            
        success, response = self.run_test(
            "Delete App",
            "DELETE",
            f"apps/{app_id}",
            200,
            description=f"Delete app {app_id}"
        )
        
        return success, response

    def test_delete_nonexistent_app(self):
        """Test deleting a non-existent app"""
        fake_id = "non-existent-id-12345"
        success, response = self.run_test(
            "Delete Non-existent App",
            "DELETE",
            f"apps/{fake_id}",
            404,
            description="Should return 404 for non-existent app"
        )
        
        return success, response

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Software Download Hub API Tests")
        print("=" * 60)
        
        # Test basic connectivity
        self.test_root_endpoint()
        
        # Test getting apps and stats
        apps_success, apps_data = self.test_get_apps()
        self.test_get_stats()
        
        # Test CRUD operations
        create_success, test_app_id = self.test_create_app()
        
        if test_app_id:
            # Test download increment
            self.test_download_increment(test_app_id)
            
            # Test update
            self.test_update_app(test_app_id)
            
            # Test delete
            self.test_delete_app(test_app_id)
        
        # Test error handling
        self.test_delete_nonexistent_app()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            failed_tests = [test for test in self.test_results if not test["success"]]
            print(f"\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test.get('error', 'Unknown error')}")
            return 1

def main():
    tester = SoftwareHubAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())