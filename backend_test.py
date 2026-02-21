#!/usr/bin/env python3
"""
Telegram Intelligence Platform Backend API Tests
Tests all endpoints for the Telegram Intelligence module
"""
import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, List

class TelegramIntelAPITester:
    def __init__(self, base_url="https://telegram-module-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.passed_tests = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            self.passed_tests.append(name)
            print(f"✅ {name} - PASSED")
        else:
            self.failed_tests.append({"name": name, "details": details})
            print(f"❌ {name} - FAILED: {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> tuple:
        """Make HTTP request and return (success, response_data, status_code)"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                return False, {}, 0
            
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}
            
            return success, response_data, response.status_code
        except Exception as e:
            return False, {"error": str(e)}, 0

    def test_basic_health(self):
        """Test basic API health endpoints"""
        print("\n🔍 Testing Basic Health Endpoints...")
        
        # Test root API
        success, data, status = self.make_request('GET', '/api/')
        self.log_test("API Root", success and data.get("status") == "operational")
        
        # Test health endpoint
        success, data, status = self.make_request('GET', '/api/health')
        self.log_test("API Health", success and data.get("status") == "healthy")
        
        # Test Telegram Intel health
        success, data, status = self.make_request('GET', '/api/telegram-intel/health')
        self.log_test("Telegram Intel Health", success and data.get("ok") == True)

    def test_utility_list_endpoint(self):
        """Test GET /api/telegram-intel/utility/list with various filters"""
        print("\n🔍 Testing Utility List Endpoint...")
        
        # Basic list request
        success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list')
        has_items = success and data.get("ok") == True and len(data.get("items", [])) > 0
        self.log_test("Utility List - Basic", has_items, f"Got {len(data.get('items', []))} items")
        
        if has_items:
            # Test with search query
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?q=crypto')
            self.log_test("Utility List - Search Query", success and data.get("ok") == True)
            
            # Test with type filter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?type=channel')
            self.log_test("Utility List - Type Filter", success and data.get("ok") == True)
            
            # Test with member filter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?minMembers=1000')
            self.log_test("Utility List - Members Filter", success and data.get("ok") == True)
            
            # Test with growth filter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?minGrowth7=5')
            self.log_test("Utility List - Growth Filter", success and data.get("ok") == True)
            
            # Test with activity filter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?activity=High')
            self.log_test("Utility List - Activity Filter", success and data.get("ok") == True)
            
            # Test with red flags filter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?maxRedFlags=2')
            self.log_test("Utility List - Red Flags Filter", success and data.get("ok") == True)
            
            # Test with sort parameter
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?sort=growth')
            self.log_test("Utility List - Sort by Growth", success and data.get("ok") == True)
            
            # Test pagination
            success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?page=1&limit=5')
            has_pagination = success and data.get("ok") == True and data.get("page") == 1
            self.log_test("Utility List - Pagination", has_pagination)

    def test_channel_overview_endpoint(self):
        """Test GET /api/telegram-intel/channel/:username/overview"""
        print("\n🔍 Testing Channel Overview Endpoint...")
        
        # First get a channel username from the list
        success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?limit=1')
        if success and data.get("items"):
            username = data["items"][0]["username"]
            
            # Test channel overview
            success, overview_data, status = self.make_request('GET', f'/api/telegram-intel/channel/{username}/overview')
            has_overview = success and overview_data.get("ok") == True
            self.log_test("Channel Overview - Valid Channel", has_overview)
            
            if has_overview:
                # Verify required fields
                required_fields = ["profile", "topCards", "aiSummary", "metrics"]
                all_fields_present = all(field in overview_data for field in required_fields)
                self.log_test("Channel Overview - Required Fields", all_fields_present)
                
                # Test profile data
                profile = overview_data.get("profile", {})
                has_profile = profile.get("username") == username
                self.log_test("Channel Overview - Profile Data", has_profile)
        else:
            self.log_test("Channel Overview - No Channels Available", False, "No channels found in utility list")

    def test_channel_refresh_endpoint(self):
        """Test POST /api/telegram-intel/channel/:username/refresh"""
        print("\n🔍 Testing Channel Refresh Endpoint...")
        
        # Get a channel username
        success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?limit=1')
        if success and data.get("items"):
            username = data["items"][0]["username"]
            
            # Test refresh
            success, refresh_data, status = self.make_request('POST', f'/api/telegram-intel/channel/{username}/refresh')
            refresh_success = success and refresh_data.get("ok") == True
            self.log_test("Channel Refresh - Valid Channel", refresh_success)
            
            if refresh_success:
                # Verify refresh response fields
                has_status = "status" in refresh_data
                has_username = refresh_data.get("username") == username
                self.log_test("Channel Refresh - Response Fields", has_status and has_username)
        else:
            self.log_test("Channel Refresh - No Channels Available", False, "No channels found")

    def test_compare_channels_endpoint(self):
        """Test GET /api/telegram-intel/compare?left=x&right=y"""
        print("\n🔍 Testing Compare Channels Endpoint...")
        
        # Get two channel usernames
        success, data, status = self.make_request('GET', '/api/telegram-intel/utility/list?limit=2')
        if success and len(data.get("items", [])) >= 2:
            left_channel = data["items"][0]["username"]
            right_channel = data["items"][1]["username"]
            
            # Test compare
            success, compare_data, status = self.make_request('GET', f'/api/telegram-intel/compare?left={left_channel}&right={right_channel}')
            compare_success = success and compare_data.get("ok") == True
            self.log_test("Compare Channels - Valid Channels", compare_success)
            
            if compare_success:
                # Verify compare response structure
                has_left = "left" in compare_data
                has_right = "right" in compare_data
                has_diffs = "diffs" in compare_data
                self.log_test("Compare Channels - Response Structure", has_left and has_right and has_diffs)
        else:
            self.log_test("Compare Channels - Insufficient Channels", False, "Need at least 2 channels")

    def test_pipeline_status_endpoint(self):
        """Test GET /api/telegram-intel/admin/pipeline/status"""
        print("\n🔍 Testing Pipeline Status Endpoint...")
        
        success, data, status = self.make_request('GET', '/api/telegram-intel/admin/pipeline/status')
        pipeline_success = success and data.get("ok") == True
        self.log_test("Pipeline Status - Basic", pipeline_success)
        
        if pipeline_success:
            # Verify status fields
            status_data = data.get("status", {})
            has_channels = "totalChannels" in status_data
            has_posts = "totalPosts" in status_data
            has_mode = "mode" in status_data
            self.log_test("Pipeline Status - Required Fields", has_channels and has_posts and has_mode)

    def test_seed_channels_endpoint(self):
        """Test POST /api/telegram-intel/admin/seed"""
        print("\n🔍 Testing Seed Channels Endpoint...")
        
        success, data, status = self.make_request('POST', '/api/telegram-intel/admin/seed')
        seed_success = success and data.get("ok") == True
        self.log_test("Seed Channels - Basic", seed_success)
        
        if seed_success:
            # Verify seed response
            has_seeded = "seeded" in data
            has_total = "total" in data
            self.log_test("Seed Channels - Response Fields", has_seeded and has_total)

    def test_watchlist_endpoints(self):
        """Test watchlist CRUD operations"""
        print("\n🔍 Testing Watchlist Endpoints...")
        
        # Get watchlist
        success, data, status = self.make_request('GET', '/api/telegram-intel/watchlist')
        watchlist_success = success and data.get("ok") == True
        self.log_test("Watchlist - Get List", watchlist_success)
        
        # Add to watchlist
        test_username = "test_channel"
        success, data, status = self.make_request('POST', '/api/telegram-intel/watchlist', 
                                                {"username": test_username, "notes": "Test channel"})
        add_success = success and data.get("ok") == True
        self.log_test("Watchlist - Add Channel", add_success)
        
        # Check if in watchlist
        success, data, status = self.make_request('GET', f'/api/telegram-intel/watchlist/check/{test_username}')
        check_success = success and data.get("ok") == True and data.get("inWatchlist") == True
        self.log_test("Watchlist - Check Channel", check_success)
        
        # Remove from watchlist
        success, data, status = self.make_request('DELETE', f'/api/telegram-intel/watchlist/{test_username}')
        remove_success = success and data.get("ok") == True
        self.log_test("Watchlist - Remove Channel", remove_success)

    def test_legacy_endpoints(self):
        """Test legacy intel endpoints for backward compatibility"""
        print("\n🔍 Testing Legacy Intel Endpoints...")
        
        # Test intel list
        success, data, status = self.make_request('GET', '/api/telegram-intel/intel/list')
        intel_success = success and data.get("ok") == True
        self.log_test("Legacy Intel List", intel_success)
        
        # Test channel full data
        success, list_data, status = self.make_request('GET', '/api/telegram-intel/utility/list?limit=1')
        if success and list_data.get("items"):
            username = list_data["items"][0]["username"]
            success, data, status = self.make_request('GET', f'/api/telegram-intel/channel/{username}/full')
            full_success = success and data.get("ok") == True
            self.log_test("Legacy Channel Full", full_success)
        else:
            self.log_test("Legacy Channel Full - No Channels", False, "No channels available")

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Telegram Intelligence Platform API Tests")
        print(f"📡 Testing against: {self.base_url}")
        print("=" * 60)
        
        try:
            self.test_basic_health()
            self.test_utility_list_endpoint()
            self.test_channel_overview_endpoint()
            self.test_channel_refresh_endpoint()
            self.test_compare_channels_endpoint()
            self.test_pipeline_status_endpoint()
            self.test_seed_channels_endpoint()
            self.test_watchlist_endpoints()
            self.test_legacy_endpoints()
        except Exception as e:
            print(f"💥 Test suite error: {e}")
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print("\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"  • {test['name']}: {test['details']}")
        
        if self.passed_tests:
            print(f"\n✅ Passed Tests ({len(self.passed_tests)}):")
            for test in self.passed_tests[:10]:  # Show first 10
                print(f"  • {test}")
            if len(self.passed_tests) > 10:
                print(f"  ... and {len(self.passed_tests) - 10} more")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = TelegramIntelAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())