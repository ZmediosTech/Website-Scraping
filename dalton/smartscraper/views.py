# scraper/views.py

import asyncio
from datetime import date

from django.http import JsonResponse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from django.shortcuts import render

from .models import RightbizListing, BusinessForSaleListing


def dashboard(request):
    today = date.today()
    listings = RightbizListing.objects.filter(scraped_on=today,type='franchises').order_by('id')
    return render(request, 'latest.html', {
        'listings': listings,
        'year': today.year
    })

def get_filter_data(request):
    filter_name = request.GET.get('filter_name')
    rb_franchise_count = request.GET.get('rb_franchise_count')
    rb_bta_count = request.GET.get('rb_bta_count')
    bfs_franchise_count = request.GET.get('bfs_franchise_count')
    bfs_bta_count = request.GET.get('bfs_bta_count')

    today = date.today()
    if filter_name == 'franchises':
        if rb_franchise_count == '0':
            scrape_view_franchises(request)
            rb_franchise_count = '1'
        listings = RightbizListing.objects.filter(scraped_on=today,type='franchises').order_by('id')
    elif filter_name == 'all_franchises':
        listings = RightbizListing.objects.filter(type='franchises').order_by('id')
    elif filter_name == 'bta':
        if rb_bta_count == '0':
            scrape_view_bta(request)
            rb_bta_count = 1
        listings = RightbizListing.objects.filter(scraped_on=today,type='bta').order_by('id')
    elif filter_name == 'all_bta':
        listings = RightbizListing.objects.filter(type='bta').order_by('id')

    elif filter_name == 'bfs_franchises':
        if bfs_franchise_count == '0':
            scrape_view_bfs_franchises(request)
            bfs_franchise_count = '1'
        listings = BusinessForSaleListing.objects.filter(scraped_on=today,type='franchises').order_by('id')
    elif filter_name == 'bfs_all_franchises':
        listings = BusinessForSaleListing.objects.filter(type='franchises').order_by('id')
    elif filter_name == 'bfs_bta':
        if bfs_bta_count =='0':
            scrape_view_bfs_bta(request)
            bfs_bta_count = '1'
        listings = BusinessForSaleListing.objects.filter(scraped_on=today,type='bta').order_by('id')
    elif filter_name == 'bfs_all_bta':
        listings = BusinessForSaleListing.objects.filter(type='bta').order_by('id')

    data = [
        {
            'id': listing.id,
            'business_name': listing.business_name,
            'extra_info': listing.extra_info,
        }
        for listing in listings
    ]
    return JsonResponse({'data': data,'rb_franchise_count': rb_franchise_count,'rb_bta_count': rb_bta_count, 'bfs_franchise_count': bfs_franchise_count, 'bfs_bta_count': bfs_bta_count})

