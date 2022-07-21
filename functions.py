import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import re
import yaml
from io import StringIO
from github import Github
from dash.dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate
from dash import html, dcc
import tempfile
import gzip

#read config file
config = open("config.yaml")
config = yaml.load(config, Loader=yaml.FullLoader)

#color palette
colors = config["palette"]
#NA color
na_color = "#E6E6E6"
#gender colors
gender_colors = {"Female": "#FA9FB5", "Male": "#9ECAE1"}

#setup analysis dropdown
repos = list(config["repos"].keys())

#multiple analysis dropdown will compare only when there are more repos to choose
if len(repos) > 1:
	multiple_analysis = False
else:
	multiple_analysis = True

repos_options = []
for repo in repos:
	repos_options.append({"label": config["repos"][repo]["analysis"], "value": config["repos"][repo]["path"]})

#login to github
github_session = requests.Session()
github_username = config["github"]["username"]
github_token = config["github"]["token"]
github_session.auth = (github_username, github_token)
session = Github(github_token)

#function for downloading files from GitHub
def download_from_github(path, file_url):
	file_url = "https://raw.githubusercontent.com/" + path + file_url
	download = github_session.get(file_url).content
	#decompress gzip data
	if file_url.split(".")[-1] == "gz":
		download = gzip.decompress(download)
	#read the downloaded content and make a pandas dataframe
	df_downloaded_data = StringIO(download.decode('utf-8'))

	return df_downloaded_data

#function to list GitHub repo content of a folder
def get_content_from_github(path, folder_path):
	dirs = []
	match = re.match(r"(.+/.+)/(.+)/", path)
	github_repo_name = match.group(1)
	github_branch_name = match.group(2)
	if github_branch_name == "master":
		github_branch_name = "main"
	repo = session.get_repo(github_repo_name, lazy=False)
	contents = repo.get_contents(folder_path, ref=github_branch_name)
	for folder in contents:
		folder = folder.name
		dirs.append(folder)
	return dirs

#get repo name from path
def get_repo_name_from_path(path, repos):
	for repo in repos:
		if path == config["repos"][repo]["path"]:
			return repo

#styles for tabs and selected tabs
tab_style = {
	"padding": 6, 
	"backgroundColor": "#FAFAFA"
}

tab_selected_style = {
    "padding": 6,
	"border-top": "3px solid #597ea2"
}

#dbc switch as boolean switch
def boolean_switch(switch_value):
	if len(switch_value) == 1:
		boolean_switch_value = True
	else:
		boolean_switch_value = False
		
	return boolean_switch_value

#function to assign colors
def get_color(color_mapping, metadata_column, variable):
	if metadata_column == "NA":
		color = na_color
	elif metadata_column == "Log2 expression":
		color = "reds"
	else:
		color = color_mapping[metadata_column][variable]
	
	return color

#feature dropdown dataset variables
def get_list_label_placeholder_feature_dropdown(path, expression_dataset):
	if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
		features = "data/" + expression_dataset + "/counts/genes_list.tsv"
		if expression_dataset in ["human", "mouse"]:
			placeholder = "Type here to search host genes"
			label = "Host gene"
		else:
			placeholder = "Type here to search {}".format(expression_dataset.replace("_", " "))
			label = expression_dataset.capitalize().replace("_", " ")
	else:
		if "lipid" in expression_dataset:
			features = "data/" + expression_dataset + "/counts/lipid_list.tsv"
			label = expression_dataset.capitalize().replace("_", " ")
			if expression_dataset == "lipid":
				placeholder = "Type here to search lipids"
			else:
				placeholder = "Type here to search lipid categories"
		else:
			features = "data/" + expression_dataset + "/counts/feature_list.tsv"
			placeholder = "Type here to search {}".format(expression_dataset.replace("_", " ").replace("order", "orders").replace("family", "families"))
			label = expression_dataset.capitalize().replace("_", " by ")

	features = download_from_github(path, features)
	features = pd.read_csv(features, sep = "\t", header=None, names=["feature"])
	features = features["feature"].tolist()
	
	return features, label, placeholder

