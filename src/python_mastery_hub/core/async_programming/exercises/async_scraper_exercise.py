"""
Async Web Scraper Exercise - Build an efficient async web scraper with rate limiting.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from ..base import AsyncDemo


@dataclass
class ScrapingStats:
    """Statistics for scraping operations."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    bytes_downloaded: int = 0


class AsyncRateLimiter:
    """Rate limiter for controlling request frequency."""
    
    def __init__(self, rate: float):
        self.rate = rate  # requests per second
        self.last_request = 0.0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            time_since_last = now - self.last_request
            
            if time_since_last < self.rate:
                sleep_time = self.rate - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request = time.time()


class AsyncScraperExercise(AsyncDemo):
    """Exercise for building an async web scraper."""
    
    def __init__(self):
        super().__init__("Async Web Scraper Exercise")
        self.instructions = self._get_instructions()
        self.starter_code = self._get_starter_code()
        self.solution = self._get_solution()
    
    def _get_instructions(self) -> Dict[str, Any]:
        """Get exercise instructions."""
        return {
            "title": "Build an Efficient Async Web Scraper",
            "description": "Create a production-ready async web scraper with rate limiting and error handling",
            "objectives": [
                "Implement async HTTP client with session management",
                "Add rate limiting to respect server resources",
                "Include retry logic for failed requests",
                "Handle different types of errors gracefully", 
                "Create progress tracking and statistics",
                "Implement concurrent request limiting",
                "Add response validation and filtering"
            ],
            "requirements": [
                "Must use aiohttp for HTTP requests",
                "Implement exponential backoff for retries",
                "Rate limit to avoid overwhelming servers",
                "Track detailed statistics",
                "Handle timeouts and connection errors",
                "Support custom headers and user agents",
                "Validate response content before processing"
            ],
            "difficulty": "Advanced",
            "estimated_time": "2-3 hours"
        }
    
    def _get_starter_code(self) -> str:
        """Get starter code template."""
        return '''
import asyncio
import aiohttp
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ScrapingStats:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    bytes_downloaded: int = 0

class AsyncWebScraper:
    def __init__(self, max_concurrent=10, rate_limit=1.0, retry_attempts=3):
        self.max_concurrent = max_concurrent
        self.rate_limit = rate_limit
        self.retry_attempts = retry_attempts
        # TODO: Initialize rate limiter, semaphore, session, stats
        pass
    
    async def __aenter__(self):
        """Async context manager entry."""
        # TODO: Create aiohttp session with proper configuration
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        # TODO: Close session and cleanup
        pass
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL with rate limiting and retries."""
        # TODO: Implement rate limiting
        # TODO: Implement retry logic with exponential backoff
        # TODO: Handle different types of errors
        # TODO: Update statistics
        pass
    
    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        # TODO: Create tasks for all URLs
        # TODO: Process with progress tracking
        # TODO: Return results
        pass
    
    def get_stats(self) -> ScrapingStats:
        """Get current scraping statistics."""
        # TODO: Return current stats
        pass

# Example usage
async def main():
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/status/200",
        "https://httpbin.org/json"
    ] * 3  # 9 URLs total
    
    async with AsyncWebScraper(max_concurrent=3, rate_limit=0.5) as scraper:
        results = await scraper.scrape_urls(urls)
        stats = scraper.get_stats()
        
        print(f"Scraped {len(results)} URLs")
        print(f"Success rate: {stats.successful_requests}/{stats.total_requests}")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    def _get_solution(self) -> str:
        """Get complete solution."""
        return '''
