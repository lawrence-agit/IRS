import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import urllib.request 
import os


def get_file_path(form_number, year, extension_file):
  try:
    path_to_create = os.path.dirname(os.path.realpath(__file__))+"\\"+form_number
    if not os.path.exists(path_to_create):
      os.makedirs(path_to_create)
                            
    file_path = path_to_create+"\\"+str(form_number + " - " + str(year) + extension_file)
    if(os.path.exists(file_path)):
      i = 2
      while True:
        file_path = path_to_create+"\\"+str(form_number + " - " + str(year) + "_" +str(i)+"v" + extension_file) 
        if(i > 10000): #safety mecanishm
          return ""
        elif(os.path.exists(file_path)):
          i += 1
        else:
          return file_path
  except:
    return "";

def get_url_response_filtered_and_download(filter,start_year = 0, finish_year = 0):
    # this method will be load website information and save pdf files in script folder
    current_page = 1 # set first page
    results_per_page = 200 # maximum value
    number_of_results = 0 # calculate number of results

    # for each filter, get all results:
    for value in filter.split(","):
      # while exist data:
      while(True):
        first_row = number_of_results + (current_page-1)*results_per_page # Set Current page
        # Create URL with page, index of first row and filter form number
        URL = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html?value="+str(value)+"&criteria=formNumber&submitSearch=Find&indexOfFirstRow="+str(first_row)+"&sortColumn=sortOrder&value=&criteria=&resultsPerPage="+str(results_per_page)+"&isDescending=false"
        # Get Response from HTTP request
        page = requests.get(URL)
        if(page.status_code == 200): #Response OK
          try:
            # parse content
            soup = BeautifulSoup(page.content, "html.parser")
            # find table
            table = soup.find("table", { "class" : "picklist-dataTable" })
            # Calculate result of results
            new_results_count = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
            # Sum number of results
            number_of_results += new_results_count -1
            if(new_results_count == 1): # no more results to read
                break
            else: # exist result, let's read them
                for row in table.find_all('tr'): # Find Table rows
                    cols = row.find_all('td') # Find Table Columns
                    if cols: #Check if it is empty
                        link_to_download = cols[0].find('a').get('href') # get document link to download
                        if(link_to_download != "" and link_to_download is not None): # check link exists
                          cols = [ele.text.strip() for ele in cols] # parse row information
                          auxiliar = [ele for ele in cols if ele] # Get rid of empty values
                          year = 0
                          title = "_default_title"
                          number = "_no_number_"
                          # parse data
                          try:
                            number = auxiliar[0]
                            title = auxiliar [1]
                            year = int(auxiliar[2])
                          except Exception as error:
                            print("Error during parse html response:\n"+str(error))
                          # check the date conditions are checked 
                          if((start_year == 0 and finish_year == 0) # if not exist date filter
                             or (start_year <= year <= finish_year)): # or if year is between boundaries
                            # get file path
                            file_path = get_file_path(number,year,os.path.splitext(link_to_download)[1])
                            if(file_path != ""):
                              urllib.request.urlretrieve(link_to_download, file_path)                 
                if(new_results_count-1 < results_per_page): # if the answer is less than the limit per page, it is over
                    break
          except Exception as e:
            print("An exception occurred:" + str(e))
            return False,os.path.realpath(__file__)
    # everything ok:
    return True,os.path.realpath(__file__)

def get_url_response_filtered(filter):
    # this method will be load website information based on filter and return json result with structure:
    #[{
	  #  "form_number": "Example",
	  #  "form_title": "Title Example"
	  #  "max_year": "1998",
	  #  "min_year": "2020"
    #}... ]
    #
    dict = {}
    current_page = 1 # set first page
    results_per_page = 200 # maximum value
    number_of_results = 0 # calculate number of results

    # for each filter, get all results
    for value in filter.split(","):
      # while exist data:
      while(True):
        first_row = number_of_results + (current_page-1)*results_per_page # Set Current page
        # Create URL with page and index of first row
        URL = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html?value="+str(value)+"&criteria=formNumber&submitSearch=Find&indexOfFirstRow="+str(first_row)+"&sortColumn=sortOrder&value=&criteria=&resultsPerPage="+str(results_per_page)+"&isDescending=false"
        # Get Response from HTTP request
        page = requests.get(URL)
        if(page.status_code == 200): #Response OK
          try:
            # parse content
            soup = BeautifulSoup(page.content, "html.parser")
            # find table
            table = soup.find("table", { "class" : "picklist-dataTable" })
            # Calculate result of results
            new_results_count = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
            # Sum number of results
            number_of_results += new_results_count -1
            if(new_results_count == 1): # no more results to read
                break
            else: # exist result, let's read them
                for row in table.find_all('tr'): # Find Table rows
                    cols = row.find_all('td') # Find Table Columns
                    if cols: #Check if it is empty
                        cols = [ele.text.strip() for ele in cols]
                        auxiliar = [ele for ele in cols if ele] # Get rid of empty values
                        key = auxiliar[0]+auxiliar[1]

                        # algorithm to check if taxes already exist, if yes, check years to establish new max or min. If not exist create new JSON input
                        if key  not in dict:
                            dict[key] = {"form_number":auxiliar[0],"form_title": auxiliar[1],"min_year":auxiliar[2], "max_year":auxiliar[2]}
                        else:
                            value = dict[key]
                            if(value["max_year"]<auxiliar[2]):
                                dict[key]["max_year"] = auxiliar[2]
                            if(value["min_year"]>auxiliar[2]):
                                dict[key]["min_year"] = auxiliar[2]
                                    
                if(new_results_count-1 < results_per_page): # if the answer is less than the limit per page, it is over
                    break
          except Exception as e:
            print("An exception occurred:" + str(e))
    return list(dict.values())
          

