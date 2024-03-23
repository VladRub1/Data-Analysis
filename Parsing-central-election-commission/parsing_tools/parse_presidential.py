import logging
import selenium
import pandas as pd

from bs4 import BeautifulSoup
from time import sleep
from lxml import etree
from IPython.display import clear_output

from selenium import webdriver as wb
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def find_presidential_elections_links(br: selenium.webdriver.chrome.webdriver.WebDriver,
                                      s: selenium.webdriver.chrome.service.Service) -> list[set[str]]:
    """
    Function for finding links to regional election commissions with
    the results of four Russian presidential elections: in 2004, 2008, 2012, 2018.
    Simulates the behavior of a real user on the Central Electoral Commission (CEC)
    website with election results.
    Follows the "user's path" if he/she wanted to get electoral statistics on these votes.

    :param br: An object of type selenium.webdriver.chrome.webdriver.WebDriver
               that represents a browser (Google Chrome) in remote control mode.
    :param s:  An object of type selenium.webdriver.chrome.service.Service
               that is required to initialize a new Google Chrome browser 
               in remote management mode. 
               Uses ChromeDriver utility to automate browser management.
    :return:   A list of sets with strings - links to election results
               by regional election commissions, which you will need to click on
               to get detailed statistics on voting results in the region.
               The list consists of 4 sets: links to election results
               for 2004, 2008, 2012, 2018, respectively.
    """
    # We'll collect data from the CEC website:
    url = 'http://www.vybory.izbirkom.ru/region/izbirkom'
    # Open the start page of the section with election results
    br.get(url)

    # Open the filters tab
    filters_show = br.find_element(By.CSS_SELECTOR, ".filter")
    filters_show.click()

    # We set time limits for the search by taking dates that include
    # all presidential elections
    inp_start_date = '01.01.2000'
    inp_end_date = '31.12.2023'

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

    # Get the page code
    sleep(10)
    br.implicitly_wait(5)
    page = br.page_source
    # Pass the page code to BeautifulSoup
    soup = BeautifulSoup(page)

    # All elections found
    elections = soup.find_all('ul', attrs={'class': 'list-group list-group-flush vibory-list'})[0]

    # Collecting links to each year's election pages
    elections_links = []

    for election in elections.find_all('li'):
        election_info = election.find_all('a')
        if len(election_info) > 0:
            if 'президент' in election_info[0].text.lower():
                presidential_elections_link = election_info[0].get('href')
                print('[INFO] Found a link to the presidential election:', presidential_elections_link)
                elections_links.append(presidential_elections_link)

    election_years = ['2004', '2008', '2012', '2018']
    region_links_all_years = []

    for i, elections_link in enumerate(elections_links):
        # Create a browser and open the election link
        br = wb.Chrome(service=s)
        br.get(elections_link)
        sleep(10)
        # Get the page code
        page = br.page_source
        # Pass the page code to BeautifulSoup
        soup = BeautifulSoup(page)

        # Collect links to the regions within this election
        regions = soup.find_all('ul', attrs={'style': 'opacity: 1; transition-duration: 0.5s;'})[0]

        region_links = set()

        for region in regions.find_all('li'):
            if 'цик' in region.find_all('a')[1].text.lower():
                # The level of the whole of Russia is unnecessary
                continue
            # The rel_link will contain a relative link, which
            # needs to be folded into the domain name
            rel_link = region.find_all('a')[1].get('href')
            full_link = 'http://www.vybory.izbirkom.ru/' + rel_link
            region_links.add(full_link)

        print(f'[INFO] {len(region_links)} links were found for {election_years[i]}')
        region_links_all_years.append(region_links)
        # Close the browser
        br.close()

    return region_links_all_years


