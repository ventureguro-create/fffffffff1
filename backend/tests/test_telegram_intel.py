"""
Telegram Intelligence API Tests
Tests for utility list, channel overview, filters, sparklines, MTProto status, and admin endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://crypto-channel-scan.preview.emergentagent.com').rstrip('/')


class TestHealthEndpoints:
    """Health check endpoints"""
    
    def test_api_health(self):
        """Test main API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "mongodb" in data
        assert "timestamp" in data
    
    def test_telegram_intel_health(self):
        """Test Telegram Intel module health"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/health")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["module"] == "telegram-intel"
        assert "runtime" in data


class TestUtilityListAPI:
    """Tests for /api/telegram-intel/utility/list endpoint"""
    
    def test_utility_list_basic(self):
        """Test basic utility list returns items with sparkline data"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "items" in data
        assert "total" in data
        assert "stats" in data
        assert len(data["items"]) > 0
        
        # Verify sparkline data exists in items
        first_item = data["items"][0]
        assert "sparkline" in first_item, "Sparkline data missing from items"
        assert isinstance(first_item["sparkline"], list), "Sparkline should be a list"
        assert len(first_item["sparkline"]) > 0, "Sparkline should have data points"
    
    def test_utility_list_item_structure(self):
        """Test that list items have all required fields"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = [
            "username", "title", "type", "members", "avgReach", 
            "growth7", "activity", "redFlags", "fomoScore", "sparkline"
        ]
        
        for item in data["items"]:
            for field in required_fields:
                assert field in item, f"Missing field: {field}"
    
    def test_utility_list_search_filter(self):
        """Test search/query filter"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?q=crypto&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # If results found, verify they match search
        if data["items"]:
            for item in data["items"]:
                assert "crypto" in item["username"].lower() or "crypto" in item["title"].lower()
    
    def test_utility_list_type_filter(self):
        """Test type filter (channel/group)"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?type=channel&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        for item in data["items"]:
            assert item["type"] == "Channel"
    
    def test_utility_list_activity_filter(self):
        """Test activity level filter"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?activity=High&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        for item in data["items"]:
            assert item["activity"] == "High"
    
    def test_utility_list_members_range_filter(self):
        """Test members range filter"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?minMembers=10000&maxMembers=100000&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        for item in data["items"]:
            assert item["members"] >= 10000
            assert item["members"] <= 100000
    
    def test_utility_list_growth_filter(self):
        """Test growth 7D filter"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?minGrowth7=5&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        for item in data["items"]:
            assert item["growth7"] >= 5
    
    def test_utility_list_red_flags_filter(self):
        """Test max red flags filter"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?maxRedFlags=2&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        for item in data["items"]:
            assert item["redFlags"] <= 2
    
    def test_utility_list_sort_by_growth(self):
        """Test sorting by growth"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?sort=growth&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        # Verify descending order
        if len(data["items"]) > 1:
            for i in range(len(data["items"]) - 1):
                assert data["items"][i]["growth7"] >= data["items"][i+1]["growth7"]
    
    def test_utility_list_sort_by_members(self):
        """Test sorting by members"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?sort=members&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        
        if len(data["items"]) > 1:
            for i in range(len(data["items"]) - 1):
                assert data["items"][i]["members"] >= data["items"][i+1]["members"]
    
    def test_utility_list_pagination(self):
        """Test pagination works correctly"""
        # Get page 1
        response1 = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?page=1&limit=5")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Get page 2
        response2 = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?page=2&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify different items on different pages
        if data1["items"] and data2["items"]:
            page1_usernames = {item["username"] for item in data1["items"]}
            page2_usernames = {item["username"] for item in data2["items"]}
            assert page1_usernames != page2_usernames, "Pages should have different items"
    
    def test_utility_list_stats(self):
        """Test stats are returned correctly"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/utility/list?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        stats = data["stats"]
        assert "tracked" in stats
        assert "avgUtility" in stats
        assert "highGrowth" in stats
        assert "highRisk" in stats


