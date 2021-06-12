from scrapy.item import Field
from scrapy.item import Item
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.loader.processors import MapCompose
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader


class Articulo(Item):
    titulo = Field()
    contenido = Field()
    
class Review(Item):
    Titulo = Field()
    calificacion = Field()
    
class Video(Item):
    titulo = Field()
    fecha_publicacion = Field()


class IGNCrawler(CrawlSpider):
    name = 'ign'
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'CLOSESPIDER_PAGECOUNT': 30
    }
    
    allowed_domains = ['latam.ign.com']
    
    download_delay = 1
    
    start_urls = ['https://latam.ign.com/se/?model=article&q=ps4']
    
    rules = (
        #Horizontalidad por tipo de informacion
        Rule(
            LinkExtractor(
                allow=r'type='
            ), follow=True
        ),
        #Horizontalidad por paginacion
        Rule(
            LinkExtractor(
                allow=r'&page=\d+'
            ), follow=True
        ),
        #Una regla por cada tipo de contenido donde ire verticalmente
        #Reviews
        Rule(
            LinkExtractor(
                allow=r'/review/'
            ), follow=True, callback='parse_review'
        ),
        #Videos
        Rule(
            LinkExtractor(
                allow=r'/video/'
            ), follow=True, callback='parse_video'
        ),
        #Articulos
        Rule(
            LinkExtractor(
                allow=r'/news/'
            ), follow=True, callback='parse_news'
        ),
    )
    
    def parse_news(self, response):
        item = ItemLoader(Articulo(), response)
        item.add_xpath('titulo', '//h1/text()')
        item.add_xpath('contenido', '//div[@id="id_text"]//*/text()')
        
        yield item.load_item()
    
    def parse_review(self, response):
        item = ItemLoader(Review(), response)
        item.add_xpath('titulo', '//h1/text()')
        item.add_xpath('calificacion', '//div[@class="review"]//span[@class="side-wrapper side-wrapper hexagon-content"]/text()')
        
        yield item.load_item()

    def parse_video(self, response):
        item = ItemLoader(Video(), response)
        item.add_xpath('titulo', '//h1/text()')
        item.add_xpath('fecha_publicacion', '//span[@class="publish-date"]/text()')
        
        yield item.load_item()