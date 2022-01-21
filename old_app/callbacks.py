#import packages
import dash
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from dash_table.Format import Format, Scheme
import re
import pandas as pd
import numpy as np
import urllib.parse
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
from functools import reduce
from sklearn.preprocessing import scale
from layout import label_to_value, tissues
import functions
from functions import na_color, colors, gender_colors, na_color, config

def define_callbacks(app):

	##### elements ######
	
	#placeholder for heatmap_text_area
	@app.callback(
		Output("heatmap_text_area", "placeholder"),
		Input("expression_dataset_dropdown", "value")
	)
	def get_placeholder_heatmap_text_area(expression_dataset):
		if expression_dataset in ["human", "mouse"]:
			placeholder = "Paste list (plot allowed for max 10 features)"
		else:
			placeholder = "Paste list (plot allowed for max 10 features, one per line)"

		return placeholder

	#expression/abundance profiling label
	@app.callback(
		Output("expression_abundance_profiling", "label"),
		Input("expression_dataset_dropdown", "value")
	)
	def label_expression_abundance_profiling_tab(expression_dataset):
		if expression_dataset in ["human", "mouse"]:
			label = "Gene expression profiling"
		else:
			label = expression_dataset.replace("_", " ").capitalize() + " abundance profiling"
		
		return label

	#dge tooltip
	@app.callback(
		Output("dge_table_tooltip", "children"),
		Input("target_prioritization_switch", "value")
	)
	def define_dge_table_tooltip(target_prioritization_switch):
		#transform switches to booleans switches
		boolean_target_prioritization_switch = functions.boolean_switch(target_prioritization_switch)
		
		if boolean_target_prioritization_switch:
			children = dcc.Markdown("""
				Table showing the differential gene expression between the two conditions upon target prioritization, unless filtered otherwise.
				Targets were prioritized by: 1) being overexpressed, 2) harboring genetic variations associated with IBD, and 3) having FDA-approved drugs targeting them, with or without recommendations.

				Click on a gene to highlight the feature in the MA plot.
			""")
		else:
			children = dcc.Markdown("""
				Table showing the differential gene/species/family/order expression/abundance between the two conditions, unless filtered otherwise.

				Click on headers to reorder the table.

				Click on a gene/species/family/order to highlight the feature in the MA plot.
				Click on an icon in the last column to open external resources.
			""")
		return children

	#search genes for heatmap
	@app.callback(
		Output("gene_species_heatmap_dropdown", "value"),
		Output("genes_not_found_heatmap_div", "children"),
		Output("genes_not_found_heatmap_div", "hidden"),
		Output("heatmap_text_area", "value"),
		Output("update_heatmap_plot_button", "n_clicks"),
		Input("heatmap_search_button", "n_clicks"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_graph", "clickData"),
		State("heatmap_text_area", "value"),
		State("expression_dataset_dropdown", "value"),
		State("gene_species_heatmap_dropdown", "value"),
		State("genes_not_found_heatmap_div", "hidden"),
		State("genes_not_found_heatmap_div", "children"),
		State("update_heatmap_plot_button", "n_clicks")
	)
	def serach_genes_in_text_area_heatmap(n_clicks_search, contrast, stringency_info, go_plot_click, text, expression_dataset, already_selected_genes_species, log_hidden_status, log_div, n_clicks_plot):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#click on GO-plot
		if trigger_id == "go_plot_graph.clickData":
			if isinstance(go_plot_click["points"][0]["y"], str):

				#do not add genes to metatranscriptomics elements!
				if expression_dataset not in ["human", "mouse"]:
					raise PreventUpdate

				#read go table
				go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency_info + "/" + contrast + ".merged_go.tsv")
				go_df = pd.read_csv(go_df, sep = "\t")
				
				#create a column with the GO ID that will be used for searching the GO category -> the name can be truncated if too long, the GO ID will always be present
				go_df["go_id"] = go_df["Process~name"].str.split("~", expand=True)[0]
				go_df = go_df.set_index("go_id")
				#search GO ID and get genes
				genes = go_df.loc[go_plot_click["points"][0]["y"].split("~")[0], "Genes"]
				#remove last ;
				genes = genes[:-1]
				#add genes to text area
				if len(text) > 0:
					text += "; "
				text += genes
				#create a list of genes and add them to the multidropdown
				genes = genes.split("; ")
				already_selected_genes_species = already_selected_genes_species + genes
			
			#click on the enrichment legend should not trigger anything
			else:
				raise PreventUpdate

		#reset text area if you change the input dropdowns
		elif trigger_id in ["contrast_dropdown.value", "stringency_dropdown.value"]:
			#reset log div
			log_div = []
			log_hidden_status = True
			
			diffexp_df = functions.download_from_github("data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
			diffexp_df = pd.read_csv(diffexp_df, sep = "\t")
			diffexp_df["Gene"] = diffexp_df["Gene"].fillna("NA")
			diffexp_df = diffexp_df[diffexp_df["Gene"] != "NA"]

			#stingency specs
			pvalue_type = stringency_info.split("_")[0]
			pvalue_value = stringency_info.split("_")[1]

			#find DEGs
			diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] > 0), "DEG"] = "Up"
			diffexp_df.loc[(diffexp_df[pvalue_type] <= float(pvalue_value)) & (diffexp_df["log2FoldChange"] < 0), "DEG"] = "Down"

			#get top up 15 DEGs by log2FC
			up_genes = diffexp_df[diffexp_df["DEG"] == "Up"]
			#sort by log2FC
			up_genes = up_genes.sort_values(by=["log2FoldChange"], ascending=False)
			#take top 15
			up_genes = up_genes.head(15)
			#get genes
			up_genes = up_genes["Gene"].tolist()
			#get top down 15 DEGs by log2FC
			down_genes = diffexp_df[diffexp_df["DEG"] == "Down"]
			#sort by log2FC
			down_genes = down_genes.sort_values(by=["log2FoldChange"])
			#take top 15
			down_genes = down_genes.head(15)
			#get genes
			down_genes = down_genes["Gene"].tolist()

			#add genes in text area
			if expression_dataset in ["human", "mouse"]:
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

			#add genes to dropdown
			already_selected_genes_species = up_genes + down_genes
			already_selected_genes_species = [gene_species.replace(" ", "_") for gene_species in already_selected_genes_species]
		
		#button click by the user
		else:
			#text is none, do almost anything
			if text is None or text == "":
				if expression_dataset in ["human", "mouse"]:
					log_div = [html.Br(), "No host genes in the search area!"]
				else:
					element = expression_dataset.replace("_", " ").replace("viruses", "viral").replace("bacteria", "bacterial").replace("archaea", "archaeal").replace("eukaryota", "eukaryotic").replace("order", "orders").replace("family", "families")
					log_div = [html.Br(), "No " + element + " in the search area!"]
				log_hidden_status = False
			else:
				#list of features
				if expression_dataset in ["human", "mouse"]:
					list = "data/" + expression_dataset + "/counts/genes_list.tsv"
				else:
					list = "data/" + expression_dataset + "/counts/feature_list.tsv"
				all_genes = functions.download_from_github(list)
				all_genes = pd.read_csv(all_genes, sep = "\t", header=None, names=["genes"])
				all_genes = all_genes["genes"].dropna().tolist()

				#upper for case insensitive search
				if expression_dataset not in ["human", "mouse"]:
					original_names = {}
					for gene in all_genes:
						original_names[gene.upper()] = gene
					all_genes = [x.upper() for x in all_genes]
					already_selected_genes_species = [x.upper() for x in already_selected_genes_species]
				
				#search genes in text
				if expression_dataset in ["human", "mouse"]: 
					genes_species_in_text_area = re.split(r"[\s,;]+", text)
				else:
					genes_species_in_text_area = re.split(r"[\n]+", text)

				#remove last gene if empty
				if genes_species_in_text_area[-1] == "":
					genes_species_in_text_area = genes_species_in_text_area[0:-1]

				#parse gene
				genes_species_not_found = []
				for gene in genes_species_in_text_area:
					if expression_dataset != "mouse":
						gene = gene.upper().replace(" ", "_")
					else:
						gene = gene.capitalize().replace(" ", "_")
					#gene existing but not in selected: add it to selected
					if gene in all_genes:
						if already_selected_genes_species is None:
							already_selected_genes_species = [gene]
						elif gene not in already_selected_genes_species:
							already_selected_genes_species.append(gene)
					#gene not existing
					elif gene not in all_genes:
						if gene not in genes_species_not_found:
							genes_species_not_found.append(gene)

				if expression_dataset not in ["human", "mouse"]:
					already_selected_genes_species = [original_names[gene.upper()] for gene in already_selected_genes_species]
					genes_species_not_found = [gene.lower().capitalize() for gene in genes_species_not_found]

				#log for genes not found
				if len(genes_species_not_found) > 0:
					log_div_string = ", ".join(genes_species_not_found)
					log_div = [html.Br(), "Can not find:", html.Br(), log_div_string]
					log_hidden_status = False
				#hide div if all genes has been found
				else:
					log_div = []
					log_hidden_status = True

		return already_selected_genes_species, log_div, log_hidden_status, text, n_clicks_plot

	#search genes for multi boxplots
	@app.callback(
		Output("gene_species_multi_boxplots_dropdown", "value"),
		Output("genes_not_found_multi_boxplots_div", "children"),
		Output("genes_not_found_multi_boxplots_div", "hidden"),
		Output("multiboxplot_graph_div", "style"),
		Input("multi_boxplots_search_button", "n_clicks"),
		Input("expression_dataset_dropdown", "value"),
		State("multi_boxplots_text_area", "value"),
		State("gene_species_multi_boxplots_dropdown", "value"),
		State("genes_not_found_multi_boxplots_div", "hidden"),
		prevent_initial_call=True
	)
	def serach_genes_in_text_area_multiboxplots(n_clicks, expression_dataset, text, already_selected_genes_species, log_hidden_status):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == "expression_dataset_dropdown.value":
			already_selected_genes_species = []
			log_div = []
			log_hidden_status = True
		else:
			#text is none, do almost anything
			if text is None or text == "":
				if expression_dataset in ["human", "mouse"]:
					log_div = [html.Br(), "No host genes in the search area!"]
				else:
					element = expression_dataset.replace("_", " ").replace("viruses", "viral").replace("bacteria", "bacterial").replace("archaea", "archaeal").replace("eukaryota", "eukaryotic").replace("order", "orders").replace("family", "families")
					log_div = [html.Br(), "No " + element + " in the search area!"]
				log_hidden_status = False
			else:
				genes_species_not_found = []

				#get all genes
				if expression_dataset in ["human", "mouse"]:
					list = "data/" + expression_dataset + "/counts/genes_list.tsv"
				else:
					list = "data/" + expression_dataset + "/counts/feature_list.tsv"
				list = functions.download_from_github(list)
				all_genes = pd.read_csv(list, sep = "\t", header=None, names=["genes"])
				all_genes = all_genes["genes"].dropna().tolist()

				#upper for case insensitive search
				if expression_dataset not in ["human", "mouse"]:
					original_names = {}
					for gene in all_genes:
						original_names[gene.upper()] = gene
					all_genes = [x.upper() for x in all_genes]
					already_selected_genes_species = [x.upper() for x in already_selected_genes_species]
				
				#search genes in text
				if expression_dataset in ["human", "mouse"]: 
					genes_species_in_text_area = re.split(r"[\s,;]+", text)
				else:
					genes_species_in_text_area = re.split(r"[\n]+", text)

				#remove last gene if empty
				if genes_species_in_text_area[-1] == "":
					genes_species_in_text_area = genes_species_in_text_area[0:-1]

				#parse gene
				for gene in genes_species_in_text_area:
					if expression_dataset != "mouse":
						gene = gene.upper().replace(" ", "_")
					else:
						gene = gene.capitalize().replace(" ", "_")
					#gene existing but not in selected: add it to selected
					if gene in all_genes:
						if already_selected_genes_species is None:
							already_selected_genes_species = [gene]
						elif gene not in already_selected_genes_species:
							already_selected_genes_species.append(gene)
					#gene not existing
					elif gene not in all_genes:
						if gene not in genes_species_not_found:
							genes_species_not_found.append(gene)

				if expression_dataset not in ["human", "mouse"]:
					already_selected_genes_species = [original_names[gene.upper()] for gene in already_selected_genes_species]
					genes_species_not_found = [gene.lower().capitalize() for gene in genes_species_not_found]

				#log for genes not found
				if len(genes_species_not_found) > 0:
					log_div_string = ", ".join(genes_species_not_found)
					log_div = [html.Br(), "Can not find:", html.Br(), log_div_string]
					log_hidden_status = False
				#hide div if all genes has been found
				else:
					log_div = []
					log_hidden_status = True

		div_style = {"height": 600 + 25*(len(already_selected_genes_species)/3), "width": "75%", "display": "inline-block"}

		return already_selected_genes_species, log_div, log_hidden_status, div_style

	##### dropdowns #####

	#gene_species dropdown
	@app.callback(
		Output("gene_species_dropdown", "value"),
		Output("gene_species_dropdown", "options"),
		Output("gene_species_label", "children"),
		Output("gene_species_heatmap_dropdown", "options"),
		Output("gene_species_multi_boxplots_dropdown", "options"),
		Output("gene_species_multi_boxplots_dropdown", "placeholder"),
		Input("expression_dataset_dropdown", "value"),
		Input("ma_plot_graph", "clickData"),
		Input("dge_table", "active_cell"),
		Input("dge_table_filtered", "active_cell"),
		State("gene_species_dropdown", "options")
	)
	def get_gene_species(expression_dataset, selected_point_ma_plot, active_cell_full, active_cell_filtered, current_dropdown_options):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#dataset specific variables
		if expression_dataset in ["human", "mouse"]:
			list = "data/" + expression_dataset + "/counts/genes_list.tsv"
			placeholder = "Type here to search host genes"
			label = "Host gene"
		else:
			list = "data/" + expression_dataset + "/counts/feature_list.tsv"
			placeholder = "Type here to search {}".format(expression_dataset.replace("_", " ").replace("order", "orders").replace("family", "families"))
			label = expression_dataset.capitalize().replace("_", " by ")

		#if you click a gene, update only the dropdown value and keep the rest as it is
		if trigger_id == "ma_plot_graph.clickData":
			selected_element = selected_point_ma_plot["points"][0]["customdata"][0].replace(" ", "_")
			if selected_element == "NA":
				raise PreventUpdate
			else:
				value = selected_element
				options = current_dropdown_options

		#active cell in dge_table
		elif trigger_id in ["dge_table.active_cell", "dge_table_filtered.active_cell"]:
			#find out which active table to use
			if trigger_id == "dge_table.active_cell":
				active_cell = active_cell_full
			else:
				active_cell = active_cell_filtered
			#prevent update for click on wrong column or empty gene
			if active_cell["column_id"] != "Gene" or active_cell["column_id"] == "Gene" and active_cell["row_id"] == "":
				raise PreventUpdate
			#return values
			else:
				value = active_cell["row_id"]
				options = current_dropdown_options
		else:
			#load and open input file			
			list = functions.download_from_github(list)
			list = pd.read_csv(list, sep = "\t", header=None, names=["gene_species"])
			list = list["gene_species"].tolist()
			#parse file and get options and value
			options = []
			for object in list:
				options.append({"label": object.replace("_", " ").replace("[", "").replace("]", ""), "value": object})
			if expression_dataset not in ["human", "mouse"]:
				value = options[0]["value"]
				label = expression_dataset.capitalize().replace("_", " by ")
			else:
				if expression_dataset == "human":
					value = "GAPDH"
				elif expression_dataset == "mouse":
					value = "Gapdh"
				label = "Host gene"

		#populate children
		children = [
			label, 	
			dcc.Dropdown(
				id="gene_species_dropdown",
				clearable=False,
				value=value,
				options=options
			)
		]

		return value, options, children, options, options, placeholder

	#dge tagle genes multidropdown
	@app.callback(
		Output("multi_gene_dge_table_selection_dropdown", "options"),
		Output("multi_gene_dge_table_selection_dropdown", "placeholder"),
		Output("multi_gene_dge_table_selection_dropdown", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("target_prioritization_switch", "value"),
		State("multi_gene_dge_table_selection_dropdown", "value")
	)
	def get_dge_table_multidropdown_options(dataset, fdr, contrast, target_prioritization_switch, old_selected_genes):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		boolean_target_prioritization_switch = functions.boolean_switch(target_prioritization_switch)

		value = []
		if trigger_id == "expression_dataset_dropdown.value":
			if dataset == "human":
				genes = functions.download_from_github("manual/genes_list.tsv")
				genes = pd.read_csv(genes, sep = "\t", header=None, names=["genes"])
				genes = genes["genes"].dropna().tolist()
				options = [{"label": i, "value": i} for i in genes]
			else:
				species = functions.download_from_github("manual/{}_list.tsv".format(dataset))
				species = pd.read_csv(species, sep = "\t", header=None, names=["species"])
				species = species["species"].dropna().tolist()
				options = [{"label": i.replace("_", " ").replace("[", "").replace("]", ""), "value": i} for i in species]
		
		elif trigger_id in ["target_prioritization_switch.on", "stringency_dropdown.value", "contrast_dropdown.value"]:
			if boolean_target_prioritization_switch:
				genes = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
				genes = pd.read_csv(genes, sep = "\t")
				genes = genes[genes["padj"] < fdr]
				genes = genes["Gene"].dropna().tolist()
				options = [{"label": i.replace("_", " ").replace("[", "").replace("]", ""), "value": i} for i in genes]
				if old_selected_genes is not None:
					for gene in old_selected_genes:
						if gene in genes:
							value.append(gene)
			else:
				genes = functions.download_from_github("manual/genes_list.tsv")
				genes = pd.read_csv(genes, sep = "\t", header=None, names=["genes"])
				genes = genes["genes"].dropna().tolist()
				options = [{"label": i, "value": i} for i in genes]
				value = old_selected_genes

		if dataset == "human":
			placeholder_multidropdown_dge_table = "Type here to search host genes"
		else:
			placeholder_multidropdown_dge_table = "Type here to search {}".format(dataset.replace("_", " ").replace("order", "orders").replace("family", "families"))

		return options, placeholder_multidropdown_dge_table, value

	#comparison filter callback
	@app.callback(
		Output("comparison_filter_dropdown", "options"),
		Output("comparison_filter_dropdown", "value"),
		Input("expression_dataset_dropdown", "value")
	)
	def get_comparison_filter_options(dataset):
		
		diffexp_contrasts = functions.get_content_from_github("data/{dataset}/dge".format(dataset=dataset))
		diffexp_contrasts = [contrast.split(".")[0] for contrast in diffexp_contrasts]
		
		#get all tissues and groups for dataset
		metadata = functions.download_from_github("metadata.tsv")
		metadata = pd.read_csv(metadata, sep = "\t")
		if dataset != "human":
			metadata = metadata.dropna(subset=["kraken2"])
		tissues = metadata["tissue"].unique().tolist()
		groups = metadata["group"].unique().tolist()

		#loop over tissues and contrasts
		filtered_tissues = []
		filtered_groups = []
		for contrast in diffexp_contrasts:
			#define the two tiessues in the contrast
			re_result = re.search(r"(\w+)_(\w+)-vs-(\w+)_(\w+)", contrast)
			tissue_1 = re_result.group(1)
			tissue_2 = re_result.group(3)
			group_1 = re_result.group(2)
			group_2 = re_result.group(4)
			for tissue in tissues:
				#check if they are the same
				if tissue == tissue_1 and tissue == tissue_2:
					if tissue not in filtered_tissues:
						filtered_tissues.append(tissue)
			for group in groups:
				if group == group_1 and group == group_2:
					if group not in filtered_groups:
						filtered_groups.append(group)

		#define default value and options
		value = "All comparisons"
		options = [{"label": "All comparisons", "value": "All comparisons"}]
		tissues_options = [{"label": "Tissue: " + i.replace("_", " "), "value": "tissue_" + i} for i in filtered_tissues]
		group_options = [{"label": "Group: " + i, "value": "group_" + i} for i in filtered_groups]
		options.extend(tissues_options)
		options.extend(group_options)

		return options, value

	#contrast callback
	@app.callback(
		Output("contrast_dropdown", "options"),
		Output("contrast_dropdown", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("comparison_filter_dropdown", "value"),
		State("contrast_dropdown", "value")
	)
	def filter_contrasts(dataset, filter_element, contrast):
		#get all contrasts for selected dataset
		metadata = functions.download_from_github("metadata.tsv")
		metadata = pd.read_csv(metadata, sep = "\t")

		#contrasts for dataset
		diffexp_contrasts = functions.get_content_from_github("data/{dataset}/dge".format(dataset=dataset))
		diffexp_contrasts = [contrast.split(".")[0] for contrast in diffexp_contrasts]

		#if all, then remove totally insane constrasts
		filtered_contrasts = []
		if filter_element == "All comparisons":
			for contrast in diffexp_contrasts:
				#define the two items to comapre in the contrast
				re_result = re.search(r"(\w+)_(\w+)-vs-(\w+)_(\w+)", contrast)
				tissue_1 = re_result.group(1)
				tissue_2 = re_result.group(3)
				group_1 = re_result.group(2)
				group_2 = re_result.group(4)
				if tissue_1 == tissue_2 or group_1 == group_2:
					filtered_contrasts.append(contrast)
		#filter by same tissue or group
		else:
			if "tissue" in filter_element:
				result_number_1 = 1
				result_number_2 = 3
			elif "group" in filter_element:
				result_number_1 = 2
				result_number_2 = 4

			filter_element = filter_element.replace("tissue_", "").replace("group_", "")
			for contrast in diffexp_contrasts:
				#define the two items to comapre in the contrast
				re_result = re.search(r"(\w+)_(\w+)-vs-(\w+)_(\w+)", contrast)
				result_1 = re_result.group(result_number_1)
				result_2 = re_result.group(result_number_2)
				if filter_element == result_1 and filter_element == result_2:
					filtered_contrasts.append(contrast)

		#define contrast_value
		if filter_element == "All comparisons" and dataset == "human":
			contrast_value = "Esophagus_EoE-vs-Esophagus_Control"
		else:
			if "Esophagus_EoE-vs-Esophagus_Control" in filtered_contrasts:
				contrast_value = "Esophagus_EoE-vs-Esophagus_Control"
			else:
				contrast_value = filtered_contrasts[0]
		contrasts = [{"label": i.replace("_", " ").replace("-", " "), "value": i} for i in filtered_contrasts]

		return contrasts, contrast_value

	#stringecy dropdown
	@app.callback(
		Output("stringency_label", "children"),
		Input("expression_dataset_dropdown", "value")
	)
	def get_stringecy_value(expression_dataset):
		if expression_dataset not in ["human", "mouse"]:
			options = [{"label": "0.05", "value": "pvalue_0.05"}]
			value = "pvalue_0.05"
			label = "P-value"
		else:
			folders = functions.get_content_from_github("data/{}".format(expression_dataset))
			options = []
			#get all dge analyisis performed
			for folder in folders:
				if folder not in ["counts", "dge", "mds", "mofa"]:

					#stringency value
					stringency_value = folder.split("_")[1]
					pvalue_type = folder.split("_")[0]
					if pvalue_type == "padj":
						label = "FDR"
					else:
						label = "P-value"
					
					#populate options
					options.append({"label": stringency_value, "value": folder})
		
			#default value defined in config file
			value = functions.config["stringecy"]

		#populate children
		children = [
			label, 	
			dcc.Dropdown(
				id="stringency_dropdown",
				clearable=False,
				value=value,
				options=options
			)
		]

		return children

	### DOWNLOAD CALLBACKS ###

	#download diffexp
	@app.callback(
		Output("download_diffexp", "href"),
		Output("download_diffexp", "download"),
		Input("download_diffexp_button", "n_clicks"),
		Input("expression_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value")
	)
	def downlaod_diffexp_table(button_click, dataset, contrast):

		#download from GitHub
		df = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		#read the downloaded content and make a pandas dataframe
		df = pd.read_csv(df, sep="\t")
		df = df[["Gene", "Geneid", "log2FoldChange", "lfcSE", "pvalue", "padj", "baseMean"]]

		if dataset not in ["human", "mouse"]:
			df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]

		#define dataset specific variables
		if dataset in ["human", "mouse"]:
			base_mean_label = "Average expression"
		else:
			base_mean_label = "Average abundance"
			gene_column_name = dataset.split("_")[1].capitalize()
			df = df.rename(columns={"Gene": gene_column_name})

		#data carpentry and links
		df = df.rename(columns={"Geneid": "Gene ID", "log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
		df = df.sort_values(by=["FDR"])

		#remove a geneid in non human dge
		if dataset not in ["human", "mouse"]:
			df = df[[gene_column_name, "log2 FC", "log2 FC SE", "P-value", "FDR", base_mean_label]]

		#create a downloadable tsv file forced to excel by extension
		link = df.to_csv(index=False, encoding="utf-8", sep="\t")
		link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
		file_name = "DGE_{}_{}.xls".format(dataset, contrast)

		return link, file_name

	#download partial diffexp
	@app.callback(
		Output("download_diffexp_partial", "href"),
		Output("download_diffexp_partial", "download"),
		Output("download_diffexp_button_partial", "disabled"),
		Input("download_diffexp_button_partial", "n_clicks"),
		Input("expression_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("multi_gene_dge_table_selection_dropdown", "value"),
	)
	def downlaod_diffexp_table_partial(button_click, dataset, contrast, dropdown_values):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		if dropdown_values is None or dropdown_values == [] or trigger_id == "expression_dataset_dropdown.value":
			link = ""
			file_name = ""
			disabled_status = True
		
		else:
			disabled_status = False
			#download from GitHub
			url = "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv"
			#read the downloaded content and make a pandas dataframe
			df = functions.download_from_github(url)
			df = pd.read_csv(df, sep="\t")

			#filter selected genes
			if dataset not in ["human", "mouse"]:
				df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			df = df[df["Gene"].isin(dropdown_values)]

			#define dataset specific variables
			if dataset in ["human", "mouse"]:
				base_mean_label = "Average expression"
			else:
				base_mean_label = "Average abundance"
				gene_column_name = dataset.split("_")[1].capitalize()
				df = df.rename(columns={"Gene": gene_column_name})

			#data carpentry and links
			df = df.rename(columns={"Geneid": "Gene ID", "log2FoldChange": "log2 FC", "lfcSE": "log2 FC SE", "pvalue": "P-value", "padj": "FDR", "baseMean": base_mean_label})
			df = df.sort_values(by=["FDR"])

			#remove a geneid in non human dge
			if dataset not in ["human", "mouse"]:
				df = df[[gene_column_name, "log2 FC", "log2 FC SE", "P-value", "FDR", base_mean_label]]

			#create a downloadable tsv file forced to excel by extension
			link = df.to_csv(index=False, encoding="utf-8", sep="\t")
			link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
			file_name = "DGE_{}_{}_filtered.xls".format(dataset, contrast)

		return link, file_name, disabled_status

	#download go
	@app.callback(
		Output("download_go", "href"),
		Output("download_go", "download"),
		Input("download_go", "n_clicks"),
		Input("stringency_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("expression_dataset_dropdown", "value")
	)
	def download_go_table(button_click, stringency, contrast, expression_dataset):
		if expression_dataset not in ["human", "mouse"]:
			raise PreventUpdate

		#download from GitHub
		df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		df = pd.read_csv(df, sep="\t")

		df = df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		df = df.rename(columns={"Process~name": "GO biological process", "num_of_Genes": "DEGs", "gene_group": "Dataset genes", "percentage%": "Enrichment"})

		link = df.to_csv(index=False, encoding="utf-8", sep="\t")
		link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
		file_name = "GO_human_{}.xls".format(contrast)

		return link, file_name

	#download partial go
	@app.callback(
		Output("download_go_partial", "href"),
		Output("download_go_partial", "download"),
		Output("download_go_button_partial", "disabled"),
		Input("download_go_partial", "n_clicks"),
		Input("contrast_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value")
	)
	def download_partial_go_table(n_clicks, contrast, search_value, expression_dataset, stringency):
		if expression_dataset not in ["human", "mouse"]:
			raise PreventUpdate
		
		#define search query if present
		if search_value is not None and search_value != "":
			go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
			go_df = pd.read_csv(go_df, sep="\t")
			go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			
			processes_to_keep = functions.serach_go(search_value, go_df)

			#filtering
			go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]
			#if there are no categories, disable button
			if go_df.empty:
				disabled_status = True
			else:	
				disabled_status = False

			go_df = go_df.rename(columns={"Process~name": "GO biological process", "num_of_Genes": "DEGs", "gene_group": "Dataset genes", "percentage%": "Enrichment"})

			link = go_df.to_csv(index=False, encoding="utf-8", sep="\t")
			link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(link)
			file_name = "GO_human_{}_shown.xls".format(contrast)
		else:
			link = ""
			file_name = ""
			disabled_status = True

		return link, file_name, disabled_status

	### TABLES ###

	#dge table filtered by multidropdown
	@app.callback(
		Output("dge_table_filtered", "columns"),
		Output("dge_table_filtered", "data"),
		Output("dge_table_filtered", "style_data_conditional"),
		Output("filtered_dge_table_div", "hidden"),
		Input("multi_gene_dge_table_selection_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value")
	)
	def get_filtered_dge_table(dropdown_values, contrast, dataset, fdr):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		if dropdown_values is None or dropdown_values == [] or trigger_id == "expression_dataset_dropdown.value":
			hidden_div = True
			columns = []
			data = [{}]
			style_data_conditional = []
		else:
			hidden_div = False
			#open tsv
			table = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
			table = pd.read_csv(table, sep = "\t")

			#filter selected genes
			if dataset not in ["human", "mouse"]:
				table["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			table = table[table["Gene"].isin(dropdown_values)]

			columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, fdr)

		return columns, data, style_data_conditional, hidden_div

	#dge table full
	@app.callback(
		Output("dge_table", "columns"),
		Output("dge_table", "data"),
		Output("dge_table", "style_data_conditional"),
		Input("contrast_dropdown", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value")
	)
	def display_dge_table(contrast, dataset, strincency):
		#open tsv
		table = functions.download_from_github("data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		table = pd.read_csv(table, sep = "\t")
		
		columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, strincency)

		return columns, data, style_data_conditional

	#go table
	@app.callback(
		Output("go_table", "columns"),
		Output("go_table", "data"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("expression_dataset_dropdown", "value")
	)
	def display_go_table(contrast, stringency, search_value, expression_dataset):
		if expression_dataset not in ["human", "mouse"]:
			raise PreventUpdate
		
		go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]

		#define search query if present
		if search_value is not None and search_value != "":
			processes_to_keep = functions.serach_go(search_value, go_df)
			#filtering
			go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]

		go_df["Process~name"] = ["[{}](".format(process) + str("http://amigo.geneontology.org/amigo/term/") + process.split("~")[0] + ")" for process in go_df["Process~name"]]
		go_df = go_df.rename(columns={"Process~name": "GO biological process", "num_of_Genes": "DEGs", "gene_group": "Dataset genes", "percentage%": "Enrichment"})
		columns = [
			{"name": "DGE", "id":"DGE"}, 
			{"name": "Genes", "id":"Genes"},
			{"name": "GO biological process", "id":"GO biological process", "type": "text", "presentation": "markdown"},
			{"name": "DEGs", "id":"DEGs"},
			{"name": "Dataset genes", "id":"Dataset genes"},
			{"name": "Enrichment", "id":"Enrichment", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)}
			]
		data = go_df.to_dict("records")

		return columns, data

	##### PLOTS #####

	#legend
	@app.callback(
		Output("legend", "figure"),
		Output("legend_div", "hidden"),
		Output("metadata_dropdown", "value"),
		Output("contrast_only_switch", "value"),
		Input("metadata_dropdown", "value"),
		Input("contrast_only_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("update_legend_button", "n_clicks"),
		State("legend", "figure")
	)
	def legend(selected_metadata, contrast_switch, contrast, update_legend, legend_fig):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#transform switch to boolean switch
		boolean_contrast_switch = functions.boolean_switch(contrast_switch)

		#function to create legend_fig from tsv
		def rebuild_legend_fig_from_tsv(selected_metadata):
			#open tsv
			metadata = functions.download_from_github("metadata.tsv")
			metadata = pd.read_csv(metadata, sep = "\t")

			#prepare df
			if str(metadata.dtypes[selected_metadata]) == "object":
				metadata[selected_metadata] = metadata[selected_metadata].fillna("NA")
				metadata[selected_metadata] = [i.replace("_", " ") for i in metadata[selected_metadata]]
			#rename columns
			metadata = metadata.rename(columns=label_to_value)
			metadata = metadata.replace("_", " ", regex=True)
			#mock column for plot
			metadata["mock_column"] = None

			#create figure
			legend_fig = go.Figure()
			#discrete variables
			if str(metadata.dtypes[label_to_value[selected_metadata]]) == "object":
				i = 0
				metadata[selected_metadata] = metadata[label_to_value[selected_metadata]].str.replace("_", " ")
				if selected_metadata == "condition" and config["sorted_conditions"]:
					metadata_fields_ordered = config["condition_list"]
					metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
				else:
					metadata_fields_ordered = metadata[label_to_value[selected_metadata]].unique().tolist()
					metadata_fields_ordered.sort()
				for metadata_field in metadata_fields_ordered:
					marker_color = functions.get_color(metadata_field, i)
					legend_fig.add_trace(go.Scatter(x=metadata["mock_column"], y=metadata["mock_column"], marker_color=marker_color, marker_size=4, mode="markers", legendgroup=metadata_field, showlegend=True, name=metadata_field))
					i += 1
				
				#update layout
				legend_fig.update_layout(legend_title_text=selected_metadata.capitalize().replace("_", " "), legend_orientation="h", legend_itemsizing="constant", legend_tracegroupgap = 0.05, legend_title_side="top", xaxis_visible=False, yaxis_visible=False, margin_t=0, margin_b=340, height=300, legend_font_family="Arial", legend_x = -0.15)
			#continue variables, heatmap as colorbar
			else:
				metadata = metadata.dropna(subset=[label_to_value[selected_metadata]])
				metadata[label_to_value[selected_metadata]] = metadata[label_to_value[selected_metadata]].astype(int)
				z = list(range(metadata[label_to_value[selected_metadata]].min(), metadata[label_to_value[selected_metadata]].max() + 1))
				legend_fig.add_trace(go.Heatmap(z=[z], y=[label_to_value[selected_metadata]], colorscale="blues", hovertemplate="%{z}<extra></extra>", hoverlabel_bgcolor="lightgrey", zsmooth="best"))
				legend_fig.update_traces(showscale=False)
				legend_fig.update_layout(height=300, margin_b=220, margin_t=50, margin_l=150, xaxis_linecolor="#9EA0A2", yaxis_linecolor="#9EA0A2", yaxis_ticks="", xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_mirror=True, yaxis_mirror=True, legend_font_family="Arial")

			#transparent paper background
			legend_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"

			return legend_fig

		#change in metadata always means to update all the legend
		if trigger_id == "metadata_dropdown.value" or legend_fig is None:
			#if contrast only is true and you change metadata then it have to be set as false
			if selected_metadata != "condition" and contrast_switch is True:
				contrast_switch = False
			legend_fig = rebuild_legend_fig_from_tsv(selected_metadata)
			#all traces are visible
			for trace in legend_fig["data"]:
				trace["visible"] = True
		else:
			#false contrast switch
			if boolean_contrast_switch is False:
				#manually switch of will reset the legend to all true
				if trigger_id == "contrast_only_switch.value":
					for trace in legend_fig["data"]:
						trace["visible"] = True
			#true contrast switch
			elif boolean_contrast_switch:
				#find conditions
				condition_1 = contrast.split("-vs-")[0].replace("_", " ")
				condition_2 = contrast.split("-vs-")[1].replace("_", " ")
				if trigger_id in ["contrast_only_switch.value", "contrast_dropdown.value"]:
					#force condition in metadata dropdown
					if selected_metadata != "condition":
						selected_metadata = "condition"
						legend_fig = rebuild_legend_fig_from_tsv(selected_metadata)
					#setup "visible" only for the two conditions in contrast
					for trace in legend_fig["data"]:
						if trace["name"] in [condition_1, condition_2]:
							trace["visible"] = True
						else:
							trace["visible"] = "legendonly"
				#click on update plot
				elif trigger_id == "update_legend_button.n_clicks":
					for trace in legend_fig["data"]:
						if trace["visible"] is True:
							if trace["name"] not in [condition_1, condition_2]:
								contrast_switch = []

		return legend_fig, False, selected_metadata, contrast_switch

	#mds
	@app.callback(
		#figures
		Output("mds_metadata", "figure"),
		Output("mds_expression", "figure"),
		#config
		Output("mds_metadata", "config"),
		Output("mds_expression", "config"),
		#div
		Output("mds_metadata_div", "style"),
		Output("mds_expression_div", "style"),
		#legend_switch
		Output("show_legend_metadata_switch", "value"),
		Output("show_legend_metadata_switch", "options"),
		#dropdowns
		Input("mds_dataset", "value"),
		Input("metadata_dropdown", "value"),
		Input("expression_dataset_dropdown", "value"),
		Input("gene_species_dropdown", "value"),
		#zoom
		Input("mds_metadata", "relayoutData"),
		Input("mds_expression", "relayoutData"),
		#legend switch and update plots
		Input("show_legend_metadata_switch", "value"),
		Input("update_legend_button", "n_clicks"),
		#states
		State("mds_metadata", "figure"),
		State("mds_expression", "figure"),
		State("legend", "figure")
	)
	def plot_mds(mds_dataset, metadata, expression_dataset, gene_species, zoom_metadata, zoom_expression, show_legend_switch, update_plots, mds_metadata_fig, mds_expression_fig, legend_fig):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		mds_type = "umap"
		height = 440

		#transform switches to booleans switches
		boolean_legend_switch = functions.boolean_switch(show_legend_switch)

		#get hover template and get columns to keep for customdata
		metadata_columns = []
		i = 0
		general_hover_template = ""
		for key in label_to_value:
			metadata_columns.append(label_to_value[key])
			general_hover_template += "{key}: %{{customdata[{i}]}}<br>".format(key=label_to_value[key], i=i)
			i += 1

		#function for zoom synchronization
		def synchronize_zoom(mds_to_update, reference_umap):
			mds_to_update["layout"]["xaxis"]["range"] = reference_umap["layout"]["xaxis"]["range"]
			mds_to_update["layout"]["yaxis"]["range"] = reference_umap["layout"]["yaxis"]["range"]
			mds_to_update["layout"]["xaxis"]["autorange"] = reference_umap["layout"]["xaxis"]["autorange"]
			mds_to_update["layout"]["yaxis"]["autorange"] = reference_umap["layout"]["yaxis"]["autorange"]

			return mds_to_update

		#function for creating a discrete colored umap from tsv file
		def plot_mds_discrete(mds_type, mds_dataset, selected_metadata, boolean_legend_switch, mds_discrete_fig):
			#open tsv
			mds_df = functions.download_from_github("data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
			mds_df = pd.read_csv(mds_df, sep = "\t")
			number_of_samples = len(mds_df["sample"].tolist())
			if number_of_samples > 20:
				marker_size = 6
			else:
				marker_size = 8

			#prepare df
			mds_df = mds_df.sort_values(by=[selected_metadata])
			mds_df[selected_metadata] = mds_df[selected_metadata].fillna("NA")
			mds_df = mds_df.rename(columns=label_to_value)
			mds_df = mds_df.replace("_", " ", regex=True)

			#plot
			i = 0
			if config["sorted_conditions"]:
				metadata_fields_ordered = config["condition_list"]
				metadata_fields_ordered = [metadata_field.replace("_", " ") for metadata_field in metadata_fields_ordered]
			else:
				metadata_fields_ordered = mds_df[label_to_value[selected_metadata]].unique().tolist()
				metadata_fields_ordered.sort()

			#hover template for this trace
			hover_template = general_hover_template + "<extra></extra>"

			#define x and y
			if mds_type == "tsne":
				x = "x"
				y = "y"
			elif mds_type == "umap":
				x = "UMAP1"
				y = "UMAP2"

			#add traces
			print(metadata_fields_ordered)
			for metadata in metadata_fields_ordered:
				filtered_mds_df = mds_df[mds_df[label_to_value[selected_metadata]] == metadata]
				filtered_mds_df = filtered_mds_df.round(2)
				custom_data = filtered_mds_df[metadata_columns].fillna("NA")
				marker_color = functions.get_color(metadata, i)
				mds_discrete_fig.add_trace(go.Scatter(x=filtered_mds_df[x], y=filtered_mds_df[y], marker_opacity = 1, marker_color = marker_color, marker_size = marker_size, customdata = custom_data, mode="markers", legendgroup = metadata, showlegend = boolean_legend_switch, hovertemplate = hover_template, name=metadata))
				i += 1

			#update layout
			mds_discrete_fig.update_layout(height = height, xaxis_title_text = x, yaxis_title_text = y, title_xref="paper", title_xanchor="center", title_x=0.5, title_y=0.95,title_font_size=14, legend_title_text=selected_metadata.capitalize().replace("_", " "), legend_orientation="v", legend_xanchor="left", legend_x=-1, legend_yanchor="top", legend_y=1.2, legend_itemsizing="constant", legend_tracegroupgap = 0.05, legend_title_side="top", legend_itemclick=False, legend_itemdoubleclick=False, legend_font_size=12, xaxis_automargin=True, yaxis_automargin=True, font_family="Arial", margin=dict(t=70, b=0, l=10, r=10))
			
			#mds_discrete_fig["layout"]["paper_bgcolor"]="LightSteelBlue"

			return mds_discrete_fig

		#function for creating a continuous colored umap from tsv file
		def plot_mds_continuous(mds_type, mds_dataset, expression_dataset, gene_species, samples_to_keep, selected_metadata, colorscale, mds_category, mds_continuous_fig):	
			#get umap df
			mds_df = functions.download_from_github("data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
			mds_df = pd.read_csv(mds_df, sep = "\t")
			number_of_samples = len(mds_df["sample"].tolist())
			if number_of_samples > 20:
				marker_size = 6
			else:
				marker_size = 8
			mds_df = mds_df.rename(columns=label_to_value)
			mds_df = mds_df.replace("_", " ", regex=True)

			#expression continuous umap will have counts
			if mds_category == "expression":
				continuous_variable_to_plot = "Log2 expression"

				#download counts
				counts = functions.download_from_github("data/" + expression_dataset + "/counts/" + gene_species + ".tsv")
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
				if expression_dataset in ["human", "mouse"]:
					expression_or_abundance = " expression"
				else:
					expression_or_abundance = " abundance"
				#plot parameters
				colorbar_title = "Log2 {}".format(expression_or_abundance)
				hover_template = general_hover_template + "Log2{expression_or_abundance}: %{{marker.color}}<br><extra></extra>".format(expression_or_abundance=expression_or_abundance)
			#metadata continuous umap will use the metadata without counts
			elif mds_category == "metadata":
				continuous_variable_to_plot = label_to_value[selected_metadata]
				colorbar_title = label_to_value[selected_metadata]
				hover_template = general_hover_template + "<extra></extra>"
			
			#fill nan with NA
			mds_df = mds_df.fillna("NA")
			mds_df = mds_df.round(2)
			
			#define x and y
			if mds_type == "tsne":
				x = "x"
				y = "y"
			elif mds_type == "umap":
				x = "UMAP1"
				y = "UMAP2"

			#select only NA values
			na_df = mds_df.loc[mds_df[continuous_variable_to_plot] == "NA"]
			custom_data = na_df[metadata_columns]
			#add discrete trace for NA values
			mds_continuous_fig.add_trace(go.Scatter(x=na_df[x], y=na_df[y], marker_color=na_color, marker_size=marker_size, customdata=custom_data, mode="markers", showlegend=False, hovertemplate=hover_template, name=metadata, visible=True))
			#select only not NA
			mds_df = mds_df.loc[mds_df[continuous_variable_to_plot] != "NA"]
			custom_data = mds_df[metadata_columns]
			marker_color = mds_df[continuous_variable_to_plot]
			#add continuous trace
			mds_continuous_fig.add_trace(go.Scatter(x=mds_df[x], y=mds_df[y], marker_color=marker_color, marker_colorscale=colorscale, marker_showscale=True, marker_opacity=1, marker_size=marker_size, marker_colorbar_title=colorbar_title, marker_colorbar_title_side="right", marker_colorbar_title_font_size=14, marker_colorbar_thicknessmode="pixels", marker_colorbar_thickness=15, marker_colorbar_tickfont={"family": "Arial", "size": 14}, mode="markers", customdata=custom_data, hovertemplate=hover_template, showlegend=False, visible=True))
			
			#update layout
			mds_continuous_fig.update_layout(height = height, title = {"x": 0.5, "y": 0.95, "font_size": 14, "xref": "paper", "xanchor": "center"}, font_family="Arial", hoverlabel_bgcolor="lightgrey", xaxis_automargin=True, yaxis_automargin=True, margin=dict(t=70, b=0, l=10, r=60), xaxis_title_text=x, yaxis_title_text=y)
			
			#mds_continuous_fig["layout"]["paper_bgcolor"]="#E5F5F9"

			return mds_continuous_fig

		#function to get samples to keep from visibility status in mds_metadata_fig
		def get_samples_to_keep(mds_metadata_fig):
			samples_to_keep = []
			#parse metadata figure data 
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] is True:
					for dot in trace["customdata"]:
						#stores samples to keep after filtering
						samples_to_keep.append(dot[0])
			return samples_to_keep
		
		##### UMAP METADATA #####
		
		#open metadata
		metadata_df = functions.download_from_github("metadata.tsv")
		metadata_df = pd.read_csv(metadata_df, sep = "\t")

		#change dataset or metadata: create a new figure from tsv
		if trigger_id in ["mds_dataset.value", "metadata_dropdown.value"] or mds_metadata_fig is None:
			
			#preserve old zoom
			keep_old_zoom = False
			if mds_metadata_fig is not None:
				xaxis_range = mds_metadata_fig["layout"]["xaxis"]["range"]
				yaxis_range = mds_metadata_fig["layout"]["yaxis"]["range"]
				keep_old_zoom = True
			if trigger_id in ["mds_type.value", "mds_dataset.value", "metadata_dropdown.value"] and mds_metadata_fig is not None:
				keep_old_zoom = False
				mds_metadata_fig["layout"]["xaxis"]["autorange"] = True
				mds_metadata_fig["layout"]["yaxis"]["autorange"] = True

			#create figure from tsv
			mds_metadata_fig = go.Figure()
			if str(metadata_df.dtypes[metadata]) == "object":
				mds_metadata_fig = plot_mds_discrete(mds_type, mds_dataset, metadata, boolean_legend_switch, mds_metadata_fig)
			else:
				samples_to_keep = "all"
				mds_metadata_fig = plot_mds_continuous(mds_type, mds_dataset, expression_dataset, gene_species, samples_to_keep, metadata, "blues", "metadata", mds_metadata_fig)

			#apply legend trace visibility
			for i in range(0, len(legend_fig["data"])):
				if legend_fig["data"][i]["visible"] is True:
					mds_metadata_fig["data"][i]["visible"] = True
				else:
					mds_metadata_fig["data"][i]["visible"] = False

			#apply old zoom if present
			if keep_old_zoom:
				mds_metadata_fig["layout"]["xaxis"]["range"] = xaxis_range
				mds_metadata_fig["layout"]["yaxis"]["range"] = yaxis_range
				mds_metadata_fig["layout"]["xaxis"]["autorange"] = False
				mds_metadata_fig["layout"]["yaxis"]["autorange"] = False
		
		#change umap expression means just to update the zoom
		elif trigger_id == "mds_expression.relayoutData":
			mds_metadata_fig = synchronize_zoom(mds_metadata_fig, mds_expression_fig)

		#get df and change visibility of traces
		elif trigger_id == "update_legend_button.n_clicks":
			for i in range(0, len(legend_fig["data"])):
				mds_metadata_fig["data"][i]["visible"] = legend_fig["data"][i]["visible"]

		##### UMAP EXPRESSION #####
		#change umap dataset, expression dataset or gene/species: create a new figure from tsv
		if trigger_id in ["mds_dataset.value", "expression_dataset_dropdown.value", "gene_species_dropdown.value", "metadata_dropdown.value"] or mds_expression_fig is None:
			#preserve old zoom
			keep_old_zoom = False
			if mds_expression_fig is not None:
				xaxis_range = mds_expression_fig["layout"]["xaxis"]["range"]
				yaxis_range = mds_expression_fig["layout"]["yaxis"]["range"]
				keep_old_zoom = True
			if trigger_id in ["mds_type.value", "mds_dataset.value", "metadata_dropdown.value"]:
				keep_old_zoom = False
				mds_metadata_fig["layout"]["xaxis"]["autorange"] = True
				mds_metadata_fig["layout"]["yaxis"]["autorange"] = True

			samples_to_keep = get_samples_to_keep(mds_metadata_fig)
			#create figure
			mds_expression_fig = go.Figure()
			mds_expression_fig = plot_mds_continuous(mds_type, mds_dataset, expression_dataset, gene_species, samples_to_keep, metadata, "reds", "expression", mds_expression_fig)

			#apply old zoom if present
			if keep_old_zoom:
				mds_expression_fig["layout"]["xaxis"]["range"] = xaxis_range
				mds_expression_fig["layout"]["yaxis"]["range"] = yaxis_range
				mds_expression_fig["layout"]["xaxis"]["autorange"] = False
				mds_expression_fig["layout"]["yaxis"]["autorange"] = False

		#update plot from legend change
		elif trigger_id == "update_legend_button.n_clicks":
			#select samples to filter
			samples_to_keep = get_samples_to_keep(mds_metadata_fig)
			#get new filtered mds_expression_fig
			mds_expression_fig = go.Figure()
			mds_expression_fig = plot_mds_continuous(mds_type, mds_dataset, expression_dataset, gene_species, samples_to_keep, metadata, "reds", "expression", mds_expression_fig)
			#in this case, msd_expression will be the reference zoom
			mds_metadata_fig = synchronize_zoom(mds_metadata_fig, mds_expression_fig)
 
		#changes in umap metadata zoom and its legend
		elif trigger_id in ["show_legend_metadata_switch.value", "mds_metadata.relayoutData"]:
			
			#show legend switch has changed
			if trigger_id == "show_legend_metadata_switch.value":
				#show legend with only selected elements in the legend fig
				if boolean_legend_switch is True:
					for i in range(0, len(legend_fig["data"])):
						mds_metadata_fig["data"][i]["showlegend"] = True
				#hide legend
				elif boolean_legend_switch is False:
					for i in range(0, len(legend_fig["data"])):
						mds_metadata_fig["data"][i]["showlegend"] = False

			#update zoom from metadata
			mds_expression_fig = synchronize_zoom(mds_expression_fig, mds_metadata_fig)
			
		##### NUMBER OF DISPLAYED SAMPLES #####
		def get_displayed_samples(figure_data):
			x_range = figure_data["layout"]["xaxis"]["range"]
			y_range = figure_data["layout"]["yaxis"]["range"]
			
			#start of the app: give an artificial big range for axes
			if x_range is None or y_range is None:
				x_range = [-1000000000000000, 1000000000000000]
				y_range = [-1000000000000000, 1000000000000000]
			
			n_samples = 0
			#parse only visible traces
			for trace in figure_data["data"]:
				if trace["visible"] is True:
					#check all points
					for i in range(0, len(trace["x"])):
						x = trace["x"][i]
						y = trace["y"][i]
						if x != "NA" and y != "NA":
							if x > x_range[0] and x < x_range[1] and y > y_range[0] and y < y_range[1]:
								n_samples += 1

			return n_samples

		n_samples_mds_metadata = get_displayed_samples(mds_metadata_fig)
		n_samples_mds_expression = get_displayed_samples(mds_expression_fig)

		#labels for graph title
		if expression_dataset in ["human", "mouse"]:
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"
		if mds_dataset in ["human", "mouse"]:
			transcriptome_title = mds_dataset
		elif "archaea" in mds_dataset:
			transcriptome_title = "archaeal " + mds_dataset.split("_")[1]
		elif "bacteria" in mds_dataset:
			transcriptome_title = "bacterial " + mds_dataset.split("_")[1]
		elif "eukaryota" in mds_dataset:
			transcriptome_title = "eukaryota " + mds_dataset.split("_")[1]
		elif "viruses" in mds_dataset:
			transcriptome_title = "viral " + mds_dataset.split("_")[1]

		#apply title
		mds_metadata_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + transcriptome_title + " transcriptome MDS<br>colored by " + metadata.replace("_", " ") + " metadata n=" + str(n_samples_mds_metadata)
		mds_expression_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + transcriptome_title + " transcriptome MDS<br>colored by " + gene_species.replace("_", " ").replace("[", "").replace("]", "") + expression_or_abundance + " n=" + str(n_samples_mds_expression)

		##### CONFIG OPTIONS ####
		config_mds_metadata = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}}
		config_mds_expression = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}}

		config_mds_metadata["toImageButtonOptions"]["filename"] = "mds_{mds_metadata}_colored_by_{metadata}".format(mds_metadata = mds_dataset, metadata = metadata)
		config_mds_expression["toImageButtonOptions"]["filename"] = "mds_{mds_metadata}_colored_by_{gene_species}_{expression_abundance}".format(mds_metadata = mds_dataset, gene_species = gene_species, expression_abundance = "expression" if expression_dataset in ["human", "mouse"] else "abundance")

		##### DIV STYLES #####
		#discrete metadata can have the legend
		if str(metadata_df.dtypes[metadata]) == "object":
			legend_switch_disabled = [{"label": "", "value": 1, "disabled": False}]
			#if the legend is shown, add space on the left by reducing the spacer
			if boolean_legend_switch:
				legend_switch = [1]
				mds_metadata_div_style = {"width": "54.5%", "display": "inline-block"}
				mds_expression_div_style = {"width": "38%", "display": "inline-block"}
			#no legend, discrete umap
			else:
				legend_switch = []
				mds_metadata_div_style = {"width": "31.5%", "display": "inline-block"}
				mds_expression_div_style = {"width": "37.5%", "display": "inline-block"}
		#continuous metadata need space for the colorbar and will not have the legend
		else:
			legend_switch = []
			legend_switch_disabled = [{"label": "", "value": 1, "disabled": True}]
			mds_metadata_div_style = {"width": "32%", "display": "inline-block"}
			mds_expression_div_style = {"width": "34%", "display": "inline-block"}

		return mds_metadata_fig, mds_expression_fig, config_mds_metadata, config_mds_expression, mds_metadata_div_style, mds_expression_div_style, legend_switch, legend_switch_disabled

	#boxplots
	@app.callback(
		Output("boxplots_graph", "figure"),
		Output("boxplots_graph", "config"),
		Input("expression_dataset_dropdown", "value"),
		Input("gene_species_dropdown", "value"),
		Input("update_legend_button", "n_clicks"),
		Input("x_boxplot_dropdown", "value"),
		Input("group_by_boxplot_dropdown", "value"),
		Input("y_boxplot_dropdown", "value"),
		State("legend", "figure"),
		State("boxplots_graph", "figure")
	)
	def plot_boxplots(expression_dataset, gene_species, update_plots, x, group_by, y, legend_fig, box_fig):

		#labels
		if expression_dataset not in ["human", "mouse"]:
			expression_or_abundance = "abundance"
		else:
			expression_or_abundance = "expression"
		
		#general config for boxplots
		config_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}}

		#open metadata
		metadata_df = functions.download_from_github("metadata.tsv")
		metadata_df = pd.read_csv(metadata_df, sep = "\t")
		
		#add counts
		if y == "log2_expression":
			counts = functions.download_from_github("data/" + expression_dataset + "/counts/" + gene_species + ".tsv")
			counts = pd.read_csv(counts, sep = "\t")
			#merge and compute log2 and replace inf with 0
			metadata_df = metadata_df.merge(counts, how="left", on="sample")
			metadata_df["Log2 counts"] = np.log2(metadata_df["counts"])
			metadata_df["Log2 counts"].replace(to_replace = -np.inf, value = 0, inplace=True)
		
		#clean df
		metadata_df[x] = metadata_df[x].fillna("NA")
		metadata_df = metadata_df.replace("_", " ", regex=True)

		#create figure
		box_fig = go.Figure()
		i = 0
		if x == "condition" and config["sorted_conditions"]:
			metadata_fields_ordered = config["condition_list"]
			metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
		else:	
			metadata_fields_ordered = metadata_df[x].unique().tolist()
			metadata_fields_ordered.sort()
		
		for metadata in metadata_fields_ordered:
			filtered_metadata = metadata_df[metadata_df[x] == metadata]
			#do not plot values for NA
			if metadata == "NA":
				y_values = None
				x_values = None
			else:
				y_values = filtered_metadata["Log2 counts"]
				x_values = filtered_metadata[x]
			
			#label to value with counts in it
			label_to_value_plus_counts = label_to_value.copy()
			if expression_dataset in ["human", "mouse"]:
				label_to_value_plus_counts["Log2 counts"] = "Log2 expression"
			else:
				label_to_value_plus_counts["Log2 counts"] = "Log2 abundance"
			#get all additional metadata
			additional_metadata = []
			for label in label_to_value_plus_counts:
				if label not in ["sample", "condition", "Log2 counts"]:
					additional_metadata.append(label)
			#reorder columns
			filtered_metadata = filtered_metadata[["sample", "condition", "Log2 counts"] + additional_metadata]
			#only 2 decimals
			filtered_metadata = filtered_metadata.round(2)
			#create hovertext
			filtered_metadata["hovertext"] = ""
			for column in filtered_metadata.columns:
				if column in label_to_value_plus_counts:
					filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + label_to_value_plus_counts[column] + ": " + filtered_metadata[column].astype(str) + "<br>"
			hovertext = filtered_metadata["hovertext"].tolist()

			marker_color = functions.get_color(metadata, i)
			box_fig.add_trace(go.Box(y=y_values, x=x_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", marker_size=2, line_width=4))
			i += 1
		box_fig.update_traces(showlegend=False)
		if expression_or_abundance == "expression":
			title_text = gene_species.replace("_", " ").replace("[", "").replace("]", "") + " {}<br>profile per ".format(expression_or_abundance) + x.replace("_", " ").capitalize()
			top_margin = 45
			height = 400
		else:
			title_text = gene_species.replace("_", " ").replace("[", "").replace("]", "") + "<br>{} profile<br>per ".format(expression_or_abundance) + x.replace("_", " ").capitalize()
			top_margin = 60
			#15
			height = 415
		box_fig.update_layout(title = {"text": title_text, "x": 0.55, "font_size": 14, "y": 0.97}, legend_title_text = None, yaxis_title = "Log2 {}".format(expression_or_abundance), xaxis_automargin=True, xaxis_tickangle=-90, yaxis_automargin=True, font_family="Arial", height=height, margin=dict(t=top_margin, b=120, l=5, r=10))

		#define visible status
		for trace in box_fig["data"]:
			trace["visible"] = True

		#syncronyze legend status with umap metadata
		if legend_fig is not None:
			for i in range(0, len(legend_fig["data"])):
				box_fig["data"][i]["visible"] = legend_fig["data"][i]["visible"]

		#plot name when saving
		config_boxplots["toImageButtonOptions"]["filename"] = "boxplots_with_{gene_species}_{expression_or_abundance}_colored_by_{metadata}".format(gene_species = gene_species, expression_or_abundance = expression_or_abundance, metadata = x)

		#box_fig["layout"]["paper_bgcolor"] = "#BCBDDC"

		return box_fig, config_boxplots

	#MA-plot
	@app.callback(
		Output("ma_plot_graph", "figure"),
		Output("ma_plot_graph", "config"),
		Input("expression_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("gene_species_dropdown", "value"),
		State("ma_plot_graph", "figure")
	)
	def plot_MA_plot(expression_dataset, contrast, stringecy_info, gene, old_ma_plot_figure):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#stingency specs
		pvalue_type = stringecy_info.split("_")[0]
		pvalue_value = stringecy_info.split("_")[1]

		#labels
		if expression_dataset in ["human", "mouse"]:
			gene_or_species = "Gene"
			expression_or_abundance = "gene expression"
			xaxis_title = "Log2 average expression"
		else:
			xaxis_title = "Log2 average abundance"
			gene_or_species = expression_dataset.split("_")[1]
			expression_or_abundance = gene_or_species + " abundance"
			gene_or_species = gene_or_species.capitalize()

		#clean gene name
		gene = gene.replace("_", " ").replace("[", "").replace("]", "")

		#read tsv if change in dataset or contrast
		if trigger_id in ["expression_dataset_dropdown.value", "contrast_dropdown.value"] or old_ma_plot_figure is None:
			table = functions.download_from_github("data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
			table = pd.read_csv(table, sep = "\t")
			table["Gene"] = table["Gene"].fillna("NA")
			#log2 base mean
			table["log2_baseMean"] = np.log2(table["baseMean"])
			#clean gene/species name
			table["Gene"] = [i.replace("_", " ").replace("[", "").replace("]", "") for i in table["Gene"]]

		#parse existing figure for change in stringency or gene
		elif trigger_id in ["stringency_dropdown.value", "gene_species_dropdown.value"] and old_ma_plot_figure is not None:
			figure_data = {}
			figure_data["Gene"] = []
			figure_data[pvalue_type] = []
			figure_data["log2_baseMean"] = []
			figure_data["log2FoldChange"] = []

			for trace in range(0, len(old_ma_plot_figure["data"])):
				figure_data["log2_baseMean"].extend(old_ma_plot_figure["data"][trace]["x"])
				figure_data["log2FoldChange"].extend(old_ma_plot_figure["data"][trace]["y"])
				for dot in old_ma_plot_figure["data"][trace]["customdata"]:
					figure_data["Gene"].append(dot[0])
					if dot[1] == "NA":
						dot[1] = np.nan
					figure_data[pvalue_type].append(dot[1])
			
			table = pd.DataFrame(figure_data)

		#find DEGs
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] > 0), "DEG"] = "Up"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] < 0), "DEG"] = "Down"
		table.loc[table["DEG"].isnull(), "DEG"] = "no_DEG"

		#replace nan values with NA
		table = table.fillna(value={pvalue_type: "NA"})

		#count DEGs
		up = table[table["DEG"] == "Up"]
		up = len(up["Gene"])
		down = table[table["DEG"] == "Down"]
		down = len(down["Gene"])

		#find selected gene
		table.loc[table["Gene"] == gene, "DEG"] = "selected_gene"
		table["selected_gene"] = ""
		table.loc[table["Gene"] == gene, "selected_gene"] = gene

		#assign color for the selected gene
		table = table.set_index("Gene")
		selected_gene_log2fc = table.loc[gene, "log2FoldChange"]
		selected_gene_fdr = table.loc[gene, pvalue_type]
		selected_gene_log2_base_mean = table.loc[gene, "log2_baseMean"]
		table = table.reset_index()
		
		#assign color for marker to the selected gene
		if selected_gene_fdr != "NA":
			if selected_gene_fdr <= float(pvalue_value):
				#red
				if selected_gene_log2fc > 0:
					selected_gene_marker_color = "#D7301F"
				#blue
				elif selected_gene_log2fc < 0:
					selected_gene_marker_color = "#045A8D"
			#grey
			elif selected_gene_fdr > float(pvalue_value):
				selected_gene_marker_color = "#636363"
			
			#round it for annotation
			selected_gene_fdr = "{:.1e}".format(selected_gene_fdr)
		#grey
		elif selected_gene_fdr == "NA":
			selected_gene_marker_color = "#636363"

		#colors for discrete sequence
		colors = ["#636363", "#D7301F", "#045A8D", selected_gene_marker_color]
		#rename column if not human
		if expression_dataset not in ["human", "mouse"]:
			table = table.rename(columns={"Gene": gene_or_species})

		#plot
		ma_plot_fig = go.Figure()
		i = 0
		for deg_status in ["no_DEG", "Up", "Down", "selected_gene"]:
			filtered_table = table[table["DEG"] == deg_status]
			custom_data = filtered_table[[gene_or_species, pvalue_type]]
			if pvalue_type == "padj":
				pvalue_type_for_labels = "FDR"
			else:
				pvalue_type_for_labels = "P-value"
			hover_template = gene_or_species + ": %{{customdata[0]}}<br>{pvalue_type}: %{{customdata[1]:.2e}}<br>{expression_or_abundance}: %{{x:.2e}}<br>Log2 fold change: %{{y:.2e}}<extra></extra>".format(expression_or_abundance=xaxis_title, pvalue_type=pvalue_type_for_labels)
			ma_plot_fig.add_trace(go.Scattergl(x=filtered_table["log2_baseMean"], y=filtered_table["log2FoldChange"], marker_opacity = 1, marker_color = colors[i], marker_symbol = 2, marker_size = 5, customdata = custom_data, mode="markers", hovertemplate = hover_template))
			#special marker for selected gene
			if deg_status == "selected_gene":
				ma_plot_fig["data"][i]["marker"] = {"color": "#D9D9D9", "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}
			i += 1

		#update layout
		ma_plot_fig.update_layout(title={"text": "Differential {expression_or_abundance} {pvalue_type} < ".format(expression_or_abundance=expression_or_abundance, pvalue_type=pvalue_type_for_labels) + "{}".format(float(pvalue_value)) + "<br>" + contrast.replace("_", " ").replace("-", " ").replace("Control", "Control"), "xref": "paper", "x": 0.5, "font_size": 14}, xaxis_automargin=True, xaxis_title=xaxis_title, yaxis_automargin=True, yaxis_title="Log2 fold change", font_family="Arial", height=350, margin=dict(t=50, b=0, l=5, r=130), showlegend = False)
		#line at y=0
		ma_plot_fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=0, line=dict(color="black", width=3), xref="paper", layer="below")

		#define annotations
		up_genes_annotation = [dict(text = str(up) + " higher in<br>" + contrast.split("-vs-")[0].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.98, showarrow=False, font=dict(size=14, color="#DE2D26", family="Arial"))]
		down_genes_annotation = [dict(text = str(down) + " higher in<br>" + contrast.split("-vs-")[1].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.02, showarrow=False, font=dict(size=14, color="#045A8D", family="Arial"))]
		annotaton_title = [dict(text = "Show annotations", align="center", xref="paper", yref="paper", x=1.61, y=0.9, showarrow=False, font_size=12)]
		selected_gene_annotation = [dict(x=ma_plot_fig["data"][3]["x"][0], y=ma_plot_fig["data"][3]["y"][0], xref="x", yref="y", text=ma_plot_fig["data"][3]["customdata"][0][0] + "<br>Log2 avg expr: " +  str(round(selected_gene_log2_base_mean, 1)) + "<br>Log2 FC: " +  str(round(selected_gene_log2fc, 1)) + "<br>{pvalue_type}: ".format(pvalue_type=pvalue_type_for_labels) + selected_gene_fdr, showarrow=True, font=dict(family="Arial", size=12, color="#252525"), align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#525252", ax=50, ay=50, bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.9)]

		#add default annotations
		ma_plot_fig["layout"]["annotations"] = annotaton_title + up_genes_annotation + down_genes_annotation + selected_gene_annotation

		#buttons
		ma_plot_fig.update_layout(updatemenus=[dict(
			type="buttons",
			pad=dict(r=5),
			active=0,
			x=1.70,
			y=0.8,
			buttons=list([
				dict(label="All",
					method="update",
					args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5 , "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": "#D9D9D9", "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]},
						{"annotations": annotaton_title + up_genes_annotation + down_genes_annotation + selected_gene_annotation}]
				),
				dict(label="Differential analysis",
					method="update",
					args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": selected_gene_marker_color, "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]},
						{"annotations": annotaton_title + up_genes_annotation + down_genes_annotation}]
				),
				dict(label="Selected {gene_or_species}".format(gene_or_species = gene_or_species),
					method="update",
					args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5 , "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": "#D9D9D9", "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]},
						{"annotations": annotaton_title + selected_gene_annotation}]
				),
				dict(label="None",
					method="update",
					args=[
						{"marker": [{"color": colors[0], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[1], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors[2], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": selected_gene_marker_color, "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]},
						{"annotations": annotaton_title}]
				)
			])
		)])

		config_ma_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}, "plotGlPixelRatio": 5000}
		config_ma_plot["toImageButtonOptions"]["filename"] = "MA-plot_with_{contrast}_stringency_{pvalue_type}_{pvalue}".format(contrast = contrast, pvalue_type = pvalue_type.replace("padj", "FDR"), pvalue = pvalue_value)

		#ma_plot_fig["layout"]["paper_bgcolor"] = "#E0F3DB"
		
		return ma_plot_fig, config_ma_plot
	
	#GO-plot
	@app.callback(
		Output("go_plot_graph", "figure"),
		Output("go_plot_graph", "config"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		State("expression_dataset_dropdown", "value")
	)
	def plot_go_plot(contrast, stringecy, search_value, expression_dataset):
		#check if stringency is in human GO analysis
		human_dirs = functions.get_content_from_github("data/{}".format(expression_dataset))
		if stringecy not in human_dirs:
			raise PreventUpdate

		#get pvalue type and value
		pvalue_type = stringecy.split("_")[0]
		pvalue_type = pvalue_type.replace("padj", "FDR").replace("pvalue", "P-value")
		pvalue_threshold = stringecy.split("_")[1]

		#open df
		go_df = functions.download_from_github("data/{}/".format(expression_dataset) + stringecy + "/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep = "\t")
		hide_go_axis = False
		
		#empty gene ontology
		if go_df.empty:
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
			go_df["Enrichment"] = 1
			go_df_up = go_df
			go_df_down = go_df
			all_enrichments = [33, 66, 99]
			sizeref = 2. * max(all_enrichments)/(5.5 ** 2)
			computed_height = 460
			hide_go_axis = True
		#gene ontology is not empty
		else:
			#filter out useless columns
			go_df = go_df[["DGE", "Process~name", "P-value", "percentage%"]]
			#remove duplicate GO categories for up and down
			#go_df.drop_duplicates(subset ="Process~name", keep = False, inplace = True)

			#define search query if present
			if search_value is not None and search_value != "":
				processes_to_keep = functions.serach_go(search_value, go_df)
				#filtering
				go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]
				if go_df.empty:
					hide_go_axis = True

			#rename columns
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
			#crop too long process name
			processes = []
			for process in go_df["Process"]:
				if len(process) > 80:
					process = process[0:79] + " ..."
				processes.append(process)
			go_df["Process"] = processes

			#divide up and down GO categories
			go_df_up = go_df[go_df["DGE"] == "up"]
			go_df_down = go_df[go_df["DGE"] == "down"]

			#function to select GO categories
			def select_go_categories(df):
				#sort by pvalue
				df = df.sort_values(by=["GO p-value"])
				#take top 15
				df = df.head(15)
				#sort by enrichment
				df = df.sort_values(by=["Enrichment"])

				return df

			#apply function
			go_df_up = select_go_categories(go_df_up)
			go_df_down = select_go_categories(go_df_down)

			#find out max enrichment for this dataset
			all_enrichments = go_df_up["Enrichment"].append(go_df_down["Enrichment"], ignore_index=True)
			if len(all_enrichments) > 0:
				sizeref = 2. * max(all_enrichments)/(5.5 ** 2)
			else:
				sizeref = None

			#compute figure height
			pixels_per_go_category = 20
			computed_height = len(all_enrichments) * pixels_per_go_category

			#min and max height
			if computed_height < 480:
				computed_height = 480
			elif computed_height > 600:
				computed_height = 600

		#create figure
		go_plot_fig = go.Figure()
		#create subplots
		go_plot_fig = make_subplots(rows=7, cols=4, specs=[[{"rowspan": 7}, None, None, None], [None, None, {"rowspan": 2}, None], [None, None, None, None], [None, None, None, None], [None, None, {"rowspan": 2}, None], [None, None, None, None], [None, None, None, None]], column_widths=[0.5, 0.1, 0.3, 0.1], subplot_titles=(None, "GO p-value", "Enrichment"))

		#function for hover text
		def create_hover_text(df):
			hover_text = []
			for index, row in df.iterrows():
				hover_text.append(("DGE: {dge}<br>" + "Process: {process}<br>" + "Enrichment: {enrichment:.2f}<br>" + "GO p-value: {pvalue:.2f}").format(dge=row["DGE"], process=row["Process"], enrichment=row["Enrichment"], pvalue=row["GO p-value"]))

			return hover_text

		#up trace
		hover_text = create_hover_text(go_df_up)
		go_plot_fig.add_trace(go.Scatter(x=go_df_up["DGE"], y=go_df_up["Process"], marker_size=go_df_up["Enrichment"], marker_opacity = 1, marker_color = go_df_up["GO p-value"], marker_colorscale=["#D7301F", "#FCBBA1"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)
		#down trace
		hover_text = create_hover_text(go_df_down)
		go_plot_fig.add_trace(go.Scatter(x=go_df_down["DGE"], y=go_df_down["Process"], marker_size=go_df_down["Enrichment"], marker_opacity = 1, marker_color = go_df_down["GO p-value"], marker_colorscale=["#045A8D", "#C6DBEF"], marker_showscale=False, marker_sizeref = sizeref, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext = hover_text, hoverinfo = "text"), row = 1, col = 1)

		#legend colorbar trace
		go_plot_fig.add_trace(go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color = [0], marker_colorscale=["#737373", "#D9D9D9"], marker_cmax=0.05, marker_cmin=0, marker_colorbar = dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=(computed_height/5), y=0.68, x=0.8, xpad=0, ypad=0, xanchor="center", yanchor="middle")), row = 2, col = 3)

		#size legend trace
		if len(all_enrichments) > 0:
			legend_sizes = [min(all_enrichments), np.average([max(all_enrichments), min(all_enrichments)]), max(all_enrichments)]
			legend_sizes_text = [round(min(all_enrichments)), round(np.average([max(all_enrichments), min(all_enrichments)])), round(max(all_enrichments))]
		else:
			legend_sizes = [11, 22, 33]
			legend_sizes_text = [11, 22, 33]
		go_plot_fig.add_trace(go.Scatter(x = [1, 1, 1], y = [8, 43, 78], marker_size = legend_sizes, marker_sizeref = sizeref, marker_color = "#737373", mode="markers+text", text=["min", "mid", "max"], hoverinfo="text", hovertext=legend_sizes_text, textposition="top center"), row = 5, col = 3)

		#figure layout
		go_plot_fig.update_layout(title={"text": "Gene ontology enrichment plot<br>{host} transcriptome DGE {pvalue_type} < {pvalue_threshold}<br>".format(host=expression_dataset.capitalize(), pvalue_type=pvalue_type, pvalue_threshold=pvalue_threshold) + contrast.replace("_", " ").replace("-", " ").replace("Control", "Control"), "x": 0.75, "xanchor": "center", "font_size": 14}, 
									font_family="Arial",
									height=computed_height,
									showlegend=False,
									autosize=False,
									margin=dict(t=60, b=5, l=410, r=5),
									#titles
									xaxis_title = None, 
									yaxis_title = None, 
									#linecolors
									xaxis_linecolor="rgb(255,255,255)",
									yaxis_linecolor="rgb(255,255,255)",
									#fixed range for enrichment legend
									yaxis3_range=[0, 100],
									#no zoom
									xaxis_fixedrange=True, 
									xaxis2_fixedrange=True, 
									xaxis3_fixedrange=True,
									yaxis_fixedrange=True,
									yaxis2_fixedrange=True, 
									yaxis3_fixedrange=True,
									#hide axis of legends
									xaxis2_visible=False,
									xaxis3_visible=False,
									yaxis2_visible=False, 
									yaxis3_visible=False)

		#legend title dimension and position
		go_plot_fig["layout"]["annotations"][0]["font"]["size"] = 12
		go_plot_fig["layout"]["annotations"][1]["font"]["size"] = 12

		#hide xaxis and yaxis for empty GO
		if hide_go_axis:
			go_plot_fig.update_layout(xaxis_visible=False, yaxis_visible=False)

		#go_plot_fig["layout"]["paper_bgcolor"] = "#FDE0DD"

		config_go_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}, "responsive": True}
		config_go_plot["toImageButtonOptions"]["filename"] = "GO-plot_with_{contrast}".format(contrast = contrast)

		return go_plot_fig, config_go_plot

	#heatmap
	@app.callback(
		Output("heatmap_graph", "figure"),
		Output("heatmap_graph", "config"),
		Output("hetamap_height_input", "value"),
		Output("hetamap_height_input", "max"),
		Output("hetamap_width_input", "value"),
		Output("hetamap_height_input", "disabled"),
		Output("hetamap_width_input", "disabled"),
		Output("heatmap_resize_button", "disabled"),
		Output("comparison_only_heatmap_switch", "value"),
		Input("update_heatmap_plot_button", "n_clicks"),
		Input("clustered_heatmap_switch", "value"),
		Input("comparison_only_heatmap_switch", "value"),
		Input("hide_unselected_heatmap_switch", "value"),
		Input("heatmap_resize_button", "n_clicks"),
		State("gene_species_heatmap_dropdown", "value"),
		State("annotation_dropdown", "value"),
		State("expression_dataset_dropdown", "value"),
		State("heatmap_graph", "figure"),
		State("contrast_dropdown", "value"),
		#resize
		State("hetamap_height_input", "value"),
		State("hetamap_height_input", "max"),
		State("hetamap_width_input", "value"),
		State("hetamap_width_input", "max"),
	)
	def plot_heatmap(n_clicks, clustered_switch, comparison_only_switch, hide_unselected_switch, n_clicks_resize, features, annotations, expression_dataset, old_figure, contrast, height, max_height, width, width_max):
		# jak1 jak2 jak3 stat3 stat4 stat5a stat5b

		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#resize
		if trigger_id == "heatmap_resize_button.n_clicks":
			if height <= max_height and height >= 200 and width <= width_max and width >= 200:
				old_figure["layout"]["height"] = height 
				old_figure["layout"]["width"] = width
				height_fig = height
				width_fig = width
				if expression_dataset in ["human", "mouse"]:
					colorbar_title = "gene expression"
				else:
					colorbar_title = expression_dataset.replace("_", " ") + " abundance"
				if functions.boolean_switch(clustered_switch):
					clustered_or_sorted = ", hierarchically clustered"
				else:
					clustered_or_sorted = ", sorted by condition"
				
				config_filename_title = colorbar_title + " heatmap" + clustered_or_sorted
				fig = old_figure
				disabled = False
			else:
				raise PreventUpdate
		#plot
		else:
			if trigger_id == "update_heatmap_plot_button.n_clicks":
				comparison_only_switch = []
			#transform switch to boolean switch
			boolean_clustering_switch = functions.boolean_switch(clustered_switch)
			boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
			boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)

			#coerce features to list
			if features is None:
				features = []
			#annotations will have always condition by default and these will be at the top of the other annotations
			if annotations == None or annotations == []:
				annotations = ["condition"]
			else:
				annotations.insert(0, "condition")

			#plot only if at least one feature is present
			if len(features) > 1:
				#get counts dfs
				counts_df_list = []
				for feature in features:
					df = functions.download_from_github("data/" + expression_dataset + "/counts/" + feature + ".tsv")
					df = pd.read_csv(df, sep = "\t")
					df = df.rename(columns={"counts": feature})
					df = df[["sample", feature]]
					counts_df_list.append(df)
				
				#merge all counts
				counts = reduce(lambda x, y: pd.merge(x, y, on = "sample"), counts_df_list)
				counts = counts.replace("_", " ", regex=True)
				counts = counts.set_index("sample")
				#log 2 and row scaling
				counts = np.log2(counts)
				counts = counts.replace(to_replace = -np.inf, value = 0)
				counts = pd.DataFrame(scale(counts), index=counts.index, columns=counts.columns)

				#open metadata
				metadata = functions.download_from_github("metadata.tsv")
				metadata = pd.read_csv(metadata, sep="\t")
				metadata = metadata.replace("_", " ", regex=True)
				metadata = metadata.set_index("sample")
				
				#by default all conditions are visible
				legend_data = {}
				if config["sorted_conditions"]:
					sorted_conditions = config["condition_list"]
					conditions = [condition.replace("_", " ") for condition in sorted_conditions]
				else:
					conditions = metadata["condition"].unique().tolist()
					conditions.sort()
				i = 0
				for condition in conditions:
					legend_data[condition] = {}
					legend_data[condition]["visible"] = True
					legend_data[condition]["color"] = colors[i]
					i += 1

				#avoid parsing an empty figure
				if old_figure is not None:
					if len(old_figure["data"]) != 0:
						#find out if some conditions have to be removed
						for trace in old_figure["data"]:
							#find out if there is the legend in the trace
							if "legendgroup" in trace:
								#only comparison conditions are visible
								if boolean_comparison_only_switch:
									contrast = contrast.replace("_", " ")
									if trace["legendgroup"] in contrast.split("-vs-"):
										legend_data[trace["legendgroup"]]["visible"] = True
									else:
										legend_data[trace["legendgroup"]]["visible"] = "legendonly"
								#non contrast-related selection
								else:
									#clicking on the switch to false will turn all traces to true
									if trigger_id == "comparison_only_heatmap_switch.value":
										legend_data[trace["legendgroup"]]["visible"] = True
									#get the previous legend selection
									else:
										legend_data[trace["legendgroup"]]["visible"] = trace["visible"]

						#hide/show unselected
						for trace in legend_data:
							if boolean_hide_unselected_switch:
								if legend_data[trace]["visible"] == "legendonly":
									legend_data[trace]["visible"] = False
							elif not boolean_hide_unselected_switch:
								if legend_data[trace]["visible"] == False:
									legend_data[trace]["visible"] = "legendonly"

						#filter samples according to legend status
						conditions_to_keep = []
						for condition in legend_data:
							#keep only the traces that have showlegend True
							if legend_data[condition]["visible"] is True:
								conditions_to_keep.append(condition)
						#filter metadata and get remaining samples
						metadata_filtered = metadata[metadata["condition"].isin(conditions_to_keep)]
						samples_to_keep = metadata_filtered.index.tolist()
						#filter counts for these samples
						counts = counts[counts.index.isin(samples_to_keep)]
					else:
						metadata_filtered = metadata.copy()
				#create df with features as columns
				feature_df = counts
				#create df with samples as columns
				sample_df = counts.T

				#get a list of features and samples
				features = list(sample_df.index)
				samples = list(sample_df.columns)

				#dendrogram colors and initialize figure
				blacks = ["#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969"]
				fig = go.Figure()

				#the number of yaxis will be the number of annotations + 2 (main heatmap + dendrogram), keep track of the number of annotations
				number_of_annotations = len(annotations)

				#top dendrofram (samples) only if switch is true
				if boolean_clustering_switch:
					dendro_top = ff.create_dendrogram(feature_df, orientation="bottom", labels=samples, colorscale=blacks)
					#set as the last yaxis
					dendro_top.update_traces(yaxis="y" + str(number_of_annotations + 2), showlegend=False)
					
					#save top dendro yaxis
					top_dendro_yaxis = "yaxis" + str(number_of_annotations + 2)
					
					#add top dendrogram traces to figure
					for trace in dendro_top["data"]:
						fig.add_trace(trace)

				#right dengrogram (features)
				dendro_side = ff.create_dendrogram(sample_df.values, orientation='left', labels=features, colorscale=blacks)
				#set as xaxis2
				dendro_side.update_traces(xaxis="x2", showlegend=False)
				#add right dendrogram data to figure
				for data in dendro_side["data"]:
					fig.add_trace(data)

				#add annotations
				y_axis_number = 2
				all_annotations_yaxis = []
				i = 0
				for annotation in annotations:
					
					#if colors are finished, starts form the first after the condition colors
					if i == len(colors):
						i = len(metadata["condition"].unique().tolist())
					
					# for condition annotation reorder conditions and samples
					if annotation == "condition":
						#condition must be the annotation closer to the dendrogram
						current_y_axis_number = number_of_annotations + 1
						
						#save the yaxis for condition annotation
						condition_annotation_yaxis = "yaxis" + str(current_y_axis_number)

						#get elements with clustered order
						clustered_features = dendro_side["layout"]["yaxis"]["ticktext"]
					#any other annotation
					else:
						current_y_axis_number = y_axis_number
						
						#save all additional annotation yaxis in a list
						all_annotations_yaxis.append("yaxis" + str(current_y_axis_number))

					#order conditions by clustered samples
					if boolean_clustering_switch:
						clustered_samples = dendro_top["layout"]["xaxis"]["ticktext"]
						clustered_conditions = []
						for sample in clustered_samples:
							clustered_conditions.append(metadata.loc[sample, annotation])
					#order alphabetically or by numeric value
					else:
						if annotation == "condition" and config["sorted_conditions"]:
							df_slices = []
							for condition in conditions:
								df_slice = metadata_filtered[metadata_filtered["condition"] == condition]
								df_slices.append(df_slice)
							metadata_sorted = pd.concat(df_slices)
						else:
							metadata_sorted = metadata_filtered.sort_values(by=["condition"])
						clustered_samples = metadata_sorted.index.tolist()
						clustered_conditions = metadata_sorted[annotation].tolist()

					#discrete annotation
					if str(metadata.dtypes[annotation]) == "object":
						hovertemplate = "%{customdata}<extra></extra>"
						if annotation == "condition" and config["sorted_conditions"]:
							conditions_for_discrete_color_mapping = conditions
						else:
							conditions_for_discrete_color_mapping = metadata[annotation].unique().tolist()
							conditions_for_discrete_color_mapping.sort()

						#color mapping
						annotation_colors = []
						#link between condition and number for discrete color mapping
						condition_number_mapping = {}
						for condition in conditions_for_discrete_color_mapping:
							#give a number to the condition
							condition_number_mapping[condition] = i
							#map a color to this number
							annotation_colors.append(colors[i])
							#increase incrementals
							i += 1

						#translate clustered conditions in numbers
						z = []
						for condition in clustered_conditions:
							z.append(condition_number_mapping[condition])
						zmin = 0
						zmax = i-1

					#continuous annotation
					else:
						hovertemplate = "%{z}<extra></extra>"
						annotation_colors = ["#FFFFFF", colors[i]]
						i += 1
						z = []
						for sample in clustered_samples:
							z.append(metadata_filtered.loc[sample, annotation])
						zmin = min(z)
						zmax = max(z)

					# create annotation heatmap
					annotation_heatmap = go.Heatmap(z=[z], x=clustered_samples, y=[label_to_value[annotation]], colorscale=annotation_colors, customdata=[clustered_conditions], showscale=False, hovertemplate=hovertemplate, hoverlabel_bgcolor="lightgrey", zmin=zmin, zmax=zmax)
					if boolean_clustering_switch:
						annotation_heatmap["x"] = dendro_top["layout"]["xaxis"]["tickvals"]
					annotation_heatmap["yaxis"] = "y" + str(current_y_axis_number)
					fig.add_trace(annotation_heatmap)

					# increase count only when not condition
					if annotation != "condition":
						y_axis_number += 1
				
				#reorder sample df with clustered items
				heat_data = sample_df
				heat_data = heat_data.reindex(columns=clustered_samples)
				heat_data = heat_data.reindex(index=clustered_features)

				#dataset specific variables
				if expression_dataset in ["human", "mouse"]:
					feature = "Gene"
					colorbar_title = "gene expression"
					space_for_legend = 80
				else:
					feature = expression_dataset.replace("_", " ").capitalize()
					colorbar_title = expression_dataset.replace("_", " ") + " abundance"
					space_for_legend = 200

				#create main heatmap
				heatmap = go.Heatmap(x=clustered_samples, y=clustered_features, z=heat_data, colorscale="Reds", hovertemplate="Sample: %{{x}}<br>{feature}:%{{y}}<extra></extra>".format(feature=feature), hoverlabel_bgcolor="lightgrey", colorbar_title="Row scaled " + colorbar_title, colorbar_title_side="right", colorbar_title_font_family="Arial", colorbar_thicknessmode="pixels", colorbar_thickness=20, colorbar_lenmode="pixels", colorbar_len=100)
				if boolean_clustering_switch:
					heatmap["x"] = dendro_top["layout"]["xaxis"]["tickvals"]
				heatmap["y"] = dendro_side["layout"]["yaxis"]["tickvals"]
				heatmap["yaxis"] = "y"
				fig.add_trace(heatmap)

				##update layout
				if boolean_clustering_switch:
					dendro_top_height = 75
				else:
					dendro_top_height = 0

				#the height and the width will be adaptive to features and samples
				heigth_multiplier = 30
				width_multiplier = 30
				height_fig = heigth_multiplier*len(clustered_features) + heigth_multiplier*number_of_annotations + dendro_top_height + 50
				if height_fig < 245:
					height_fig = 245
				width_fig = width_multiplier*len(clustered_samples) + 75 + space_for_legend

				#max height
				max_height = dendro_top_height + 30*30 + heigth_multiplier*number_of_annotations + 50
				if height_fig > max_height:
					height_fig = max_height
					max_height_flag = True
				else:
					max_height_flag = False
				#max width
				if width_fig > 885:
					width_fig = 885

				### xaxis ###
				dendro_x_left_domain = 0.95 - (75/width_fig)
				#xaxis (x heatmap)
				fig.update_layout(xaxis={"domain": [0, dendro_x_left_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "ticks":""})
				#xaxis2 (x dendrogram side)
				fig.update_layout(xaxis2={"domain": [dendro_x_left_domain, 0.95], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": False, "ticks":""})

				### yaxis ###

				#the last yaxis is the dendrogram
				if boolean_clustering_switch:
					bottom_dendro_domain = 0.95-(dendro_top_height/height_fig)
					fig["layout"][top_dendro_yaxis] = {"domain":[bottom_dendro_domain, 0.95], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": False, "ticks":""}
					top_condition_annotation_domain = bottom_dendro_domain
					bot_condition_annotation_domain = 0.95-((dendro_top_height + heigth_multiplier)/height_fig)
				#the last yaxis is the condition annotation
				else:
					top_condition_annotation_domain = 0.95
					bot_condition_annotation_domain = 0.95-(heigth_multiplier/height_fig)
				#update domain for condition annotation yaxis
				fig["layout"][condition_annotation_yaxis] = {"domain":[bot_condition_annotation_domain, top_condition_annotation_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks":""}

				#additional annotations
				if len(all_annotations_yaxis) > 0:
					additional_annotation_area = heigth_multiplier/height_fig
					#start from the top annotation
					all_annotations_yaxis.reverse()
					#at the beginning use condition annotation domain as starting point
					annotation_top_domain = bot_condition_annotation_domain
					annotation_bot_domain = bot_condition_annotation_domain - additional_annotation_area
					#add additional annotations
					for annotation_yaxis in all_annotations_yaxis:
						fig["layout"][annotation_yaxis] = {"domain":[annotation_bot_domain, annotation_top_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks":""}
						#reassign domain for next yaxis
						annotation_top_domain = annotation_bot_domain
						annotation_bot_domain = annotation_bot_domain - additional_annotation_area
					annotation_bot_domain += additional_annotation_area
				#start heatmap from condition annotation domain
				else:
					annotation_bot_domain = bot_condition_annotation_domain

				#main heatmap yaxis
				fig.update_layout(yaxis={"domain": [0, annotation_bot_domain], "mirror": False, "showgrid": False, "showline": False, "zeroline": False, "showticklabels": True, "ticks": ""})

				#add traces for legend
				for condition in conditions:
					fig.add_trace(go.Scatter(x=[None], y=[None], marker_color=legend_data[condition]["color"], marker_size=8, mode="markers", legendgroup=condition, showlegend=True, name=condition, visible=legend_data[condition]["visible"]))
				
				if max_height_flag:
					fig["layout"]["yaxis"]["showticklabels"] = False
				#add feature labels
				fig["layout"]["yaxis"]["tickvals"] = dendro_side["layout"]["yaxis"]["tickvals"]
				fig["layout"]["yaxis"]["ticktext"] = [clustered_feature.replace("_", " ").replace("[", "").replace("]", "") for clustered_feature in clustered_features]
				#add sample labels and define title
				if boolean_clustering_switch:
					fig["layout"]["xaxis"]["tickvals"] = dendro_top["layout"]["xaxis"]["tickvals"]
					clustered_or_sorted = ", hierarchically clustered"
				else:
					clustered_or_sorted = ", sorted by condition"
				fig["layout"]["xaxis"]["ticktext"] = clustered_samples
				fig["layout"]["xaxis"]["showticklabels"] = False

				#update layout
				fig.update_layout(title_text=colorbar_title.capitalize() + " heatmap" + clustered_or_sorted, title_font_family="arial", title_font_size=14, title_x=0.5, title_y = 0.98, plot_bgcolor="rgba(0,0,0,0)", legend_title="Condition", legend_title_side="top", legend_orientation="h", legend_tracegroupgap=0.05, margin_t=30, margin_b=0, margin_l=0, margin_r=0, legend_x=0, legend_y=0, legend_yanchor="top", legend_xanchor="left", width=width_fig, height=height_fig)
				
				config_filename_title = colorbar_title + " heatmap" + clustered_or_sorted
				disabled = False
				max_height = height_fig + 200
				#fig["layout"]["paper_bgcolor"] = "#FDE0DD"

			else:
				fig = go.Figure()
				fig.add_annotation(text="Please select at least two features to plot the heatmap.", showarrow=False)
				width_fig = 885
				height_fig = 450
				max_height = height_fig
				config_filename_title = "empty_heatmap"
				fig.update_layout(xaxis_linecolor="rgb(255,255,255)", yaxis_linecolor="rgb(255,255,255)", xaxis_showticklabels=False, yaxis_showticklabels=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_ticks="", yaxis_ticks="")
				disabled = True

		config_fig = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": width_fig, "height": height_fig, "scale": 5, "filename": config_filename_title}}

		return fig, config_fig, height_fig, max_height, width_fig, disabled, disabled, disabled, comparison_only_switch

	#heatmap annotation legend
	@app.callback(
		Output("heatmap_legend_div", "children"),
		Output("heatmap_legend_div", "hidden"),
		Input("heatmap_graph", "figure"),
		State("annotation_dropdown", "value")	
	)
	def plot_heatmap_annotation_legend(heatmap_fig, annotations):
		#setup empty children
		children = []

		#no annotations
		if len(annotations) == 0:
			hidden = True
		#any number of annotation
		else:
			hidden = False
			#open metadata
			metadata = functions.download_from_github("metadata.tsv")
			metadata = pd.read_csv(metadata, sep="\t")
			metadata = metadata.replace("_", " ", regex=True)
			#save initial conditions for selecting the right colors
			all_conditions = metadata["condition"].unique().tolist()

			#filter metadata for selected conditions in the heatmap condition legend
			if len(heatmap_fig["data"]) > 0:
				conditions_to_keep = []
				for trace in heatmap_fig["data"]:
					#find out if there is the legend in the trace
					if "legendgroup" in trace:
						if trace["visible"] is True:
							conditions_to_keep.append(trace["legendgroup"])
				#filter
				metadata = metadata[metadata["condition"].isin(conditions_to_keep)]

			#setup subplots
			legends_to_plot = len(annotations)
			rows = int(np.ceil(legends_to_plot/6))
			specs = []
			specs_done = 0
			for row in range(1, rows+1):
				#last row means that some of these plots can be None
				if row == rows:
					number_of_missing_elements = legends_to_plot - specs_done
					last_row = []
					for i in range(1, 7):
						if i <= number_of_missing_elements:
							last_row.append({})
						else:
							last_row.append(None)
					specs.append(last_row)
				#any non-last row will be filled by plots
				else:
					specs.append([{}, {}, {}, {}, {}, {}])
					specs_done += 6
			
			#find out how many categories will have each annotation and use the one with the most categories as a reference
			max_categories = 0
			discrete_annotation_count = 1
			#order names for subplots: first discrete, then continue
			discrete_annotations = []
			continue_annotations = []
			for annotation in annotations:
				if str(metadata.dtypes[annotation]) == "object":
					discrete_annotations.append(annotation)
					categories = metadata[annotation].unique().tolist()
					number_of_categories = len(categories)
					#the continue annotations will be after the discrete, 
					#so count the number of discrete annotations to see where will be the first continue x and y axes
					discrete_annotation_count += 1
				else:
					continue_annotations.append(annotation)
					number_of_categories = 5
				
				#update the number of max categories
				if number_of_categories > max_categories:
					max_categories = number_of_categories

			#make subplot
			fig = make_subplots(rows=rows, cols=6, specs=specs, subplot_titles=discrete_annotations + continue_annotations, shared_yaxes=True, horizontal_spacing=0)

			#setup loop
			i = len(all_conditions)
			discrete_legends = []
			continue_legends = []
			#loop over annotations
			for annotation in annotations:		
				#discrete annotation
				if str(metadata.dtypes[annotation]) == "object":		
					#get unique categories for legend creation
					categories_for_legend = metadata[annotation].unique().tolist()
					categories_for_legend.sort()

					#the starting point depends on the number of categories related to the legend with more categories
					y = 1
					if len(categories_for_legend) < max_categories:
						y += max_categories - len(categories_for_legend)
					#add traces to legend
					discrete_legend = []
					for category in categories_for_legend:
						#colors are finished
						if i == len(colors):
							i = len(all_conditions)
						trace = go.Scatter(x=[1], y=[y], marker_color=colors[i], marker_size=8, mode="markers+text", name=category, text= "   " + category, textposition="middle right", hoverinfo="none")
						discrete_legend.append(trace)
						i += 1
						y += 1
					#transparent trace to move the colored markes on the left of the area
					trace = go.Scatter(x=[3], y=[1, max_categories], marker_color="rgb(255,255,255)", hoverinfo="none")
					discrete_legend.append(trace)
					discrete_legends.append(discrete_legend)
				
				#continuous annotation
				else:
					#colors are finished
					if i == len(colors):
						i = len(all_conditions)
					#get current xaxis and yaxis
					if discrete_annotation_count == 1:
						annotation_xaxis = "xaxis"
						annotation_yaxis = "yaxis"
					else:
						annotation_xaxis = "xaxis" + str(discrete_annotation_count)
						annotation_yaxis = "yaxis" + str(discrete_annotation_count)
					#get coordinates for colorbar in between of domain values
					colorbar_x = np.mean(fig["layout"][annotation_xaxis]["domain"])
					colorbar_y = np.mean(fig["layout"][annotation_yaxis]["domain"])

					continue_legend = []
					trace = go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color=metadata[annotation], marker_colorscale=["#FFFFFF", colors[i]], marker_colorbar=dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=80, x=colorbar_x, y=colorbar_y, xanchor="right"))
					continue_legend.append(trace)
					i += 1

					#add legends to legends list
					continue_legends.append(continue_legend)
					#increase discrete annotation number count
					discrete_annotation_count += 1

			#add discrete legends to plot
			working_col = 1
			working_row = 1
			#loop over legends
			for legend_type in [discrete_legends, continue_legends]:
				for legend in legend_type:
					#loop over traces in legends
					for trace in legend:
						fig.add_trace(trace, row=working_row, col=working_col)
					#update position on the subplot
					working_col += 1
					if working_col == 7:
						working_col = 1
						working_row += 1

			#update axes
			fig.update_xaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_yaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_annotations(font_size=12, xanchor="left")
			#move legend titles to the left so that they line up with markers
			for annotation in fig["layout"]["annotations"]:
				current_x = annotation["x"]
				annotation["x"] = current_x - 0.087
				current_y = annotation["y"]
				annotation["y"] = current_y
			#compute height
			margin_height = 200
			category_height = 20
			subplot_title_height = 30
			row_height = (category_height*max_categories) + subplot_title_height
			height = (row_height*rows) #+ margin_height
			#update layout
			fig.update_layout(width=885, height=height, showlegend=False, margin=dict(t=30, b=10, l=0, r=0, autoexpand=False))

			#add figure to children
			children.append(dcc.Graph(figure=fig, config={"modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "hoverClosestGl2d", "hoverClosestPie", "toggleHover", "sendDataToCloud", "toggleSpikelines", "resetViewMapbox", "hoverClosestCartesian", "hoverCompareCartesian"], "toImageButtonOptions": {"format": "png", "width": 885, "height": height, "scale": 5, "filename": "heatmap_legend_for_" + "_".join(annotations)}}))

			#fig["layout"]["paper_bgcolor"] = "#FDE0DD"
			
		return children, hidden

	#multiboxplots callback
	@app.callback(
		Output("multi_boxplots_graph", "figure"),
		Output("multi_boxplots_graph", "config"),
		Output("multi_boxplots_div", "hidden"),
		Output("popover_plot_multiboxplots", "is_open"),
		Input("update_legend_button", "n_clicks"),
		Input("update_multixoplot_plot_button", "n_clicks"),
		Input("metadata_dropdown", "value"),
		State("gene_species_multi_boxplots_dropdown", "value"),
		State("expression_dataset_dropdown", "value"),
		State("legend", "figure"),
		State("multi_boxplots_graph", "figure"),
		State("multi_boxplots_div", "hidden"),
		prevent_initial_call=True
	)
	def plot_multiboxplots(n_clicks_general, n_clicks_multiboxplots, metadata_field, selected_genes_species, expression_dataset, legend_fig, box_fig, hidden_status):
		# MEN1; CIT; NDC80; AURKA; PPP1R12A; XRCC2; ENSA; AKAP8; BUB1B; TADA3; DCTN3; JTB; RECQL5; YEATS4; CDK11B; RRM1; CDC25B; CLIP1; NUP214; CETN2
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		#default values used when the figure is hidden
		height_fig = 900
		title_text = ""

		#open metadata
		metadata_df_original = functions.download_from_github("metadata.tsv")
		metadata_df_original = pd.read_csv(metadata_df_original, sep = "\t")

		#empty dropdown
		if selected_genes_species is None or selected_genes_species == [] or str(metadata_df_original.dtypes[metadata_field]) != "object":
			hidden_status = True
			popover_status = False
		#filled dropdown
		else:
			#change umap legend
			if trigger_id == "update_legend_button.n_clicks":
				popover_status = False
				#identify how many plots there are
				n_plots = len(selected_genes_species)
				i = 0
				for plot in range(0, n_plots):
					actual_traces_to_change = [trace + i for trace in range(0, len(legend_fig["data"]))]
					#apply each change
					for n in range(0, len(legend_fig["data"])):
						box_fig["data"][actual_traces_to_change[n]]["visible"] = legend_fig["data"][n]["visible"]
					i += len(legend_fig["data"])
			#any other change
			elif trigger_id != "update_legend_button.n_clicks":
				#up to 10 elements to plot
				if len(selected_genes_species) < 21:

					#create figure
					box_fig = go.Figure()
					
					#define number of rows
					if (len(selected_genes_species) % 4) == 0:
						n_rows = len(selected_genes_species)/4
					else:
						n_rows = int(len(selected_genes_species)/4) + 1
					n_rows = int(n_rows)

					#define specs for subplot
					specs = []
					for i in range(0, n_rows):
						specs.append([{}, {}, {}, {}])
					#in case of odd number of selected elements, some plots in the grid are None
					if (len(selected_genes_species) % 4) != 0:
						odd_elements_to_plot = len(selected_genes_species) - 4 * (n_rows - 1)
						for i in range(1, (5 - odd_elements_to_plot)):
							specs[-1][-i] = None

					#make subplots
					if expression_dataset in ["human", "mouse"]:
						expression_or_abundance = "expression"
					else:
						expression_or_abundance = "abundance"
					box_fig = make_subplots(rows=n_rows, cols=4, specs=specs, subplot_titles=[gene.replace("[", "").replace("]", "").replace("_", " ") for gene in selected_genes_species], shared_xaxes=True, vertical_spacing=(0.25/n_rows), y_title="Log2 {}".format(expression_or_abundance))

					#loop 1 plot per gene
					working_row = 1
					working_col = 1
					for gene in selected_genes_species:
						#open counts
						counts = functions.download_from_github("data/" + expression_dataset + "/counts/" + gene + ".tsv")
						counts = pd.read_csv(counts, sep = "\t")
						#merge and compute log2 and replace inf with 0
						metadata_df = metadata_df_original.merge(counts, how="left", on="sample")
						metadata_df["Log2 counts"] = np.log2(metadata_df["counts"])
						metadata_df["Log2 counts"].replace(to_replace = -np.inf, value = 0, inplace=True)
						#clean metadata field column
						metadata_df[metadata_field] = [i.replace("_", " ") for i in metadata_df[metadata_field]]
						
						#group by switch operations
						visible_traces = []
						for trace in legend_fig["data"]:
							if trace["visible"] is True:
								visible_traces.append(trace["name"])

						#plot
						if metadata_field == "condition" and config["sorted_conditions"]:
							metadata_fields_ordered = config["condition_list"]
							metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
						else:	
							metadata_fields_ordered = metadata_df[metadata_field].unique().tolist()
							metadata_fields_ordered.sort()
						i = 0
						for metadata in metadata_fields_ordered:
							filtered_metadata = metadata_df[metadata_df[metadata_field] == metadata]
							
							#visible setting
							if metadata in visible_traces:
								visible_status = True
							else:
								visible_status = False
							
							#do not plot values for NA
							if metadata == "NA":
								y_values = None
								x_values = None
							else:
								y_values = filtered_metadata["Log2 counts"]
								x_values = filtered_metadata[metadata_field]
							
							#label to value with counts in it
							label_to_value_plus_counts = label_to_value.copy()
							if expression_dataset in ["human", "mouse"]:
								label_to_value_plus_counts["Log2 counts"] = "Log2 expression"
							else:
								label_to_value_plus_counts["Log2 counts"] = "Log2 abundance"
							#get all additional metadata
							additional_metadata = []
							for label in label_to_value_plus_counts:
								if label not in ["sample", "condition", "Log2 counts"]:
									additional_metadata.append(label)
							#reorder columns
							filtered_metadata = filtered_metadata[["sample", "condition", "Log2 counts"] + additional_metadata]
							#only 2 decimals
							filtered_metadata = filtered_metadata.round(2)
							#create hovertext
							filtered_metadata["hovertext"] = ""
							for column in filtered_metadata.columns:
								if column in label_to_value_plus_counts:
									filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + label_to_value_plus_counts[column] + ": " + filtered_metadata[column].astype(str) + "<br>"
							hovertext = filtered_metadata["hovertext"].tolist()
							marker_color = functions.get_color(metadata, i)
							box_fig.add_trace(go.Box(x=x_values, y=y_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", visible=visible_status, legendgroup=metadata, showlegend=False, offsetgroup=metadata), row=int(working_row), col=working_col)
							i += 1

						#row and column count
						working_row += 0.25
						working_col += 1
						#reset count
						if working_col == 5:
							working_col = 1

					#update all traces markers
					box_fig.update_traces(marker_size=4)
					#compute height
					height_fig = 180 + n_rows*190
					if expression_dataset in ["human", "mouse"]:
						title_text = "{host} gene expression profiles per ".format(host=expression_dataset.capitalize()) + metadata_field.replace("_", " ").capitalize()
					else:
						title_text = "{} abundance profiles per ".format(expression_dataset.replace("_", " ").replace("viruses", "viral").capitalize()) + metadata_field.replace("_", " ").capitalize()
					#update layout
					box_fig.update_layout(height=height_fig, title = {"text": title_text, "x": 0.5, "y": 0.98}, font_size=14, font_family="Arial", margin_r=10, margin_t=80, margin_b=120)

					popover_status = False
					hidden_status = False
				#more then 20 elements to plot
				else:
					hidden_status = True
					popover_status = True

		config_multi_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}}
		config_multi_boxplots["toImageButtonOptions"]["filename"] = "multiboxplots_{title_text}".format(title_text = title_text.replace(" ", "_") + metadata_field)

		return box_fig, config_multi_boxplots, hidden_status, popover_status