def parse_2004_presidential_elections(s: selenium.webdriver.chrome.service.Service,
                                      region_links_2004: set[str],
                                      logger: logging.Logger) -> pd.DataFrame:
    """
    Function for processing the results of the 2004 Russian presidential election.
    It simulates the behavior of a real user who, having selected a specific
    election, would switch between different regions in order to study electoral
    results in different regions at the level of TECs (territorial election commissions).

    :param s: An object of type selenium.webdriver.chrome.service.Service 
              that is required to initialize a new Google Chrome browser 
              in remote management mode. 
              Uses ChromeDriver utility to automate browser management.
    :param region_links_2004: A set of the rows are links to election results for
              regional election commissions in one region.
              They should be clicked to collect data on election results.
    :param logger: A logger that logs data processing errors during parsing
              and writes them to the `errors.log` file.
    :return: pandas.DataFrame with election results for all regions of
    the Russian Federation at the time of the 2004 elections, broken down to
    the TEC level. In addition to the basic information, it also contains
    additional information collected by election commissions during the elections.
    """
    # Follow the links to the results by region
    for i, link in enumerate(region_links_2004):
        print(f'[INFO] Собираю данные про регион №{i + 1} из {len(region_links_2004)} \nURL: {link}')
        # Create a new browser, open a link to the results by region
        br = wb.Chrome(service=s)
        br.get(link)
        try:
            sleep(10)
            br.implicitly_wait(10)
            # Select the results section
            results_button = br.find_element(By.CSS_SELECTOR, "#election-results-name")
            results_button.click()
            sleep(10)
            br.implicitly_wait(10)
            # Select the required data representation
            # ("Summary table of voting results" / "Сводная таблица итогов голосования")
            table_button = br.find_element(By.CSS_SELECTOR, r"#election-results > table > tbody > tr:nth-child(2) > td > a")
            table_button.click()
            sleep(10)
            br.implicitly_wait(10)
        except:
            # If something went wrong, log the error
            logger.error(f"Didn't get the data about the 2004 election results in the region at the link: \n{link}")
            br.close()
            continue
        # Get the page code
        page = br.page_source
        soup = BeautifulSoup(page)
        # Collect data
        # Name of the commission
        commission_name = soup.find_all('table', attrs={'class': 'table-borderless table-sm',
                                                        'style': "width:100%"})[0].find_all('td')[1].text
        # Date of voting
        vote_date_raw = soup.find_all('div', attrs={'id': 'election-info'})[0]
        vote_date_full = vote_date_raw.find_all('td')[-1].text
        # Results table
        vote_data_raw = soup.find_all('table', attrs={'class': 'table-bordered table-striped table-sm',
                                                      'style': 'width:100%;overflow:auto'})[0]

        # Collect the name of the TECs
        sub_level_names = []

        # Here you can additionally get the value of the href attribute in the <a> tag
        # to get links to the level below (PECs)
        for sub_level_name in vote_data_raw.find_all('td', attrs={'class': 'text-center'}):
            sub_level_names.append(sub_level_name.text)

        # Collect the results
        full_data = []

        rows = vote_data_raw.find_all('tr')
        for row in rows:
            cols = row.find_all('td', attrs={'class': 'text-right'})
            if len(cols) == 0:
                continue
            full_data.append([col.text.strip() for col in cols])

        participation = full_data[:-7]
        vote_results_raw = full_data[-7:]

        results_abs = []
        results_percent = []

        for vote_results_for_candidate in vote_results_raw:
            results_abs.append([res.split()[0] for res in vote_results_for_candidate])
            results_percent.append([res.split()[1].replace('%', '') for res in vote_results_for_candidate])

        # Generate dataset by region
        df = pd.DataFrame(
            # Electoral statistics
            {'elections_year': [vote_date_full] * len(sub_level_names),
             'region': [commission_name] * len(sub_level_names),
             'commission_name': sub_level_names,
             'voters_number': participation[0],
             'ballots_number_received': participation[1],
             'issued_ballots_number_early': participation[2],
             'issued_ballots_number_voting_day_incide': participation[3],
             'issued_ballots_number_voting_day_outside': participation[4],
             'ballots_number_extinguished': participation[5],
             'ballots_number_portable_boxes': participation[6],
             'ballots_number_stationary_boxes': participation[7],
             'ballots_number_invalid': participation[8],
             'ballots_number_valid': participation[9],
             'ballots_number_absentee_received': participation[10],
             'ballots_number_absentee_issued': participation[11],
             'voters_number_voted_on_absentee_ballots': participation[12],
             'number_absentee_ballots_unused': participation[13],
             'ballots_number_absentee_issued_to_tik_voters': participation[14],
             'ballots_number_lost': participation[15],
             'ballots_number_not_counted': participation[16],
             # Votes for candidates
             'glazyev_sergey_yurievich_number': results_abs[0],
             'glazyev_sergey_yurievich_percent': results_percent[0],
             'malyshkin_oleg_alexandrovich_number': results_abs[1],
             'malyshkin_oleg_alexandrovich_percent': results_percent[1],
             'mironov_sergey_mikhailovich_number': results_abs[2],
             'mironov_sergey_mikhailovich_percent': results_percent[2],
             'putin_vladimir_vladimirovich_number': results_abs[3],
             'putin_vladimir_vladimirovich_percent': results_percent[3],
             'khakamada_irina_mutsuovna_number': results_abs[4],
             'khakamada_irina_mutsuovna_percent': results_percent[4],
             'kharitonov_nikolai_mikhailovich_number': results_abs[5],
             'kharitonov_nikolai_mikhailovich_percent': results_percent[5],
             'against_all_number': results_abs[6],
             'against_all_percent': results_percent[6],
             'link': [link] * len(sub_level_names)
             }
        )

        if i == 0:
            stacked_df = df.copy()
        else:
            stacked_df = pd.concat([stacked_df, df])

        # Close the browser
        br.close()
        # Clear the output in the cell
        clear_output()

    return stacked_df