import asyncio
import aiohttp
import time
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ScrapingStats:
    """Statistics for scraping operations."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_time: float = 0.0
    bytes_downloaded: int = 0

class AsyncRateLimiter:
    """Rate limiter for controlling request frequency."""
    
    def __init__(self, rate: float):
        self.rate = rate  # seconds between requests
        self.last_request = 0.0
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            time_since_last = now - self.last_request
            
            if time_since_last < self.rate:
                sleep_time = self.rate - time_since_last
                await asyncio.sleep(sleep_time)
            
            self.last_request = time.time()

class AsyncWebScraper:
    """Production-ready async web scraper."""
    
    def __init__(self, max_concurrent=10, rate_limit=1.0, retry_attempts=3, timeout=30):
        self.max_concurrent = max_concurrent
        self.rate_limiter = AsyncRateLimiter(rate_limit)
        self.retry_attempts = retry_attempts
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.stats = ScrapingStats()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        connector = aiohttp.TCPConnector(
            limit=100,  # Total connection pool size
            limit_per_host=20,  # Max connections per host
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=self.timeout,
            connect=10,
            sock_read=10
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'AsyncWebScraper/1.0 (+https://example.com/bot)',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            # Give time for connections to close
            await asyncio.sleep(0.1)
    
    async def scrape_url(self, url: str) -> Dict[str, Any]:
        """Scrape a single URL with comprehensive error handling."""
        async with self.semaphore:  # Limit concurrency
            await self.rate_limiter.acquire()  # Rate limiting
            
            self.stats.total_requests += 1
            
            for attempt in range(self.retry_attempts):
                try:
                    start_time = time.time()
                    
                    async with self.session.get(url) as response:
                        content = await response.read()
                        duration = time.time() - start_time
                        
                        # Validate response
                        if response.status >= 400:
                            raise aiohttp.ClientResponseError(
                                request_info=response.request_info,
                                history=response.history,
                                status=response.status,
                                message=f"HTTP {response.status}"
                            )
                        
                        # Update statistics
                        self.stats.successful_requests += 1
                        self.stats.bytes_downloaded += len(content)
                        self.stats.total_time += duration
                        
                        return {
                            'url': url,
                            'status': response.status,
                            'content_length': len(content),
                            'content_type': response.headers.get('content-type', 'unknown'),
                            'response_time': duration,
                            'attempt': attempt + 1,
                            'success': True,
                            'headers': dict(response.headers),
                            'encoding': response.charset or 'utf-8'
                        }
                
                except asyncio.TimeoutError:
                    error_msg = f"Timeout after {self.timeout}s"
                    if attempt == self.retry_attempts - 1:
                        self.stats.failed_requests += 1
                        return self._create_error_result(url, error_msg, attempt + 1)
                    await self._wait_with_backoff(attempt)
                
                except aiohttp.ClientConnectionError as e:
                    error_msg = f"Connection error: {str(e)}"
                    if attempt == self.retry_attempts - 1:
                        self.stats.failed_requests += 1
                        return self._create_error_result(url, error_msg, attempt + 1)
                    await self._wait_with_backoff(attempt)
                
                except aiohttp.ClientResponseError as e:
                    error_msg = f"HTTP {e.status}: {e.message}"
                    if e.status < 500 or attempt == self.retry_attempts - 1:
                        # Don't retry client errors (4xx) or final attempt
                        self.stats.failed_requests += 1
                        return self._create_error_result(url, error_msg, attempt + 1)
                    await self._wait_with_backoff(attempt)
                
                except Exception as e:
                    error_msg = f"Unexpected error: {str(e)}"
                    if attempt == self.retry_attempts - 1:
                        self.stats.failed_requests += 1
                        return self._create_error_result(url, error_msg, attempt + 1)
                    await self._wait_with_backoff(attempt)
    
    def _create_error_result(self, url: str, error: str, attempt: int) -> Dict[str, Any]:
        """Create standardized error result."""
        return {
            'url': url,
            'error': error,
            'attempt': attempt,
            'success': False,
            'response_time': 0,
            'content_length': 0
        }
    
    async def _wait_with_backoff(self, attempt: int):
        """Wait with exponential backoff."""
        backoff_time = (2 ** attempt) + random.uniform(0, 1)
        await asyncio.sleep(backoff_time)
    
    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with progress tracking."""
        print(f"Starting to scrape {len(urls)} URLs...")
        print(f"Max concurrent requests: {self.max_concurrent}")
        print(f"Rate limit: {self.rate_limiter.rate}s between requests")
        print(f"Retry attempts: {self.retry_attempts}")
        
        start_time = time.time()
        
        # Create tasks for all URLs
        tasks = [self.scrape_url(url) for url in urls]
        
        # Process tasks with progress updates
        results = []
        completed = 0
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            completed += 1
            
            # Progress updates
            if completed % max(1, len(urls) // 10) == 0 or completed == len(urls):
                progress = (completed / len(urls)) * 100
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                print(f"Progress: {completed}/{len(urls)} ({progress:.1f}%) - "
                      f"{rate:.1f} URLs/sec")
        
        total_time = time.time() - start_time
        self.stats.total_time = total_time
        
        self._print_summary()
        
        return results
    
    def _print_summary(self):
        """Print comprehensive scraping summary."""
        print(f"\\n{'='*60}")
        print("SCRAPING SUMMARY")
        print(f"{'='*60}")
        
        # Basic statistics
        total = self.stats.total_requests
        successful = self.stats.successful_requests
        failed = self.stats.failed_requests
        success_rate = (successful / total * 100) if total > 0 else 0
        
        print(f"Total requests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        # Performance metrics
        if self.stats.total_time > 0:
            throughput = total / self.stats.total_time
            avg_response_time = self.stats.total_time / max(successful, 1)
            
            print(f"\\nPerformance:")
            print(f"Total time: {self.stats.total_time:.2f}s")
            print(f"Throughput: {throughput:.2f} requests/sec")
            print(f"Average response time: {avg_response_time:.3f}s")
        
        # Data transfer
        mb_downloaded = self.stats.bytes_downloaded / (1024 * 1024)
        print(f"\\nData transfer:")
        print(f"Bytes downloaded: {self.stats.bytes_downloaded:,}")
        print(f"Data downloaded: {mb_downloaded:.2f} MB")
        
        if self.stats.total_time > 0:
            transfer_rate = mb_downloaded / self.stats.total_time
            print(f"Transfer rate: {transfer_rate:.2f} MB/sec")
    
    def get_stats(self) -> ScrapingStats:
        """Get current scraping statistics."""
        return self.stats

# Example usage and testing
async def test_scraper():
    """Test the async web scraper."""
    # Test URLs with various scenarios
    test_urls = [
        "https://httpbin.org/status/200",  # Success
        "https://httpbin.org/delay/1",     # Slow response
        "https://httpbin.org/json",        # JSON response
        "https://httpbin.org/status/404",  # Client error
        "https://httpbin.org/status/500",  # Server error (will retry)
        "https://httpbin.org/html",        # HTML content
        "https://httpbin.org/xml",         # XML content
        "https://httpbin.org/delay/2",     # Another slow response
    ]
    
    print("Testing AsyncWebScraper with various scenarios...")
    
    async with AsyncWebScraper(
        max_concurrent=3,
        rate_limit=0.5,
        retry_attempts=2,
        timeout=10
    ) as scraper:
        results = await scraper.scrape_urls(test_urls)
        
        # Analyze results
        successful = [r for r in results if r.get('success', False)]
        failed = [r for r in results if not r.get('success', True)]
        
        print(f"\\nDetailed Results:")
        print(f"Successful requests: {len(successful)}")
        print(f"Failed requests: {len(failed)}")
        
        if failed:
            print(f"\\nFailure details:")
            for result in failed:
                print(f"  {result['url']}: {result.get('error', 'Unknown error')}")
        
        # Show sample successful result
        if successful:
            sample = successful[0]
            print(f"\\nSample successful result:")
            print(f"  URL: {sample['url']}")
            print(f"  Status: {sample['status']}")
            print(f"  Content-Type: {sample.get('content_type', 'unknown')}")
            print(f"  Size: {sample['content_length']} bytes")
            print(f"  Response time: {sample['response_time']:.3f}s")

# Demo with custom URLs
async def demo_custom_scraping():
    """Demo scraping with custom URLs."""
    # You can replace these with real URLs for testing
    demo_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/user-agent", 
        "https://httpbin.org/headers",
        "https://httpbin.org/ip",
        "https://httpbin.org/uuid",
    ] * 2  # Duplicate for testing
    
    print("\\nDemo: Custom URL scraping...")
    
    async with AsyncWebScraper(
        max_concurrent=2,
        rate_limit=1.0,  # 1 second between requests
        retry_attempts=3
    ) as scraper:
        results = await scraper.scrape_urls(demo_urls)
        
        # Filter and display results
        for result in results[:3]:  # Show first 3 results
            if result.get('success'):
                print(f"\\n✓ {result['url']}")
                print(f"  Status: {result['status']}")
                print(f"  Size: {result['content_length']} bytes")
            else:
                print(f"\\n✗ {result['url']}")
                print(f"  Error: {result.get('error')}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_scraper())
    
    # Run the demo
    asyncio.run(demo_custom_scraping())
'''
    
    def get_explanation(self) -> str:
        """Get explanation for the exercise."""
        return (
            "This exercise teaches you to build a production-ready async web scraper "
            "that handles real-world challenges like rate limiting, error handling, "
            "retries, and concurrent request management. You'll learn to use aiohttp "
            "effectively while respecting server resources and handling edge cases."
        )
    
    def get_best_practices(self) -> List[str]:
        """Get best practices for async web scraping."""
        return [
            "Always use rate limiting to avoid overwhelming servers",
            "Implement exponential backoff for retries",
            "Use appropriate timeouts for different types of requests", 
            "Handle different HTTP status codes appropriately",
            "Validate response content before processing",
            "Use connection pooling for efficiency",
            "Implement proper session management",
            "Track detailed statistics for monitoring",
            "Respect robots.txt and server policies",
            "Use appropriate User-Agent headers"
        ]
    
    def validate_solution(self, solution_code: str) -> List[str]:
        """Validate student solution."""
        feedback = []
        
        # Check for key components
        required_components = [
            ("aiohttp", "Must use aiohttp for HTTP requests"),
            ("AsyncWebScraper", "Must implement AsyncWebScraper class"),
            ("rate", "Must implement rate limiting"),
            ("retry", "Must implement retry logic"),
            ("semaphore", "Must limit concurrent requests"),
            ("__aenter__", "Must implement async context manager"),
            ("stats", "Must track statistics")
        ]
        
        for component, message in required_components:
            if component.lower() in solution_code.lower():
                feedback.append(f"✓ {message}")
            else:
                feedback.append(f"✗ {message}")
        
        return feedback