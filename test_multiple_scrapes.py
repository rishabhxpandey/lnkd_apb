#!/usr/bin/env python3
"""
Test script to verify that multiple consecutive Playwright scraping attempts work correctly.
This tests the improved JobScraper with browser pooling and resource management.
"""

import asyncio
import sys
import time
from backend.services.job_scraper import JobScraper

async def test_multiple_scrapes():
    """Test multiple consecutive scraping attempts"""
    
    # Use a public LinkedIn job URL for testing (you can replace with your own)
    test_url = "https://www.linkedin.com/jobs/view/4107690676/"
    
    scraper = JobScraper()
    results = []
    total_attempts = 3
    
    print(f"🧪 Testing {total_attempts} consecutive LinkedIn job scraping attempts...")
    print(f"📋 Test URL: {test_url}")
    print("=" * 80)
    
    try:
        for attempt in range(total_attempts):
            print(f"\n🔄 Attempt {attempt + 1}/{total_attempts}")
            start_time = time.time()
            
            try:
                result = await scraper.scrape_job(test_url)
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                results.append({
                    "attempt": attempt + 1,
                    "status": "✅ SUCCESS",
                    "duration": duration,
                    "job_title": result.get("title", "Unknown")[:50] + "...",
                    "company": result.get("company", "Unknown"),
                    "description_length": len(result.get("description", "")),
                })
                
                print(f"   ✅ Success in {duration}s")
                print(f"   📝 Title: {result.get('title', 'Unknown')[:50]}...")
                print(f"   🏢 Company: {result.get('company', 'Unknown')}")
                print(f"   📄 Description: {len(result.get('description', ''))} characters")
                
            except Exception as e:
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                results.append({
                    "attempt": attempt + 1,
                    "status": "❌ FAILED",
                    "duration": duration,
                    "error": str(e)[:100] + "..." if len(str(e)) > 100 else str(e)
                })
                
                print(f"   ❌ Failed in {duration}s")
                print(f"   🔥 Error: {str(e)[:100]}...")
    
    finally:
        # Clean up browser resources
        print(f"\n🧹 Cleaning up browser resources...")
        await scraper.cleanup()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    successful_attempts = len([r for r in results if "SUCCESS" in r["status"]])
    success_rate = (successful_attempts / total_attempts) * 100
    
    print(f"✨ Total attempts: {total_attempts}")
    print(f"✅ Successful: {successful_attempts}")
    print(f"❌ Failed: {total_attempts - successful_attempts}")
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    print(f"\n📋 Individual Results:")
    for result in results:
        print(f"   {result['attempt']}. {result['status']} ({result['duration']}s)")
        if "error" in result:
            print(f"      Error: {result['error']}")
        else:
            print(f"      {result['job_title']} at {result['company']}")
    
    # Determine if test passed
    if success_rate >= 66.7:  # At least 2/3 success rate
        print(f"\n🎉 TEST PASSED! Success rate: {success_rate:.1f}%")
        print("✅ Multiple consecutive scraping attempts work correctly!")
        return True
    else:
        print(f"\n💥 TEST FAILED! Success rate: {success_rate:.1f}%")
        print("❌ Multiple consecutive scraping attempts still have issues.")
        return False

if __name__ == "__main__":
    print("🚀 LinkedIn Job Scraper - Multiple Attempts Test")
    print("=" * 80)
    
    try:
        success = asyncio.run(test_multiple_scrapes())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⛔ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with unexpected error: {e}")
        sys.exit(1)
