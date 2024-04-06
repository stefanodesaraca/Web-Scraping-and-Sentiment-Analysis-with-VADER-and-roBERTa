from TReviewsUsefulInfo import TrustpilotLink, TrustpilotCompanyName, CPUsNumber
from ReviewsScraping import RevScraping as RS
from ReviewsDatabase import reviewsDatabaseManagement as RDBM
import ReviewsAnalysis as RA
import pandas as pd

pd.set_option("display.max_columns", None)

tLink = TrustpilotLink
companyName = TrustpilotCompanyName
nCPUs = CPUsNumber

def scrapePage():

    pageScraper = RS(tLink, companyName)
    pageScraper.createCompanyDirectory()

    pageScraper.getHTMLs()

    return None


def parseAndStoreData():

    pageScraper = RS(tLink, companyName)
    dbManagement = RDBM()
    dbManagement.createCompanyDB(companyName)

    pageScraper.readHTMLAndDBInsert(CPULevel=0.70) #CPULevel goes from 0.00 to 1.00

    return None


def getReviewsAnalysis():

    analyzer = RA.ReviewsAnalyzer(companyName)
    analyzer.createAnalysisDirs()

    analyzer.analyzeRevs()


    return None


def saveData():

    saver = RDBM()
    saver.exportData()

    return None




if __name__ == "__main__":

    while True:

        print("""\n--------------- Menu ---------------
1. Get HTML
2. Insert Data Into DB
3. Generate Reviews EDA and Sentiment Analysis
4. Export Data Into CSV and Parquet
0. Exit""")

        option = int(input("Choose option: "))

        if option == 1:
            scrapePage()

        elif option == 2:
            parseAndStoreData()

        elif option == 3:
            getReviewsAnalysis()

        elif option == 4:
            saveData()

        elif option == 0:
            break


    exit()



























































