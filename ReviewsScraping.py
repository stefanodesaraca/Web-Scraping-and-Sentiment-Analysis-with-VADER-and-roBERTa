import sys
import numpy as np
from TReviewsUsefulInfo import TrustpilotLinkIntervals, CPUsNumber, seleniumExecutablePath
from ReviewsDatabase import reviewsDatabaseManagement as reviewsDB
import time
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import uuid
import re
import os
from pathlib import Path
import math
import concurrent.futures
from tqdm import tqdm
import heapq
import gc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

pd.set_option("display.max_columns", None)


class RevScraping:

    def __init__(self, tLink, companyName):
        self.tLink = tLink
        self.companyName = companyName
        self.quitReOpenSteps = TrustpilotLinkIntervals # If the trustpilot page has less than n-thousand pages this can just be an empty list
        self.RDB = reviewsDB()


    def __repr__(self):
        print(f"Trustpilot Link: {self.tLink} | Company Name: {self.companyName}")


    def createCompanyDirectory(self):
        os.makedirs(f"{self.companyName}", exist_ok=True)  # If the folder already exists it won't raise any errors
        os.makedirs(f"./{self.companyName}/{self.companyName}-EDA", exist_ok=True)
        os.makedirs(f"./{self.companyName}/{self.companyName}-Data", exist_ok=True)

        return None

    @staticmethod
    def closest(lst, K):
        return heapq.nsmallest(1, lst, key=lambda x: abs(x - K))[0]


    @staticmethod
    def startDriver():
        ser = Service(executable_path=seleniumExecutablePath)
        chrome_options = Options()
        chrome_options.add_argument(r'obtainedCookies')
        chrome_options.add_argument('--start-minimized')
        driver = webdriver.Chrome(service=ser, options=chrome_options)

        return driver


    @staticmethod
    def acceptCookies(driver):
        try:
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()  # Accepts cookies
        except:
            print("No cookies button found")
            pass
        return None


    def setPagesNumber(self, driver):

        driver.get(self.tLink + "?languages=all")

        time.sleep(1.5)

        self.acceptCookies(driver)

        pagesNumber = int(driver.find_element(By.NAME, "pagination-button-last").text)  # Finds the total number of pages
        time.sleep(3)

        assert pagesNumber not in self.quitReOpenSteps, "Total pages number was already in quitReOpenSteps variable"

        self.quitReOpenSteps.append(pagesNumber)  # Appending as the last element the last page, so when that has been scraped too, the while loop closes
        print(f"Total pages: {pagesNumber}")

        return None


    def getHTMLs(self):
        pageCnt = 0
        progressBarCnt = 0
        baseLink = self.tLink + "?languages=all"  # Applying the "all languages" filter from the URL instead of clicking buttons on the page

        print("Base Trustpilot Link: ", baseLink)

        driver = self.startDriver()
        self.setPagesNumber(driver)
        driver.close()

        print("Intervals: ", self.quitReOpenSteps)

        assert len(self.quitReOpenSteps) != 0, "No elements in self.quitReOpenSteps list"


        #Main while loop
        #Until the pageCnt isn't equal to the last page the loop won't stop
        while pageCnt != self.quitReOpenSteps[-1]:

            htmlList = []

            driver = self.startDriver()  # Starting the webdriver

            #The second condition is needed, otherwise it will bring trustpilot the home page without the "?languages=all" filter applied
            if pageCnt != self.quitReOpenSteps[-1] and pageCnt != 0:
                newLink = baseLink + f"&page={str(pageCnt + 1)}"  # Updating the Trustpilot link, so it starts from the page it has stopped on before. Adding one because the last page before stopping for the next iteration of the main while loop is included in the htmlList
                driver.get(newLink)  # Gets on the correct page link
            else:
                driver.get(baseLink)

            time.sleep(3)

            self.acceptCookies(driver)

            time.sleep(3)

            # buttonFilter = driver.find_element(By.CSS_SELECTOR, "#__next > div > div > main > div > div.styles_mainContent__nFxAv > section > div.paper_paper__1PY90.paper_outline__lwsUX.card_card__lQWDv.styles_reviewsOverview__mVIJQ > div.styles_container__0e2OC > button") #Filter button
            # buttonFilter.click() #Clicks filter button
            # time.sleep(3)

            # buttonLanguages = driver.find_element(By.ID, "language-option-all") #Sets "all" on languages option
            # buttonLanguages.click() #Confirms choice
            # time.sleep(3)

            # buttonSave = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[3]/div/button[2]") #Saves changes
            # buttonSave.click() #Confirms changes
            # time.sleep(3)

            # -----------------------------------------------------------------------------------------------------------------
            # HTML PAGES PROCESSING

            progressBar = tqdm(total=self.quitReOpenSteps[progressBarCnt])

            if pageCnt != 0 and pageCnt in self.quitReOpenSteps:
                progressBar.update(self.quitReOpenSteps[progressBarCnt - 1])
            else:
                progressBar.update(pageCnt)

            try:
                while True:

                    moreReviewsButtonsList = driver.find_elements(By.NAME, "review-stack-show")  # Finding other reviews of the same user

                    for j in range(len(moreReviewsButtonsList)):
                        moreReviewsButtonsList[j].send_keys("\n")
                        time.sleep(0.3)

                    htmlList.append(driver.page_source)  # Adding the page to the htmlList
                    #print(f"Page {pageCnt} HTML appended")

                    #The NextPageButton gets clicked one extra time, this is because when the last iteration of this while loop (while True) arrives, after collecting the last page the NextPageButton gets clicked again, but no data is collected because the cycle stops just after changing page
                    buttonNextPage = driver.find_element(By.NAME, "pagination-button-next")  # Next page button
                    buttonNextPage.send_keys("\n")  # Simulates "enter" key typing on the keyboard to switch to the next page

                    pageCnt += 1  #pageCnt updates only if the current page has been appended to the htmlLIst, so in case an exception is raised that won't compromise the total count of the correctly scraped pages
                    progressBar.update(1)  #Updating the progress bar

                    time.sleep(3)

                    #This is where the cycle ends after changing page after the last one to collect data from for the specific iteration of the main while loop
                    if pageCnt in self.quitReOpenSteps:
                        break  # Including the last page of the iteration

                progressBarCnt += 1

            except:
                #In case of exceptions raised the driver will stop running and so that's considered as a non-expected (but existing) interval step. Because of this we insert the pageCnt next to the closest last interval
                closestElement = self.closest(self.quitReOpenSteps, pageCnt) #We first find the closest element
                closestElementIndex = self.quitReOpenSteps.index(closestElement) #Then we find its index
                self.quitReOpenSteps.insert(closestElementIndex+1, pageCnt) #Then appending it into the right index of the self.quitReOpenSteps list
                #This way the files that will be saved when exceptions are raised will be read too since all the intervals (including when the driver stops because of an exception) will be saved into intervals.txt correctly

            # -----------------------------------------------------------------------------------------------------------------

            driver.quit()  # Quitting the driver
            progressBar.close()


            htmlCode = "\n".join(htmlList) # Joins all the gathered html pages

            f = open(f"./{self.companyName}/{self.companyName}TrustpilotReviews-{pageCnt}.html", "w", encoding="utf-8")  #Including which section of all the reviews this specific file contains
            f.write(htmlCode)
            f.close()

            print(f"{self.companyName}TrustpilotReviews-{pageCnt}.html Written Correctly")

            time.sleep(100)  #You can set this interval time between one take and another as you prefer


        print(f"\nTotal Collected Pages: {pageCnt}")


        with open(f"./{self.companyName}/intervals.txt", "w") as f:
            for interval in self.quitReOpenSteps:
                f.write(str(interval) + "\n")

        return None





    # Company Data Extraction ------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def getCompanyDetails(html):  # Get Auxiliary Company Soup
        soup = BeautifulSoup(html, "html.parser")  # General Soup (Whole Web Page)
        companySoup = soup.find("div", {"id": "business-unit-title"})
        return companySoup

    @staticmethod
    def getCompanyID():
        companyIdentifier = str(uuid.uuid4())
        return companyIdentifier

    @staticmethod
    def getCompanyName(soup):
        cName = soup.find("span", {"class": "typography_display-s__qOjh6 typography_appearance-default__AAY17 title_displayName__TtDDM"})
        return cName.text.strip().replace("\xa0", "")

    @staticmethod
    def getCompanyTotalReviews(soup):
        TR = soup.find("span", {"class": "typography_body-l__KUYFJ typography_appearance-subtle__8_H2l styles_text__W4hWi"})  # Total Reviews
        TR = TR.text

        totalReviewsNumber = re.search(r'\d+(,\d+)*', TR).group()  # Getting the total number of reviews using a regex since parsing it differently would be difficult

        return totalReviewsNumber

    @staticmethod
    def getCompanyStatus(soup):
        cStatus = soup.find("span", {"class": "typography_body-l__KUYFJ typography_appearance-subtle__8_H2l styles_text__W4hWi"})
        return cStatus.text[10:]

    @staticmethod
    def getCompanyReviewsScore(soup):
        reviewsScore = soup.find("p", {"class": "typography_body-l__KUYFJ typography_appearance-subtle__8_H2l"})
        return reviewsScore.text

    @staticmethod
    def getCompanyDescription(mainPageSoup):
        description = mainPageSoup.find("div", {"class": "styles_container__9nZxD customer-generated-content"}) #This mainPageSoup soup is different from the other ones of this block of functions since it take the whole page source as a soup, while the other only take the single review section as a soup
        return description.text

    # Company Data Extraction ------------------------------------------------------------------------------------------------------------------------------


    # Reviews Data Extraction ------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def getReviewID():  # Fare sì che i singoli ID siano differenti per ogni recensioni, ma che possano essere riproducibili
        RID = str(uuid.uuid4())
        return RID

    @staticmethod
    def getAuthor(soup):

        #The author of a review can be also the same of multiple ones, in that case Trustpilot doesn't show his username, in this case we return None and then replace them with the previous author name during the dataframe creation
        authorName = soup.find("span", {"class": "typography_heading-xxs__QKBS8 typography_appearance-default__AAY17"})
        if authorName is not None:
            return authorName.text
        else:
            return None

    @staticmethod
    def getTitle(soup):
        reviewTitle = soup.find("h2", {"class": "typography_heading-s__f7029 typography_appearance-default__AAY17"})
        if reviewTitle is not None:
            return reviewTitle.text
        else:
            return ""

    @staticmethod
    def getDate(soup):
        reviewDateSoup = soup.find("time")
        reviewDate = reviewDateSoup["datetime"][:10]
        return reviewDate

    @staticmethod
    def getTime(soup):
        reviewTimeSoup = soup.find("time")
        reviewTime = reviewTimeSoup["datetime"][11:16]
        return reviewTime

    def getDateOfExperience(self, soup):
        rawExperienceDT = soup.find("p", "typography_body-m__xgxZ_")
        intermediateEDT = rawExperienceDT.text.strip()[20:]

        experienceDT = self.dateConversion(intermediateEDT)

        return experienceDT

    @staticmethod
    def getRating(soup):
        ratingSoup = soup.find("section", {"class": "styles_reviewContentwrapper__zH_9M"}).findChild()
        rating = int(ratingSoup["data-service-review-rating"])
        return rating

    @staticmethod
    def getUserLocation(soup):

        #When the same author posts multiple reviews only the last one is shown and the other ones are hidden and the user's data isn't repeated, for this reason in these cases None values are gonna be filled with the previous value in the table containing the reviews' data

        userLocation = soup.find("div", {"class": "typography_body-m__xgxZ_ typography_appearance-subtle__8_H2l styles_detailsIcon__Fo_ua"})
        # print(userLocation)

        if userLocation is not None:
            return userLocation.text
        else:
            return None

    @staticmethod
    def getText(soup):
        reviewText = soup.find("p", {"class": "typography_body-l__KUYFJ typography_appearance-default__AAY17 typography_color-black__5LYEn"})
        if reviewText is not None:
            return reviewText.text
        else:
            return ""

    # Reviews Data Extraction ------------------------------------------------------------------------------------------------------------------------------


    def getCompanyData(self, html):
        soup = BeautifulSoup(html, "html.parser")  # General Soup (Whole Web Page)
        companySoup = soup.find("div", {"id": "business-unit-title"})

        dctCompanyInformation = {
            "companyID": self.getCompanyID(),
            "companyName": self.getCompanyName(companySoup),
            "totalReviews": self.getCompanyTotalReviews(companySoup),
            "companyStatus": self.getCompanyStatus(companySoup),
            "reviewsScore": self.getCompanyReviewsScore(companySoup),
            "companyDescription": self.getCompanyDescription(soup)
        }

        # print(dctCompanyInformation)

        return dctCompanyInformation


    def getReviewsData(self, html):

        timeStart = datetime.now()

        soup = BeautifulSoup(html, "html.parser")
        reviews = soup.find_all("div", {"class": "styles_reviewCardInner__EwDq2"}) #This is the operation that requires the most time and processing power

        print("\nReviews Parsing Start at: ", timeStart)

        reviewsDictList = [] #Using a dict and updating it adding every review

        #revIndexRange is a range containing every single review index
        for i in tqdm(reviews):
            dctInput = {
                "reviewID": self.getReviewID(),
                "author": self.getAuthor(i),
                "title": self.getTitle(i),
                "reviewDate": self.getDate(i),
                "reviewTime": self.getTime(i),
                "dateOfExperience": self.getDateOfExperience(i),
                "serviceRating": self.getRating(i),
                "userLocation": self.getUserLocation(i),
                "text": self.getText(i)
            }

            reviewsDictList.append(dctInput)


        timeEnd = datetime.now()
        print("Reviews Parsing End at: ", timeEnd)

        timeDiff = timeEnd - timeStart
        timeDiff = round(timeDiff.total_seconds(), ndigits=2)

        print("Parsing Duration (Seconds): ", timeDiff)
        print("Size of This Data Chunk (Kb): ", sys.getsizeof(reviewsDictList))
        print("Number of Reviews Found: ", len(reviewsDictList), "\n")

        return reviewsDictList


    # Auxiliary Functions ------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def dateConversion(rawDate):
        inputForm = "%B %d, %Y"  # Input form
        outputForm = "%d-%m-%Y"  # Output form

        dateInputDef = datetime.strptime(rawDate, inputForm)
        convertedDate = dateInputDef.strftime(outputForm)  # Conversion

        return convertedDate


    @staticmethod
    def readHTML(fileName: str):
        f = open(fileName, encoding="utf-8", mode="r")
        htmlContent = f.read()
        #print("Read HTML Data Type: ", type(htmlContent))
        f.close()
        return htmlContent


    # Auxiliary Functions ------------------------------------------------------------------------------------------------------------------------------


    def readHTMLAndDBInsert(self, CPULevel=0.50):

        optimalProcessesNumber = math.ceil(CPUsNumber * CPULevel) # 0.50 Number of groups defined to use 50% of the processors and to always be at least 1 (in case of old computers)

        print("Optimal Concurrent Processes Number: ", optimalProcessesNumber)

        f = open(f"./{self.companyName}/intervals.txt", "r")
        intervals = f.readlines()
        intervals = map(lambda x: x.strip(), intervals) #Removing \n from every element of the list
        f.close()

        intervals = list(intervals)
        print("Intervals: ", intervals)


        #Preparing HTML files' name
        pagesNames = [] #HTML Pages names
        for i in intervals:
            #Checking if file exists
            if Path(f"./{self.companyName}/{self.companyName}TrustpilotReviews-{i}.html").is_file():
                pagesNames.append(f"./{self.companyName}/{self.companyName}TrustpilotReviews-{i}.html")
            else:
                print(f"File {self.companyName}TrustpilotReviews-{i}.html Not Found")

        print("Number of Pages", len(pagesNames))


        #Checking if there are HTML files to collect and parse
        if len(pagesNames) == 0:
            raise Exception("No HTML Files Found")
        else:
            pass


        if len(pagesNames) > optimalProcessesNumber:
            n = optimalProcessesNumber #Number of files that will be parsed at the same time (so n is the number of concurrent processes)
            groups = [pagesNames[i:i+n] for i in range(0, len(pagesNames), n)]
            print("Groups: ", groups, "\n")
        else:
            groups = pagesNames
            print("Groups: ", groups, "\n")


        key = "reviewIndex"  # Dictionary key
        indexCnt = 0

        try:

            if all(isinstance(element, list) for element in groups):

                ithGroup = 0
                for g in groups:
                    with concurrent.futures.ProcessPoolExecutor() as executor:
                        print(f"Process Pool on {ithGroup} Group: ", g)
                        htmls = list(executor.map(self.readHTML, g))  # Getting HTML content
                        reviews = list(executor.map(self.getReviewsData, htmls))  # Parsing HTML --> At every cycle this object will be overwritten by new data

                    totalReviews = 0
                    for reviewsList in reviews:
                        totalReviews += len(reviewsList)

                    print(f"Total Reviews for Group {ithGroup}: ", totalReviews)

                    for revsList in reviews:
                        for rev in revsList:
                            rev.update({key: indexCnt})  # Adding key-value pair with reviewIndex: *counter value*
                            indexCnt += 1

                    for revsBlock in reviews:
                        self.RDB.companyDBInsert(revsBlock, "Reviews")

                    # print(reviews)


                    ithGroup += 1

            else:

                #The groups object is just a simple list (NOT a list of lists)
                with concurrent.futures.ProcessPoolExecutor() as executor:
                    htmls = list(executor.map(self.readHTML, groups)) #Getting HTML content
                    reviews = list(executor.map(self.getReviewsData, htmls))  # Parsing HTML and getting back lists of dictionaries that get yet wrapped again in another list
                    #reviews is a list of lists of dictionaries

                totalReviews = 0
                for reviewsList in reviews:
                    totalReviews += len(reviewsList)

                print("Total Reviews: ", totalReviews)

                for revsList in reviews:
                    for rev in revsList:
                        rev.update({key: indexCnt}) #Adding key-value pair with reviewIndex: *counter value*
                        indexCnt += 1

                #print(reviews)

                #Inserting every list of dictionaries (where every dictionary is a review) into the db
                for revsBlock in reviews:
                    self.RDB.companyDBInsert(revsBlock, "Reviews")


            companyData = self.getCompanyData(htmls[0])
            self.RDB.companyDBInsert(companyData, "Company")

            gc.collect()

            return None

        except MemoryError:
            print("Memory size exceeded, try again with shorter intervals")
            return None















































