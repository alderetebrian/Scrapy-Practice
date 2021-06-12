from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Articulo(Item):
    titulo = Field()
    precio = Field()
    descripcion = Field()
    caracteristicas = Field()

class MercadoLibreCrawler(CrawlSpider):
    name = "mercadoLibre"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 20
    }

    download_delay = 1

    allowed_domains = ['listado.mercadolibre.com.ar', 'casa.mercadolibre.com.ar', 'terreno.mercadolibre.com.ar', 'departamento.mercadolibre.com.ar']

    start_urls = ['https://listado.mercadolibre.com.ar/inmueble_DisplayType_LF']

    rules = (
        Rule(
            LinkExtractor(
                allow=r'/inmueble_Desde_'
            ), follow=True
        ),

        Rule(
            LinkExtractor(
                allow=r'/MLA-'
            ), follow=True, callback='parse_items'
        ),
    )
    
    def limpiarTexto(self, texto):
        nuevoTexto = texto.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()
        return nuevoTexto

    def precioLimpio(self, texto):
        nuevoPrecio = texto.replace('.', '')
        return nuevoPrecio

    def parse_items(self, response):
        item = ItemLoader(Articulo(), response) 
        item.add_xpath('titulo', '//h1[@class="item-title__primary"]/text()', MapCompose(self.limpiarTexto))
        item.add_xpath('descripcion', '//div[@class="item-description__text"]/p/text()', MapCompose(self.limpiarTexto))
        item.add_xpath('precio', '//span[contains(@class, "price-tag-motors")]/span[2]/text()', MapCompose(self.precioLimpio))

        yield item.load_item()