# ⬇️ Asynchronous function to fetch the page using Playwright
async def fetch_rightbiz_listings_franchises(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        # Scroll and wait for content to load
        await page.mouse.wheel(0, 1500)
        await page.wait_for_timeout(5000)

        try:
            await page.wait_for_selector(".content__body__item-img-list", timeout=30000)
        except Exception as e:
            print("Timeout waiting for selector:", e)

        html = await page.content()
        await browser.close()
        return html

# ⬇️ Synchronous function to parse HTML using BeautifulSoup
def extract_listings_franchises(html):
    soup = BeautifulSoup(html, "html.parser")
    franchise_items = soup.select(".franchise-result-item-content")

    results = []
    for item in franchise_items:
        name_tag = item.select_one(".franchise-result-item-user")
        business_name = name_tag.text.strip() if name_tag else "No Name"
        results.append({
            "business_name": business_name,
        })

    return results

def scrape_view_franchises(request):
    url = "https://www.rightbiz.co.uk/franchise-for-sale/"
    html = asyncio.run(fetch_rightbiz_listings_franchises(url))
    listings = extract_listings_franchises(html)
    for data in listings:
        if not RightbizListing.objects.filter(business_name=data["business_name"]).exists():
            RightbizListing.objects.create(
                business_name=data["business_name"],
                type='franchises',
                scraped_on=date.today()
            )
    return JsonResponse({"message": "Scraping and saving completed"})


# ⬇️ Asynchronous function to fetch the page using Playwright
async def fetch_rightbiz_listings_bta(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        # Scroll and wait for content to load
        await page.mouse.wheel(0, 1500)
        await page.wait_for_timeout(5000)

        try:
            await page.wait_for_selector(".content__body__item-list", timeout=30000)
        except Exception as e:
            print("Timeout waiting for selector:", e)

        html = await page.content()
        await browser.close()
        return html

# ⬇️ Synchronous function to parse HTML using BeautifulSoup
def extract_listings_bta(html):
    soup = BeautifulSoup(html, "html.parser")
    bta_items = soup.select(".content__body__item-info")

    results = []
    for item in bta_items:
        name_tag = item.select_one("a.link-title")
        business_name = name_tag.text.strip() if name_tag else "No Name"
        results.append({
            "business_name": business_name,
        })

    return results

def scrape_view_bta(request):
    url = "https://www.rightbiz.co.uk/search/?more_category=none&sector=businesses&location=uk&more_category=none&sortby=ctr&noindex=1"
    html = asyncio.run(fetch_rightbiz_listings_bta(url))
    listings = extract_listings_bta(html)
    for data in listings:
        if not RightbizListing.objects.filter(business_name=data["business_name"]).exists():
            RightbizListing.objects.get_or_create(
                business_name=data["business_name"],
                type='bta',
                scraped_on=date.today()

            )
    return JsonResponse({"message": "Scraping and saving completed"})


# ⬇️ Asynchronous function to fetch the page using Playwright
async def fetch_bfs_franchises(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        # Scroll and wait
        await page.mouse.wheel(0, 3000)
        await page.wait_for_timeout(5000)

        try:
            await page.wait_for_selector("div.listings.requestListContainer", timeout=20000)
        except Exception as e:
            print("Timeout waiting for selector:", e)

        html = await page.content()
        await browser.close()
        return html

# ⬇️ Synchronous function to parse HTML using BeautifulSoup
def extract_listings_bfs_franchises(html):
    soup = BeautifulSoup(html, "html.parser")
    image_tags = soup.select("div.listings.requestListContainer img")

    results = []
    for img in image_tags:
        business_name = img.get("alt", "").strip()
        if business_name:
            results.append({
                "business_name": business_name
            })

    return results

def scrape_view_bfs_franchises(request):
    url = "https://uk.businessesforsale.com/uk/franchises/search/franchise-opportunities"
    html = asyncio.run(fetch_bfs_franchises(url))
    listings = extract_listings_bfs_franchises(html)
    for data in listings:
        if not BusinessForSaleListing.objects.filter(business_name=data["business_name"]).exists():
            BusinessForSaleListing.objects.get_or_create(
                business_name=data["business_name"],
                type='franchises',
                scraped_on=date.today()

            )
    return JsonResponse({"message": "Scraping and saving completed"})


async def fetch_bfs_bta(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.goto(url, timeout=60000)

        # Scroll and wait
        await page.mouse.wheel(0, 3000)
        await page.wait_for_timeout(5000)

        try:
            await page.wait_for_selector("div.result", timeout=20000)
        except Exception as e:
            print("Timeout waiting for selector:", e)

        html = await page.content()
        await browser.close()
        return html

# ⬇️ Synchronous function to parse HTML using BeautifulSoup
def extract_listings_bfs_bta(html):
    soup = BeautifulSoup(html, "html.parser")
    business_links = soup.select("div.result h2.with-label-1 a")

    results = []
    for link in business_links:
        business_name = link.get_text(strip=True)
        if business_name:
            results.append({
                "business_name": business_name
            })

    return results

def scrape_view_bfs_bta(request):
    url = "https://uk.businessesforsale.com/uk/search/businesses-for-sale"
    html = asyncio.run(fetch_bfs_bta(url))
    listings = extract_listings_bfs_bta(html)
    for data in listings:
        if not BusinessForSaleListing.objects.filter(business_name=data["business_name"]).exists():
            BusinessForSaleListing.objects.get_or_create(
                business_name=data["business_name"],
                type='bta',
                scraped_on=date.today()

            )
    return JsonResponse({"message": "Scraping and saving completed"})