def parse_2008_presidential_elections(s: selenium.webdriver.chrome.service.Service,
                                      region_links_2008: set[str],
                                      logger: logging.Logger) -> pd.DataFrame:
    """
    Function for processing the results of the 2008 Russian presidential election.
    It simulates the behavior of a real user who, having selected a specific
    election, would switch between different regions in order to study electoral
    results in different regions at the level of TECs (territorial election commissions).

    :param s: An object of type selenium.webdriver.chrome.service.Service 
              that is required to initialize a new Google Chrome browser 
              in remote management mode. 
              Uses ChromeDriver utility to automate browser management.
    :param region_links_2008: A set of the rows are links to election results for
              regional election commissions in one region.
              They should be clicked to collect data on election results.
    :param logger: A logger that logs data processing errors during parsing
              and writes them to the `errors.log` file.
    :return: pandas.DataFrame with election results for all regions of
    the Russian Federation at the time of the 2008 elections, broken down to
    the TEC level. In addition to the basic information, it also contains
    additional information collected by election commissions during the elections.
    """
    # Follow the links to the results by region
    for i, link in enumerate(region_links_2008):
        print(f'[INFO] Собираю данные про регион №{i + 1} из {len(region_links_2008)} \nURL: {link}')
        # Create a new browser, open a link to the results by region
        br = wb.Chrome(service=s)
        br.get(link)
        sleep(10)
        br.implicitly_wait(10)
        # Select the results section
        results_button = br.find_element(By.CSS_SELECTOR, "#election-results-name")
        results_button.click()
        sleep(10)
        br.implicitly_wait(10)
        try:
            # Select the required data representation
            # ("Summary table of voting results" / "Сводная таблица итогов голосования")
            table_button = br.find_element(By.CSS_SELECTOR,
                                           r"#election-results > table > tbody > tr:nth-child(2) > td > a")
            table_button.click()
            sleep(10)
            br.implicitly_wait(10)
        except:
            # If something went wrong, log the error
            logger.error(f"Didn't get the data about the 2008 election results in the region at the link: \n{link}")
            br.close()
            continue
        # Get the page code
        page = br.page_source
        soup = BeautifulSoup(page)
        # Collect data
        # Name of the commission
        commission_name = soup.find_all('table', attrs={'class': 'table-borderless',
                                                        'width': "100%"})[0].find_all('td')[1].text
        # Date of voting
        vote_date_raw = soup.find_all('div', attrs={'id': 'election-info'})[0]
        vote_date_full = vote_date_raw.find_all('div')[-1].text
        # Results table
        vote_data_raw = soup.find_all('div', attrs={'class': 'table-wrapper'})[0]
        # Collect the name of the TECs
        sub_level_names = []
        # Here you can additionally get the value of the href attribute in the <a> tag
        # to get links to the level below (PECs)
        for sub_level_name in vote_data_raw.find_all('th', attrs={'class': 'text-center'}):
            sub_level_names.append(sub_level_name.text)

        # Collect the results
        full_data = []

        rows = vote_data_raw.find_all('tr')
        for row in rows:
            cols = row.find_all('td', attrs={'class': 'text-right'})
            if len(cols) == 0:
                continue
            full_data.append([col.text.strip() for col in cols])

        participation = full_data[:-4]
        vote_results_raw = full_data[-4:]

        results_abs = []
        results_percent = []

        for vote_results_for_candidate in vote_results_raw:
            results_abs.append([res.split()[0] for res in vote_results_for_candidate])
            results_percent.append([res.split()[1].replace('%', '') for res in vote_results_for_candidate])

        # Generate dataset by region
        df = pd.DataFrame(
            # Electoral statistics
            {'elections_year': [vote_date_full] * len(sub_level_names[1:]),
             'region': [commission_name] * len(sub_level_names[1:]),
             'commission_name': sub_level_names[1:],
             'voters_number': participation[0],
             'ballots_number_received': participation[1],
             'issued_ballots_number_early': participation[2],
             'issued_ballots_number_voting_day_incide': participation[3],
             'issued_ballots_number_voting_day_outside': participation[4],
             'ballots_number_extinguished': participation[5],
             'ballots_number_portable_boxes': participation[6],
             'ballots_number_stationary_boxes': participation[7],
             'ballots_number_invalid': participation[8],
             'ballots_number_valid': participation[9],
             'ballots_number_absentee_received': participation[10],
             'ballots_number_absentee_issued': participation[11],
             'voters_number_voted_on_absentee_ballots': participation[12],
             'number_absentee_ballots_unused': participation[13],
             'ballots_number_absentee_issued_to_tik_voters': participation[14],
             'ballots_number_lost': participation[15],
             'ballots_number_not_counted': participation[16],
             'number_absentee_ballots_lost': participation[17],
             'number_absentee_ballots_not_taken': participation[18],
             # Votes for candidates
             'bogdanov_andrey_vladimirovich_number': results_abs[0],
             'bogdanov_andrey_vladimirovich_percent': results_percent[0],
             'zhirinovsky_vladimir_volfovich_number': results_abs[1],
             'zhirinovsky_vladimir_volfovich_percent': results_percent[1],
             'zyuganov_gennady_andreevich_number': results_abs[2],
             'zyuganov_gennady_andreevich_percent': results_percent[2],
             'medvedev_dmitry_anatolyevich_number': results_abs[3],
             'medvedev_dmitry_anatolyevich_percent': results_percent[3],
             'link': [link] * len(sub_level_names[1:])
             }
        )

        if i == 0:
            stacked_df = df.copy()
        else:
            stacked_df = pd.concat([stacked_df, df])

        # Close the browser
        br.close()
        # Clear the output in the cell
        clear_output()

    return stacked_df


