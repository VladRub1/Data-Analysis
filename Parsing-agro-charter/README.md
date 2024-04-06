# Parsing Agro-Industrial Complex Charter

---

In this project I automatically collect information about legal entities — participants
of **Agro-Industrial Complex (AIC) Charter** in Russia.

Charter is an organization that unites companies working in the agro-industrial 
sector in Russia, as well as advocates fair competition in the entire agricultural 
market and the formation of intolerant attitude towards companies that violate 
the tax legislation of the Russian Federation. 
As of April 2024, the Charter includes 9366 legal entities.

The official website of the Charter is on the [link](https://хартия-апк.радо.рус/). 

The `requests` and `BeautifulSoup` libraries are used for parsing. 
The collected data has **no missing values**.

---

### Project content:
* [data](./data): data obtained after parsing
* [logs](./logs): logs during data collection
* [Data-collection.ipynb](./Data-collection.ipynb): **data collection** file
* [requirements.txt](./requirements.txt): project dependency description
