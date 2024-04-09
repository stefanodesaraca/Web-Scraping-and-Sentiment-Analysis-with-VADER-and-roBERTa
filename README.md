
# Trustpilot Reviews Web Scraping and Sentiment Analysis Using VADER and CardiffNLP's roBERTa

## **📚 Introduction:**

### This project consists of four main parts:
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
### 3. Add all the stopwords you need in the stopwords.txt file.
### 4. Set the level of multiprocessing you want by adjusting the CPULevel parameter in the readHTMLAndDBInsert() function. <br> This will determine the number of logic processors your CPU will use to parse data from n HTML files at a time. Be aware that this parameter needs to be between 0 and 1.
### 5. Define a decent amount of intervals for each trustpilot page you want to extract data from.

<br>

## **⚠️ Warnings**:
### 1. The processing power and memory available required to run this code are directly proportional to the quantity of data you'll be scraping, parsing and analyzing afterwards.
### 2. With thousands of pages the process can be a bit slow, so don't worry if BeautifulSoup or Selenium functions don't run very fast because they're dealing with potentially Gb of data.
### 3. IMPORTANT: Trustpilot's pages HTML tags can change overtime, thus if the code happens to not be able to parse the HTML code that's likely the problem.
### 4. Keep an eye on the countryCodesISO3166.csv file containing ISO3166 country codes. Because there are many files like this around I got one from online and added some missing countries. Be sure that none are missing, otherwise the data insertion in the db won't be possible.
### 5. Install all the libraries required to run the code.
### 6. Do not delete intervals.txt files, otherwise you might not be able to parse all of the HTML files.
### 7. Do not execute the db insertion more than one time without clearing the database first, otherwise you'll be trying to insert duplicated rows.
### 8. The roBERTa model can sometimes raise errors because of the text beign too long, so do not edit the try-except construct there.

<br>

## **📋 Notes:**
### Every helpful suggestion is very much appreciated :))

<br>

## **⚙️ How to Use**
### This code has been thought to extract and analyze any Trustpilot page and export useful data and a complete Sentiment Analysis using two different approaches: Bag of Words (VADER) and Transformers (roBERTa).
<br>

## 0. To Know
### A Trustpilot user (that can represent a company, a shop, etc.) has a specific part of its page dedicated to show informations about itself.
### A Trustpilot user may have one or more pages that contain reviews with details of the person who leaves the reivew.
### A person can leave more than one review for the same user and this makes the other ones be hidden by a "Read n More Reviews About COMPANY_NAME".
### All the reviews are shown just after applying the Languages = All filter.
### The number of pages can get really big in some cases, meaning thousands or tens of thousands.



<br>

## 1. Gathering Data From the Trustpilot User's Reviews Pages
### First of all set in the TReviewsUsefulInfo.py the link you want to extract data from and the intervals that describe the number of splits in which the whole mass of reviews will be saved.<br>

### *Example:*
#### *Having 5000 pages of reviews you can set your intervals to [1000, 2000, 3000, 4000, 5000]*
#### *This way you'll have 5 separated HTML files each containing a chunk of the total reviews*
#### *Keep in mind that the program will automatically add to the intervals list the last page number so it knows where to stop scraping*
#### NOTE: Intervals may vary in case of errors or other events that block Selenium from working. These errors get cought by a try-except and the last page scraped before the error raised is set as an interval too. <br>
### The intervals solution has been used just to reduce the size of each single HTML file and apply mulitiprocesses to parse more than one at a time to speed up the process.

<br>

## 2. Inserting Data Into a Custom DB
### Once you gathered all of the HTML files in a custom folder called just like the Trustpilot user's name, you can start parsing them using BeautifulSoup4 and save the data into a DB.
### The parsing process is managed by the concurrent.futures module that creates a processes pool.
### Specifically, the number of processes is equal to the number of HTML files. Each process will parse a specific HTML file.
### If the number of files is bigger than a threshold you'll set, then the program will gather them into groups and then execute one group at a time.
### The threshold is determined by a percentage that you may set which by default is .50, meaning it will take the number of logic processors and do a ceil division with that. The result will be the number of processes in a group.
### Else, if the number of HTML files is lower than that it will just parse them all toghether at once.

```python
CPUsNumber = multiprocessing.cpu_count()
```

```python
    def readHTMLAndDBInsert(self, CPULevel=0.50):

        optimalProcessesNumber = math.ceil(CPUsNumber * CPULevel)

        ...
```

<br>

## 2.1 Data Collected
#### Disclaimer: the names used in the code have been chosen assuming the Trustpilot User is a company.
### Company's Data
### <ol>
###     <ul><li>Company ID (Generated using UUIDs)</ul></li>
###     <ul><li>Company Name</ul></li>
###     <ul><li>Total Reviews</ul></li>
###     <ul><li>Company Status</ul></li>
###     <ul><li>Review Score</ul></li>
###     <ul><li>Company Description</ul></li>
### </ol>
###
### <br>Reviews's Data
### <ol>
###     <ul><li>Review Index</ul></li>
###     <ul><li>Review ID (Generated Using UUIDs)</ul></li>
###     <ul><li>Author</ul></li>
###     <ul><li>Title</ul></li>
###     <ul><li>Review Date</ul></li>
###     <ul><li>Review Time</ul></li>
###     <ul><li>Date of Experience</ul></li>
###     <ul><li>Rating</ul></li>
###     <ul><li>User Location (ISO3166-alpha2 Country Code)</ul></li>
###     <ul><li>Country Name (Full Name)</ul></li>
###     <ul><li>ISO3166-alpha3 Country Code</ul></li>
###     <ul><li>Region</ul></li>
###     <ul><li>Text</ul></li>
### </ol>
###
### <br>
###

## 3. Sentiment Analysis Using VADER and roBERTa
### When the reviews are all inserted into the database you may start the analysis.
### First of all you'll see a short EDA with some plots and useful information about the dataset and the data itself.
### Afterwards a word frequency analysis will start and you'll be shown the top 10 most frequent words common to all reviews.
### Finally the sentiment analysis (only on the reviews where text is not None) begins.
###
### <br>
###
## 3.1 VADER (Bag of Words)
### Using NLTK's SentimentIntensityAnalyzer (VADER) we'll collect the Negative, Neutral, Positive and Compound scores for each review and gather all of them into a dataframe adding the review index for each row, so we can merge the VADER scores dataframe with the roBERTa one.

<br>

## 3.2 roBERTa (HuggingFace Transformers)
### With HuggingFace's transformers module we'll use the CardiffNLP's roBERTa to get Negative, Neutral and Positive scores for each review. We'll then create a dataframe with all the scores and the review indexes too.
###
### <br>


## 3.3 Sentiment Scores Insertion Into Database
### Having merged previously VADER and roBERTa scores dataframe doing an inner join between them we'll insert them into a dedicated table in the database called "sentiment".
### As both a primary key and foreign key we have the review index which will enable us to execute joins to see both the review text from the "reviews" table and the sentiment from the "sentiment" table.
###
###  <br>


## 4. Data Export in JSON, CSV and Parquet
### We'll export the reviews which have both VADER and roBERTa scores in JSON, CSV and Parquet.
###
###
###
###
###
