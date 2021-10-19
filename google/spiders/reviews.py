import scrapy
import re

class ReviewSpider(scrapy.Spider):
    name = "google-reviews"

    HEADERS = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        'referer': None
    }

    def start_requests(self):

        urls = ["https://www.google.com/async/reviewSort?vet=12ahUKEwiF6ILdr9fzAhXhyIUKHRa9C6cQxyx6BAgBEBU..i&ved=2ahUKEwiF6ILdr9fzAhXhyIUKHRa9C6cQjit6BAgBEHs&rlst=f&tbs=lrf:!1m4!1u3!2m2!3m1!1e1!1m4!1u2!2m2!2m1!1e1!2m1!1e2!2m1!1e3!3sIAE,lf:1,lf_ui:2&yv=3&async=feature_id:0x12a4a32290113c61%3A0x2bbaa81a2b0c6a57,review_source:All%20reviews,sort_by:qualityScore,is_owner:false,filter_text:,associated_topic:,next_page_token:EgIICg,_pms:s,_fmt:pc"]

        for url in urls:
            yield scrapy.Request(url=url, headers=self.HEADERS, callback=self.parse)

    def parse(self, response):

        all_reviews = response.css('.jxjCjc')

        for review in all_reviews:

            reviewer = review.css('div.TSUbDb a::text').extract_first()
            description = review.css('.Jtu6Td span::text').get("")
            review_rating = float(re.findall("\d", review.xpath('.//span[@class="Fam1ne EBe2gf"]/@aria-label').extract_first())[0])
            review_date = review.xpath('.//span[@class="dehysf lTi8oc"]/text()').extract_first()
            yield {
                "reviewer": reviewer,
                "description": description,
                "rating": review_rating,
                "review_date": review_date
            }

        next_page = response.css(".gws-localreviews__general-reviews-block::attr('data-next-page-token')").get(None)

        if next_page is not None:
            new_url = response.url
            new_url = re.sub("next_page_token:.{6}", "next_page_token:{}".format(next_page), new_url)

            yield scrapy.Request(url=new_url,
                                 callback=self.parse,
                                 headers=self.HEADERS)