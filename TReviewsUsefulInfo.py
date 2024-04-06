import re
import multiprocessing

def getCompanyNameFromURL(url):  # Get Company Name By Reading the Last Part of the Input URL

    url = url.split("/")[-1]

    regex = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+)\.'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None


tLinksList = {"TRUSTPILOT LINK": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]}

idx = 0
TrustpilotLink = list(tLinksList.keys())[idx]
TrustpilotLinkIntervals = list(tLinksList.values())[idx]
TrustpilotCompanyName = getCompanyNameFromURL(TrustpilotLink)
CPUsNumber = multiprocessing.cpu_count()

seleniumExecutablePath = "YOUR PATH/chromedriver.exe"


































