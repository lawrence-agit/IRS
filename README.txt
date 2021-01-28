Python 3.9.1

Script arguments:

- To list all taxes in website (https://apps.irs.gov/app/picklist/list/priorFormPublication.html):

#command: python AmericaIRS.py list_taxes

#result: for each form_number and form_title, print and save localy (all_taxes_result.txt) the following structure:

[{
	"form_number": "Example",
	"form_title": "Title Example"
	"max_year": "1998",
	"min_year": "2020"
}... ] 

- To list filtered taxes in website:

#command: python AmericaIRS.py list_taxes "form name 1,form name 2"
#obs: The filters must be separated by commas and without space after the same. The entire filter must be within "filter" 

#result: for each form_number given as a parameter , print and save localy (filtered_taxes_result.txt) the following structure:

[{
	"form_number": "form name 1",
	"form_title": "Title Example"
	"max_year": "1998",
	"min_year": "2020"
}... ] 

- To download taxes documents from website:

#command: python AmericaIRS.py download_taxes "form name 1, form name 2" 
#obs: The filters must be separated by commas and without space after the same. The entire filter must be within "filter". 

#result: If there is a file to download, it will be saved in a folder next to the script, like: [form_number]/[form_number] - [year].pdf

- To download taxes documents from website between dates:

#command: python AmericaIRS.py download_taxes "form name 1, form name 2" 2010 2020
#obs: The filters must be separated by commas and without space after the same. The entire filter must be within "filter". Years must be entered as an integer

#result: If there is a file to download, it will be saved in a folder next to the script, like: [form_number]/[form_number] - [year].pdf
