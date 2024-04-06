
# Trustpilot Reviews Web Scraping and Sentiment Analysis Using VADER and CardiffNLP's roBERTa

## **📚 Introduction:**

### This project consists in four parts:
### 1. Web Scraping and Data Collection
### 2. Data Extraction from HTML Files and Insertion in an Sqlite3 Database
### 3. Executing a Complete Analysis Structured in:
###     <ol>
###         <ul> - EDA (Exploratory Data Analysis)</ul> 
###         <ul> - Frequency Analysis Using RE (Regular Expressions)</ul>
###         <ul> - Sentiment Analysis Using VADER and CardiffNLP's roBERTa</ul>
###     </ol>
### 
### 4. Data Export in CSV and Parquet

</br>

## **💡 Tips:**

### 1. Insert your data into TReviewsUsefulInfo.py file matching the fields that will communicate with the other files and supply the necessary data to execute many of the functions present in the scripts.

```python
import re
import multiprocessing

def getCompanyNameFromURL(url):  # Get Company Name By Reading the Last Part of the Input URL

    url = url.split("/")[-1]

    regex = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+)\.'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None


tLinksList = {"TRUSTPILOT LINK": [10, 20, 30, 40, 50, ...]} #Trustpilot link and relative intervals to stop

idx = 0
TrustpilotLink = list(tLinksList.keys())[idx]
TrustpilotLinkIntervals = list(tLinksList.values())[idx]
TrustpilotCompanyName = getCompanyNameFromURL(TrustpilotLink)
CPUsNumber = multiprocessing.cpu_count()

seleniumExecutablePath = "YOUR PATH/chromedriver.exe"

```

### 2. Be sure to insert a trustpilot<u>.com</u> link and not local domain ones like .eu, .us, .fr, etc.
### 3. Add all the stopwords you need in the stopwords.txt file
### 4. Set the level of multiprocessing you want by adjusting the CPULevel parameter in the readHTMLAndDBInsert() function. <br> This will determine the number of logic processors your CPU will use to parse data from n HTML files at a time. Be aware that this parameter needs to be between 0 and 1.
### 5. Define a decent amount of intervals for each trustpilot page you want to extract data from.

<br>

## **⚠️ Warnings**:
### 1. The processing power and memory available required to run this code are directly proportional to the quantity of data you'll be scraping, parsing and analyzing afterwards.
### 2. With thousands of pages the process can be a bit slow, so don't worry if BeautifulSoup or Selenium functions don't run very fast because they're dealing with potentially Gb of data.
### 3. IMPORTANT: Trustpilot's pages HTML tags can change overtime, thus if the code happens to not be able to parse the HTML code that's likely the problem.
### 4. Keep an eye on the countryCodesISO3166.csv file containing ISO3166 country codes. Because there are many files like this around I got one from online and added some missing countries. Be sure that none are missing, otherwise the data insertion in the db won't be possible.
### 5. Install all the libraries required to run the code.

<br>

## **📋 Notes:**
### Every helpful suggestion is very much appreciated :))






























