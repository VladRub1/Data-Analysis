# Steam parsing

---

This project is dedicated to creating an automated parsing machine for the 
[Steam](https://store.steampowered.com/) website — one of the most popular 
services for digital distribution of video games. 
The project actively uses `scrapy` framework and `bs4` library (`BeautifulSoup`).

Project content:
* [examples](./examples): example of the parser result in `.json` format
* [steam](./steam): the main code for the parser
* [Python_scrapy_steam_parsing.ipynb](./Python_scrapy_steam_parsing.ipynb):
  file with code creation and parser result analysis
* [requirements.txt](./requirements.txt): project dependency description


## Starting the parser
Create a project with `scrapy` in the terminal:
```bash
python -m scrapy startproject steam
cd .\steam\
```

Run the parser, collect the result in `items.json`:
```bash
python -m scrapy crawl Steam -o items.json
```
