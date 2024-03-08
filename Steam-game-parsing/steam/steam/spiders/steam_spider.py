import scrapy
import requests
import re

from bs4 import BeautifulSoup
from lxml import etree
from steam.items import SteamItem

queries = ['shooter', 'racing', 'survival']  # quiries (what we are looking for)
API = ''  # API key for ScraperAPI (not needed)


def parse_links_on_games(url):
    """
    A function that searches for valid links to all games that there are
    as a result of the search query (usually there are 25 of them)
    :param url: str, a link to a search query of the format
        f'https://store.steampowered.com/search/?term={query}&ignore_preferences=1&page={page}'
    :return: list, links to all games that are in the result of the search query (usually there are 25 of them)
    """
    # read the page input
    r = requests.get(url)
    page = r.content.decode("utf-8")
    soup = BeautifulSoup(page, 'html.parser')

    # look for links to games
    # first take all the candidates for links
    all_games = soup.find('div', attrs={'id': 'search_resultsRows'})  # there's one element, all the games

    links = set()
    for game in all_games.find_all('a'):
        # run some tests
        if game.get('href') is not None:
            link = game.get('href')
            if link == '' or 'app' not in link or 'agecheck' in link:
                print('BAD', link)
                # if the link is broken or there's a captcha, skip it
                continue
            else:
                links.add(link)

    return list(links)


def make_start_urls(queries):
    """
    A function that searches for links to all games on the first two pages 
    of Steam search (without filters).
    :param queries: list[str], a list of natural language queries,
        that the user is interested in searching for
        e.g. ['shooter', 'racing', 'survival']
    :return: list[str], a list of links to games matching the search
        for the specified keywords
    """
    start_urls = []
    for query in queries:
        for page in range(1, 3):
            # link format:
            # https://store.steampowered.com/search/?term=shooter&ignore_preferences=1&page=1
            # term - request body
            # ignore_preferences - not to take into account any filters (geographical, linguistic)
            # page - page number (even if the default is infinite scrolling)
            url = f'https://store.steampowered.com/search/?term={query}&ignore_preferences=1&page={page}'
            print(url)
            # collect all references to games found in the query
            games_links = parse_links_on_games(url)
            # add to the overall list
            start_urls.extend(games_links)

    return start_urls


class SteamSpider(scrapy.Spider):
    name = 'Steam'
    allowed_domains = ['store.steampowered.com']

    def __init__(self):
        # search for starting links, i.e., those that match the specified query
        self.start_urls = make_start_urls(queries)
        self.log(f'Found {len(self.start_urls)} links')

    def parse(self, response):
        """
        Method that parses a specific game (product) link
        :param response: scrapy request to url passed to self.start_urls
        """
        
        # I will use both BeautifulSoup and xpath (search as xml)
        soup = BeautifulSoup(response.body, 'html.parser')
        dom = etree.HTML(str(soup))

        # Looking for a link to the game
        link_raw = soup.find('meta', attrs={'property': 'og:url'}).get('content')
        link = link_raw.strip()

        # Game title
        name_raw = dom.xpath('//div[@id="appHubAppName"][@class="apphub_AppName"]/text()')
        name = ''.join(name_raw).strip()

        # The categories to which the game belongs
        categories_raw = dom.xpath('//div[@class="blockbg"]/a/text()')
        categories = '/'.join([one_category.strip() for one_category in categories_raw[1:]])  # названия самой игры тут нет

        # Number of reviews
        rev_number_raw = dom.xpath('//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="responsive_hidden"]/text()')
        rev_number = ','.join([re.sub(r'\D', '', rev_num) for rev_num in rev_number_raw])  # тут всегда должно быть одно число, но вдруг...

        # Overall score based on feedback
        overall_score_raw = dom.xpath('//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="game_review_summary positive"]/text()')
        overall_score = ''.join(overall_score_raw).strip()

        # Release date
        rel_date_raw = dom.xpath('//div[@class="release_date"]/div[@class="date"]/text()')
        rel_date = ''.join(rel_date_raw).strip()

        # Developer (usually one)
        developer_raw = dom.xpath('//div[@class="dev_row"]/div[@id="developers_list"]/a/text()')
        developer = ','.join([one_developer.strip() for one_developer in developer_raw])

        # Tags (usually many)
        tags_raw = dom.xpath('//div[@class="glance_tags popular_tags"]/a/text()')
        tags = '/'.join([one_tags.strip() for one_tags in tags_raw])

        # Price
        price_raw = dom.xpath('//div[@class="discount_final_price"]/text()')
        if len(price_raw) == 0:
            # if there is no discount, this field will be empty
            price_raw = dom.xpath('//div[@class="game_purchase_price price"]/text()')

        price = '/'.join(price_raw).strip()

        # Available platforms
        platforms_raw = dom.xpath('//div[@class="sysreq_tabs"]/div/text()')
        platforms = '/'.join([one_platform.strip() for one_platform in platforms_raw])

        # Create an instance of the SteamItem class, pass information to it
        item = SteamItem()

        item["name"] = name
        item["categories"] = categories
        item["rev_number"] = rev_number
        item["overall_score"] = overall_score
        item["rel_date"] = rel_date
        item["developer"] = developer
        item["tags"] = tags
        item["price"] = price
        item["platforms"] = platforms
        item["link"] = link

        yield item
