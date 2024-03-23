import selenium
import pandas as pd

from bs4 import BeautifulSoup
from time import sleep
from lxml import etree

from selenium import webdriver as wb
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def find_regional_links(br: selenium.webdriver.chrome.webdriver.WebDriver) -> set[str]:
    """
    Function for finding links to regional election commissions with
    the results of nationwide voting on amendments to the Russian Constitution in 2020.
    Simulates the behavior of a real user on the Central Electoral Commission (CEC) site
    with election results. Follows the "user's path" if he/she would like to get electoral
    statistics for a given vote.

    :param br: An object of type selenium.webdriver.chrome.webdriver.WebDriver
               that represents a browser (Google Chrome) in remote control mode.
    :return:   A set of strings consisting of links to election results by
               regional election commission, which you will need to click on
               to get detailed statistics on the voting results in the region.
    """
    # We'll collect data from the CEC website:
    url = 'http://www.vybory.izbirkom.ru/region/izbirkom'
    # Open the start page of the section with election results
    br.get(url)

    # Open the filters tab
    filters_show = br.find_element(By.CSS_SELECTOR, ".filter")
    filters_show.click()

    # We set time limits for the search, taking dates that include
    # constitutional amendment vote
    inp_start_date = '01.01.2020'
    inp_end_date = '31.12.2020'

    # Insert dates into the filter
    start_date = br.find_element(By.CSS_SELECTOR, "#start_date")
    start_date.clear()
    sleep(3)  # wait a little while
    start_date.send_keys(inp_start_date)
    sleep(3)  # wait a little while

    end_date = br.find_element(By.CSS_SELECTOR, "#end_date")
    end_date.clear()
    sleep(3)  # wait a little while
    end_date.send_keys(inp_end_date)
    sleep(3)  # wait a little while

    # Set the filter value by election level
    elect_level = br.find_element(By.CSS_SELECTOR, ".select2-search__field")
    elect_level_useropt = ['Федеральный']  # choose federal

    for i in elect_level_useropt:
        sleep(3)
        elect_level.send_keys(i)
        sleep(1)
        elect_level.send_keys(Keys.ENTER)
        sleep(1)
        elect_level.clear()

    # We do not set a filter on the type of election
    # Filter for currently existing entities
    elect_actreg_useropt = ['Москва', 'Санкт-Петербург']

    elect_actreg = br.find_element(By.CSS_SELECTOR, "[aria-describedby='select2-actual_regions_subjcode-container']")
    for i in elect_actreg_useropt:
        elect_actreg.send_keys(i)
        sleep(1)  # wait a little while
        br.implicitly_wait(5)  # this function asks the browser to wait for the page to load all the way through
        elect_actreg.send_keys(Keys.ENTER)
        sleep(1)  # wait a little while
        br.implicitly_wait(5)
        elect_actreg.clear()

    # We do not set a filter for abolished entities
    # We do not put a filter on the electoral system

    # Click on the search button
    sleep(5)
    search_button = br.find_element(By.ID, "calendar-btn-search")
    sleep(1)
    search_button.click()

    # Choosing the right election (by amendment)
    sleep(5)
    elections_button = br.find_element(By.CSS_SELECTOR,
                                       "#vibory > ul > li:nth-child(2) > div > div.col-12.col-md-8 > a")
    sleep(1)
    elections_button.click()

    # Get the page code
    sleep(10)
    br.implicitly_wait(5)
    page = br.page_source
    # Pass the page code to BeautifulSoup
    soup = BeautifulSoup(page)

    # Look for links to results by region
    regions = soup.find_all('li', attrs={'id': '100100163596969'})[0]
    links = set()

    # Collect links
    for region in regions.find_all('li'):
        # The rel_link will contain a relative link, which
        # needs to be folded into the domain name
        rel_link = region.find_all('a')[1].get('href')
        full_link = 'http://www.vybory.izbirkom.ru/' + rel_link
        links.add(full_link)

    print(f'[INFO] {len(links)} links found')
    # Close the browser
    br.close()

    return links


