import scrapy
from scrapy.crawler import CrawlerProcess
from datetime import datetime
from urllib.parse import urlencode
from scrapy.loader import ItemLoader
import pandas as pd
import re

from items import FastTracksItem


class FastTrackCrawler(scrapy.Spider):
    name = "fasttrack"
    allowed_domains = ["fasttrack.grv.org.au"]
    from_date = datetime(2018, 1, 1)
    to_date = datetime(2023, 9, 22)
    dates = []

    def generate_params(self, from_date: str, to_date: str, page: int = 1):
        params = {
            "MeetingDateFrom": from_date,
            "MeetingDateTo": to_date,
            "Status": "Results Finalised",
            "DisplayAdvertisedEvents": False,
            "AllTracks": True,
            "SelectedTracks": "AllTracks",
            "searchbutton": "Search",
            "page": page,
        }
        return urlencode(params)

    def start_requests(self):
        params = self.generate_params(
            from_date=self.from_date.strftime(r"%d/%m/%Y"),
            to_date=self.to_date.strftime(r"%d/%m/%Y"),
            page=1,
        )
        url = "https://fasttrack.grv.org.au/Meeting/Search?" + params
        yield scrapy.Request(url, callback=self.parse)

    def get_pages(self, response):
        is_number = lambda value: re.search(r"\d", value)
        pages = response.css("div.pager span ::text").getall()
        pages = list(filter(is_number, pages))
        pages = list(map(int, pages))
        pages.remove(1)
        return pages

    def parse(self, response):
        items = self.parse_table(response)
        for item in items:
            yield item

        # iterate the pages
        pages = self.get_pages(response)
        for i in pages:
            params = self.generate_params(
                from_date=self.from_date.strftime(r"%d/%m/%Y"),
                to_date=self.to_date.strftime(r"%d/%m/%Y"),
                page=i,
            )
            url = "https://fasttrack.grv.org.au/Meeting/Search?" + params
            yield scrapy.Request(url, callback=self.parse_table)

        # check the latest date from the list of dates
        dt = max(self.dates)
        if dt < self.to_date:
            # update the `from_date` to the latest scraped date on each page
            self.from_date = dt
            # trigger the start requests again and construct new url with different from_date
            new_params = self.generate_params(
                from_date=self.from_date.strftime(r"%d/%m/%Y"),
                to_date=self.to_date.strftime(r"%d/%m/%Y"),
                page=1,
            )
            # url
            url = "https://fasttrack.grv.org.au/Meeting/Search?" + new_params
            # get requests with callback to this function
            yield scrapy.Request(url, callback=self.parse)

        # stop the iteration if the any scraped date equal to `to_date` variable

    def parse_table(self, response):
        results = []
        rows = response.css("table#results tbody tr")
        for row in rows:
            loader = ItemLoader(item=FastTracksItem(), selector=row)
            loader.add_css("day", "td:first-child::text")
            loader.add_css("track", "td:nth-child(2) a::text")
            loader.add_css("url", "td:nth-child(2) a::attr(href)")
            loader.add_css("date", "td:nth-child(3)::text")
            loader.add_css("time_slot", "td:nth-child(4)::text")
            loader.add_css("nominations_close", "td:nth-child(5)::text")
            loader.add_css("scratchings_close", "td:nth-child(6)::text")
            loader.add_css("status", "td:nth-child(7)::text")
            loader.add_css("options", "td:nth-child(8)::text")
            item = loader.load_item()
            path = item["url"]
            # join the url path with the url origin
            if "http" not in path:
                item["url"] = response.urljoin(path)
            # append the value into the item list
            results.append(item)
            # convert the date string into datetime obj
            date = datetime.strptime(item["date"], r"%d/%m/%Y")
            self.dates.append(date)
        return results


filename = "output.csv"
process = CrawlerProcess(
    settings={
        "FEED_URI": filename,
        "FEED_FORMAT": "csv",
    }
)

process.crawl(FastTrackCrawler)
process.start()

df = pd.read_csv(filename)
df.drop_duplicates("url", inplace=True)
df.to_csv(filename, index=False)
