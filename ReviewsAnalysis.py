import os
import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
from cleantext import clean
import time
from tqdm import tqdm
from functools import wraps
import plotly
import plotly.express as px
import seaborn as sns
from warnings import simplefilter
from transformers import AutoTokenizer, AutoModelForSequenceClassification #Tokenizer and roBERTa
from scipy.special import softmax
from scipy import stats
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
#nltk.downloader.download('vader_lexicon')

simplefilter("ignore")

pd.set_option("display.max_columns", None)
viridisColorScale = sns.color_palette("viridis")
magmaColorScale = sns.color_palette("magma")
crestColorScale = sns.color_palette("crest")
flareColorScale = sns.color_palette("flare")

#Defining a decorator to save plots
def savePlots(plotFunction):

    def checkPlots(plotNames, plots):
        if isinstance(plotNames, list) and isinstance(plots, list):
            return True
        else:
            #print("\033[91mCheckPlots: object obtained are not lists\033[0m")
            return False

    def checkPlotsTypeAndSave(plotName, plots, filePath):
        if isinstance(plots, (plt.Figure, plt.Axes, sns.axisgrid.FacetGrid, sns.axisgrid.PairGrid, list)):
            plt.savefig(f"{filePath}{plotName}.png", dpi=300)
            print(f"{plotName} Exported Correctly")

        elif isinstance(plots, plotly.graph_objs._figure.Figure):
            plots.write_html(f"{filePath}{plotName}.html")
            print(f"{plotName} Exported Correctly")

        else:
            try:
                plt.savefig(f"{filePath}{plotName}.png", dpi=300)
                print(f"{plotName} Exported Correctly")
            except:
                print("\033[91mExporting the plots wasn't possible, the returned type is not included in the decorator function\033[0m")

        return None

    @wraps(plotFunction)
    def wrapper(*args, **kwargs):

        plotsNames, generatedPlots, filePath = plotFunction(*args, **kwargs)
        #print("File path: " + filePath)

        if checkPlots(plotsNames, generatedPlots) is True:

            for plotName, plot in zip(plotsNames, generatedPlots):
                checkPlotsTypeAndSave(plotName, plot, filePath)

        elif checkPlots(plotsNames, generatedPlots) is False:
            #print("Saving Single Graph...")
            checkPlotsTypeAndSave(plotsNames, generatedPlots, filePath)

        else:
            print(f"\033[91mExporting the plots wasn't possible, here's the data types obtained by the decorator: PlotNames: {type(plotsNames)}, Generated Plots (could be a list of plots): {type(generatedPlots)}, File Path: {type(filePath)}\033[0m")

        return None

    return wrapper




