import re
from datetime import date, datetime as dt

import scrapy

from gazette.items import Gazette
from gazette.spiders.base import BaseGazetteSpider


class UFMunicipioSpider(BaseGazetteSpider):
    name = "rj_barra_do_pirai"
    TERRITORY_ID = ""
    allowed_domains = ["transparencia.portalbarradopirai.com.br"]
    BASE_URL = "https://transparencia.portalbarradopirai.com.br/index.php/pt/links/boletim-municipal"
    start_date = date(2009, 1, 7)
    first_time = True

    def start_requests(self):
        yield scrapy.Request(self.BASE_URL)

    def parse(self, response):
        print(f"url: {response.url}")
        links = response.css('div[itemprop="articleBody"]')
        links = links.css(
            'a[target="_blank"]::attr(href)'
        ).getall()  # é para fazer o reverse aqui
        links.reverse()
        links = list(dict.fromkeys(links))
        print(links)
        if links:
            first_url = f"https://transparencia.portalbarradopirai.com.br{links[0]}"
            # Passa os links restantes junto com a requisição
            yield scrapy.Request(
                first_url,
                callback=self.parse_document,
                cb_kwargs={"remaining_links": links[1:]},  # Armazena os links restantes
            )

    def parse_document(self, response, remaining_links):
        print(f"Processando documento em: {response.url}")
        year = response.css(
            'h1[itemprop="headline"]::text'
        ).get()  # retorna 'boletim municipal <ano>'
        match = re.search(r"\d+", year)
        year = int(match.group())
        if year == 2010:
            return
        print(year)

        data = response.css("table.easyfolderlisting")
        data = data.css(
            'a[target="_blank"]'
        )  # fazer reverse aqui, aquie dentro tem o link no href e a data no ::text
        pdfs_link = data.css("::attr(href)").getall()
        pdfs_link.reverse()
        for pdf_link in pdfs_link:
            edition = re.search(r"\/(\d+)\s-\s", pdf_link)
            if edition:
                edition.group(1)
            else:
                edition = re.search(r"(\d+\w?)\s*- Data", pdf_link).group(1)
            try:
                date_tmp = re.search(r" -\s*Data\s+(\d{2}-\d{2})\.pdf", pdf_link)
                if date_tmp:
                    date_tmp = date_tmp.group(1)
                    date_tmp = f"{date_tmp}-{year}"
                    yield Gazette(
                        date=dt.strptime(date_tmp, "%d-%m-%Y").date(),
                        edition_number=edition,
                        is_extra_edition=False,
                        file_urls=[pdf_link],
                        power="executive",
                    )
            except Exception as error:
                print(error)
        # https://transparencia.portalbarradopirai.com.br/images/boletim/2009/222 - Data  07-01.pdf

        if remaining_links:
            next_url = (
                f"https://transparencia.portalbarradopirai.com.br{remaining_links[0]}"
            )
            yield scrapy.Request(
                next_url,
                callback=self.parse_document,  # função chamada apos a requisição ser concluida
                cb_kwargs={
                    "remaining_links": remaining_links[1:]
                },  # Passa os links restantes
            )

        # Lógica de extração de metadados

        # partindo de response ...
        #
        # ... o que deve ser feito para coletar DATA DO DIÁRIO?
        # ... o que deve ser feito para coletar NÚMERO DA EDIÇÃO?
        # ... o que deve ser feito para coletar se a EDIÇÃO É EXTRA?
        # ... o que deve ser feito para coletar a URL DE DOWNLOAD do arquivo?

        # yield Gazette(
        #    date = date(),
        #    edition_number = "",
        #    is_extra_edition = False,
        #    file_urls = [""],
        #    power = "executive",
        # )