class TestChannelOverviewAPI:
    """Tests for /api/telegram-intel/channel/{username}/overview endpoint"""
    
    def test_channel_overview_basic(self):
        """Test channel overview returns full data"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/cryptonews/overview")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "profile" in data
        assert "topCards" in data
        assert "metrics" in data
        assert "timeline" in data
        assert "recentPosts" in data
    
    def test_channel_overview_profile(self):
        """Test channel profile data structure"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/bitcoinmagazine/overview")
        assert response.status_code == 200
        data = response.json()
        
        profile = data["profile"]
        assert "username" in profile
        assert "title" in profile
        assert "type" in profile
        assert "avatarColor" in profile
    
    def test_channel_overview_top_cards(self):
        """Test top cards metrics"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/ethresearch/overview")
        assert response.status_code == 200
        data = response.json()
        
        top_cards = data["topCards"]
        assert "subscribers" in top_cards
        assert "viewsPerPost" in top_cards
        assert "messagesPerDay" in top_cards
    
    def test_channel_overview_timeline(self):
        """Test timeline data for charts"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/defi_pulse/overview")
        assert response.status_code == 200
        data = response.json()
        
        timeline = data["timeline"]
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        # Verify timeline entry structure
        entry = timeline[0]
        assert "date" in entry
        assert "views" in entry
    
    def test_channel_overview_metrics(self):
        """Test metrics for chart rendering"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/nft_drops/overview")
        assert response.status_code == 200
        data = response.json()
        
        metrics = data["metrics"]
        assert "utilityScore" in metrics
        assert "growth7" in metrics
        assert "fraud" in metrics
    
    def test_channel_overview_recent_posts(self):
        """Test recent posts data"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/whale_alerts/overview")
        assert response.status_code == 200
        data = response.json()
        
        posts = data["recentPosts"]
        assert isinstance(posts, list)
        assert len(posts) > 0
        
        post = posts[0]
        assert "id" in post
        assert "date" in post
        assert "text" in post
        assert "views" in post
    
    def test_channel_overview_related_channels(self):
        """Test related channels data"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/trading_signals/overview")
        assert response.status_code == 200
        data = response.json()
        
        related = data["relatedChannels"]
        assert isinstance(related, list)
        if related:
            assert "username" in related[0]
            assert "title" in related[0]


class TestMTProtoStatus:
    """Tests for MTProto status endpoint"""
    
    def test_mtproto_status(self):
        """Test MTProto status returns availability info"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/admin/mtproto/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "ok" in data
        assert "available" in data
        assert "secretsLoaded" in data


class TestAdminEndpoints:
    """Tests for admin/pipeline endpoints"""
    
    def test_pipeline_status(self):
        """Test pipeline status endpoint"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/admin/pipeline/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "status" in data
        status = data["status"]
        assert "totalChannels" in status
        assert "mode" in status
    
    def test_census_summary(self):
        """Test census summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/admin/census/summary")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "stages" in data
        assert "policy" in data
    
    def test_census_status(self):
        """Test census status endpoint"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/admin/census/status")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "now" in data


class TestWatchlistAPI:
    """Tests for watchlist endpoints"""
    
    def test_watchlist_add_and_check(self):
        """Test adding to watchlist and checking"""
        # Add to watchlist
        add_response = requests.post(
            f"{BASE_URL}/api/telegram-intel/watchlist",
            json={"username": "TEST_watchlist_channel", "notes": "Test entry"}
        )
        assert add_response.status_code == 200
        add_data = add_response.json()
        assert add_data["ok"] is True
        
        # Check if in watchlist
        check_response = requests.get(f"{BASE_URL}/api/telegram-intel/watchlist/check/TEST_watchlist_channel")
        assert check_response.status_code == 200
        check_data = check_response.json()
        assert check_data["ok"] is True
        assert check_data["inWatchlist"] is True
        
        # Clean up - remove from watchlist
        delete_response = requests.delete(f"{BASE_URL}/api/telegram-intel/watchlist/TEST_watchlist_channel")
        assert delete_response.status_code == 200
    
    def test_watchlist_get_all(self):
        """Test getting all watchlist items"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/watchlist")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "items" in data
        assert "total" in data


class TestChannelCompare:
    """Tests for channel comparison endpoint"""
    
    def test_compare_channels(self):
        """Test comparing two channels"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/compare?left=cryptonews&right=bitcoinmagazine")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "left" in data
        assert "right" in data
        assert "diffs" in data


class TestChannelRefresh:
    """Tests for channel refresh endpoint"""
    
    def test_channel_refresh(self):
        """Test refreshing channel data"""
        response = requests.post(f"{BASE_URL}/api/telegram-intel/channel/cryptonews/refresh")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "username" in data
        assert "mode" in data  # Should be 'mock' since MTProto not authorized


class TestLegacyEndpoints:
    """Tests for legacy endpoint compatibility"""
    
    def test_intel_list(self):
        """Test legacy intel list endpoint"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/intel/list?limit=5")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "items" in data
        assert "stats" in data
    
    def test_channel_full(self):
        """Test legacy channel full endpoint"""
        response = requests.get(f"{BASE_URL}/api/telegram-intel/channel/cryptonews/full")
        assert response.status_code == 200
        data = response.json()
        
        assert data["ok"] is True
        assert "intel" in data
        assert "compare" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