#get options based on user search features dropdown
def get_options_feature_dropdown(expression_dataset, features, search_value, current_value, dropdown_type):
	options = []
	if search_value is not None:
		for feature in features:
			#get feature label
			if expression_dataset in ["human", "mouse"]:
				feature_label = feature.replace("€", "/")
				search_value = search_value.replace("€", "/")
			elif "genes" in expression_dataset:
				feature_gene = feature.split("@")[0]
				feature_beast = feature.split("@")[1]
				feature_beast = feature_beast.replace("_", " ")
				feature_label = feature_gene + " - " + feature_beast
				if "@" in search_value:
					search_gene = search_value.split("@")[0]
					search_beast = search_value.split("@")[1]
					search_beast = search_beast.replace("_", " ")
					search_value = search_gene + " - " + search_beast
			else:
				feature_label = feature.replace("_", " ").replace("[", "").replace("]", "")
				search_value = search_value.replace("_", " ").replace("[", "").replace("]", "")

			#single and multidropdown
			if dropdown_type == "single":
				if search_value.upper() in feature_label.upper():
					options.append({"label": feature_label, "value": feature})
			elif dropdown_type == "multi":
				if search_value.upper() in feature_label.upper() or feature in (current_value or []):
					options.append({"label": feature_label, "value": feature})
		
	return options

#function for creating a discrete colored mds from tsv file
def plot_mds_discrete(mds_df, color_mapping, x, y, selected_metadata, mds_discrete_fig, label_to_value, path):

	#need original selected metadata
	for key in label_to_value:
		if selected_metadata == label_to_value[key]:
			selected_metadata_for_color_mapping = key
			break

	#too many samples will need smaller dots
	number_of_samples = len(mds_df["Sample"].tolist())
	if number_of_samples > 20:
		marker_size = 6
	else:
		marker_size = 8

	#get repo
	repo = get_repo_name_from_path(path, repos)

	#plot
	i = 0
	if config["repos"][repo]["sorted_conditions"] and selected_metadata == "Condition":
		metadata_fields_ordered = config["repos"][repo]["condition_list"]
		metadata_fields_ordered = [metadata_field.replace("_", " ") for metadata_field in metadata_fields_ordered]
	else:
		metadata_fields_ordered = mds_df[selected_metadata].unique().tolist()
		metadata_fields_ordered.sort()

	#get hover template and get columns to keep for customdata
	metadata_columns = []
	i = 0
	general_hover_template = ""
	for key in label_to_value:
		metadata_columns.append(label_to_value[key])
		general_hover_template += "{key}: %{{customdata[{i}]}}<br>".format(key=label_to_value[key], i=i)
		i += 1

	#hover template for this trace
	hover_template = general_hover_template + "<extra></extra>"

	#add traces
	for metadata in metadata_fields_ordered:
		filtered_mds_df = mds_df[mds_df[selected_metadata] == metadata]
		filtered_mds_df = filtered_mds_df.round(2)
		custom_data = filtered_mds_df[metadata_columns].fillna("NA")
		marker_color = get_color(color_mapping, selected_metadata_for_color_mapping, metadata)
		mds_discrete_fig.add_trace(go.Scatter(x=filtered_mds_df[x], y=filtered_mds_df[y], marker_opacity=1, marker_color=marker_color, marker_size=marker_size, customdata=custom_data, mode="markers", legendgroup=metadata, showlegend=True, hovertemplate=hover_template, name=metadata, visible=True), row=1, col=1)
	
	#mds_discrete_fig["layout"]["paper_bgcolor"]="LightSteelBlue"

	return mds_discrete_fig

