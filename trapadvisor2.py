from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

class Opinion(Item):
    titulo = Field()
    calificacion = Field()
    contenido = Field()
    autor = Field()


class TrapAdvisor(CrawlSpider):
    name = "OpinionesTripAdvisor"
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 100
    }
    
    allowed_domains = ['tripadvisor.com.ar']
    start_urls = ['https://www.tripadvisor.com.ar/Hotels-g303506-Rio_de_Janeiro_State_of_Rio_de_Janeiro-Hotels.html']
    
    download_delay = 1
    
    rules = (
        #Paginacion de hoteles (h)
        Rule(
            LinkExtractor(
                allow=r'-oa\d+-'
            ), follow=True
        ),
        #Detalle de hoteles (v)
        Rule(
            LinkExtractor(
                allow=r'/Hotel_Review-',
                restrict_xpaths=['//div[@id="taplc_hsx_hotel_list_lite_dusty_hotels_combined_sponsored_0"]//a[@data-clicksource="HotelName"]']
            ), follow=True
        ),
        #Paginacion de opiniones dentro de un hotel (h)
        Rule(
            LinkExtractor(
                allow=r'-or\d+-'
            ), follow=True
        ),
        #Detalle de perfil de usuario (v)
        Rule(
            LinkExtractor(
                allow=r'/Profile/',
                restrict_xpaths=['//div[@data-test-target="reviews-tab"]//a[contains(@class, "ui_header")]']
            ), follow=True, callback='parse_opinion'
        )
    )
    
    def obtenerCalificacion(self, texto):
        #ui_bubble_rating bubble_10
        calificacion = texto.split("_")[-1]
        return calificacion
    
    def parse_opinion(self, response):
        sel = Selector(response)
        opiniones = sel.xpath('//div[@id="content"]/div/div')
        autor = sel.xpath('//h1/span/text()').get()
        
        for opinion in opiniones:
            item = ItemLoader(Opinion(), opinion)
            item.add_value('autor', autor)
            item.add_xpath('titulo', './/div[@class="_3IEJ3tAK _2K4zZcBv"]')
            item.add_xpath('contenido', './/q/text()')
            item.add_xpath('calificacion', './/div[@class="_1VhUEi8g _2K4zZcBv"]/span/@class', MapCompose(self.obtenerCalificacion))
            
            yield item.load_item()