def get_url_response():
    # this method will be load all website information and return json result with structure:
    #[{
	  #  "form_number": "Example",
	  #  "form_title": "Title Example"
	  #  "max_year": "1998",
	  #  "min_year": "2020"
    #}... ]
    #
    dict = {}
    current_page = 1 # set first page
    results_per_page = 200 # maximum value
    number_of_results = 0 # calculate number of results
    while(True):
      first_row = number_of_results + (current_page-1)*results_per_page # Set Current page
      # Create URL with page and index of first row
      URL = "https://apps.irs.gov/app/picklist/list/priorFormPublication.html?indexOfFirstRow="+str(first_row)+"&sortColumn=sortOrder&value=&criteria=&resultsPerPage="+str(results_per_page)+"&isDescending=false"
      # Get Response from HTTP request
      page = requests.get(URL)
      if(page.status_code == 200): #Response OK
     
        try:
          soup = BeautifulSoup(page.content, "html.parser")          
          table = soup.find("table", { "class" : "picklist-dataTable" })
          # Calculate result of results
          new_results_count = len(table.findAll(lambda tag: tag.name == 'tr' and tag.findParent('table') == table))
          # Sum number of results
          number_of_results += new_results_count -1
          if(new_results_count == 1): # no more results to read
              return list(dict.values())
          else: # exist result, let's read them
              for row in table.find_all('tr'): # Find Table rows
                  cols = row.find_all('td') # Find Table Columns
                  if cols: #Check if it is empty
                      cols = [ele.text.strip() for ele in cols]
                      auxiliar = [ele for ele in cols if ele] # Get rid of empty values
                      key = auxiliar[0]+auxiliar[1]
                      # algorithm to check if taxes already exist, if yes, check years to establish new max or min. If not exist create new JSON input
                        
                      if key  not in dict:
                          dict[key] = {"form_number":auxiliar[0],"form_title": auxiliar[1],"min_year":auxiliar[2], "max_year":auxiliar[2]}
                      else:
                          value = dict[key]
                          if(value["max_year"]<auxiliar[2]):
                              dict[key]["max_year"] = auxiliar[2]
                          if(value["min_year"]>auxiliar[2]):
                              dict[key]["min_year"] = auxiliar[2]
                                    
              if(new_results_count-1 < results_per_page): # if the answer is less than the limit per page, it is over
                  return list(dict.values())
        except Exception as e:
          print("An exception occurred:" + str(e))
          
def run_script(args):
  # this method will validate input arguments.if everything is ok, call next methods based on inputs
  try:
     # Validate arguments
     # 1st - list all taxs withou filter:
    if len(sys.argv) == 2 and sys.argv[1] == "list_taxes":
      print("Start reading data, it may take a few minutes") 
      website_data = get_url_response() 
      with open('all_taxes_result.txt', 'w') as outfile:
        json.dump(website_data, outfile)
      print("# Result:\n " + str(json.dumps(website_data, indent=4, sort_keys=True)))
    #2nd - list taxs based on filter input. This must be separated by comma and between "". Example "filter 1,filter 2"
    elif len(sys.argv) == 3 and sys.argv[1] == "list_taxes" and sys.argv[2] != "":
      print("Start reading filtered data") 
      website_data = get_url_response_filtered(sys.argv[2])
      with open('filtered_taxes_result.txt', 'w') as outfile:
        json.dump(website_data, outfile)
      print("# Result:\n " + str(json.dumps(website_data, indent=4, sort_keys=True)))
    #3rd - download taxes bases on filter input. This must be separated by comma and between "". Example "filter 1,filter 2"
    elif len(sys.argv) == 3 and sys.argv[1] == "download_taxes" and sys.argv[2] != "":
      print("Start downloading data...") 
      result, path = get_url_response_filtered_and_download(sys.argv[2])
      if(result):
        print("Finish download with success:" + str(path))
      else:
        print("Some troubles during download")
    #4th - download taxes based on filter input and date boundaries. The number filter must be separated by comma and between "". Example "filter 1,filter 2"
    # and Date filter must be integer format. Example python script_name "filter 1, filter 2" 2010 2020
    elif len(sys.argv) == 5 and sys.argv[1] == "download_taxes" and sys.argv[2] != "" and type(int(sys.argv[3])) is int and type(int(sys.argv[4])) is int:
      print("Start downloading data...") 
      # validate if dates was correct format
      start_year = int(sys.argv[3])
      finish_year = int(sys.argv[4])
      if(start_year>finish_year):
        start_year = finish_year
        finish_year = int(sys.argv[3])
      result, path = get_url_response_filtered_and_download(sys.argv[2],start_year,finish_year)
      if(result):
        print("Finish download with success: " + str(path))
      else:
        print("Some troubles during download")
    else:
        print("Please check README.TXT")
  except Exception as e:
    print("Please check arguments. \nError: " + str(e))


def main():
    print("America IRS Program!\nRead README.txt File to understand all arguments")
    run_script(sys.argv)
       

if __name__ == "__main__":
    main()