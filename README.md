# Data-Analysis

This section contains large-scale projects on **data collection** and 
**applied data analysis**:
* **[Logging-and-testing](./Logging-and-testing)**: examples of working with _logging_ 
  and _testing_ in Python using `logging` and `pytest` libraries
  * creating several custom loggers for logging the operation of the differential 
    evolution optimization method
  * achievement of 100% coverage of tests of the differential evolution optimization method 
* **[Numpy-and-Scipy](./Numpy-and-Scipy)**: examples of advanced work with `numpy` and `scipy` 
  modules for applied data analysis and scientific computing
* **[Olist-marketplace-analysis](./Olist-marketplace-analysis)**: advanced data analytics 
  based on data from Brazilian marketplace [Olist](https://olist.com/pt-br/)
  * building a _dashboard_ with interactive visualization, cross filters and 
    geodata with `dash` and `plotly`
  * analyzing order and payment data with `pandas`
  * visualization with `matplotlib` and `seaborn` to provide business insights and 
    make data-driven business decisions
* **[Parsing-central-election-commission](./Parsing-central-election-commission)**: 
  parsing of the Central election commission in Russia 
  [website](http://www.vybory.izbirkom.ru/region/izbirkom) to collect the 
  results of the largest federal elections in Russia for 2004–2020 and related 
  information (turnout, number of spoiled ballots, etc.). 
  The source has serious protection against automatic data collection, so to  
  bypass it a combination of `Selenium`, `BeautifulSoup` and `lxml` libraries is 
  used as a technical solution for the project.
* **[Pymongo-non-relational-db](./Pymongo-non-relational-db)**: an example of working 
  with _non-relational databases_ using `pymongo`. Analyzing different data 
  domains (student grade data, social media posts, a service for rating restaurants, 
  and banking data on financial transactions) with direct database queries
* **[Restaurant-analysis](./Restaurant-analysis)**: _parsing_ of the cartographic service
  website https://2gis.it/ 
  * gathering information about all branches of a café or 
    restaurant chain (average bill, attendance, working hours, etc.)
  * analysis and visualization of the data
  * the service functionality is available in the following countries: Italy, Czech Republic, 
    Cyprus, Chile, UAE, Kyrgyzstan, Ukraine, Uzbekistan, 
    Azerbaijan, Belarus, Russia, Kazakhstan
* **[Steam-game-parsing](./Steam-game-parsing)**: creating an automated _parsing machine_ 
  for the Internet site [Steam](https://store.steampowered.com/) (a video game digital 
  distribution service), using `scrapy` and `bs4` (`BeautifulSoup`).
