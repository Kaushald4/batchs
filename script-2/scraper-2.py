from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from time import sleep
import re
import json
import random
from selenium.webdriver.common.action_chains import ActionChains
import logging
from pymongo import MongoClient
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get('DB_URL')

client = MongoClient(DB_URL)

db = client['lawyers_db']
collection = db.get_collection('lawyers')

logging.basicConfig(filename="scraper1", filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument("User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")



driver = uc.Chrome(version_main=114, options=options)
# driver = webdriver.Chrome(options=options)
driver.maximize_window()
# driver.get("https://attorneys.superlawyers.com/personal-injury-plaintiff/new-york/new-york/?page=1")
# elem = driver.find_elements(By.CLASS_NAME, "lawyer-info-container > section a")

with open("batch-2.json", 'r') as file:
    firm_urls = json.load(file)

lawyers = []

RESTART_TIME = 2
PAGE_NUM = 0
LAWYER_DATA = 0

def init():
    if os.path.exists('script_running'):
        with open("script_running", 'r') as file:
            page_info = file.read()

        page_num = re.findall("SCRAPING\sPAGE:(\d*)", page_info)
        if len(page_num) >= 1:
            page_num = page_num[0]
        lawyer_data_num = re.findall("LAWYER_DATA:(\d*)", page_info)
        if len(lawyer_data_num) >= 1:
            lawyer_data_num = lawyer_data_num[0]
        
        global PAGE_NUM
        global LAWYER_DATA

        PAGE_NUM = int(page_num) if page_num else 0
        LAWYER_DATA = int(lawyer_data_num) if lawyer_data_num else 0



def scrape_lawyers_links():
    init()


    for i in range(PAGE_NUM, len(firm_urls)):
        print(f"Scraping.... page {i}/{len(firm_urls)}", firm_urls[i])
        logging.info(f"Scraping.... page {i}/{len(firm_urls)} url={firm_urls[i]}")
        driver.get(firm_urls[i])

        with open("script_running", 'w') as file:
            file.write(f"SCRAPING PAGE {i}/{len(firm_urls)}  PAGE_URL:{firm_urls[i]}")

        # all 35 lawyers url of current page
        lawyers_urls = []

        try:
            top_spots_el = driver.find_element(By.ID, "topspots_wrapper")
            top_spots_el = top_spots_el.find_elements(By.CLASS_NAME, 'full-name.fw-bold.mb-0.text-center.text-lg-start .directory_profile')
            top_spots_el = [top_spot.get_attribute('href') for top_spot in top_spots_el]
            lawyers_urls = [*top_spots_el, *lawyers_urls]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            spotlights_el = driver.find_element(By.ID, "spotlights_wrapper")
            spotlights_el = spotlights_el.find_elements(By.CLASS_NAME, 'full-name.fw-bold.mb-0.text-center.text-lg-start .directory_profile')
            spotlights_el = [spotlight.get_attribute('href') for spotlight in spotlights_el]
            lawyers_urls = [*lawyers_urls, *spotlights_el]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            poap_results_el = driver.find_element(By.ID, "poap_results")
            poap_results_el = poap_results_el.find_elements(By.CLASS_NAME, 'full-name.fw-bold.mb-0.text-center.text-lg-start .directory_profile')
            poap_results_el = [poap_result.get_attribute('href') for poap_result in poap_results_el]
            lawyers_urls = [*lawyers_urls, *poap_results_el]
        except NoSuchElementException as e:
            print(e.msg)

        scrape_lawyer_data(lawyers_urls, i)
    

def scrape_lawyer_data(urls, page_num):
    
    global LAWYER_DATA

    for i in range(LAWYER_DATA, len(urls)):
        print(f"Scraping lawyer data... {i}/{len(urls)}", urls[i])
        logging.info(f"Scraping lawyer data... {i}/{len(urls)} url={urls[i]}")
        driver.get(urls[i])

        with open("script_running", 'w') as file:
            file.write(f"SCRAPING PAGE:{page_num} LAWYER_DATA:{i}/{len(urls)} LAWYER_PAGE_URL:{urls[i]}")

        lawyer_name = ""
        lawyer_phone = ""
        practise_areas = []
        social_links = []
        selections = []
        bio = "",
        lectures = []
        awards = []
        clients = []
        educations = []
        bar_activity = []
        verdicts = []
        videos = []
        white_paper = []
        achievements = []
        firm_name = ''
        licensed_since = ''
        languages = ''
        profile_image = ""
        community_service = []
        industry_groups = []

        try:
            profile_image = driver.find_element(By.CLASS_NAME, 'profile-img.order-1.order-xl-2.mb-xl-4 img').get_attribute('src')

        except NoSuchElementException as e:
            print(e.msg)

        try:
            lawyer_name = driver.find_element(By.ID, "attorney_name").text
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            lawyer_phone = driver.find_element(By.CLASS_NAME, 'profile-phone-header.single-link').text
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'about')
            bio = element.text
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'languages')
            languages = element.text
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'licensed_since')
            licensed_since = element.text
        except NoSuchElementException as e:
            print(e.msg)

        try:
            firm_name = driver.find_element(By.CLASS_NAME, 'profile-info-card .profile-profile-header.d-none.d-xl-block.paragraph-large-xl.mb-0.mb-xl-3')
            if firm_name:
                firm_name = firm_name.get_attribute('text')
        except NoSuchElementException as e:
            print(e.msg)

        #profile switch tab
        try:
            element = driver.find_element(By.ID, 'practice-areas')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            pi_chart_el = driver.find_element(By.ID, 'piechart_legend')
            pi_chart_el = pi_chart_el.find_elements(By.CLASS_NAME, 'piechart_legend_row .piechart_legend_label_item')
            if pi_chart_el:
                practise_areas = [p_area.text for p_area in pi_chart_el]
        except NoSuchElementException as e:
            print(e.msg)

        # print(practise_areas)

        try:
            elements = driver.find_elements(By.CLASS_NAME, 'social_links .sm-container')
            for el in elements:
                if el:
                    link = el.find_element(By.TAG_NAME, 'a')
                    if link:
                        link = link.get_attribute('href')
                    
                    title = el.find_element(By.CLASS_NAME ,"sm-name")
                    if title:
                        title = title.text
            # social_links = [{'link': element.find_element(By.TAG_NAME ,"a").get_attribute('href'), 'title': element.find_element(By.CLASS_NAME ,"sm-name").text} for element in elements]
                    social_links.append({'link': link, 'title': title})
            # print(social_links)
        except NoSuchElementException as e:
            print(e.msg)

        try:
            element = driver.find_element(By.ID, 'selection_years')
            elements = element.find_elements(By.TAG_NAME, 'li')
            for selection in elements:
                if selection:
                    selections.append(selection.text)
            # selections = [selection.text for selection in elements]
        except NoSuchElementException as e:
            print(e.msg)


        
        # achievements tab switch
        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            lecture = driver.find_element(By.ID, 'lectures')
            lectures_elements = lecture.find_elements(By.CLASS_NAME, 'list-spaced-small li span')

            for lecture_el in lectures_elements:
                if lecture_el:
                    lectures.append({'value': lecture_el.text, 'title': 'lectures/writings'})      
            # lectures = [{'value':lecture_el.text, 'title': "lectures/writings"} for lecture_el in lectures]
        except NoSuchElementException as e:
            print(e.msg)

        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            community_services = driver.find_element(By.ID, 'community_service')
            community_services = community_services.find_elements(By.CLASS_NAME, 'list-spaced-small li span')

            for community_service_el in community_service:
                if community_service_el:
                    community_service.append(community_service_el.text)              
            # community_service = [community_service_el.text for community_service_el in community_services]
        except NoSuchElementException as e:
            print(e.msg)

        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            industry_group_element = driver.find_element(By.ID, 'industry_groups')
            industry_group_elements = industry_group_element.find_elements(By.CLASS_NAME, 'list-spaced-small li')
            
            for industry_group_el in industry_group_elements:
                if industry_group_el:
                    industry_groups.append(industry_group_el.text)


            # industry_groups = [industry_group_el.text for industry_group_el in industry_groups]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            award = driver.find_element(By.ID, 'awards')
            awards_element = award.find_elements(By.CLASS_NAME, 'list-spaced-small li span')

            for awards_el in awards_element:
                if awards_el:
                    awards.append({'value': awards_el.text, 'title': 'award'})

            # awards = [{'value':awards_el.text, 'title': "awards"} for awards_el in awards]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            client = driver.find_element(By.ID, 'clients')
            clients_element = client.find_elements(By.CLASS_NAME, 'list-spaced-small li span')
            clients = [client_el.text if client_el else 'N/A' for client_el in clients_element]
        except NoSuchElementException as e:
            print(e.msg)

        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            education = driver.find_element(By.ID, 'educational')
            educations_element = education.find_elements(By.CLASS_NAME, 'list-spaced-small li')
            educations = [education_el.text if education_el else "N/A" for education_el in educations_element]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            bar_activity = driver.find_element(By.ID, 'bar_activity')
            bar_activity = bar_activity.find_elements(By.CLASS_NAME, 'list-spaced-small li')
            bar_activity = [bar_activity_el.text if bar_activity_el else "N/A" for bar_activity_el in bar_activity]
        except NoSuchElementException as e:
            print(e.msg)
        
        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            verdicts = driver.find_element(By.ID, 'verdicts')
            verdicts = verdicts.find_elements(By.CLASS_NAME, 'list-spaced-small li')
            verdicts = [verdicts_el.text if verdicts_el else "N/A" for verdicts_el in verdicts]
        except NoSuchElementException as e:
            print(e.msg)

        # try:
        #     element = driver.find_element(By.ID, 'achievements')
        #     driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
        #     videos = driver.find_element(By.ID, 'videos')
        #     videos = videos.find_elements(By.CLASS_NAME, 'list-spaced-small span')
        #     videos = [{'title': videos_el.find_element(By.TAG_NAME, 'li span').text, 'link': videos_el.find_element(By.TAG_NAME, 'a').get_attribute('href')} for videos_el in videos]
        # except NoSuchElementException as e:
        #     print(e.msg)

        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            white_paper_element = driver.find_element(By.ID, 'white_paper')
            white_papers = white_paper_element.find_elements(By.CLASS_NAME, 'list-spaced-small > li > span')
            white_paper = [white_paper_el.text if white_paper_el else "N/A" for white_paper_el in white_papers]
        except NoSuchElementException as e:
            print(e.msg)
        

        try:
            element = driver.find_element(By.ID, 'achievements')
            driver.execute_script("arguments[0].setAttribute('class','tab-pane fade active show')", element)
            achievements = driver.find_element(By.ID, 'achievements')
            achievements = achievements.find_elements(By.CLASS_NAME, 'list-spaced-small li')
            achievements = [achievements_el.text if achievements_el else "N/A" for achievements_el in achievements]
        except NoSuchElementException as e:
            print(e.msg)
        
        data = {
            "lawyer_name":lawyer_name,
            "profile_image":profile_image,
            "lawyer_phone":lawyer_phone,
            "practise_areas":practise_areas,
            "social_links":social_links,
            "selections":selections,
            "bio":bio,
            "lectures":lectures,
            "awards":awards,
            "clients":clients,
            "educations":educations,
            "bar_activity":bar_activity,
            "verdicts":verdicts,
            "white_paper":white_paper,
            "achievements":achievements,
            "firm_name":firm_name,
            "licensed_since":licensed_since,
            "languages":languages,
            "industry_groups": industry_groups,
            "community_service":community_service
        }
        
        saved_data = collection.insert_one(data)
        logging.info(f"Saved to DB...  url={urls[i]}")
        print(f"Saved to DB...  url={urls[i]}")
        # total_saved_count+=1
        # lawyers.append(data)
        # with open("result-1.json", 'w') as file:
        #     json.dump(lawyers, file, indent=4)

        LAWYER_DATA = 0


scrape_lawyers_links()