def parse_one_regional_page(s: selenium.webdriver.chrome.service.Service, link: str) -> pd.DataFrame:
    """
    A function that processes a single page with the results of the nationwide
    voting on amendments to the Russian Constitution in 2020 within a single
    regional election commission.
    It simulates the behavior of a real user who, having selected a specific election,
    would switch between different regions in order to research electoral results
    in different regions at the level of TECs (territorial election commissions).

    :param s:    An object of type selenium.webdriver.chrome.service.Service
                 that is required to initialize a new Google Chrome browser
                 in remote management mode.
                 Uses ChromeDriver utility to automate browser management.
    :param link: String, a link to election results in one region.
    :return:     pandas.DataFrame, processed data on election results
                 in one region, which are available on the `link` page.
    """
    print(f'[INFO] Link analyzed: {link}')
    # Open a new browser with a new region
    br = wb.Chrome(service=s)
    br.get(link)
    sleep(10)
    # Select the results section
    results_button = br.find_element(By.CSS_SELECTOR, "#vote-results-name")
    results_button.click()
    sleep(10)
    # Select the required data representation
    # ("Summary table of voting results" / "Сводная таблица итогов голосования")
    table_button = br.find_element(By.CSS_SELECTOR,
                                   r"#vote-results > table > tbody > tr.trReport.\32 0200701 > td > a")
    table_button.click()
    sleep(10)
    # Get the page code
    page = br.page_source
    # Read the page code through BeautifulSoup
    soup = BeautifulSoup(page)
    # Read page code as XML code
    dom = etree.HTML(str(soup))
    # Name of commission (region)
    commission_name = soup.find_all('table', attrs={'class': 'table-borderless', 'width': "100%"})[0].find_all('td',
                                             attrs={'class': 'text-center'})[0].text

    print(f'[INFO] Region: {commission_name}')

    # Using XPath to address as an XML page
    vote_date = dom.xpath('/html/body/div[2]/main/div[2]/div[2]/div[2]/div/div[10]/div/table[1]/tbody/tr/td/text()')[0]

    # Voting data (table)
    vote_data = soup.find_all('div', attrs={'class': 'table-wrapper'})[0]

    # Collect the names of the TECs
    sub_level_names = []

    # Here you can additionally get the value of the href attribute in the <a> tag
    # to get links to the level below (PECs)
    for sub_level_name in vote_data.find_all('th', attrs={'class': 'text-center'}):
        sub_level_names.append(sub_level_name.text)

    participation = []
    # Collect the rows of the table and run through them
    rows = vote_data.find_all('tr')

    for row in rows:
        cols = row.find_all('td', attrs={'align': 'right'})
        if len(cols) == 0:
            # If there is no data in the row (these are not results)
            continue
        participation.append([col.text for col in cols])

    # The rows with votes for/against have the number of votes and the percentage:
    # let's divide them up
    results_abs = []
    results_percent = []

    for row in rows:
        cols = row.find_all('td', attrs={'class': 'text-right'})
        if len(cols) == 0:
            # If there is no data in the row (these are not results)
            continue
        results_abs.append([col.text.split()[0] for col in cols])
        results_percent.append([col.text.split()[1] for col in cols])

    # Generate dataset by region
    df = pd.DataFrame({
        'vote_date': [vote_date] * len(sub_level_names[1:]),
        'region': [commission_name] * len(sub_level_names[1:]),
        'commission_name': sub_level_names[1:],
        'voters_number': participation[0],
        'issued_ballots_number': participation[1],
        'turned_ballots_number': participation[2],
        'bad_ballots_number': participation[3],
        'for_votes_number': results_abs[0],
        'for_votes_percent': results_percent[0],
        'against_votes_number': results_abs[1],
        'against_votes_percent': results_percent[1],
        'link': [link] * len(sub_level_names[1:])
    })

    # Close the browser
    br.close()

    return df
