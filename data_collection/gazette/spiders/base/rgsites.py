import re
from datetime import datetime as dt

import scrapy

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class BaseRgSites(BaseGazetteSpider):
    def start_requests(self):
        yield scrapy.Request(self.BASE_URL)

    def parse(self, response):
        self.end_date
        years = response.css('div[role="tabpanel"]')
        years.reverse()
        for year in years:
            year_temp = year.css("::attr(id)").get()
            year_temp = year_temp.replace("tab_", "")
            if int(year_temp) < self.start_date.year:
                continue
            months = year.css("div.panel.panel-primary.rg-border-radius-none")
            for month in months:
                days = month.css("td.edicao")
                for day in days:
                    edition = day.css('a[data-toggle="modal-pdf"]::text').get()
                    edition = re.sub(r"\D", "", edition)
                    url_pdf = day.css('a[data-toggle="modal-pdf"]::attr(href)').get()
                    date_temp = day.css("span.visible-xs-inline-block::text").get()
                    date_temp = (
                        date_temp.strip()
                        .replace("\xa0", "")
                        .replace("(", "")
                        .replace(")", "")
                    )
                    date_temp = dt.strptime(date_temp, "%d/%m/%Y").date()
                    if (
                        int(year_temp) == self.start_date.year
                        and date_temp.month < self.start_date.month
                    ):
                        break

                    if date_temp < self.start_date:
                        continue

                    if date_temp > self.end_date:
                        return
                    else:
                        yield Gazette(
                            date=date_temp,
                            edition_number=edition,
                            is_extra_edition=False,
                            file_urls=[url_pdf],
                            power="executive",
                        )