def parse_2012_presidential_elections(s: selenium.webdriver.chrome.service.Service,
                                      region_links_2012: set[str],
                                      logger: logging.Logger) -> pd.DataFrame:
    """
    Function for processing the results of the 2012 Russian presidential election.
    It simulates the behavior of a real user who, having selected a specific
    election, would switch between different regions in order to study electoral
    results in different regions at the level of TECs (territorial election commissions).

    :param s: An object of type selenium.webdriver.chrome.service.Service 
              that is required to initialize a new Google Chrome browser 
              in remote management mode. 
              Uses ChromeDriver utility to automate browser management.
    :param region_links_2012: A set of the rows are links to election results for
              regional election commissions in one region.
              They should be clicked to collect data on election results.
    :param logger: A logger that logs data processing errors during parsing
              and writes them to the `errors.log` file.
    :return: pandas.DataFrame with election results for all regions of
    the Russian Federation at the time of the 2012 elections, broken down to
    the TEC level. In addition to the basic information, it also contains
    additional information collected by election commissions during the elections.
    """
    # Follow the links to the results by region
    for i, link in enumerate(region_links_2012):
        print(f'[INFO] Собираю данные про регион №{i + 1} из {len(region_links_2012)} \nURL: {link}')
        # Create a new browser, open a link to the results by region
        br = wb.Chrome(service=s)
        br.get(link)
        try:
            sleep(10)
            br.implicitly_wait(10)
            # Select the results section
            results_button = br.find_element(By.CSS_SELECTOR, "#election-results-name")
            results_button.click()
            sleep(10)
            br.implicitly_wait(10)
            # Select the required data representation
            # ("Summary table of voting results" / "Сводная таблица итогов голосования")
            table_button = br.find_element(By.CSS_SELECTOR,
                                           r"#election-results > table > tbody > tr.trReport.\32 0120304 > td > a")
            table_button.click()
            sleep(10)
            br.implicitly_wait(10)
        except:
            # If something went wrong, log the error
            logger.error(f"Didn't get the data about the 2012 election results in the region at the link: \n{link}")
            br.close()
            continue
        # Get the page code
        page = br.page_source
        soup = BeautifulSoup(page)
        # Collect data
        # Name of the commission
        commission_name = soup.find_all('table', attrs={'class': 'table-borderless',
                                                        'width': "100%"})[0].find_all('td', attrs={'class': 'text-center'})[0].text
        # Date of voting
        vote_date_raw = soup.find_all('div', attrs={'class': 'row tab-pane active show'})[0]
        vote_date_full = vote_date_raw.find_all('td')[0]
        # Results table
        vote_data_raw = soup.find_all('div', attrs={'class': 'table-wrapper'})[0]
        # Collect the name of the TECs
        sub_level_names = []
        # Here you can additionally get the value of the href attribute in the <a> tag
        # to get links to the level below (PECs)
        for sub_level_name in vote_data_raw.find_all('th', attrs={'class': 'text-center'}):
            sub_level_names.append(sub_level_name.text)

        # Collect the results
        full_data = []

        rows = vote_data_raw.find_all('tr')

        for row in rows:
            cols = row.find_all('td', attrs={'class': 'text-right'})
            if len(cols) == 0:
                continue
            full_data.append([col.text.strip() for col in cols])

        participation = full_data[:-5]
        vote_results_raw = full_data[-5:]

        results_abs = []
        results_percent = []

        for vote_results_for_candidate in vote_results_raw:
            results_abs.append([res.split()[0] for res in vote_results_for_candidate])
            results_percent.append([res.split()[1].replace('%', '') for res in vote_results_for_candidate])

        # Generate dataset by region
        df = pd.DataFrame(
            # Electoral statistics
            {'elections_year': [vote_date_full] * len(sub_level_names[1:]),
             'region': [commission_name] * len(sub_level_names[1:]),
             'commission_name': sub_level_names[1:],
             'voters_number': participation[0],
             'ballots_number_received': participation[1],
             'issued_ballots_number_early': participation[2],
             'issued_ballots_number_voting_day_incide': participation[3],
             'issued_ballots_number_voting_day_outside': participation[4],
             'ballots_number_extinguished': participation[5],
             'ballots_number_portable_boxes': participation[6],
             'ballots_number_stationary_boxes': participation[7],
             'ballots_number_invalid': participation[8],
             'ballots_number_valid': participation[9],
             'ballots_number_absentee_received': participation[10],
             'ballots_number_absentee_issued_at_polling_station': participation[11],
             'voters_number_voted_on_absentee_ballots': participation[12],
             'number_absentee_ballots_unused': participation[13],
             'ballots_number_absentee_issued_to_tik_voters': participation[14],
             'number_absentee_ballots_lost': participation[15],
             'ballots_number_lost': participation[16],
             'ballots_number_not_counted': participation[17],
             # Votes for candidates
             'zhirinovsky_vladimir_volfovich_number': results_abs[0],
             'zhirinovsky_vladimir_volfovich_percent': results_percent[0],
             'zyuganov_gennady_andreevich_number': results_abs[1],
             'zyuganov_gennady_andreevich_percent': results_percent[1],
             'mironov_sergey_mikhailovich_number': results_abs[2],
             'mironov_sergey_mikhailovich_percent': results_percent[2],
             'prokhorov_mikhail_dmitrievich_number': results_abs[3],
             'prokhorov_mikhail_dmitrievich_percent': results_percent[3],
             'putin_vladimir_vladimirovich_number': results_abs[4],
             'putin_vladimir_vladimirovich_percent': results_percent[4],
             'link': [link] * len(sub_level_names[1:])
             }
        )

        if i == 0:
            stacked_df = df.copy()
        else:
            stacked_df = pd.concat([stacked_df, df])

        # Close the browser
        br.close()
        # Clear the output in the cell
        clear_output()

    return stacked_df


