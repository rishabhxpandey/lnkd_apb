import os
import re
import random
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Playwright, Browser
import asyncio
import time

class JobScraper:
    def __init__(self):
        self.timeout = 20000  # 20 seconds timeout - balanced for stability
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        self._browser_pool = None
        self._playwright = None
        self._last_scrape_time = 0
        self._min_delay_between_scrapes = 3  # Minimum 3 seconds between scrapes
    
    def _is_valid_linkedin_job_url(self, url: str) -> bool:
        """Validate if the URL is a LinkedIn job posting"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc in ['www.linkedin.com', 'linkedin.com'] and
                '/jobs/view/' in parsed.path
            )
        except Exception:
            return False
    
    def _extract_job_id_from_url(self, url: str) -> Optional[str]:
        """Extract job ID from LinkedIn URL"""
        try:
            # LinkedIn job URLs are typically: https://www.linkedin.com/jobs/view/1234567890/
            match = re.search(r'/jobs/view/(\d+)', url)
            return match.group(1) if match else None
        except Exception:
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove common LinkedIn artifacts
        text = re.sub(r'Show more|Show less|See more|See less', '', text)
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    async def _get_browser(self) -> Browser:
        """Get or create a persistent browser instance"""
        if self._playwright is None:
            self._playwright = await async_playwright().start()
        
        if self._browser_pool is None or self._browser_pool.is_connected() is False:
            print("Creating new browser instance...")
            self._browser_pool = await self._playwright.chromium.launch(
                headless=True,
                slow_mo=500,  # Reduced for better performance
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu',
                    '--window-size=1366,768',
                    '--disable-blink-features=AutomationControlled',
                    '--exclude-switches=enable-automation',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
        
        return self._browser_pool
    
    async def _enforce_rate_limit(self):
        """Enforce minimum delay between scraping attempts"""
        current_time = time.time()
        time_since_last_scrape = current_time - self._last_scrape_time
        
        if time_since_last_scrape < self._min_delay_between_scrapes:
            sleep_time = self._min_delay_between_scrapes - time_since_last_scrape
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            await asyncio.sleep(sleep_time)
        
        self._last_scrape_time = time.time()
    
    async def cleanup(self):
        """Clean up browser resources"""
        if self._browser_pool and self._browser_pool.is_connected():
            try:
                await asyncio.wait_for(self._browser_pool.close(), timeout=5.0)
            except Exception as e:
                print(f"Error closing browser: {e}")
        
        if self._playwright:
            try:
                await asyncio.wait_for(self._playwright.stop(), timeout=5.0)
            except Exception as e:
                print(f"Error stopping playwright: {e}")
        
        self._browser_pool = None
        self._playwright = None
    
    async def scrape_job(self, url: str, max_retries: int = 2) -> Dict[str, Any]:
        """Scrape job description and metadata from LinkedIn job URL with retry logic"""
        
        if not self._is_valid_linkedin_job_url(url):
            raise ValueError("Invalid LinkedIn job URL. Please provide a valid LinkedIn job posting URL.")
        
        job_id = self._extract_job_id_from_url(url)
        if not job_id:
            raise ValueError("Could not extract job ID from URL")
        
        # Enforce rate limiting
        await self._enforce_rate_limit()
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            if attempt > 0:
                print(f"Retry attempt {attempt}/{max_retries}")
                # Exponential backoff for retries
                await asyncio.sleep(2 ** attempt)
                # Force browser restart on retry
                await self.cleanup()
            
            try:
                return await self._scrape_job_attempt(url, job_id)
            except Exception as e:
                last_exception = e
                print(f"Scraping attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries:
                    break
        
        # All retries failed
        raise Exception(f"Failed to scrape job after {max_retries + 1} attempts. Last error: {str(last_exception)}")
    
    async def _scrape_job_attempt(self, url: str, job_id: str) -> Dict[str, Any]:
        """Single attempt at scraping a job"""
        browser = None
        page = None
        context = None
        
        try:
            print("Getting browser instance...")
            browser = await self._get_browser()
            
            # Create a new context for isolation
            print("Creating browser context...")
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1366, 'height': 768},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Charset': 'utf-8',
                    'Upgrade-Insecure-Requests': '1',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                }
            )
            
            # Create new page from context
            print("Creating new page...")
            page = await context.new_page()
            
            # Remove automation signatures that LinkedIn detects
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Remove automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Mock missing browser features
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
            """)
            
            print(f"Navigating to job URL: {url}")
            
            # Add random delay before navigation (human-like behavior)
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigate to the job URL with more conservative wait strategy
            try:
                # Check browser connection before navigation
                if not browser.is_connected():
                    raise Exception("Browser connection lost before navigation")
                
                response = await page.goto(url, wait_until='domcontentloaded', timeout=self.timeout)
                print(f"Page response status: {response.status if response else 'No response'}")
            except Exception as nav_error:
                print(f"Navigation timeout or error: {nav_error}")
                raise Exception(f"Failed to navigate to page: {nav_error}")
            
            if not response or response.status >= 400:
                raise Exception(f"Failed to load page. Status: {response.status if response else 'No response'}")
            
            # Simulate minimal human-like page interaction
            print("Simulating page interaction...")
            
            # Simple scroll to load dynamic content
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3);")
                await asyncio.sleep(1)
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2);")
                await asyncio.sleep(1)
            except Exception as scroll_error:
                print(f"Scroll error (continuing anyway): {scroll_error}")
            
            # Wait for network to settle with shorter timeout for stability
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except Exception:
                print("Network idle timeout, continuing anyway...")
                await asyncio.sleep(2)
            
            # Short delay before extraction
            await asyncio.sleep(2)
            
            # Wait for the main content to load with better error handling
            print("Waiting for job content to load...")
            try:
                await page.wait_for_selector('[data-job-id], .job-view-layout, .jobs-search__job-details, h1', timeout=15000)
            except Exception as e:
                print(f"Warning: Could not find expected selectors: {e}")
                # If specific selectors don't work, wait a bit for general content
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(3)
            
            print("Page loaded, extracting job information...")
            
            # Extract job title
            job_title = ""
            title_selectors = [
                'h1[data-test-id="job-title"]',
                '.job-details-jobs-unified-top-card__job-title h1',
                '.jobs-unified-top-card__job-title h1', 
                'h1.jobs-unified-top-card__job-title',
                'h1.job-details-jobs-unified-top-card__job-title',
                '.job-view-layout h1',
                'h1',  # Fallback to any h1 tag
                '.job-title',
                '[data-automation-id="jobPostingHeader"] h1'
            ]
            
            for selector in title_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        job_title = await element.inner_text()
                        job_title = self._clean_text(job_title)
                        if job_title:
                            print(f"Found job title: {job_title}")
                            break
                except Exception as e:
                    print(f"Error with selector {selector}: {e}")
                    continue
            
            # Extract company name
            company_name = ""
            company_selectors = [
                '.job-details-jobs-unified-top-card__primary-description a',
                '.jobs-unified-top-card__company-name a',
                '.job-details-jobs-unified-top-card__company-name a',
                '[data-test-id="job-details-company-name"] a',
                '.jobs-unified-top-card__subtitle a',
                '.job-details-jobs-unified-top-card__primary-description',
                '.jobs-unified-top-card__company-name',
                '.company-name',
                '[data-automation-id="jobPostingCompanyLink"]'
            ]
            
            for selector in company_selectors:
                try:
                    # Check if page is still valid before querying
                    if page.is_closed():
                        print("Page closed during company extraction")
                        break
                    element = await page.query_selector(selector)
                    if element:
                        company_name = await element.inner_text()
                        company_name = self._clean_text(company_name)
                        if company_name:
                            print(f"Found company: {company_name}")
                            break
                except Exception as e:
                    print(f"Error with company selector {selector}: {e}")
                    continue
            
            # Extract job description
            job_description = ""
            description_selectors = [
                '[data-test-id="job-details-description"]',
                '.job-view-layout .jobs-description',
                '.jobs-description__content',
                '.job-details-jobs-unified-top-card__job-description',
                '.jobs-box__html-content',
                '.jobs-description',
                '.description',
                '.job-description',
                '[data-automation-id="jobPostingDescription"]',
                '.jobs-search__job-details',
                '.jobs-box__html-content .jobs-description-content__text'
            ]
            
            for selector in description_selectors:
                try:
                    # Check if page is still valid before querying
                    if page.is_closed():
                        print("Page closed during description extraction")
                        break
                    element = await page.query_selector(selector)
                    if element:
                        # Try to click "Show more" button if present
                        try:
                            if not page.is_closed():
                                show_more_btn = await page.query_selector('.jobs-description__footer button, .inline-show-more-text__button')
                                if show_more_btn:
                                    await show_more_btn.click()
                                    await asyncio.sleep(1)
                        except Exception:
                            pass
                        
                        if not page.is_closed():
                            job_description = await element.inner_text()
                            job_description = self._clean_text(job_description)
                            if job_description and len(job_description) > 100:
                                print(f"Found job description: {len(job_description)} characters")
                                break
                except Exception as e:
                    print(f"Error with description selector {selector}: {e}")
                    continue
            
            # Extract posting date
            post_date = None
            date_selectors = [
                '[data-test-id="job-post-date"]',
                '.jobs-unified-top-card__posted-date',
                '.job-details-jobs-unified-top-card__posted-date'
            ]
            
            for selector in date_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        date_text = await element.inner_text()
                        # Extract relative dates like "2 days ago" or "1 week ago"
                        if date_text:
                            post_date = self._clean_text(date_text)
                            break
                except Exception:
                    continue
            
            print("Extraction complete, validating data...")
            
            # Validate extracted data
            if not job_title:
                raise Exception("Could not extract job title")
            
            if not job_description or len(job_description) < 50:
                raise Exception("Could not extract sufficient job description content")
            
            print("Data validation successful")
            
            # Return structured data
            result = {
                "job_id": job_id,
                "url": url,
                "title": job_title,
                "company": company_name or "Unknown Company",
                "description": job_description,
                "post_date": post_date,
                "scraped_at": datetime.utcnow().isoformat(),
                "source": "linkedin"
            }
            
            return result
            
        except Exception as e:
            print(f"Scraping error: {str(e)}")
            raise Exception(f"Failed to scrape job: {str(e)}")
        
        finally:
            # Clean up page and context (but keep browser for reuse)
            cleanup_tasks = []
            
            if page and not page.is_closed():
                try:
                    cleanup_tasks.append(asyncio.wait_for(page.close(), timeout=3.0))
                except Exception as page_close_error:
                    print(f"Error closing page: {page_close_error}")
            
            if context:
                try:
                    cleanup_tasks.append(asyncio.wait_for(context.close(), timeout=3.0))
                except Exception as context_close_error:
                    print(f"Error closing context: {context_close_error}")
            
            # Execute cleanup tasks with timeout protection
            if cleanup_tasks:
                try:
                    await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                except Exception as cleanup_error:
                    print(f"Cleanup timeout or error: {cleanup_error}")
    
    def _create_mock_job_data(self, url: str, job_id: str) -> Dict[str, Any]:
        """Create mock job data when scraping fails"""
        return {
            "job_id": job_id,
            "url": url,
            "title": "Software Engineer Position (Demo)",
            "company": "Tech Company",
            "description": """We are seeking a talented Software Engineer to join our team. 
            
            Responsibilities:
            • Develop and maintain software applications
            • Collaborate with cross-functional teams
            • Write clean, efficient, and maintainable code
            • Participate in code reviews and technical discussions
            • Troubleshoot and debug applications
            
            Requirements:
            • Bachelor's degree in Computer Science or related field
            • 3+ years of experience in software development
            • Proficiency in programming languages such as Python, Java, or JavaScript
            • Experience with databases and web technologies
            • Strong problem-solving and communication skills
            
            Note: This is mock data generated because LinkedIn blocked automated scraping. 
            Please manually copy the job description for accurate interview preparation.""",
            "post_date": "1 week ago",
            "scraped_at": datetime.utcnow().isoformat(),
            "source": "linkedin_mock"
        }
    
    async def test_scraper(self) -> Dict[str, Any]:
        """Test the scraper with a mock response"""
        return {
            "job_id": "test_123",
            "url": "https://www.linkedin.com/jobs/view/test_123/",
            "title": "Senior Software Engineer",
            "company": "Tech Corp",
            "description": "We are looking for a Senior Software Engineer to join our team...",
            "post_date": "1 week ago",
            "scraped_at": datetime.utcnow().isoformat(),
            "source": "linkedin"
        }
    
    def __del__(self):
        """Cleanup on object destruction"""
        if self._browser_pool or self._playwright:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, schedule cleanup as a task
                    loop.create_task(self.cleanup())
                else:
                    # If no loop is running, run cleanup synchronously
                    loop.run_until_complete(self.cleanup())
            except Exception:
                # Ignore cleanup errors during destruction
                pass
