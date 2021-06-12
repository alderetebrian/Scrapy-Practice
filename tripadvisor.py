from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Hotel(Item):
    nombre = Field()
    precio = Field()
    descripcion = Field()
    facilidades = Field()

class TripAdvisor(CrawlSpider):
    name = "Hoteles"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    start_urls = ['https://www.tripadvisor.com.ar/Hotels-g303506-Rio_de_Janeiro_State_of_Rio_de_Janeiro-Hotels.html']

    download_delay = 2

    rules = (
        Rule(
            LinkExtractor(
                allow=r'/Hotel_Review-'
            ), follow=True, callback="parse_hotel"            
        ),
    )

    def quitarSimboloDolar(self, texto):
        nuevoTexto = texto.replace("$", "")
        return nuevoTexto
            

    def parse_hotel(self, response):
        sel = Selector(response)
        item = ItemLoader(Hotel(), sel)
        descripciones = item.get_xpath('//div[@class="cPQsENeY"]/div//p/text()')
        descripciones = " ".join(descripciones)

        item.add_xpath('nombre', '//h1[@id="HEADING"]/text()')
        item.add_xpath('precio', '//div[@class="CEf5oHnZ"]/text()', MapCompose(self.quitarSimboloDolar))
        item.add_value('descripcion', descripciones)
        #item.add_xpath('descripcion', '//div[@class="cPQsENeY"]/div//p/text()')
        item.add_xpath('facilidades', '//div[@data-test-target="amenity_text"]/text()')

        yield item.load_item()