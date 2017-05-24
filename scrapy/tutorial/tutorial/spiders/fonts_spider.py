import scrapy

class FontSpider(scrapy.Spider):
    name = "fonts"

    def start_requests(self):
        # recurse_depth = 10
        categories = {
            # 501: "sans_serif",
            # 502: "serif",
            # 503: "mono",
            601: "calligraphy",
            401: "blackletter",
            603: "handwritten",
            604: "brush"

        }

        urls = [
            ('http://www.dafont.com/theme.php?cat={}'.format(i), i) for i in categories.keys()
        ]



        for url in urls:
            request = scrapy.Request(url=url[0], callback=self.parse)
            request.meta['category'] = url[1]
            request.meta['categories'] = categories
            request.meta['counter'] = 0
            # request.meta['recurse-depth'] = recurse_depth
            yield request

    def parse(self, response):
        category = response.meta['category']
        categories = response.meta['categories']
        counter = response.meta['counter']+1
        # recurse_depth = response.meta['recurse-depth']
        for download_link in response.css('.dl::attr(href)').extract():

            yield {
                'file_url': download_link,
                'name': download_link[download_link.find("=")+1:],
                'category': categories.get(category)
            }

        try:
            next_page = response.css('.noindex a::attr(href)').extract()[-1]

            if next_page is not None and next_page.find("page") != -1:
                follow_link = response.follow(next_page, callback=self.parse)
                follow_link.meta['category'] = category
                follow_link.meta['categories'] = categories
                follow_link.meta['counter'] = counter
                # follow_link.meta['recurse-depth'] = recurse_depth
                yield follow_link

        except Exception:
            pass

