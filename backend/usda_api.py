import requests
import pandas as pd

# Define state FIPS codes and years
"""
states = {
    "01": "2022", "02": "2019", "04": "2019", "05": "2022",
    "06": "2021", "08": "2019", "09": "2021", "10": "2021",
    "12": "2020", "13": "2022", "15": "2019", "16": "2019",
    "17": "2021", "18": "2021", "19": "2021", "20": "2021",
    "21": "2019", "22": "2020", "23": "2021", "24": "2021",
    "25": "2021", "26": "2021", "27": "2021", "28": "2022",
    "29": "2021", "30": "2019", "31": "2021", "32": "2019",
    "33": "2021", "34": "2021", "35": "2019", "36": "2021",
    "37": "2022", "38": "2021", "39": "2021", "40": "2021",
    "41": "2020", "42": "2021", "44": "2021", "45": "2021",
    "46": "2021", "47": "2020", "48": "2020", "49": "2019",
    "50": "2021", "51": "2021", "53": "2020", "54": "2021",
    "55": "2021", "56": "2019"
}
"""
states = {
    "40": "2021", "41": "2020", "42": "2021", "44": "2021", "45": "2021",
    "46": "2021", "47": "2020", "48": "2020", "49": "2019",
    "50": "2021", "51": "2021", "53": "2020", "54": "2021",
    "55": "2021", "56": "2019"
}


# Base API URL
base_url = "https://apps.fs.usda.gov/fiadb-api/fullreport"


# Iterate through each state
for fips, year in states.items():
    wc = f"{fips}{year}"
    #url = f"{base_url}?rselected=County%20code%20and%20name&cselected=Present%20nonforest%20code%20remeasurement%20plots&snum=79&wc={wc}"
    url = f"https://apps.fs.usda.gov/fiadb-api/fullreport?rselected=County%20code%20and%20name&cselected=Present%20nonforest%20code%20remeasurement%20plots&snum=79&wc={wc}&outputFormat=NJSON"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.json_normalize(data, 'estimates')  # Adjust this based on actual data structure
        # Check if file exists and append without header or create new with header
        header = not pd.io.common.file_exists('usda_api.csv')
        df.to_csv('usda_api.csv', mode='a', header=header, index=False)
    else:
        print(f"Failed to retrieve data for state FIPS {fips} for year {year}")

print("Data collection complete.")
