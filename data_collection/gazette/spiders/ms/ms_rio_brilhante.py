from datetime import date

from gazette.spiders.base.dosp import BaseDospSpider


class MsRioBrilhanteSpider(BaseDospSpider):
    TERRITORY_ID = "5007208"
    name = "ms_rio_brilhante"
    start_urls = ["https://www.imprensaoficialmunicipal.com.br/rio_brilhante"]
    start_date = date(2024, 2, 1)
