from io import StringIO
from github import Github
import requests
import yaml
import re
from dash_table.Format import Format, Scheme

#read config file
config = open("config.yaml")
config = yaml.load(config, Loader=yaml.FullLoader)

#data
github_username = config["github"]["username"]
github_token = config["github"]["token"]
github_repo_name = config["github"]["repo_name"]
github_raw_link = "https://raw.githubusercontent.com/" + github_repo_name + "/master/"

#session for file download
github_session = requests.Session()
github_session.auth = (github_username, github_token)

#session for content
session = Github(github_token)
repo = session.get_repo(github_repo_name, lazy=False)

#function for downloading files from GitHub
def download_from_github(file_url):
	file_url = github_raw_link + file_url
	download = github_session.get(file_url).content
	#read the downloaded content and make a pandas dataframe
	df_downloaded_data = StringIO(download.decode('utf-8'))

	return df_downloaded_data

#function to list GitHub repo content of a folder
def get_content_from_github(folder_path):
	dirs = []
	if folder_path[-1] == "/":
		folder_path = folder_path.rstrip()
	contents = repo.get_contents(folder_path)
	for folder in contents:
		folder = folder.name
		dirs.append(folder)
	return dirs

#dbc switch as boolean switch
def boolean_switch(switch_value):
	if len(switch_value) == 1:
		boolean_switch_value = True
	else:
		boolean_switch_value = False
		
	return boolean_switch_value

#color palettes
colors = ["#E31A1C", "#FF7F00", "#D9F0A3", "#33A02C", "#3B5DFF", "#6A3D9A", "#F46D43", "#FDAE61", "#E3DF00", "#B2DF8A", "#A6CEE3", "#CAB2D6", "#9E0142", "#FDB462", "#FFED6F", "#008941", "#1F78B4", "#5E4FA2", "#D53E4F", "#CCAA35", "#F4D749", "#B3DE69", "#3288BD", "#BC80BD", "#FB9A99", "#FED976", "#B15928", "#ABDDA4", "#8FB0FF", "#BB8BFF", "#CC002B", "#FB8072", "#CDA727", "#009131", "#0A09AE", "#5D00B9", "#772600", "#F7924C", "#FAD09F", "#006C31", "#5B93FF", "#5C006A", "#FF3944", "#BEAC3B", "#C48700", "#008531", "#4C43ED", "#BC29E1", "#AB2E00", "#DFFB71", "#E69A49", "#00B433", "#0000A6", "#6300A3", "#6B002C", "#CA834E", "#CCEBC5", "#9FA064", "#002DB5", "#9F94F0"]
gender_colors = {"Female": "#FA9FB5", "Male": "#9ECAE1"}
na_color = "#E6E6E6"

def get_color(metadata, i):
	if metadata == "NA":
		color = na_color
	elif metadata in ["Female", "Male"]:
		color = gender_colors[metadata]
	else:
		color = colors[i]
	
	return color

#go search function
def serach_go(search_value, df):
	#define search query if present
	if search_value.endswith(" "):
		search_value = search_value.rstrip()
	search_query = re.split(r"[\s\-/,_]+", search_value)
	search_query = [x.lower() for x in search_query]

	#search keyword in processes
	processes_to_keep = []
	for process in df["Process~name"]:
		#force lowecase
		process_lower = process.lower()
		#check each keyword
		for x in search_query:
			#if it is a GO id, search for GO id
			if x.startswith("go:"):
				go_id = process_lower.split("~")[0]
				if x == go_id:
					if process not in processes_to_keep:
						processes_to_keep.append(process)
			#else, just search in the name og the GO category
			else:
				if x in process_lower.split("~")[1]:
					processes_to_keep.append(process)
					if process not in processes_to_keep:
						processes_to_keep.append(process)

	return processes_to_keep

