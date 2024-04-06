from TReviewsUsefulInfo import TrustpilotCompanyName
import sqlite3
import pandas as pd



class reviewsDatabaseManagement:

    def __init__(self):
        self.companyName = TrustpilotCompanyName


    def createCompanyDB(self, companyName):

        db = sqlite3.connect(f"./{companyName}/{companyName}DB.db")

        createTableCompanyInfo = '''CREATE TABLE IF NOT EXISTS companyInfo(
    
            companyID TEXT PRIMARY KEY,
            companyName TEXT NOT NULL,
            totalReviews INT NOT NULL,
            companyStatus TEXT NOT NULL,
            reviewsScore REAL,
            companyDescription TEXT
    
            );
            '''

        db.execute(createTableCompanyInfo)

        createTableReviews = '''CREATE TABLE IF NOT EXISTS reviews(
    
            reviewIndex TEXT PRIMARY KEY,
            reviewID TEXT NOT NULL,
            author TEXT NOT NULL,
            title TEXT NOT NULL,
            reviewDate TEXT NOT NULL,
            reviewTime TEXT NOT NULL,
            dateOfExperience TEXT NOT NULL,
            serviceRating INT NOT NULL,
            userLocation TEXT NOT NULL,
            countryName TEXT NOT NULL,
            country3LCode TEXT NOT NULL,
            region TEXT NOT NULL,
            text TEXT NOT NULL
    
            );
            '''

        db.execute(createTableReviews)

        db.commit()

        db.close()


    def companyDBInsert(self, data, passedInfo: str):

        db = sqlite3.connect(f"./{self.companyName}/{self.companyName}DB.db")

        # Company data insert
        if passedInfo == "Company":
            CDF = pd.DataFrame(data, index=[0])  # Company DataFrame
            print(CDF)

            CDF.to_sql("companyInfo", db, if_exists='replace', index=False)
            print("Company Info Insert Successful\n")

        # Reviews data insert
        elif passedInfo == "Reviews":
            RDF = pd.DataFrame(data)  # Reviews DataFrame
            RDF.reindex(columns=["reviewIndex", "reviewID", "author", "title", "reviewDate", "reviewTime", "dateOfExperience", "serviceRating", "userLocation", "text"])
            RDF["author"] = RDF["author"].ffill()  # CAVEAT Filling None values with the previous author, this is because the non-last reviews from the same author aren't complete of data as the last ones
            RDF["userLocation"] = RDF["userLocation"].ffill() #The same principle shown before applies here

            countryNamesAndCode = pd.read_csv("countryCodesISO3166.csv", index_col=False, keep_default_na=False) #Loading a dictionary containing country names and codes based on ISO3166-1 Alpha 2
            countryNames = dict(zip(countryNamesAndCode["2LCode"], countryNamesAndCode["countryName"]))
            country2LCodes = dict(zip(countryNamesAndCode["2LCode"], countryNamesAndCode["3LCode"]))
            countryRegion = dict(zip(countryNamesAndCode["2LCode"], countryNamesAndCode["region"]))

            RDF["countryName"] = RDF["userLocation"].apply(lambda x: countryNames[x]) #Finding country name
            RDF["country3LCode"] = RDF["userLocation"].apply(lambda x: country2LCodes[x]) #Finding country 3 letters code
            RDF["region"] = RDF["userLocation"].apply(lambda x: countryRegion[x])


            print("Dataframe Shape: ", RDF.shape)
            print("Reviews from the same author in this chunk of data: ", RDF["author"].duplicated().sum())
            # print("Reviews with the same text: ", RDF["text"].duplicated().sum())
            # print(RDF[["title", "text"]][RDF["text"].duplicated()])
            # print(RDF[["author", "title"]][RDF[["author", "title"]].duplicated()].sort_values("author", ascending=True))

            RDF.to_sql("reviews", db, if_exists='append', index=False) #method="multi" indicates that more than one row will be written at a time, specifically 500 rows (chunksize)
            print("Reviews Info Insert Successful\n")

        else:
            raise Exception("Wrong input for 'passedInfo' parameter in companyDBInsert function, insert a valid one")

        # print(CDF.shape)

        db.commit()
        db.close()

        return None


    def exportData(self):
        db = sqlite3.connect(f"./{self.companyName}/{self.companyName}DB.db")
        reviews = pd.read_sql("SELECT * FROM reviews", db)  # Reviews Dataframe
        db.close()

        print("Data Collected")
        print("DataFrame Shape: ", reviews.shape)

        try:
            reviews.to_csv(f"./{self.companyName}/{self.companyName}TrustpilotReviewsCSV.csv", index=False)
            reviews.to_parquet(f"./{self.companyName}/{self.companyName}TrustpilotReviewsParquet.parquet", index=False)

            print("Data Exported Correctly")

        except:
            print("Error Raised")

        return None





























