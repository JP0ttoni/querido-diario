# import logging
from datetime import date

import scrapy

# from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_itatiaia"
    TERRITORY_ID = ""
    allowed_domains = ["itatiaia.rj.gov.br"]
    # start_urls = ["https://itatiaia.rj.gov.br/boletim-oficial"]
    start_date = date(2020, 5, 6)
    url = "https://itatiaia.rj.gov.br/boletim-oficial"

    # Cabeçalhos HTTP
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
        # URL da API

        # Dados do formulário
        payload = {
            "action": "jet_smart_filters",
            "provider": "jet-engine/default",
            "query[_date_query_|date]": "2023.8.1-2024.6.19",  # Intervalo de datas
            "defaults[post_status][]": "publish",
            "defaults[post_type]": "boletim-",
            "defaults[posts_per_page]": "16",
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
            url=self.url,
            method="POST",
            headers=self.headers,
            formdata=payload,
            meta={"page": 1},  # Informar a página inicial no meta
        )

    def parse(self, response):
        # html = response.css()

        page = response.meta["page"]
        total_pages = 10  # Ajuste este número para o máximo de páginas disponíveis
        if page < total_pages:
            next_page = page + 1
            payload = {
                "action": "jet_smart_filters",
                "provider": "jet-engine/default",
                "query[_date_query_|date]": "2023.8.1-2024.6.19",
                "defaults[post_status][]": "publish",
                "defaults[post_type]": "boletim-",
                "defaults[posts_per_page]": "16",
                "defaults[paged]": str(next_page),  # Atualizando para a próxima página
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
                "props[page]": str(next_page),  # Atualizando para a próxima página
            }
            yield scrapy.FormRequest(
                url="https://itatiaia.rj.gov.br/wp-admin/admin-ajax.php",
                method="POST",
                headers=self.headers,
                formdata=payload,
                callback=self.parse,
                meta={"page": next_page},
            )

        # yield Gazette(
        #    date = date(),
        #    edition_number = "",
        #    is_extra_edition = False,
        #    file_urls = [""],
        #    power = "executive",
        # )
