from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
from splinter import Browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import pymongo

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


#Gets headline and description paragraph from nasa news
def scrape_mars_news():
    browser=init_browser()
    mars_news = "https://mars.nasa.gov/news/"

    browser.visit(mars_news)
    mars_html = browser.html
    soup = bs(mars_html,'lxml')
    sleep(4)
    headline = soup.find('ul',class_='item_list').find('div',class_="content_title").find('a').text
    paragraph = soup.find('ul',class_='item_list').find('div',class_="article_teaser_body").text
    
    sleep(4)
    browser.quit()
    return [headline,paragraph]

#Gets current display image from JPL spaceimages
def scrape_jpl():
    browser=init_browser()
    jpl_images = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    jpl_root = "https://www.jpl.nasa.gov"

    browser.visit(jpl_images)
    jpl_html = browser.html
    soup = bs(jpl_html,'lxml')
    featured_image_url = jpl_root+soup.find('section',class_='main_feature').find("div",class_="carousel_items").\
                            find('article')['style'].split("'")[1]
    sleep(4)
    browser.quit()
    return [featured_image_url]

#Scrapes the weather on mars from twitter
def weather_on_mars():
    #SOURCE: https://medium.com/@dawranliou/twitter-scraper-tutorial-with-python-requests-beautifulsoup-and-selenium-part-2-b38d849b07fe
    driver = webdriver.Chrome()
    mars_twitter = "https://twitter.com/marswxreport"
    driver.get(mars_twitter)
    sleep(4)
    body = driver.find_element_by_tag_name('body')

    body.send_keys(Keys.PAGE_DOWN)

    mars_twitter_html = driver.page_source
    soup = bs(mars_twitter_html,'lxml')
    
    for result in soup.find_all(class_='css-901oao css-16my406 r-1qd0xha r-ad9z0x r-bcqeeo r-qvutc0'):
        text = result.text
        if text.split(" ")[0]=='InSight':
            sleep(4)
            driver.quit()
            return [text]

#Scrapes facts about mars
def mars_facts():
    facts_table = pd.read_html("https://space-facts.com/mars/")[0]
    facts_table = facts_table.rename(columns={0:'Measurement',1:"Mars"})
    mars_facts = facts_table.to_html(index=False)
    return [mars_facts]

#Scrapes images of mars' hemispheres
def mars_hemispheres(): 
    browser = init_browser()
    root_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(root_url)
    browser_html = browser.html


    soup = bs(browser_html,'lxml')
    a_list = soup.find_all(class_="itemLink product-item")

    urls = ['https://astrogeology.usgs.gov' + end_url for end_url in list(set([x['href'] for x in a_list]))]
    titles = [x.text for x in soup.find_all('h3')]
    url_title = {titles[i]:urls[i] for i in range(4)}


    results = []
    for title in url_title:
        url = url_title[title]
        browser.visit(url)
        browser_html = browser.html
        soup=bs(browser_html,'lxml')
        big_url = soup.find(class_='downloads').find_all('a')[1]['href']
        results.append({'title':title,'img_url':big_url})

    sleep(4)
    browser.quit()
    return [results]


def scrape():
    news = scrape_mars_news()
    data = {"news_headline": news[0],
            "news_paragraph": news[1],
            "jpl_img_url": scrape_jpl()[0],
            "mars_weather": weather_on_mars()[0],
            "mars_facts": mars_facts()[0],
            "hemisphere_img_urls": mars_hemispheres()[0]}
    return data
    


    