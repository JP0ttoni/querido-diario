# import logging
import re
from datetime import date, datetime as dt

import scrapy

from gazette.items import Gazette

# from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_itatiaia"
    TERRITORY_ID = "3302254"
    allowed_domains = ["itatiaia.rj.gov.br"]
    start_date = date(2019, 1, 28)
    BASE_URL = "https://itatiaia.rj.gov.br/wp-admin/admin-ajax.php"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://itatiaia.rj.gov.br",
        "Referer": "https://itatiaia.rj.gov.br/boletim-oficial/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    def start_requests(self):
        # Dados do formulário
        payload = {
            "action": "jet_smart_filters",
            "provider": "jet-engine/default",
            "query[_date_query_|date]": f"{self.start_date.strftime('%Y.%m.%d')}-{self.end_date.strftime('%Y.%m.%d')}",  # Intervalo de datas
            "defaults[post_status][]": "publish",
            "defaults[post_type]": "boletim-",
            "defaults[posts_per_page]": "2000",
            "defaults[paged]": "1",  # Página inicial
            "defaults[ignore_sticky_posts]": "1",
            "settings[lisitng_id]": "32705",
            "settings[columns]": "2",
            "settings[columns_tablet]": "3",
            "settings[columns_mobile]": "2",
            "settings[post_status][]": "publish",
            "settings[posts_num]": "16",
            "settings[max_posts_num]": "16",
            "settings[load_more_type]": "click",
            "settings[arrows]": "true",
            "settings[autoplay]": "true",
            "settings[autoplay_speed]": "5000",
            "settings[infinite]": "true",
            "settings[speed]": "500",
            "props[page]": "1",  # Página inicial
        }

        # Enviar requisição POST
        yield scrapy.FormRequest(
            url=self.BASE_URL,
            method="POST",
            headers=self.headers,
            formdata=payload,
            meta={"page": 1},  # Informar a página inicial no meta
        )

    def parse(self, response):
        try:
            html = response.json()["content"]
            if html:
                gazette_list = html.split("\n\t\t\t\t\t\t\t\t")
                for gazette_data in gazette_list:
                    date_match = re.search(r"<h6.*?>(.*?)</h6>", gazette_data)
                    title_match = re.search(r"<h5.*?>(.*?)</h5>", gazette_data)
                    url_match = re.search(r'href="(.*?)"', gazette_data)
                    if url_match and date_match and title_match:
                        date_match = date_match.group(1)
                        title_match = title_match.group(1)
                        edition_match = re.search(r"Nº (\d+)", title_match)
                        url_match = url_match.group(
                            1
                        )  # O método .group(1) retorna o conteúdo que foi capturado pelo primeiro grupo da expressão regular, que no caso é a URL.
                        if edition_match:
                            edition_match = edition_match.group(1)
                        else:
                            edition_match = re.search(r"nº (\d+)", title_match).group(1)
                        yield Gazette(
                            date=dt.strptime(date_match, "%d/%m/%Y").date(),
                            edition_number=edition_match,
                            is_extra_edition=False,
                            file_urls=[url_match],
                            power="executive",
                        )
        except Exception as error:
            print(f"erro foi:{error}")