def parse_2018_presidential_elections(s: selenium.webdriver.chrome.service.Service,
                                      region_links_2018: set[str],
                                      logger: logging.Logger) -> pd.DataFrame:
    """
    Function for processing the results of the 2018 Russian presidential election.
    It simulates the behavior of a real user who, having selected a specific
    election, would switch between different regions in order to study electoral
    results in different regions at the level of TECs (territorial election commissions).

    :param s: An object of type selenium.webdriver.chrome.service.Service 
              that is required to initialize a new Google Chrome browser 
              in remote management mode. 
              Uses ChromeDriver utility to automate browser management.
    :param region_links_2018: A set of the rows are links to election results for
              regional election commissions in one region.
              They should be clicked to collect data on election results.
    :param logger: A logger that logs data processing errors during parsing
              and writes them to the `errors.log` file.
    :return: pandas.DataFrame with election results for all regions of
    the Russian Federation at the time of the 2018 elections, broken down to
    the TEC level. In addition to the basic information, it also contains
    additional information collected by election commissions during the elections.
    """
    # Follow the links to the results by region
    for i, link in enumerate(region_links_2018):
        print(f'[INFO] Собираю данные про регион №{i + 1} из {len(region_links_2018)} \nURL: {link}')
        # Create a new browser, open a link to the results by region
        br = wb.Chrome(service=s)
        br.get(link)
        try:
            sleep(10)
            br.implicitly_wait(10)
            # Select the results section
            results_button = br.find_element(By.CSS_SELECTOR, "#election-results-name")
            results_button.click()
            sleep(10)
            br.implicitly_wait(10)
        except:
            # If something went wrong, log the error
            logger.error(f"Didn't get the data about the 2018 election results in the region at the link: \n{link}")
            br.close()
            continue
        # Select the required data representation
        # ("Summary table of voting results" / "Сводная таблица итогов голосования")
        table_button = br.find_element(By.CSS_SELECTOR,
                                       r"#election-results > table > tbody > tr.trReport.\32 0180318 > td > a")

        table_button.click()
        sleep(10)
        br.implicitly_wait(10)
        # Get the page code
        page = br.page_source
        soup = BeautifulSoup(page)
        # Collect data
        # Name of the commission
        commission_name = soup.find_all('table', attrs={'class': 'table-borderless',
                                                        'width': "100%"})[0].find_all('td', attrs={'class': 'text-center'})[0].text

        # Date of voting
        vote_date_raw = soup.find_all('div', attrs={'class': 'row tab-pane active show'})[0]
        vote_date_full = vote_date_raw.find_all('td')[0].text
        # Results table
        vote_data_raw = soup.find_all('div', attrs={'class': 'table-wrapper'})[0]
        # Собираю название регионов
        sub_level_names = []
        # Here you can additionally get the value of the href attribute in the <a> tag
        # to get links to the level below (PECs)
        for sub_level_name in vote_data_raw.find_all('th', attrs={'class': 'text-center'}):
            sub_level_names.append(sub_level_name.text)

        # Collect the results
        full_data = []

        rows = vote_data_raw.find_all('tr')

        for row in rows:
            cols = row.find_all('td', attrs={'class': 'text-right'})
            if len(cols) == 0:
                continue
            full_data.append([col.text.strip() for col in cols])

        participation = full_data[:-8]
        vote_results_raw = full_data[-8:]

        results_abs = []
        results_percent = []

        for vote_results_for_candidate in vote_results_raw:
            results_abs.append([res.split()[0] for res in vote_results_for_candidate])
            results_percent.append([res.split()[1].replace('%', '') for res in vote_results_for_candidate])

        # Generate dataset by region
        df = pd.DataFrame(
            # Electoral statistics
            {'elections_year': [vote_date_full] * len(sub_level_names[1:]),
             'region': [commission_name] * len(sub_level_names[1:]),
             'commission_name': sub_level_names[1:],
             'voters_number': participation[0],
             'ballots_number_received': participation[1],
             'issued_ballots_number_early': participation[2],
             'issued_ballots_number_voting_day_incide': participation[3],
             'issued_ballots_number_voting_day_outside': participation[4],
             'ballots_number_extinguished': participation[5],
             'ballots_number_portable_boxes': participation[6],
             'ballots_number_stationary_boxes': participation[7],
             'ballots_number_invalid': participation[8],
             'ballots_number_valid': participation[9],
             'ballots_number_lost': participation[10],
             'ballots_number_not_counted': participation[11],
             # Votes for candidates
             'baburin_sergey_nikolaevich_number': results_abs[0],
             'baburin_sergey_nikolaevich_percent': results_percent[0],
             'grudinin_pavel_nikolaevich_number': results_abs[1],
             'grudinin_pavel_nikolaevich_percent': results_percent[1],
             'zhirinovsky_vladimir_volfovich_number': results_abs[2],
             'zhirinovsky_vladimir_volfovich_percent': results_percent[2],
             'putin_vladimir_vladimirovich_number': results_abs[3],
             'putin_vladimir_vladimirovich_percent': results_percent[3],
             'sobchak_ksenia_anatolyevna_number': results_abs[4],
             'sobchak_ksenia_anatolyevna_percent': results_percent[4],
             'suraykin_maxim_alexandrovich_number': results_abs[5],
             'suraykin_maxim_alexandrovich_percent': results_percent[5],
             'titov_boris_yurievich_number': results_abs[6],
             'titov_boris_yurievich_percent': results_percent[6],
             'yavlinsky_grigory_alekseevich_number': results_abs[7],
             'yavlinsky_grigory_alekseevich_percent': results_percent[7],
             'link': [link] * len(sub_level_names[1:])
             }
        )

        if i == 0:
            stacked_df = df.copy()
        else:
            stacked_df = pd.concat([stacked_df, df])

        # Close the browser
        br.close()
        # Clear the output in the cell
        clear_output()

    return stacked_df