#dge table rendering
def dge_table_operations(table, dataset, stringency):
	pvalue_type = stringency.split("_")[0]
	pvalue_threshold = stringency.split("_")[1]
	
	#define dataset specific variables and link
	if dataset in ["human", "mouse"]:
		base_mean_label = "Average expression"
		gene_column_name = "Gene"
		table = table.rename(columns={"Geneid": "Gene ID"})
		#store genes and geneID without link formatting
		table["Gene"] = table["Gene"].fillna("")
		#create links
		table["External resources"] = "[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/gene/?term=" + table["Gene ID"] + ") " + "[![Ensembl](assets/icon_ensembl.png 'Ensembl')](https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=" + table["Gene ID"] + ") " + "[![GeneCards](assets/icon_genecards.png 'GeneCards')](https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + table["Gene ID"] + ") " + "[![GWAS catalog](assets/icon_gwas_catalog.png 'GWAS catalog')](https://www.ebi.ac.uk/gwas/genes/" + table["Gene"] + ") " + "[![GTEx](assets/icon_gtex.png 'GTEx')](https://www.gtexportal.org/home/gene/" + table["Gene"] + ") "
		#remove external resources where gene is not defined
		table.loc[table["Gene"] == "", "External resources"] = "[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/gene/?term=" + table["Gene ID"] + ") " + "[![Ensembl](assets/icon_ensembl.png 'Ensembl')](https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=" + table["Gene ID"] + ") " + "[![GeneCards](assets/icon_genecards.png 'GeneCards')](https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + table["Gene ID"] + ") " + "[![IBD exome browser](assets/icon_ibd_exome.png 'IBD exome browser')](https://ibd.broadinstitute.org/gene/" + table["Gene ID"] + ")"
	else:
		base_mean_label = "Average abundance"
		gene_column_name = dataset.split("_")[1].capitalize()
		table = table.rename(columns={"Gene": gene_column_name})
		table[gene_column_name] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table[gene_column_name]]
		table["External resources"] = ["[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/genome/?term=" + x.replace(" ", "+") + ")" for x in table[gene_column_name]]

	#data carpentry
	table["id"] = table[gene_column_name]
	table = table.sort_values(by=[pvalue_type])
	table = table.rename(columns={"log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
	table["P-value"] = table["P-value"].fillna("NA")
	table["FDR"] = table["FDR"].fillna("NA")

	#define data
	data = table.to_dict("records")

	#define columns
	columns = [
		{"name": gene_column_name, "id": gene_column_name}, 
		{"name": "Gene ID", "id":"Gene ID"},
		{"name": base_mean_label, "id": base_mean_label, "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
		{"name": "log2 FC", "id":"log2 FC", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
		{"name": "log2 FC SE", "id":"log2 FC SE", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
		{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
		{"name": "FDR", "id":"FDR", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
		{"name": "External resources", "id":"External resources", "type": "text", "presentation": "markdown"}
		]
	#Gene ID column not useful for metatransciptomics data
	if dataset not in ["human", "mouse"]:
		del columns[1]

	if pvalue_type == "padj":
		pvalue_column = "{FDR}"
	else:
		pvalue_column = "{P-value}"

	#color rows by pvalue and up and down log2FC
	style_data_conditional = [
		{
			"if": {
				"filter_query": '{pvalue_column} = "NA"'.format(pvalue_column=pvalue_column)
			},
			"backgroundColor": "white"
		},
		{
			"if": {
				"filter_query": "{pvalue_column} < {threshold}".format(pvalue_column=pvalue_column, threshold=pvalue_threshold) + " && {log2 FC} < 0"
			},
			"backgroundColor": "#E6F0FF"
		},
		{
			"if": {
				"filter_query": "{pvalue_column} < {threshold}".format(pvalue_column=pvalue_column, threshold=pvalue_threshold) + " && {log2 FC} > 0"
			},
			"backgroundColor": "#FFE6E6"
		}
	]

	return columns, data, style_data_conditional

