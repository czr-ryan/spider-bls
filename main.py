import os
import pymysql
from bs4 import BeautifulSoup
import urllib.request as request
import re
import xlwt


# get city info from wiki
def getCities():
    html = request.urlopen("https://en.wikipedia.org/wiki/List_of_metropolitan_statistical_areas").read()
    soup = BeautifulSoup(html, 'lxml')
    content = soup.find_all(name='table', attrs={"class": "wikitable sortable"})
    table = content[0]
    with open("cities.txt", 'a', encoding='utf8') as citytxt:
        for tr in table.findAll('tr'):
            tds = tr.findAll('td')
            if len(tds) > 0:
                citytxt.write(tds[1].getText())
                print(tds[1].getText())


# Convert the abbreviation of the state name to the full name
def getStateCity():
    pAndC = open('statesAndCity.txt', 'w', encoding='utf8')
    pro = {}
    with open("states.txt", 'r', encoding='utf8') as f:
        for line in f.readlines():
            temp = line.replace("\n", "").lower().split("	")
            pro[temp[0]] = temp[1]

    with open('cities.txt', 'r', encoding='utf8') as f:
        for line in f.readlines():
            tmp = line.replace("\n", "").replace(" MSA", "").lower().split(', ')
            # city2pro[tmp[0]] = pro[tmp[1].split('-')[0].split(' MSA')[0]]
            cityAndState = tmp[0] + ' # '
            for p in tmp[1].split("-"):
                cityAndState = cityAndState+pro[p] + ','
            cityAndState = cityAndState.strip(",")
            pAndC.write(cityAndState+'\n')

# Process each city in turn
def getStatePage():
    prifix = "https://www.bls.gov/sae/additional-resources/list-of-published-state-and-metropolitan-area-series/"
    suffix = ".htm"
    successCityCode = []  # success
    successCity = []
    notExistCities = []  # fail to find the city
    notExistManu = []  # fail to find the manufacturing data
    with open('statesAndCity.txt', 'r', encoding='utf8') as f:
        for line in f.readlines():

            existCity = False
            existManu = False
            line = line.strip('\n').lower().replace('–', '-')
            states = line.split(" # ")[-1].replace(" ", "-").split(',')  # one city may belong to several state
            city = line.split(" # ")[0]

            for state in states:

                stateHtmlAddress = prifix + state + suffix
                print(stateHtmlAddress)
                stateHtml = request.urlopen(stateHtmlAddress)
                soup = BeautifulSoup(stateHtml, 'lxml')
                # get the table in stateHtmlAddress
                content = soup.find_all(name="table", attrs={"class": "regular"})
                table = content[0]

                # scan the state table
                for tr in table.findAll('tr'):
                    tds = tr.findAll('td')
                    if len(tds) < 4:
                        continue
                    area = tds[0].getText().split(',')[0].lower()
                    industry = tds[1].getText()

                    if city in area:
                        existCity = True
                        if "Manufacturing" in industry:
                            existManu = True
                            cityCode = tr.find('p').getText()
                            successCityCode.append(cityCode)
                            successCity.append(city)
                            break
                        else:
                            print(industry)
                # success
                if existCity is True and existManu is True:
                    break

                # fail to find the full name of the city
                if existCity is False and existManu is False:
                    # look for the similar city
                    cityCode = getSimilarCity(city, table)
                    if cityCode != "-1" and cityCode != "-2":
                        successCityCode.append(cityCode)
                        successCity.append(city)
                        existCity = True
                        existManu = True
                    elif cityCode == "-1":
                        existCity = True

            #  fail to find the similar city
            if existCity is False and existManu is False:
                notExistCities.append(city)
            # fail to find the manufacturing data
            if existCity is True and existManu is False:
                notExistManu.append(city)

            print(len(successCityCode)+len(notExistCities)+len(notExistManu))

            print(""+str(len(successCityCode))+":"+str(len(notExistCities))+":"+str(len(notExistManu)))

    with open("cityCodes.txt", "w", encoding='utf8') as f:
        f.write("success codes:{\n")
        for code in successCityCode:
            f.writelines(code + '\n')
        f.write("}\n")

        f.write("fail to find city :{\n")
        for city in notExistCities:
            f.write(city + '\n')
        f.write("}\n")

        f.write("fail to find the manufacturing data:{\n")
        for city in notExistManu:
            f.write(city + '\n')
        f.write("}")


# find the similar citiy
def getSimilarCity(city, table):
    hasCity = False
    city = city.split('-')[0].split(' ')[0]
    for tr in table.findAll('tr'):
        tds = tr.findAll('td')
        if len(tds) < 4:
            continue
        area = tds[0].getText().split(',')[0].lower()
        industry = tds[1].getText()
        if city in area:
            if industry == "Manufacturing":
                cityCode = tr.find('p').getText()
                return cityCode
            hasCity = True
    if hasCity is True:
        return "-1"
    return "-2"

# extract tables from html
def extractTable():
    soup = BeautifulSoup(open('Bureau_of_Labor_Statistics_Data.html', encoding='utf8'), features='html.parser')
    tablePrifix = "table"
    catalogPrifix = "catalog"
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("data")
    row = 0
    col = 0
    for i in range(333):
        tableId = tablePrifix+str(i)
        catalodId = catalogPrifix+str(i)
        table = soup.find(name='table', attrs={"id": tableId})
        catalog = soup.find(name='table', attrs={"id": catalodId})

        # catalog
        trs = catalog.findAll('tr')
        a = trs[0].find('td')
        seriesId = trs[0].find('td').getText()
        description = trs[1].find('td').getText()
        state = trs[2].find('td').getText()
        area = trs[3].find('td').getText()
        supersector = trs[4].find('td').getText()
        industry = trs[5].find('td').getText()
        dataType = trs[6].find('td').getText()

        sheet.write(row, 0, 'Series Id:')
        sheet.write(row, 1, seriesId)
        row += 1

        sheet.write(row, 0, description)
        row += 1

        sheet.write(row, 0, 'State:')
        sheet.write(row, 1, state)
        row += 1

        sheet.write(row, 0, 'Area:')
        sheet.write(row, 1, area)
        row += 1

        sheet.write(row, 0, 'Supersector:')
        sheet.write(row, 1, supersector)
        row += 1

        sheet.write(row, 0, 'Industry:')
        sheet.write(row, 1, industry)
        row += 1

        sheet.write(row, 0, 'Data Type:')
        sheet.write(row, 1, dataType)
        row += 1

        row += 1
        col = 0

        # data table
        # thead
        thead = table.find('thead')
        ths = thead.findAll('th')
        for th in ths:
            sheet.write(row, col, th.getText())
            col += 1

        row += 1
        col = 0

        #tbody
        tbody = table.find('tbody')
        trs = tbody.findAll('tr')
        for tr in trs:
            th = tr.find('th')
            tds = tr.findAll('td')
            sheet.write(row, col, th.getText())
            col += 1
            for td in tds:
                sheet.write(row, col, td.getText())
                col += 1
            row += 1
            col = 0

        row += 2

    workbook.save('./data.xls')

extractTable()