#function for creating a continuous colored mds from tsv file
def plot_mds_continuous(mds_df, x, y, variable_to_plot, color, mds_continuous_fig, label_to_value, path, colorbar_len):
	
	#operations on mds_df
	number_of_samples = len(mds_df["Sample"].tolist())
	if number_of_samples > 20:
		marker_size = 6
	else:
		marker_size = 8
	
	#get hover template and get columns to keep for customdata
	metadata_columns = []
	i = 0
	general_hover_template = ""
	for key in label_to_value:
		metadata_columns.append(label_to_value[key])
		general_hover_template += "{key}: %{{customdata[{i}]}}<br>".format(key=label_to_value[key], i=i)
		i += 1

	#expression continuous umap will have counts
	if len(variable_to_plot) == 3:
		subplot_column = 2
		marker_colorbar_x = 1.02
		expression_dataset = variable_to_plot[0]
		feature = variable_to_plot[1]
		samples_to_keep = variable_to_plot[2]
		continuous_variable_to_plot = "Log2 expression"

		#download counts
		counts = download_from_github(path, "data/" + expression_dataset + "/counts/" + feature + ".tsv")
		counts = pd.read_csv(counts, sep = "\t")
		counts = counts.rename(columns={"sample": "Sample"})
		counts = counts.replace("_", " ", regex=True)

		#add counts to umap df
		mds_df = mds_df.merge(counts, how="outer", on="Sample")
		#filter samples that are not visible
		mds_df = mds_df[mds_df["Sample"].isin(samples_to_keep)]

		#add log2 counts column to df
		mds_df["Log2 expression"] = np.log2(mds_df["counts"])
		mds_df["Log2 expression"].replace(to_replace = -np.inf, value = 0, inplace=True)
		#labels for graph title
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"
		#plot parameters
		colorbar_title = "Log2 {}".format(expression_or_abundance)
		hover_template = general_hover_template + "Log2{expression_or_abundance}: %{{marker.color}}<br><extra></extra>".format(expression_or_abundance=expression_or_abundance)
	#metadata continuous umap will use the metadata without counts
	else:
		subplot_column = 1
		marker_colorbar_x = 0.415
		selected_metadata = variable_to_plot[0]
		continuous_variable_to_plot = selected_metadata
		colorbar_title = selected_metadata
		hover_template = general_hover_template + "<extra></extra>"
	
	#fill nan with NA
	mds_df = mds_df.fillna("NA")
	mds_df = mds_df.round(2)

	#select only NA values
	na_df = mds_df.loc[mds_df[continuous_variable_to_plot] == "NA"]
	custom_data = na_df[metadata_columns]
	#add discrete trace for NA values
	mds_continuous_fig.add_trace(go.Scatter(x=na_df[x], y=na_df[y], marker_color=na_color, marker_size=marker_size, customdata=custom_data, mode="markers", showlegend=False, hovertemplate=hover_template, name="na_continuous_trace", visible=True), row=1, col=subplot_column)
	#select only not NA
	mds_df = mds_df.loc[mds_df[continuous_variable_to_plot] != "NA"]
	custom_data = mds_df[metadata_columns]
	marker_color = mds_df[continuous_variable_to_plot]
	#add continuous trace
	if color == "reds":
		colorscale = color
	else:
		colorscale = ["#FFFFFF", color]
	mds_continuous_fig.add_trace(go.Scatter(x=mds_df[x], y=mds_df[y], name=continuous_variable_to_plot, marker_color=marker_color, marker_colorscale=colorscale, marker_showscale=True, marker_opacity=1, marker_size=marker_size, marker_colorbar_title=colorbar_title, marker_colorbar_title_side="right", marker_colorbar_title_font_size=14, marker_colorbar_thicknessmode="pixels", marker_colorbar_thickness=15, marker_colorbar_len=colorbar_len, marker_colorbar_tickfont={"family": "Arial", "size": 14}, marker_colorbar_x=marker_colorbar_x, marker_colorbar_yanchor="top", marker_colorbar_y=1, mode="markers", customdata=custom_data, hovertemplate=hover_template, showlegend=False, visible=True), row=1, col=subplot_column)
	
	#mds_continuous_fig["layout"]["paper_bgcolor"]="#E5F5F9"

	return mds_continuous_fig

#get number of displayed samples in mds
def get_displayed_samples(figure_data):

	x_range = figure_data["layout"]["xaxis"]["range"]
	y_range = figure_data["layout"]["yaxis"]["range"]
	
	#start of the app: get range for axes
	if x_range is None or y_range is None:
		full_fig = figure_data.full_figure_for_development(warn=False)
		x_range = list(full_fig.layout.xaxis.range)
		y_range = list(full_fig.layout.yaxis.range)
	
	#parse only visible traces
	n_samples = 0
	for trace in figure_data["data"]:
		if trace["visible"] is True and trace["name"] not in ["na_continuous_trace", "Log2 expression", "Log2 abundance"]:
			#check all points
			for i in range(0, len(trace["x"])):
				x = trace["x"][i]
				y = trace["y"][i]
				if x != "NA" and y != "NA":
					if x > x_range[0] and x < x_range[1] and y > y_range[0] and y < y_range[1]:
						n_samples += 1

	return n_samples

#elements in the x axis in boxplots
def get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset, path):
	#open metadata
	metadata_df = download_from_github(path, "metadata.tsv")
	metadata_df = pd.read_csv(metadata_df, sep = "\t")

	#counts as y need external file with count values
	if selected_y in ["log2_expression", "log2_abundance"]:
		#get a feature to filter metadata by selecting only samples which have counts
		if feature_dataset in ["human", "mouse"] or "genes" in feature_dataset:
			list = "data/" + feature_dataset + "/counts/genes_list.tsv"
		else:
			if "lipid" in feature_dataset:
				list = "data/" + feature_dataset + "/counts/lipid_list.tsv"
			else:
				list = "data/" + feature_dataset + "/counts/feature_list.tsv"
		list = download_from_github(path, list)
		list = pd.read_csv(list, sep = "\t", header=None, names=["gene_species"])
		list = list["gene_species"].tolist()
		feature = list[0]
		counts = download_from_github(path, "data/" + feature_dataset + "/counts/" + feature + ".tsv")
		counts = pd.read_csv(counts, sep = "\t")
		metadata_df = metadata_df.merge(counts, how="inner", on="sample")
	
	#get all x
	x_values = metadata_df[selected_x].unique().tolist()
	
	#setup options
	options = []
	for x_value in x_values:
		options.append({"label": x_value.replace("_", " "), "value": x_value})
	
	return options, x_values

