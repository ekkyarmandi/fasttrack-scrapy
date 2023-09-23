# Fasttrack Data Scraping

Data scraping script developed using Scrapy to collect dog race data from [fasttrack.grv.org.au](https://fasttrack.grv.org.au)

This project one is one of my data scraping experience in my career. You can find my other data scraping project in the list below:

- [fasttrack](https://github.com/ekkyarmandi/fasttrack-scrapy.git), dog race data scraping

\*_The rest will come_\*

## Todo

- [x] Develop the race schedule scraper
- [ ] Develop the details scraper

## How to run

0. (Optional) Create a virtual environtment

```bash
python -m venv .venv
```

1. Install the dependencies

```bash
pip install -r requirements.txt
```

2. Define the `from_date` and `to_date` inside the [fasttrack.py](fasttrack.py)

```python
class FastTrackCrawler(scrapy.Spider):
    name = "fasttrack"
    allowed_domains = ["fasttrack.grv.org.au"]
    from_date = datetime(2018, 1, 1)  # <- Define here
    to_date = datetime(2023, 9, 22)  # <- Define here
    dates = []

    def generate_params(self, from_date: str, to_date: str, page: int = 1):
    ...
```

3. Run the script

```bash
python fasttrack.py
```