class ReviewsAnalyzer:

    def __init__(self, companyName):
        self.companyName = companyName
        self.plotsPath = f"./{self.companyName}/{self.companyName}-EDA/"


    def createAnalysisDirs(self):
        os.makedirs(f"./{self.companyName}/{self.companyName}-EDA", exist_ok=True)
        return None


    def analyzeRevs(self):
        db = sqlite3.connect(f"./{self.companyName}/{self.companyName}DB.db")

        reviews = pd.read_sql("SELECT reviewIndex, reviewID, author, title, reviewDate, reviewTime, dateOfExperience, serviceRating, userLocation, countryName, country3LCode, region, text FROM reviews", db) #Reviews Dataframe


        self.reviewsEDA(reviews)
        self.analyzeSentiment(reviews)

        db.commit()
        db.close()

        return None


    def reviewsEDA(self, df: pd.DataFrame):

        colorScale = [
                '#FFB6C1',  # LightPink
                '#FFD700',  # Gold
                '#87CEEB',  # SkyBlue
                '#98FB98',  # PaleGreen
                '#FFA07A',  # LightSalmon
                '#9370DB',  # MediumPurple
                '#20B2AA',  # LightSeaGreen
                '#FF69B4',  # HotPink
                '#C71585',  # MediumVioletRed
                '#FFDAB9',  # PeachPuff
                '#FF6347',  # Tomato
                '#00CED1'   # DarkTurquoise
            ]

        totalRows, _ = df.shape
        mode, _ = stats.mode(df["serviceRating"])

        ratios = {
            "oneStarToTotal": len(df.query("serviceRating == 1")) / totalRows,
            "twoStarToTotal": len(df.query("serviceRating == 2")) / totalRows,
            "threeStarToTotal": len(df.query("serviceRating == 3")) / totalRows,
            "fourStarToTotal": len(df.query("serviceRating == 4")) / totalRows,
            "fiveStarToTotal": len(df.query("serviceRating == 5")) / totalRows,
        }


        print("\nReviews DataFrame Shape: ", df.shape)

        #print("DataFrame Head Overview")
        #print(df.head(10))

        print("Columns Data Types: ", df.dtypes, "\n")

        print("\nCountries Where Reviews Come From: ")
        print(df["userLocation"].unique())

        print("\nMedian Rating: ", df["serviceRating"].median())
        print("\nMode Rating: ", mode) #Showing the rating with the highest frequency

        print("\nTop 10 Most Frequent Words: ")
        print(self.reResearch(df).head(10), "\n") #Using regular expressions to find the most frequent word

        print("\nRating Ratios: ")
        print(ratios, "\n")


        @savePlots
        def ratingsRatiosPlot():

            ratiosKeys = list(ratios.keys())
            ratiosValues = list(ratios.values())

            plt.figure(figsize=(25, 10))
            plt.subplot(1, 2, 1)

            plt.bar(x=ratiosKeys, height=ratiosValues)
            plt.grid(axis="y")

            plt.xticks(ratiosKeys, rotation=0)
            plt.xlabel('Rating', fontweight='bold', fontsize=10)
            plt.ylabel('Ratio', fontweight='bold', fontsize=10)
            plt.title('Ratings Ratio', fontweight='bold', fontsize=20)

            plt.subplot(1, 2, 2)

            donutLabels = [f"{i} ({round(j, ndigits=2)})" for i, j in ratios.items()]
            # print(donutLabels)

            plt.pie(ratiosValues, labels=donutLabels, autopct="%.2f%%", textprops=dict(fontsize=13), colors=colorScale)

            plt.axis("equal")

            circle = plt.Circle(xy=(0, 0), radius=0.75, facecolor='white')
            plt.gca().add_artist(circle)

            plt.title("Total ", x=0.5, y=1.05, fontweight='bold', fontsize=20)

            plt.annotate(text=f'Total Ratings: {totalRows}', xy=(0, 0), ha='center', weight='bold', size=20)

            return "RatingsRatioSubPlots", plt, self.plotsPath

        @savePlots
        def ratingsFrequency():
            ax = df["serviceRating"].value_counts().sort_index().plot(kind="bar", title="Ratings Frequency", figsize=(16, 9))
            ax.set_xlabel("Rating")
            return "RatingsFrequency", plt, self.plotsPath

        @savePlots
        def fiveStarRatingsWorldwide():

            ratingsDataByCountry = df.groupby(["country3LCode", "countryName"]).count()["serviceRating"].reset_index().sort_values(by="serviceRating", ascending=False)
            print(ratingsDataByCountry)

            fiveStarRevsPlot = px.choropleth(ratingsDataByCountry, locations='country3LCode', color='serviceRating', hover_name='countryName', title='Number of 5 Star Reviews By Country', color_discrete_map=viridisColorScale)

            return "fiveStarRatingsWorldwide", fiveStarRevsPlot, self.plotsPath

        @savePlots
        def ratingByCountry():
            data = df[["countryName", "serviceRating"]].groupby("countryName").count().sort_values(by="serviceRating", ascending=False)
            data = data.head(10) #Only the TOP 10 will be displayed
            plt.figure(figsize=(15, 10))
            data.plot(kind="bar", title="Ratings Count By Country", figsize=(16, 9), rot=45)
            return "Top10RatingsCountByCountry", plt, self.plotsPath


        plotsList = [ratingsFrequency, fiveStarRatingsWorldwide, ratingsRatiosPlot, ratingByCountry]
        all((i(), plt.clf()) for i in plotsList)

        print("Plots Exported Correctly")

        return None


    def analyzeSentiment(self, df: pd.DataFrame):

        # Quick Cleaning
        reviews = df.loc[(df['text'] != "") & (df['title'] != "")]
        reviews = reviews.dropna()
        reviews['text'] = reviews['text'].apply(lambda x: ascii(x))  #Converting every character into his ASCII closest one, using ascii(reviews["text"]) raised a bug, so apply() was the only way

        reviewsRows, _ = reviews.shape

        print("\nReviews DataFrame Shape After Cleaning: ", reviews.shape, "\n")



        def VADERAnalyze() -> pd.DataFrame:

            sia = SentimentIntensityAnalyzer()

            time.sleep(0.2)

            scores = {}
            for i, row in tqdm(reviews.iterrows(), total=len(reviews)):
                text = row["text"]
                revIndex = row["reviewIndex"]

                scores[revIndex] = sia.polarity_scores(text)

            vaderScores = pd.DataFrame(scores).T
            vaderScores = vaderScores.reset_index().rename(columns={"index": "reviewIndex", "neg": "vaderNeg", "neu": "vaderNeu", "pos": "vaderPos", "compound": "vaderCompound"})

            vaderScores = vaderScores.merge(reviews[["reviewIndex", "serviceRating"]])
            #print("\nVADER Scores DataFrame Summary: ", vaderScores.describe(), "\n")


            def plotVADER():

                averageSentimentByRating = vaderScores.drop(columns="reviewIndex")
                averageSentimentByRating = averageSentimentByRating.groupby("serviceRating").mean()

                print("Average Sentiment Scores By Rating", averageSentimentByRating, "\n")

                print(vaderScores.drop(columns="vaderCompound"))

                @savePlots
                def VADERCompoundScoreByRating():
                    ax = sns.barplot(vaderScores, x="serviceRating", y="vaderCompound", hue="serviceRating", palette=crestColorScale)
                    ax.set_title("VADER Compound Score by Rating")
                    ax.set_ylabel("VADER Compound")
                    return "VADERCompoundScoreByRating", ax, self.plotsPath

                @savePlots
                def VADERPositiveScoreByRating():
                    ax = sns.barplot(vaderScores, x="serviceRating", y="vaderPos", hue="serviceRating", palette=viridisColorScale)
                    ax.set_title("VADER Positive Score by Rating")
                    ax.set_ylabel("VADER Positive")
                    return "VADERPositiveScoreByRating", ax, self.plotsPath

                @savePlots
                def VADERNeutralScoreByRating():
                    ax = sns.barplot(vaderScores, x="serviceRating", y="vaderNeu", hue="serviceRating", palette=flareColorScale)
                    ax.set_title("VADER Neutral Score by Rating")
                    ax.set_ylabel("VADER Neutral")
                    return "VADERNeutralScoreByRating", ax, self.plotsPath

                @savePlots
                def VADERNegativeScoreByRating():
                    ax = sns.barplot(vaderScores, x="serviceRating", y="vaderNeg", hue="serviceRating", palette=magmaColorScale)
                    ax.set_title("VADER Negative Score by Rating")
                    ax.set_ylabel("VADER Negative")
                    return "VADERNegativeScoreByRating", ax, self.plotsPath


                VADERPlots = [VADERCompoundScoreByRating, VADERPositiveScoreByRating, VADERNeutralScoreByRating, VADERNegativeScoreByRating]
                all((p(), plt.clf()) for p in VADERPlots)

                return None


            plotVADER()

            vaderScores = vaderScores.drop(columns="serviceRating")

            return vaderScores


        #roBERTa should be finetuned to recognize emojis too as per sad on their hugging face page
        def roBERTaAnalyze() -> pd.DataFrame:
            pretrainedModel = f"cardiffnlp/twitter-roberta-base-sentiment"
            tokenizer = AutoTokenizer.from_pretrained(pretrainedModel)
            model = AutoModelForSequenceClassification.from_pretrained(pretrainedModel)

            def roBERTaPolarityScores(textInput):

                encodedText = tokenizer(textInput, return_tensors='pt') #"pt" stands for PyTorch which is the type of tensors returned
                modelOutput = model(**encodedText)
                outputScores = modelOutput[0][0].detach().numpy()

                sfScores = softmax(outputScores) #Softmaxed scores

                #print("\n", sfScores)

                scoresDict = {
                    'roBERTaNeg': sfScores[0],
                    'roBERTaNeu': sfScores[1],
                    'roBERTaPos': sfScores[2]
                }

                return scoresDict

            scores = {}
            for i, row in tqdm(reviews.iterrows(), total=len(reviews)):
                try:
                    text = row["text"]
                    revIndex = row["reviewIndex"]

                    scores[revIndex] = roBERTaPolarityScores(text)

                except RuntimeError:
                    print("\nRuntimeError On Row: ", i, " Probably Text Too Long")
                except IndexError:
                    print("\nIndexError On Row: ", i)

            roBERTaScores = pd.DataFrame(scores).T
            roBERTaScores = roBERTaScores.reset_index().rename(columns={"index": "reviewIndex"})

            print("roBERTa Shape Before Join: ", roBERTaScores.shape)

            roBERTaScores = roBERTaScores.merge(reviews[["reviewIndex", "serviceRating"]], how="inner", on="reviewIndex")

            print("\nroBERTa Scores DataFrame Summary: \n", roBERTaScores.describe(), "\n")

            print("roBERTa Shape After Join: ", roBERTaScores.shape)


            def plotRoBERTa():

                @savePlots
                def roBERTaNegScoreByRating():
                    ax = sns.barplot(roBERTaScores, x="serviceRating", y="roBERTaNeg", hue="serviceRating", palette=crestColorScale)
                    ax.set_title("roBERTa Negative Score by Rating")
                    ax.set_ylabel("roBERTa Negative")
                    return "roBERTaNegativeScoreByRating", ax, self.plotsPath

                @savePlots
                def roBERTaNeuScoreByRating():
                    ax = sns.barplot(roBERTaScores, x="serviceRating", y="roBERTaNeu", hue="serviceRating", palette=crestColorScale)
                    ax.set_title("roBERTa Neutral Score by Rating")
                    ax.set_ylabel("roBERTa Neutral")
                    return "roBERTaCNeutralScoreByRating", ax, self.plotsPath

                @savePlots
                def roBERTaPosScoreByRating():
                    ax = sns.barplot(roBERTaScores, x="serviceRating", y="roBERTaPos", hue="serviceRating", palette=crestColorScale)
                    ax.set_title("roBERTa Positive Score by Rating")
                    ax.set_ylabel("roBERTa Positive")
                    return "roBERTaPositiveScoreByRating", ax, self.plotsPath


                roBERTaPlots = [roBERTaNegScoreByRating, roBERTaNeuScoreByRating, roBERTaPosScoreByRating]
                all((p(), plt.clf()) for p in roBERTaPlots)

            plotRoBERTa()


            return roBERTaScores



        #Executing Sentiment Analyzers
        sentimentAnalyzers = [VADERAnalyze, roBERTaAnalyze]
        sentiments = [i() for i in tqdm(sentimentAnalyzers)]

        #print(sentiments)

        sentimentDF = pd.concat(sentiments, axis=1, join="inner") #Merging sentiment dataframes on the rows axis (0) and joining them on common columns
        sentimentDF = sentimentDF.loc[:, ~sentimentDF.columns.duplicated()] #Remove duplicated columns

        print("\n------------ Sentiment DataFrames Info ------------")
        print(sentimentDF, "\n")
        print("Shape: ", sentimentDF.shape, "\n")
        print("Columns: ", sentimentDF.columns, "\n")
        print("DataFrame Summary: \n", sentimentDF.describe(), "\n")

        self.saveSentimentIntoDB(sentimentDF) #Saves data into a specific table of the database

        completeData = pd.concat([reviews, sentimentDF], axis=1, join="inner")
        completeData = completeData.loc[:, ~completeData.columns.duplicated()]

        #print("Sentiment DataFrame NaN Sum: ", completeData.isna().sum())

        self.exportCompleteData(completeData) #Export data in various formats

        print("Data Exported Correctly")


        return None




    def saveSentimentIntoDB(self, df: pd.DataFrame):

        db = sqlite3.connect(f"./{self.companyName}/{self.companyName}DB.db")

        createSentimentTable = """CREATE TABLE IF NOT EXISTS sentiment(
                                        reviewIndex TEXT PRIMARY KEY,
                                        vaderNeg FLOAT NOT NULL,
                                        vaderNeu FLOAT NOT NULL,
                                        vaderPos FLOAT NOT NULL,
                                        vaderCompound FLOAT NOT NULL,
                                        roBERTaNeg FLOAT NOT NULL,
                                        roBERTaNeu FLOAT NOT NULL,
                                        roBERTaPos FLOAT NOT NULL,
                                        FOREIGN KEY (reviewIndex) REFERENCES reviews(reviewIndex))
                               """

        db.execute(createSentimentTable)

        df.to_sql("sentiment", db, index=False, if_exists="replace")

        db.commit()
        db.close()

        print("\nSentiment Data Insert Into DB Successful")

        return None


    #Exporting data including sentiment
    def exportCompleteData(self, df: pd.DataFrame):
        #Saving data in various formats
        df.to_json(f"./{self.companyName}/{self.companyName}-Data/{self.companyName}JSON.json", index=False, indent=4)
        df.to_csv(f"./{self.companyName}/{self.companyName}-Data/{self.companyName}CSV.csv", index=False)
        df.to_parquet(f"./{self.companyName}/{self.companyName}-Data/{self.companyName}Parquet.parquet", index=False)

        return None


    @staticmethod
    def reResearch(df: pd.DataFrame) -> pd.DataFrame:

        allRev = df["text"] #All Reviews DF

        #print(allRev)

        fullText = " ".join(allRev)
        cleanFullText = clean(fullText, no_emoji=True)

        #print(cleanFullText)

        pattern = r"\w+"

        f = open("stopwords.txt", encoding='utf8')
        stopwords = f.readlines()
        stopwords = [w.strip() for w in stopwords]
        f.close()

        words = re.findall(pattern, cleanFullText)

        cleanedWords = [w for w in words if w not in stopwords]

        #print(cleanedWords)

        wordsDict = {}

        for i in cleanedWords:
            wordsDict[i] = cleanedWords.count(i)

        wordsDF = pd.DataFrame.from_dict(wordsDict, orient='index', columns=['wordsCount'])
        wordsDF = wordsDF.sort_values(['wordsCount'], ascending=False)

        #print(wordsDF)

        return wordsDF


    def generateWordcloud(self, df: pd.DataFrame): #Words DataFrame

        wcloud = WordCloud(background_color="white", max_words=50, width=1600, height=900)
        wcloud.generate_from_frequencies(df.to_dict()["wordsCount"])

        plt.figure(figsize=(16, 9))
        plt.imshow(wcloud)
        plt.axis("off")
        plt.savefig(f"./{self.companyName}/{self.companyName}WordCloud.png", dpi=300)

        print("WordCloud Saved Correctly")

        return plt










































