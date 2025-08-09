import os
import re
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import asyncio

class JobScraper:
    def __init__(self):
        self.timeout = 30000  # 30 seconds timeout - increased for better reliability
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
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
    
    async def scrape_job(self, url: str) -> Dict[str, Any]:
        """Scrape job description and metadata from LinkedIn job URL"""
        
        if not self._is_valid_linkedin_job_url(url):
            raise ValueError("Invalid LinkedIn job URL. Please provide a valid LinkedIn job posting URL.")
        
        job_id = self._extract_job_id_from_url(url)
        if not job_id:
            raise ValueError("Could not extract job ID from URL")
        
        async with async_playwright() as p:
            browser = None
            page = None
            try:
                print("Launching browser...")
                # Launch browser in headless mode with more robust settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-extensions',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                print("Creating new page...")
                # Create new page with realistic settings
                page = await browser.new_page(
                    user_agent=self.user_agent,
                    viewport={'width': 1366, 'height': 768}
                )
                
                # Set additional headers to appear more human-like
                await page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Upgrade-Insecure-Requests': '1',
                })
                
                print(f"Navigating to job URL: {url}")
                
                # Navigate to the job URL with more conservative wait strategy
                response = await page.goto(url, wait_until='load', timeout=self.timeout)
                print(f"Page response status: {response.status if response else 'No response'}")
                
                # Wait for network to settle
                await page.wait_for_load_state('networkidle', timeout=10000)
                
                if not response or response.status >= 400:
                    raise Exception(f"Failed to load page. Status: {response.status if response else 'No response'}")
                
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
                        element = await page.query_selector(selector)
                        if element:
                            # Try to click "Show more" button if present
                            try:
                                show_more_btn = await page.query_selector('.jobs-description__footer button, .inline-show-more-text__button')
                                if show_more_btn:
                                    await show_more_btn.click()
                                    await asyncio.sleep(1)
                            except Exception:
                                pass
                            
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
                
                print("Data validation successful, closing browser...")
                if browser:
                    await browser.close()
                
                # Return structured data
                return {
                    "job_id": job_id,
                    "url": url,
                    "title": job_title,
                    "company": company_name or "Unknown Company",
                    "description": job_description,
                    "post_date": post_date,
                    "scraped_at": datetime.utcnow().isoformat(),
                    "source": "linkedin"
                }
                
            except Exception as e:
                print(f"Scraping error: {str(e)}")
                try:
                    if browser:
                        await browser.close()
                except Exception as close_error:
                    print(f"Error closing browser: {close_error}")
                raise Exception(f"Failed to scrape job: {str(e)}")
    
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
