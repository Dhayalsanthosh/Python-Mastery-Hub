"""
Mocking exercise for the Testing module.
Test an API client with comprehensive mocking techniques.
"""

from typing import Dict, Any


def get_mocking_exercise() -> Dict[str, Any]:
    """Get the API client mocking exercise."""
    return {
        "title": "API Client Testing with Mocks",
        "difficulty": "hard",
        "estimated_time": "3-4 hours",
        "instructions": """
Build comprehensive tests for an API client using mocking techniques.
You'll learn to test code that depends on external services by replacing
those dependencies with controllable mock objects.

This exercise covers mocking HTTP requests, testing error conditions,
and verifying that your code interacts correctly with external APIs.
""",
        "learning_objectives": [
            "Master unittest.mock for replacing external dependencies",
            "Test HTTP client code without making real network requests",
            "Handle different response scenarios and error conditions",
            "Verify correct API usage patterns",
            "Practice testing asynchronous and synchronous code"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Build Weather API Client",
                "description": "Create a client for weather API with basic operations",
                "requirements": [
                    "Get current weather for a city",
                    "Get weather forecast",
                    "Handle API authentication",
                    "Parse JSON responses into data classes"
                ]
            },
            {
                "step": 2,
                "title": "Mock HTTP Requests",
                "description": "Test API client using mocked HTTP responses",
                "requirements": [
                    "Mock successful API responses",
                    "Test different weather conditions",
                    "Verify correct request parameters",
                    "Check proper header handling"
                ]
            },
            {
                "step": 3,
                "title": "Test Error Scenarios",
                "description": "Handle and test various error conditions",
                "requirements": [
                    "Network errors and timeouts",
                    "Invalid API keys",
                    "Rate limiting (HTTP 429)",
                    "City not found (HTTP 404)"
                ]
            },
            {
                "step": 4,
                "title": "Test Caching System",
                "description": "Add and test response caching",
                "requirements": [
                    "Cache responses for performance",
                    "Mock file system operations",
                    "Test cache hit/miss scenarios",
                    "Handle cache expiration"
                ]
            },
            {
                "step": 5,
                "title": "Advanced Mocking",
                "description": "Use advanced mocking features",
                "requirements": [
                    "Mock context managers",
                    "Test retry mechanisms",
                    "Mock time-dependent behavior",
                    "Verify call patterns and sequences"
                ]
            }
        ],
        "starter_code": '''
import unittest
from unittest.mock import Mock, patch, MagicMock
import requests
import json
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class WeatherData:
    """Weather data structure."""
    city: str
    temperature: float
    humidity: int
    description: str
    timestamp: datetime

class WeatherAPIClient:
    """Weather API client for testing with mocks."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.com"):
        # TODO: Initialize client
        pass
    
    def get_current_weather(self, city: str) -> WeatherData:
        """Get current weather for a city."""
        # TODO: Implement API call
        pass
    
    def get_forecast(self, city: str, days: int = 5) -> list[WeatherData]:
        """Get weather forecast."""
        # TODO: Implement API call
        pass

class TestWeatherAPIClient(unittest.TestCase):
    """Test suite for weather API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        # TODO: Create client instance
        pass
    
    @patch('requests.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful weather API call."""
        # TODO: Configure mock response
        # TODO: Test API call
        # TODO: Verify results
        pass
    
    def test_api_error_handling(self):
        """Test API error handling."""
        # TODO: Test various error scenarios
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)
''',
        "hints": [
            "Use patch decorators to mock requests.get and requests.post",
            "Create Mock objects for HTTP responses with status_code and json() methods",
            "Test both successful and error scenarios",
            "Use side_effect to simulate exceptions",
            "Verify that mocks are called with correct parameters",
            "Mock datetime.now() for time-dependent tests",
            "Use MagicMock for complex objects with multiple methods"
        ],
        "solution": '''
import unittest
from unittest.mock import Mock, patch, MagicMock, mock_open, call
import requests
import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

@dataclass
class WeatherData:
    """Weather data structure."""
    city: str
    temperature: float
    humidity: int
    description: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "city": self.city,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "description": self.description,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherData':
        """Create from dictionary."""
        return cls(
            city=data["city"],
            temperature=data["temperature"],
            humidity=data["humidity"],
            description=data["description"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class WeatherAPIClient:
    """Weather API client with caching and error handling."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.weather.com", 
                 cache_dir: str = "weather_cache"):
        if not api_key:
            raise ValueError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(minutes=10)  # Cache for 10 minutes
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "WeatherClient/1.0",
            "Accept": "application/json"
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries."""
        url = f"{self.base_url}/{endpoint}"
        params['key'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise WeatherAPIError("Invalid API key", 401)
            elif response.status_code == 404:
                raise WeatherAPIError("City not found", 404)
            elif response.status_code == 429:
                raise WeatherAPIError("Rate limit exceeded", 429)
            else:
                raise WeatherAPIError(f"API error: {response.status_code}", response.status_code)
                
        except requests.exceptions.Timeout:
            raise WeatherAPIError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise WeatherAPIError("Connection error")
        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Request failed: {str(e)}")
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path for a given key."""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load data from cache if available and not expired."""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                
                # Check if cache is still valid
                cached_time = datetime.fromisoformat(cached_data['cached_at'])
                if datetime.now() - cached_time < self.cache_duration:
                    return cached_data['data']
        except (OSError, json.JSONDecodeError, KeyError):
            # Ignore cache errors and fetch fresh data
            pass
        
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)
            
            cached_data = {
                'data': data,
                'cached_at': datetime.now().isoformat()
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f)
        except OSError:
            # Ignore cache save errors
            pass
    
    def get_current_weather(self, city: str) -> WeatherData:
        """Get current weather for a city."""
        if not city or not city.strip():
            raise ValueError("City name is required")
        
        city = city.strip().lower()
        cache_key = f"current_{city}"
        
        # Try to load from cache first
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return WeatherData.from_dict(cached_data)
        
        # Fetch from API
        params = {'q': city}
        response_data = self._make_request('current', params)
        
        # Parse response
        current = response_data['current']
        weather_data = WeatherData(
            city=city.title(),
            temperature=current['temp_c'],
            humidity=current['humidity'],
            description=current['condition']['text'],
            timestamp=datetime.now()
        )
        
        # Save to cache
        self._save_to_cache(cache_key, weather_data.to_dict())
        
        return weather_data
    
    def get_forecast(self, city: str, days: int = 5) -> List[WeatherData]:
        """Get weather forecast for a city."""
        if not city or not city.strip():
            raise ValueError("City name is required")
        if days < 1 or days > 10:
            raise ValueError("Days must be between 1 and 10")
        
        city = city.strip().lower()
        cache_key = f"forecast_{city}_{days}"
        
        # Try to load from cache first
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return [WeatherData.from_dict(item) for item in cached_data]
        
        # Fetch from API
        params = {'q': city, 'days': days}
        response_data = self._make_request('forecast', params)
        
        # Parse response
        forecast_data = []
        for day in response_data['forecast']['forecastday']:
            day_data = day['day']
            weather_data = WeatherData(
                city=city.title(),
                temperature=day_data['avgtemp_c'],
                humidity=day_data['avghumidity'],
                description=day_data['condition']['text'],
                timestamp=datetime.fromisoformat(day['date'] + 'T12:00:00')
            )
            forecast_data.append(weather_data)
        
        # Save to cache
        cache_data = [item.to_dict() for item in forecast_data]
        self._save_to_cache(cache_key, cache_data)
        
        return forecast_data
    
    def clear_cache(self) -> None:
        """Clear all cached data."""
        try:
            if os.path.exists(self.cache_dir):
                for filename in os.listdir(self.cache_dir):
                    if filename.endswith('.json'):
                        os.remove(os.path.join(self.cache_dir, filename))
        except OSError:
            pass

class TestWeatherAPIClient(unittest.TestCase):
    """Comprehensive test suite for weather API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key_123"
        self.client = WeatherAPIClient(self.api_key, cache_dir="test_cache")
        
        # Sample API response data
        self.sample_current_response = {
            "current": {
                "temp_c": 22.5,
                "humidity": 65,
                "condition": {
                    "text": "Partly cloudy"
                }
            }
        }
        
        self.sample_forecast_response = {
            "forecast": {
                "forecastday": [
                    {
                        "date": "2024-01-01",
                        "day": {
                            "avgtemp_c": 20.0,
                            "avghumidity": 60,
                            "condition": {"text": "Sunny"}
                        }
                    },
                    {
                        "date": "2024-01-02",
                        "day": {
                            "avgtemp_c": 18.5,
                            "avghumidity": 70,
                            "condition": {"text": "Rainy"}
                        }
                    }
                ]
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        self.client.clear_cache()
    
    @patch('requests.Session.get')
    def test_get_current_weather_success(self, mock_get):
        """Test successful current weather API call."""
        # Configure mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_current_response
        mock_get.return_value = mock_response
        
        # Make API call
        result = self.client.get_current_weather("London")
        
        # Verify request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn("current", call_args[0][0])  # URL contains 'current'
        self.assertEqual(call_args[1]['params']['q'], "london")
        self.assertEqual(call_args[1]['params']['key'], self.api_key)
        
        # Verify result
        self.assertEqual(result.city, "London")
        self.assertEqual(result.temperature, 22.5)
        self.assertEqual(result.humidity, 65)
        self.assertEqual(result.description, "Partly cloudy")
    
    @patch('requests.Session.get')
    def test_get_forecast_success(self, mock_get):
        """Test successful forecast API call."""
        # Configure mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_forecast_response
        mock_get.return_value = mock_response
        
        # Make API call
        result = self.client.get_forecast("Paris", 2)
        
        # Verify request
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertEqual(call_args[1]['params']['q'], "paris")
        self.assertEqual(call_args[1]['params']['days'], 2)
        
        # Verify result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].city, "Paris")
        self.assertEqual(result[0].temperature, 20.0)
        self.assertEqual(result[1].temperature, 18.5)
    
    @patch('requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test various API error scenarios."""
        test_cases = [
            (401, "Invalid API key"),
            (404, "City not found"),
            (429, "Rate limit exceeded"),
            (500, "API error: 500")
        ]
        
        for status_code, expected_message in test_cases:
            with self.subTest(status_code=status_code):
                # Configure mock response
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_get.return_value = mock_response
                
                # Test error handling
                with self.assertRaises(WeatherAPIError) as context:
                    self.client.get_current_weather("London")
                
                self.assertIn(expected_message, str(context.exception))
                self.assertEqual(context.exception.status_code, status_code)
    
    @patch('requests.Session.get')
    def test_network_error_handling(self, mock_get):
        """Test network error handling."""
        # Test timeout
        mock_get.side_effect = requests.exceptions.Timeout()
        
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current_weather("London")
        
        self.assertIn("timeout", str(context.exception).lower())
        
        # Test connection error
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with self.assertRaises(WeatherAPIError) as context:
            self.client.get_current_weather("London")
        
        self.assertIn("connection", str(context.exception).lower())
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('requests.Session.get')
    def test_cache_hit(self, mock_get, mock_file, mock_exists):
        """Test cache hit scenario."""
        # Configure cache to exist and be valid
        mock_exists.return_value = True
        
        cached_data = {
            'data': {
                'city': 'London',
                'temperature': 25.0,
                'humidity': 70,
                'description': 'Cached weather',
                'timestamp': datetime.now().isoformat()
            },
            'cached_at': datetime.now().isoformat()
        }
        
        mock_file.return_value.read.return_value = json.dumps(cached_data)
        
        # Make API call
        result = self.client.get_current_weather("London")
        
        # Verify API was not called (cache hit)
        mock_get.assert_not_called()
        
        # Verify cached data was returned
        self.assertEqual(result.temperature, 25.0)
        self.assertEqual(result.description, "Cached weather")
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('requests.Session.get')
    def test_cache_save(self, mock_get, mock_exists, mock_file, mock_makedirs):
        """Test that data is saved to cache."""
        # Configure no cache exists
        mock_exists.return_value = False
        
        # Configure API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_current_response
        mock_get.return_value = mock_response
        
        # Make API call
        self.client.get_current_weather("London")
        
        # Verify cache directory was created
        mock_makedirs.assert_called_once_with("test_cache", exist_ok=True)
        
        # Verify file was written
        mock_file.assert_called()
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        cached_data = json.loads(written_data)
        
        self.assertIn('data', cached_data)
        self.assertIn('cached_at', cached_data)
    
    def test_input_validation(self):
        """Test input validation."""
        # Empty city name
        with self.assertRaises(ValueError):
            self.client.get_current_weather("")
        
        # Invalid days for forecast
        with self.assertRaises(ValueError):
            self.client.get_forecast("London", 0)
        
        with self.assertRaises(ValueError):
            self.client.get_forecast("London", 15)
    
    def test_client_initialization(self):
        """Test client initialization validation."""
        # Empty API key
        with self.assertRaises(ValueError):
            WeatherAPIClient("")
        
        # Valid initialization
        client = WeatherAPIClient("valid_key")
        self.assertEqual(client.api_key, "valid_key")
        self.assertIsNotNone(client.session)
    
    @patch('requests.Session.get')
    def test_session_headers(self, mock_get):
        """Test that session has correct headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_current_response
        mock_get.return_value = mock_response
        
        # Make API call
        self.client.get_current_weather("London")
        
        # Verify session headers were set
        headers = self.client.session.headers
        self.assertIn("User-Agent", headers)
        self.assertIn("Accept", headers)
        self.assertEqual(headers["Accept"], "application/json")
    
    @patch('datetime.datetime')
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('requests.Session.get')
    def test_cache_expiration(self, mock_get, mock_file, mock_exists, mock_datetime):
        """Test cache expiration handling."""
        # Configure cache to exist but be expired
        mock_exists.return_value = True
        
        # Set current time
        current_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = current_time
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Cache from 20 minutes ago (expired)
        expired_time = current_time - timedelta(minutes=20)
        cached_data = {
            'data': {'city': 'London', 'temperature': 25.0, 'humidity': 70, 
                    'description': 'Old cached weather', 'timestamp': current_time.isoformat()},
            'cached_at': expired_time.isoformat()
        }
        
        mock_file.return_value.read.return_value = json.dumps(cached_data)
        
        # Configure fresh API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.sample_current_response
        mock_get.return_value = mock_response
        
        # Make API call
        result = self.client.get_current_weather("London")
        
        # Verify API was called (cache expired)
        mock_get.assert_called_once()
        
        # Verify fresh data was returned
        self.assertEqual(result.temperature, 22.5)  # From fresh API response

if __name__ == '__main__':
    unittest.main(verbosity=2)
'''
    }