#go search function
def serach_go(search_value, df, expression_dataset, add_gsea_switch):
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
			#else, just search in the name of the GO category
			else:
				if expression_dataset in ["human", "mouse"] and not add_gsea_switch:
					process_name = process_lower.split("~")[1]
				else:
					process_name = process_lower
				if x in process_name:
					processes_to_keep.append(process)
					if process not in processes_to_keep:
						processes_to_keep.append(process)

	return processes_to_keep

#dge table rendering
def dge_table_operations(table, dataset, stringency, target_prioritization, path):
	pvalue_type = stringency.split("_")[0]
	pvalue_threshold = stringency.split("_")[1]

	if target_prioritization:
		#keep degs and remove useless columns
		table = table.rename(columns={"log2FoldChange": "log2 FC", "padj": "FDR", "Geneid": "Gene ID"})
		table["id"] = table["Gene"]
		table = table[table["FDR"] < float(pvalue_threshold)]
		table = table[["Gene", "Gene ID", "log2 FC", "FDR", "id"]]

		#build df from data
		opentarget_df = download_from_github(path, "opentargets.tsv")
		opentarget_df = pd.read_csv(opentarget_df, sep="\t")
		table = pd.merge(table, opentarget_df, on="Gene ID")
		table = table.fillna("")

		#priority for overexpression
		if not table.empty:
			table.loc[(table["log2 FC"] > 0), "DGE"] = 1
			table.loc[(table["log2 FC"] < 0), "DGE"] = 0
			#sort values according to these columns
			table = table.sort_values(["DGE", "index"], ascending = (False, False))
			table = table.reset_index(drop=True)
			table = table.drop("DGE", axis=1)
			table = table.drop("index", axis=1)
			all_columns = list(table.columns)
			table["Rank"] = [x + 1 for x in list(table.index)]
			table = table[["Rank"] + all_columns]
		else:
			table["Rank"] = []
		
		#define columns
		columns = [
			{"name": "Rank", "id": "Rank"},
			{"name": "Gene", "id": "Gene"},
			{"name": "Gene ID", "id":"Gene ID"},
			{"name": "log2 FC", "id":"log2 FC", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "FDR", "id": "FDR", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "Drugs count", "id": "drugs_count", "type": "numeric"},
			{"name": "Drugs", "id": "drugs", "type": "text", "presentation": "markdown"},
			{"name": "Associated drugs count", "id": "related_drugs_count", "type": "numeric"},
			{"name": "Associated drugs", "id": "related_drugs", "type": "text", "presentation": "markdown"},
			{"name": "GWAS", "id": "GWAS_count", "type": "text", "presentation": "markdown"},
			{"name": "Tissue eQTL", "id": "QTL_in_tissues_count", "type": "numeric"},
			{"name": "Tissue eQTL", "id": "QTL_in_tissues", "type": "text", "presentation": "markdown"},
			{"name": "Protein expression in cell types", "id": "expression_in_tissue_cell_types_count", "type": "numeric"},
			{"name": "Protein expression in cell types", "id": "expression_in_tissue_cell_types", "type": "text", "presentation": "markdown"},
			{"name": "Protein expression in cell compartments", "id": "protein_expression_in_cell_compartment_count", "type": "numeric"},
			{"name": "Protein expression in cell compartments", "id": "protein_expression_in_cell_compartment", "type": "text", "presentation": "markdown"}
		]
	else:
		#define dataset specific variables and link
		if dataset in ["human", "mouse"]:
			base_mean_label = "Average expression"
			gene_column_name = "Gene"
			table = table.rename(columns={"Geneid": "Gene ID"})
			#store genes and geneID without link formatting
			table["Gene"] = table["Gene"].fillna("")

			#create links which use gene ID
			external_resources_geneid = "[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/gene/?term=" + table["Gene ID"] + ") " + "[![Ensembl](assets/icon_ensembl.png 'Ensembl')](https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=" + table["Gene ID"] + ") " + "[![GeneCards](assets/icon_genecards.png 'GeneCards')](https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + table["Gene ID"] + ")"

			#create links which use gene ID
			external_resources_gene = " [![GWAS catalog](assets/icon_gwas_catalog.png 'GWAS catalog')](https://www.ebi.ac.uk/gwas/genes/" + table["Gene"] + ") " + "[![GTEx](assets/icon_gtex.png 'GTEx')](https://www.gtexportal.org/home/gene/" + table["Gene"] + ")"

			#additional external resources
			if config["add_external_resources_to_dge_table"]:
				for external_resource in config["external_resources"]:
					column_to_use = config["external_resources"][external_resource]["column_to_use"]
					if column_to_use == "Gene ID":
						external_resources_to_update = external_resources_geneid
					else:
						external_resources_to_update = external_resources_gene
					external_resources_to_update += " [![{name}]({icon} '{name}')]({link_root}".format(name=external_resource, icon=config["external_resources"][external_resource]["icon"], link_root=config["external_resources"][external_resource]["link_root"]) + table[column_to_use] + ")"
			
			#paste all external resources and apply
			external_resources = external_resources_geneid + external_resources_gene
			table["External resources"] = external_resources
			
			#remove external resources where gene is not defined
			table.loc[table["Gene"] == "", "External resources"] = external_resources_geneid
		else:
			#base mean label
			if "genes" in dataset:
				base_mean_label = "Average expression"
			else:
				base_mean_label = "Average abundance"
			#all other variables
			gene_column_name = dataset.replace("_", " ").capitalize()
			if "lipid" in dataset:
				table = table.rename(columns={"Gene": gene_column_name, "Geneid": "Gene ID"})
				table["Gene ID"] = table["Gene ID"].fillna("")
				table["External resources"] = "[![LIPID MAPS](assets/icon_lipid_maps.png 'LIPID MAPS')](https://www.lipidmaps.org/databases/lmsd/" + table["Gene ID"] + ")"
				table.loc[table["Gene ID"] == "", "External resources"] = ""
			elif "genes" in dataset:
				table = table.rename(columns={"Gene": gene_column_name})
				clean_gen_column_name = []
				for x in table[gene_column_name]:
					gene_x = x.split("@")[0]
					beast_x = x.split("@")[1]
					beast_x = beast_x.replace("_", " ")
					x = gene_x + " - " + beast_x
					clean_gen_column_name.append(x)
				table[gene_column_name] = clean_gen_column_name.copy()
				table["External resources"] = ["[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/search/all/?term=" + x.replace(" - ", " ").replace(" ", "+") + ")" for x in table[gene_column_name]]
			else:
				table = table.rename(columns={"Gene": gene_column_name})
				table[gene_column_name] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table[gene_column_name]]
				table["External resources"] = ["[![NCBI](assets/icon_ncbi.png 'NCBI')](https://www.ncbi.nlm.nih.gov/genome/?term=" + x.replace(" ", "+") + ")" for x in table[gene_column_name]]

		#data carpentry
		table["id"] = table[gene_column_name]
		if "Comparison" in table.columns:
			table = table.sort_values(by=["Comparison", pvalue_type])
		else:
			table = table.sort_values(by=[pvalue_type])
		table = table.rename(columns={"log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
		table["P-value"] = table["P-value"].fillna("NA")
		table["FDR"] = table["FDR"].fillna("NA")

		#define columns
		if dataset == "lipid":
			geneid_label = "Lipid ID"
		else:
			geneid_label = "Gene ID"
		columns = [
			{"name": gene_column_name, "id": gene_column_name}, 
			{"name": geneid_label, "id":"Gene ID"},
			{"name": base_mean_label, "id": base_mean_label, "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "log2 FC", "id":"log2 FC", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "log2 FC SE", "id":"log2 FC SE", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "FDR", "id":"FDR", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)},
			{"name": "External resources", "id":"External resources", "type": "text", "presentation": "markdown"}
		]
		#Gene ID column not useful for metatransciptomics data and lipid category
		if dataset not in ["human", "mouse", "lipid"]:
			del columns[1]
			#lipid categories doesn't have any external resource
			if dataset == "lipid_category":
				del columns[-1]
		
		#add contrast column as first column if necessary
		if "Comparison" in table.columns:
			columns = [{"name": "Comparison", "id": "Comparison"}] + columns

	#define data
	data = table.to_dict("records")

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
		},
		{
			"if": {"state": "selected"},
			"backgroundColor": "rgba(44, 62, 80, 0.2)",
			"border": "1px solid #597ea2",
		}
	]

	return columns, data, style_data_conditional

#dge table download
def dge_table_download_operations(df, dataset, contrast, stringency, filtered):
	
	#define dataset specific variables
	if dataset in ["human", "mouse"] or "genes" in dataset:
		base_mean_label = "Average expression"
		gene_id = "Gene ID"
		file_name = "DGE_{}_{}.xlsx".format(dataset, contrast)
		gene_column_name = "Gene"
	else:
		base_mean_label = "Average abundance"
		if "lipid" in dataset:
			gene_column_name = dataset.replace("_", " ").capitalize()
			gene_id = "Lipid ID"
			file_name = "DLE_{}_{}.xlsx".format(dataset, contrast)
		else:
			gene_column_name = dataset.split("_")[1].capitalize()
			gene_id = "Meta ID"
			file_name = "DA_{}_{}.xlsx".format(dataset, contrast)
		df = df.rename(columns={"Gene": gene_column_name})

	#filtered file name
	if filtered:
		file_name = file_name.replace(".xlsx", "_filtered.xlsx")

	#rename
	df = df.rename(columns={"Geneid": gene_id, "log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})

	#remove a geneid in non human dge
	if dataset not in ["human", "mouse", "lipid", "lipid_id"]:
		df = df[[gene_column_name, "log2 FC", "log2 FC SE", "P-value", "FDR", base_mean_label]]

	stringecy_stype = stringency.split("_")[0]
	stringency_threshold = float(stringency.split("_")[1])
	if stringecy_stype == "padj":
		stringency_column = "FDR"
	else:
		stringency_column = "P-value"
	#sort by stringecy type
	df = df.sort_values(by=[stringency_column])
	
	(max_row, max_col) = df.shape

	with tempfile.TemporaryDirectory() as tmpdir:
		writer = pd.ExcelWriter(f"{tmpdir}/{file_name}")

		#general format
		format_white = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top"})
		format_up = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top", "bg_color": "#FFE6E6"})
		format_down = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top", "bg_color": "#E6F0FF"})
		df.to_excel(writer, sheet_name="Sheet 1", index=False, freeze_panes=(1, 1))
		sheet = writer.sheets["Sheet 1"]
		
		#write header with white formatting
		for col_num, value in enumerate(df.columns.values):
			sheet.write(0, col_num, value, format_white)
		
		#apply formatting to all the current sheet
		sheet.set_column(0, max_col, 17, format_white)
		i = 1
		for index, row in df.iterrows():
			#significant
			if row[stringency_column] < stringency_threshold:
				#up
				if row["log2 FC"] > 0:
					dge_format = format_up
				#down
				else:
					dge_format = format_down
			#not significant
			else:
				dge_format = format_white
			sheet.set_row(i, None, dge_format)
			i += 1
			
		writer.save()

		return dcc.send_file(f"{tmpdir}/{file_name}")

#go table download
def go_table_download_operations(go_df, expression_dataset, contrast, filtered):

	#dataset variables
	if expression_dataset in ["human", "mouse"]:
		process_column = "GO biological process"
		feature_columm = "Genes"
		diff_column = "DEGs"
		up_or_down_column = "DGE"
		go_df = go_df.rename(columns={"Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment"})
		file_name = "GO_{}.xlsx".format(contrast)
	else:
		go_df["Genes"] = go_df["Genes"].str.replace(";", "; ")
		go_df["Process~name"] = go_df["Process~name"].str.replace("_", " ")
		process_column = "Functional category"
		feature_columm = "Lipids"
		up_or_down_column = "DLE"
		diff_column = "LSEA DELs"
		go_df = go_df.rename(columns={"DGE": up_or_down_column, "Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment", "Genes": feature_columm})
		file_name = "LO_{}.xlsx".format(contrast)

	#filtered file name
	if filtered:
		file_name = file_name.replace(".xlsx", "_filtered.xlsx")

	#create excel
	with tempfile.TemporaryDirectory() as tmpdir:
		writer = pd.ExcelWriter(f"{tmpdir}/{file_name}")

		#general format
		(max_row, max_col) = go_df.shape
		format_white = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top"})
		format_up = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top", "bg_color": "#FFE6E6"})
		format_down = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top", "bg_color": "#E6F0FF"})
		go_df.to_excel(writer, sheet_name="Metadata", index=False, freeze_panes=(1, 1))
		sheet = writer.sheets["Metadata"]
	
		#write header with white formatting
		for col_num, value in enumerate(go_df.columns.values):
			sheet.write(0, col_num, value, format_white)
		
		#apply formatting to the columns
		sheet.set_column(0, 0, 5, format_white)
		sheet.set_column(1, 1, 60, format_white)
		sheet.set_column(2, 2, 30, format_white)
		sheet.set_column(3, max_col, 14, format_white)
		
		#color rows
		i = 1
		for index, row in go_df.iterrows():
			#up
			if row[up_or_down_column] == "up":
				dge_format = format_up
			#down
			else:
				dge_format = format_down
			sheet.set_row(i, None, dge_format)
			i += 1

		#save tmp file
		writer.save()

		return dcc.send_file(f"{tmpdir}/{file_name}")

#search genes in the textarea
def search_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, selected_features, add_gsea_switch, number_of_features, path):
	
	#click on GO-plot
	if trigger_id == "go_plot_graph.clickData":
		if isinstance(go_plot_click["points"][0]["y"], str):
			#reset log div
			log_div = []
			log_hidden_status = True

			#do not add genes to metatranscriptomics elements!
			if expression_dataset not in ["human", "mouse", "lipid"]:
				raise PreventUpdate

			#read go table
			if expression_dataset in ["human", "mouse"]:
				go_df = download_from_github(path, "data/{}/".format(expression_dataset) + stringency_info + "/" + contrast + ".merged_go.tsv")
			else:
				go_df = download_from_github(path, "data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
			go_df = pd.read_csv(go_df, sep = "\t")
			go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			#concatenate gsea results if the switch is true
			boolean_add_gsea_switch = boolean_switch(add_gsea_switch)
			if boolean_add_gsea_switch:
				gsea_df = download_from_github(path, "data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
				gsea_df = pd.read_csv(gsea_df, sep = "\t")
				gsea_df["Genes"] = [gene.replace(";", "; ") for gene in gsea_df["Genes"]]
				gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
				go_df = pd.concat([go_df, gsea_df])
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})

			#crop too long process name
			processes = []
			for process in go_df["Process"]:
				if len(process) > 80:
					process = process[0:79] + " ..."
				processes.append(process.replace("_", " "))
			go_df["Process"] = processes

			#search GO ID and get genes
			if go_plot_click["points"][0]["y"].startswith("GO"):
				process_name = go_plot_click["points"][0]["y"]
			else:
				process_name = go_plot_click["points"][0]["y"].replace("_", " ")
			go_df = go_df[go_df["Process"] == process_name]
			genes = go_df["Genes"].tolist()
			if len(genes) == 2:
				genes = genes[0] + " " + genes[1]
			else:
				genes = genes[0]
			#remove last ; if present
			if genes[-1] == ";":
				genes = genes[:-1]
			#create a list of genes and add them to the multidropdown
			genes = genes.split("; ")
			new_genes = []
			for gene in genes:
				if gene not in selected_features:
					selected_features.append(gene)
					new_genes.append(gene)
			#add genes to text area
			if len(text) > 0:
				text += "; "
			text += "; ".join(new_genes)
		
		#click on the enrichment legend should not trigger anything
		else:
			raise PreventUpdate

	#reset text area if you change the input dropdowns
	elif trigger_id in ["contrast_dropdown.value", "stringency_dropdown.value", "analysis_dropdown.value", "feature_dataset_dropdown.value", "."]:
		#reset log div
		log_div = []
		log_hidden_status = True
		
		diffexp_df = download_from_github(path, "data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
		diffexp_df = pd.read_csv(diffexp_df, sep = "\t")
		diffexp_df["Gene"] = diffexp_df["Gene"].fillna("NA")
		diffexp_df = diffexp_df[diffexp_df["Gene"] != "NA"]

		#stingency specs
		pvalue_type = stringency_info.split("_")[0]
		pvalue_value = stringency_info.split("_")[1]

		#find DEGs
		diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] > 0), "DEG"] = "Up"
		diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] < 0), "DEG"] = "Down"

		#function to select top n genes
		def get_top_n(list_type, number_of_features, diffexp_df):
			#get top up 15 DEGs by log2FC
			genes = diffexp_df[diffexp_df["DEG"] == list_type]
			#sort by log2FC
			genes = genes.sort_values(by=["log2FoldChange"], ascending=False)
			#take top n
			genes = genes.head(number_of_features)
			#get genes
			genes = genes["Gene"].tolist()

			return genes

		#apply function
		up_genes = get_top_n("Up", number_of_features, diffexp_df)
		down_genes = get_top_n("Down", number_of_features, diffexp_df)

		#add genes to dropdown
		selected_features = up_genes + down_genes
		selected_features = [gene_species.replace(" ", "_").replace("/", "€") for gene_species in selected_features]

		#clean feature names
		def clean_feature_names_for_text_area(gene_list):
			clean_list = []
			for gene in gene_list:
				if expression_dataset not in ["human", "mouse", "lipid"]:
					if "genes" in expression_dataset:
						feature_gene = gene.split("@")[0]
						feature_beast = gene.split("@")[1]
						feature_beast = feature_beast.replace("_", " ")
						gene = feature_gene + " - " + feature_beast
					else:
						gene = gene.replace("_", " ").replace("[", "").replace("]", "")
				clean_list.append(gene)
			
			return clean_list
		
		#apply function
		up_genes = clean_feature_names_for_text_area(up_genes)
		down_genes = clean_feature_names_for_text_area(down_genes)

		#add genes in text area
		if expression_dataset in ["human", "mouse", "lipid"]:
			sep = "; "
		else:
			sep = "\n"
		up_genes_string = sep.join(up_genes)
		down_genes_string = sep.join(down_genes)
		if len(up_genes) == 0 and len(down_genes) != 0:
			text = down_genes_string
		elif len(down_genes) == 0 and len(up_genes) != 0:
			text = up_genes_string
		elif len(up_genes) == 0 and len(down_genes) == 0:
			text = ""
		else:
			text = up_genes_string + sep + down_genes_string
	
	#button click by the user
	else:
		#text is none, do almost anything
		if text is None or text == "":
			if expression_dataset in ["human", "mouse", "lipid"] or "genes" in expression_dataset:
				log_div = [html.Br(), "No genes in the search area!"]
			else:
				if expression_dataset == "lipid":
					element = "lipids"
				else:
					element = expression_dataset.replace("_", " ").replace("bacteria", "bacterial").replace("archaea", "archaeal").replace("eukaryota", "eukaryotic").replace("order", "orders").replace("family", "families").replace("category", "categories")
				log_div = [html.Br(), "No " + element + " in the search area!"]
			log_hidden_status = False
		else:
			#list of features
			if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
				list = "data/" + expression_dataset + "/counts/genes_list.tsv"
			else:
				if "lipid" in expression_dataset:
					list = "data/" + expression_dataset + "/counts/lipid_list.tsv"
				else:
					list = "data/" + expression_dataset + "/counts/feature_list.tsv"
			all_features = download_from_github(path, list)
			all_features = pd.read_csv(all_features, sep = "\t", header=None, names=["genes"])
			all_features = all_features["genes"].replace("€", "/").dropna().tolist()

			#upper for case insensitive search
			if expression_dataset not in ["human", "mouse", "lipid"]:
				original_names = {}
				for feature in all_features:
					#setup metatranscriptomics genes
					if "genes" in expression_dataset:
						beast_gene = feature.split("@")[0]
						beast_feature = feature.split("@")[1]
						beast_feature = beast_feature.replace("_", " ")
						meta_gene = beast_gene + " - " + beast_feature.upper()
						original_names[meta_gene] = feature
					else:
						original_names[feature.upper().replace("[", "").replace("]", "")] = feature
				if "genes" in expression_dataset:
					#clean all_features
					clean_all_features = []
					for x in all_features:
						beast_gene = x.split("@")[0]
						beast_feature = x.split("@")[1]
						beast_feature = beast_feature.replace("_", " ")
						meta_gene = beast_gene + " - " + beast_feature
						clean_all_features.append(meta_gene.upper())
					all_features = clean_all_features.copy()
					#clean selected_features
					clean_selected_features = []
					for x in selected_features:
						beast_gene = x.split("@")[0]
						beast_feature = x.split("@")[1]
						beast_feature = beast_feature.replace("_", " ")
						meta_gene = beast_gene + " - " + beast_feature
						clean_all_features.append(meta_gene.upper())
					selected_features = clean_selected_features.copy()
				else:
					all_features = [x.upper().replace("[", "").replace("]", "") for x in all_features]
					selected_features = [x.upper().replace("[", "").replace("]", "") for x in selected_features]
			
			#search genes in text
			if expression_dataset in ["human", "mouse", "lipid"]: 
				features_in_text_area = re.split(r"[\s,;]+", text)
			else:
				features_in_text_area = re.split(r";?[\n]+", text)

			#remove last gene if empty
			if features_in_text_area[-1] == "":
				features_in_text_area = features_in_text_area[0:-1]

			#parse gene
			features_not_found = []
			for feature in features_in_text_area:
				#save what the user wrote to use it in case is not found
				user_feature = feature
				if expression_dataset == "mouse":
					feature = feature.capitalize().replace(" ", "_")
				elif "genes" in expression_dataset:
					feature = feature.upper()
				else:
					feature = feature.upper().replace(" ", "_")
				#gene existing but not in selected: add it to selected
				if feature in all_features:
					if selected_features is None:
						selected_features = [feature]
					elif feature not in selected_features:
						selected_features.append(feature)
				#gene not existing
				elif feature not in all_features:
					if feature not in features_not_found:
						features_not_found.append(user_feature)

			#get the original name to make it match with the dropdown option
			if expression_dataset not in ["human", "mouse", "lipid"]:
				if "genes" in expression_dataset:
					selected_features = [original_names[feature] for feature in selected_features]
				else:
					selected_features = [original_names[feature.upper().replace("[", "").replace("]", "")] for feature in selected_features]

			#log for genes not found
			if len(features_not_found) > 0:
				log_div_string = ", ".join(features_not_found)
				log_div = [html.Br(), "Can not find:", html.Br(), log_div_string]
				log_hidden_status = False
			#hide div if all genes has been found
			else:
				log_div = []
				log_hidden_status = True

	return selected_features, log_div, log_hidden_status, text
