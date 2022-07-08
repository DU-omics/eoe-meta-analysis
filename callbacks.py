#import packages
import dash
from dash import dcc, html
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash.dash_table.Format import Format, Scheme
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from functools import reduce
from sklearn.preprocessing import scale
import tempfile
#import modules
import functions
from functions import config, colors, gender_colors, na_color, repos, tab_style, tab_selected_style

from layout import metadata_tab_layout, heatmap_tab_layout, multi_violin_tab_layout, correlation_tab_layout, diversity_tab_layout, dge_tab_layout, go_tab_layout, mofa_tab_layout, deconvolution_tab_layout

def define_callbacks(app):

	##### START-UP ######

	#change analysis metadata callback
	@app.callback(
		#store data
		Output("color_mapping", "data"),
		Output("label_to_value", "data"),
		#tabs
		Output({"type": "tabs", "id": "main_tabs"}, "children"),
		Output({"type": "tabs", "id": "main_tabs"}, "value"),
		#metadata table data
		Output("metadata_table_store", "data"),
		Output("metadata_columns_store", "data"),
		#metadata options
		Output("metadata_dropdown", "options"),
		#heatmap annotation options
		Output("heatmap_annotation_dropdown_options", "data"),
		#discrete metadata options
		Output("discrete_metadata_options", "data"),
		#continuous metadata options
		Output("continuous_metadata_options", "data"),
		#mofa contrasts options
		Output("mofa_contrasts_options", "data"),
		#deconvolution datasets options
		Output("deconvolution_datasets_options", "data"),
		#header
		Output("header_div", "children"),
		#input
		Input("analysis_dropdown", "value")
	)
	def update_analysis_related_data(path):
		#metadata related elements
		metadata = functions.download_from_github(path, "metadata.tsv")
		metadata = pd.read_csv(metadata, sep = "\t")
		metadata = metadata.replace("_", " ", regex=True)
		metadata_options = []
		heatmap_annotation_options = []
		discrete_metadata_options = []
		continuous_metadata_options = [{"label": "Log2 expression", "value": "log2_expression"}]
		label_to_value = {"sample": "Sample"}
		columns_to_keep = []
		for column in metadata.columns:
			#color by and heatmap annotation dropdowns
			if column not in ["sample", "fq1", "fq2", "control", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
				#dict used for translating colnames
				label_to_value[column] = column.capitalize().replace("_", " ")
				metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})
				if column != "condition":
					heatmap_annotation_options.append({"label": column.capitalize().replace("_", " "), "value": column})
				#discrete and continuous metadatas
				if str(metadata.dtypes[column]) == "object":
					#condition should always be the first
					if column == "condition":
						discrete_metadata_options.insert(0, {"label": column.capitalize().replace("_", " "), "value": column})
					else:
						discrete_metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})
				else:
					continuous_metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})

			#metadata teble columns
			if column not in [ "fq1", "fq2", "control", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
				columns_to_keep.append(column)

		#color dictionary
		i = 0
		color_mapping = {}
		#discrete color mapping
		for dicscrete_option in discrete_metadata_options:
			column = dicscrete_option["value"]
			if column not in color_mapping:
				color_mapping[column] = {}
			metadata[column] = metadata[column].fillna("NA")
			values = metadata[column].unique().tolist()
			values = [str(value) for value in values]
			values.sort()
			for value in values:
				if value == "NA":
					color_mapping[column][value] = na_color
				elif value == "Male":
					color_mapping[column][value] = gender_colors["Male"]
				elif value == "Female":
					color_mapping[column][value] = gender_colors["Female"]
				else:
					if i == len(colors):
						i = 0
					color_mapping[column][value] = colors[i]
					i += 1
		#continuous color mapping
		for continuous_option in continuous_metadata_options:
			column = continuous_option["value"]
			if column != "log2_expression":
				if i == len(colors):
					i = 0
				if column not in color_mapping:
					color_mapping[column] = {}
				color_mapping[column]["continuous"] = colors[i]
				i += 1

		#shape metadata table
		metadata_table = metadata[columns_to_keep]
		metadata_table = metadata_table.rename(columns=label_to_value)
		metadata_table_columns = []
		for column in metadata_table.columns:
			metadata_table_columns.append({"name": column.capitalize().replace("_", " "), "id": column})
		metadata_table_data = metadata_table.to_dict("records")

		#header
		repo = functions.get_repo_name_from_path(path, repos)
		if config["repos"][repo]["logo"] == "NA":
			header_children = html.Div(repo, style={"width": "100%", "font-size": 50, "text-align": "center"})
		else:
			header_children = html.Img(src=config["repos"][repo]["logo"], alt="logo", style={"width": "70%", "height": "70%"}, title=repo)

		#tabs
		#metadata tab
		metadata_tab = dcc.Tab(id="metadata_tab", label="Metadata", value="metadata_tab", style=tab_style, selected_style=tab_selected_style)
		#expression/abundance profiling
		profiling_tab = dcc.Tab(id="profiling_tab", label="Profiling", value="profiling_tab", style=tab_style, selected_style=tab_selected_style)
		#differential analysis tab
		differential_analysis_tab = dcc.Tab(id="differential_analysis_tab", label="Differential analysis", value="differential_analysis_tab", style=tab_style, selected_style=tab_selected_style)

		#save main tabs in a list to use as children
		all_tabs = [metadata_tab, profiling_tab, differential_analysis_tab]

		## additional tabs ##
		main_folders = functions.get_content_from_github(path, "./")
		#mofa
		mofa_contrasts_options = []
		if "mofa" in main_folders:
			mofa_contrasts = functions.get_content_from_github(path, "mofa")
			for mofa_contrast in mofa_contrasts:
				mofa_contrasts_options.append({"label": mofa_contrast.replace("-", " ").replace("_", " "), "value": mofa_contrast})

			mofa_tab = dcc.Tab(id="mofa_tab", label="Multi-omics signatures", value="mofa_tab", style=tab_style, selected_style=tab_selected_style)
			all_tabs.append(mofa_tab)

		#deconvolution
		deconvolution_datasets_options = []
		if "deconvolution" in main_folders:
			deconvolution_datasets = functions.get_content_from_github(path, "deconvolution")

			#deconvolution datasets
			for deconvolution_dataset in deconvolution_datasets:
				dataset_name = deconvolution_dataset.split(".")[0]
				deconvolution_datasets_options.append({"label": dataset_name, "value": deconvolution_dataset})
				
			
			deconvolution_tab = dcc.Tab(id="deconvolution_tab", label="Deconvolution", value="deconvolution_tab", children=[
				], style=tab_style, selected_style=tab_selected_style)
			all_tabs.append(deconvolution_tab)
		
		return color_mapping, label_to_value, all_tabs, "metadata_tab", metadata_table_data, metadata_table_columns, metadata_options, heatmap_annotation_options, discrete_metadata_options,  continuous_metadata_options, mofa_contrasts_options, deconvolution_datasets_options, header_children

	#add gsea switch
	@app.callback(
		Output("add_gsea_switch_div", "hidden"),
		Output("add_gsea_switch", "value"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def show_add_gsea_switch(expression_dataset, path):
		if expression_dataset in ["human", "mouse"]:
			folders = functions.get_content_from_github(path, "data/{}".format(expression_dataset))
			if "gsea" in folders:
				hidden = False	
			else:
				hidden = True
		else:
			hidden = True
		value = []
		
		return hidden, value

	##### TAB-DIV ELEMENTS #####

	#display tab content
	@app.callback(
		Output("tab_content_div", "children"),
		Input({"type": "tabs", "id": ALL}, "value"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value"),
		prevent_initial_call=True
	)
	def update_tab_div_layout(main_tab_value, expression_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["value"]

		all_possible_tabs = ["metadata_tab", "profiling_tab", "heatmap_tab", "multi_violin_tab", "feature_correlation_tab", "diversity_tab", "differential_analysis_tab", "dge_tab", "go_tab", "mofa_tab", "deconvolution_tab"]
		
		#add diversity tab only if the drodpown has been switched to metatrasncriptomics species and the profiling tab is selected
		if "species" in trigger_id:
			if "profiling_tab" in main_tab_value:
				main_tab_value.remove("profiling_tab")
				trigger_id = main_tab_value[0]
			else:
				raise PreventUpdate
		#if you selected something that is not a species dataset and you are in the divrsity tab, return to heatmap tab
		else:
			if "diversity_tab" in main_tab_value and trigger_id not in all_possible_tabs:
				trigger_id = "profiling_tab"

		#click on any main tab
		if trigger_id in all_possible_tabs:

			#metadata
			if trigger_id == "metadata_tab":
				children = [metadata_tab_layout]
			#profiling
			elif trigger_id in ["profiling_tab", "heatmap_tab", "multi_violin_tab", "feature_correlation_tab", "diversity_tab"]:
				#heatmap or default
				if trigger_id in ["profiling_tab", "heatmap_tab"]:
					profiling_tab_value = "heatmap_tab"
					tab_layout = heatmap_tab_layout
				#multi violin
				elif trigger_id == "multi_violin_tab":
					profiling_tab_value = "multi_violin_tab"
					tab_layout = multi_violin_tab_layout
				#correlation
				elif trigger_id == "feature_correlation_tab":
					profiling_tab_value = "feature_correlation_tab"
					tab_layout = correlation_tab_layout
				#diversity
				else:
					profiling_tab_value = "diversity_tab"
					tab_layout = diversity_tab_layout

				#constant tab
				tabs_children = [
					dcc.Tab(id="heatmap_tab", label="Heatmap", value="heatmap_tab", style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(id="multi_violin_tab", label="Multi-violin", value="multi_violin_tab", style=tab_style, selected_style=tab_selected_style),
					dcc.Tab(id="feature_correlation_tab", label="Feature correlation", value="feature_correlation_tab", style=tab_style, selected_style=tab_selected_style)
				]

				#add diversity tab when some species expression dataset is selected
				main_folders = functions.get_content_from_github(path, "./")
				if "species" in expression_dataset and "diversity" in main_folders:
					tabs_children.append(dcc.Tab(id="diversity_tab", label="Species diversity", value="diversity_tab", style=tab_style, selected_style=tab_selected_style))
				
				#put all tab components in tabs
				children = [dcc.Tabs(id={"type": "tabs", "id": "profiling_tabs"}, value=profiling_tab_value, style= {"height": 40}, children=tabs_children)]			
				children = children + [tab_layout]
			#differential analysis
			elif trigger_id in ["differential_analysis_tab", "dge_tab", "go_tab"]:
				#dge or default
				if trigger_id in ["differential_analysis_tab", "dge_tab"]:
					differential_analysis_tab_value = "dge_tab"
					tab_layout = dge_tab_layout
				#go
				else:
					differential_analysis_tab_value = "go_tab"
					tab_layout = go_tab_layout

				#populate children
				children = [
					dcc.Tabs(id={"type": "tabs", "id": "differential_analysis_tabs"}, value=differential_analysis_tab_value, style= {"height": 40}, children=[
						dcc.Tab(id="dge_tab", value="dge_tab", style=tab_style, selected_style=tab_selected_style),
						dcc.Tab(id="go_tab", value="go_tab", style=tab_style, selected_style=tab_selected_style),
					])]
				children = children + [tab_layout]
			#mofa
			elif trigger_id == "mofa_tab":
				children = mofa_tab_layout
			#deconvolution
			elif trigger_id == "deconvolution_tab":
				children = deconvolution_tab_layout
		else:
			raise PreventUpdate
			
		return children

	### metadata tab ###

	#update metadata tab content
	@app.callback(
		Output("metadata_table", "data"),
		Output("metadata_table", "columns"),
		Input("metadata_table_store", "data"),
		Input("metadata_columns_store", "data"),
	)
	def update_metadata_tab_content(metadata_table_data, metadata_table_columns):
		return metadata_table_data, metadata_table_columns

	### profiling tab ##

	#save profiling tab labels data
	@app.callback(
		Output("profiling_tab_label_data", "data"),
		Input("feature_dataset_dropdown", "value")
	)
	def save_profiling_tabs_labels_data(expression_dataset):
		#label for profiling tab
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			profiling_tab_label = "Expression profiling"
		else:
			profiling_tab_label = "Abundance profiling"
		
		return profiling_tab_label

	#update profiling tab label
	@app.callback(
		Output("profiling_tab", "label"),
		Input("profiling_tab_label_data", "data")
	)
	def update_profiling_tabs_label(profiling_tab_label):
		return profiling_tab_label

	## heatmap ##

	#placeholder for heatmap_text_area
	@app.callback(
		Output("heatmap_text_area", "placeholder"),
		Input("feature_dataset_dropdown", "value")
	)
	def get_placeholder_heatmap_text_area(expression_dataset):
		if expression_dataset in ["human", "mouse", "lipid"] or "genes" in expression_dataset:
			placeholder = "Paste list (plot allowed for max 10 features)"
		else:
			placeholder = "Paste list (plot allowed for max 10 features, one per line)"

		return placeholder

	### differential analysis tab ###

	#save differential analysis tab labels
	@app.callback(
		Output("differential_analysis_tab_label_data", "data"),
		Input("feature_dataset_dropdown", "value"),
		Input({"type": "tabs", "id": "main_tabs"}, "value")
	)
	def save_differential_analysis_tabs_labels(expression_dataset, selected_tab):
		#no need to update the labels if the user has not selected the differential analysis tab
		if selected_tab != "differential_analysis_tab":
			raise PreventUpdate
		
		#label for dge_table_tab and go_table_tab
		if "lipid" in expression_dataset:
			dge_table_label = "DLE table"
			go_table_label = "LO table"
		else:
			dge_table_label = "DGE table"
			go_table_label = "GO table"

		data = {}
		data["dge_tab_label"] = dge_table_label
		data["go_tab_label"] = go_table_label

		return data

	#update differential analysis tab labels
	@app.callback(
		Output("dge_tab", "label"),
		Output("go_tab", "label"),
		Input("differential_analysis_tab_label_data", "data"),
	)
	def update_differential_analysis_tabs_labels(data):
		#get labels
		dge_table_label = data["dge_tab_label"]
		go_table_label = data["go_tab_label"]

		return dge_table_label, go_table_label

	#target prioritization switch
	@app.callback(
		Output("target_prioritization_switch_div", "hidden"),
		Input("feature_dataset_dropdown", "value")
	)
	def show_target_prioritization_switch(feature_dataset):
		if feature_dataset == "human" and config["opentargets"] is True:
			hidden = False
		else:
			hidden = True
		
		return hidden

	##### DROPDOWNS #####

	### main dropdowns ###

	#get mds datasets types
	@app.callback(
		Output("mds_type", "options"),
		Output("mds_type", "value"),
		Input("mds_dataset", "value"),
		State("analysis_dropdown", "value")
	)
	def get_mds_type_for_dataset(mds_dataset, path):

		mds_files = functions.get_content_from_github(path, "data/" + mds_dataset + "/mds")
		
		options = []
		for file in mds_files:
			mds_type = file.split(".")[0]
			if mds_type == "tsne":
				label = "t-SNE"
			else:
				label = "UMAP"
			options.append({"label": label, "value": mds_type})

		if "umap.tsv" in mds_files:
			value = "umap"
		else:
			value = "tsne"

		return options, value

	#change label main feature dropdown
	@app.callback(
		Output("feature_label", "children"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value"),
		State("feature_dropdown", "value")
	)
	def setup_new_dataset_features(expression_dataset, path, current_value):
		#for web app startup, get default value
		if expression_dataset not in ["human", "mouse"]:
			if "lipid" in expression_dataset:
				if expression_dataset == "lipid":
					search_value = "10-HDoHE"
				else:
					search_value = "DHA"
			else:
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					search_value = "data/" + expression_dataset + "/counts/genes_list.tsv"
				else:
					if "lipid" in expression_dataset:
						search_value = "data/" + expression_dataset + "/counts/lipid_list.tsv"
					else:
						search_value = "data/" + expression_dataset + "/counts/feature_list.tsv"
				search_value = functions.download_from_github(path, search_value)
				search_value = search_value.readline()
				search_value = search_value.rstrip()
		else:
			if expression_dataset == "human":
				search_value = "GAPDH"
			elif expression_dataset == "mouse":
				search_value = "Gapdh"

		#get feature list and label
		features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

		#populate options based on user search
		options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "single")

		#populate children
		children = [
			label, 	
			dcc.Dropdown(
				id="feature_dropdown",
				clearable=False,
				value=search_value,
				options=options
			)
		]

		return children

	#set featuere value with automatic interactions
	@app.callback(
		Output("feature_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("ma_plot_graph", "clickData"),
		Input("dge_table_click_data", "data"),
		Input("analysis_dropdown", "value")
	)
	def set_main_feature_dropdown_value(expression_dataset, selected_point_ma_plot, dge_table_cell_data, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#if you click a feature on the ma-plot, set up the search value with that value
		if trigger_id == "ma_plot_graph.clickData":
			selected_element = selected_point_ma_plot["points"][0]["customdata"][0].replace(" ", "_")
			if selected_element == "NA":
				raise PreventUpdate
			else:
				if "genes" in expression_dataset:
					selected_element = selected_element.replace("_-_", "@")
				value = selected_element
		#change of dataset, setup search value with defaults
		elif trigger_id in ["feature_dataset_dropdown.value", ".", "analysis_dropdown.value"]:
			if expression_dataset not in ["human", "mouse"]:
				if "lipid" in expression_dataset:
					if expression_dataset == "lipid":
						value = "10-HDoHE"
					else:
						value = "DHA"
				else:
					if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
						value = "data/" + expression_dataset + "/counts/genes_list.tsv"
					else:
						if "lipid" in expression_dataset:
							value = "data/" + expression_dataset + "/counts/lipid_list.tsv"
						else:
							value = "data/" + expression_dataset + "/counts/feature_list.tsv"
					value = functions.download_from_github(path, value)
					value = value.readline()
					value = value.rstrip()
			else:
				if expression_dataset == "human":
					value = "GAPDH"
				elif expression_dataset == "mouse":
					value = "Gapdh"
		#dge table active cell data
		else:
			value = dge_table_cell_data

		return value
	
	#feature dropdown options
	@app.callback(
		Output("feature_dropdown", "options"),
		Input("feature_dropdown", "search_value"),
		Input("feature_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def update_options_feature_dropdown(search_value, current_value, expression_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#don't change the options when the search value is empty
		if not search_value and trigger_id == "feature_dropdown.search_value":
			raise PreventUpdate

		#mock search when updating automatically
		if trigger_id == "feature_dropdown.value":
			search_value = current_value

		#get feature list and label
		features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

		#populate options based on user search
		options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "single")

		return options

	#feature and mds datasets dropdowns
	@app.callback(
		Output("feature_dataset_dropdown", "options"),
		Output("feature_dataset_dropdown", "value"),
		Output("mds_dataset", "options"),
		Output("mds_dataset", "value"),
		Input("analysis_dropdown", "value")
	)
	def update_feature_and_mds_datasets_dropdown(path):
		#get all subdir to populate expression dataset
		subdirs = functions.get_content_from_github(path, "data")
		expression_datasets_options = []
		mds_dataset_options = []
		for dir in subdirs:
			if dir in ["human", "mouse"]:
				organism = dir
				expression_datasets_options.append({"label": dir.capitalize(), "value": dir})
				mds_dataset_options.append({"label": dir.capitalize(), "value": dir})
			else:
				non_host_content = functions.get_content_from_github(path, "data/" + dir)
				if "lipid" in dir:
					expression_datasets_options.append({"label": dir.capitalize().replace("_", " "), "value": dir})
					if "mds" in non_host_content:
						mds_dataset_options.append({"label": dir.capitalize().replace("_", " "), "value": dir})
				else:
					kingdom = dir.split("_")[0]
					lineage = dir.split("_")[1]
					expression_datasets_options.append({"label": kingdom.capitalize() + " by " + lineage, "value": dir})
					#check if there is mds for each metatranscriptomics
					if "mds" in non_host_content:
						mds_dataset_options.append({"label": kingdom.capitalize() + " by " + lineage, "value": dir})

		return expression_datasets_options, organism, mds_dataset_options, organism

	#contrast dropdown
	@app.callback(
		Output("contrast_dropdown", "options"),
		Output("contrast_dropdown", "value"),
		Output("best_comparisons_switch", "value"),
		Output("best_comparisons_switch", "options"),
		Input("feature_dataset_dropdown", "value"),
		Input("comparison_filter_input", "value"),
		Input("best_comparisons_switch", "value"),
		State("analysis_dropdown", "value"),
		State("best_comparisons_switch", "options")
	)
	def get_contrasts(expression_dataset, input_value, best_comparisons_switch, path, best_comparisons_switch_options):
		if expression_dataset is None:
			raise PreventUpdate
		
		#trigger id
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		boolean_best_comparisons_switch = functions.boolean_switch(best_comparisons_switch)
		
		#if best contrasts is true, in case these will not be present in this expression dataset then the switch should be disabled
		if boolean_best_comparisons_switch:
			tried_to_filter_best_contrasts = True
		else:
			tried_to_filter_best_contrasts = False
		
		#by changing expression dataset, assume that is possible to use best comparisons
		if trigger_id == "feature_dataset_dropdown.value":
			best_comparisons_switch_options = [{"label": "", "value": 1, "disabled": False}]

		#get which repo has been selected
		repo = functions.get_repo_name_from_path(path, repos)

		dge_folder = "data/" + expression_dataset + "/dge"
		dge_files = functions.get_content_from_github(path, dge_folder)
		contrasts = []
		filtered_contrasts = []
		#get dge files for getting all the contrasts
		for dge_file in dge_files:
			contrast = dge_file.split("/")[-1]
			contrast = contrast.split(".")[0]
			
			#try to use the best contrasts in the config
			if boolean_best_comparisons_switch:
				if contrast in config["repos"][repo]["best_comparisons"]:
					filtered_contrasts.append(contrast)
			
			#if the input is the search bar, then try to filter
			if trigger_id == "comparison_filter_input.value":
				#get lower search values
				input_value = input_value.lower()
				search_values = input_value.split(" ")
				#check search values into the contrast
				number_of_values = len(search_values)
				matches = 0
				for search_value in search_values:
					contrast_lower = contrast.lower()
					condition_1 = contrast_lower.split("-vs-")[0]
					condition_2 = contrast_lower.split("-vs-")[1]
					#all keywords must be present in both conditions
					if search_value in condition_1 and search_value in condition_2:
						matches += 1
				#if all the keyword are in both condition, the add this contrast to the filtered contrasts
				if matches == number_of_values:
					filtered_contrasts.append(contrast)

			#save anyway all contrasts in case there are no possibilities
			contrasts.append(contrast)
		#if no filtered contrasts are present, use all the contrasts
		if len(filtered_contrasts) != 0:
			contrasts = filtered_contrasts
		#turn off the switch if any of the best comparisons is in this new dataset and disable the switch
		else:
			if trigger_id == "feature_dataset_dropdown.value" and tried_to_filter_best_contrasts:
				best_comparisons_switch = []
				best_comparisons_switch_options = [{"label": "", "value": 1, "disabled": True}]

		#define options and default value
		options = []
		possible_values = []
		for contrast in contrasts:
			options.append({"label": contrast.replace("-", " ").replace("_", " "), "value": contrast})
			possible_values.append(contrast)
		if config["repos"][repo]["default_comparison"] != "First" and config["repos"][repo]["default_comparison"] in possible_values:
			value = config["repos"][repo]["default_comparison"]
		else:
			value = options[0]["value"]

		return options, value, best_comparisons_switch, best_comparisons_switch_options

	#stringency dropdown
	@app.callback(
		Output("stringency_dropdown", "value"),
		Output("stringency_dropdown", "options"),
		Input("feature_dataset_dropdown", "value"),
		Input("analysis_dropdown", "value")
	)
	def get_stringency_value(expression_dataset, path):	
		if expression_dataset in ["human", "mouse"]:
			folders = functions.get_content_from_github(path, "data/{}".format(expression_dataset))
			options = []
			#get all dge analyisis performed
			for folder in folders:
				if folder not in ["counts", "dge", "mds", "gsea"]:
					#label will be constructed
					label = ""
					#strincecy type
					stringency_type = folder.split("_")[0]
					if stringency_type == "pvalue":
						label += "P-value "
					else:
						label += "FDR "
					#stringency value
					stringency_value = folder.split("_")[1]
					label += stringency_value
					
					#populate options
					options.append({"label": label, "value": folder})
		
			#default value defined in config file
			repo = functions.get_repo_name_from_path(path, repos)
			value = functions.config["repos"][repo]["stringency"]
		else:
			options = [{"label": "P-value 0.05", "value": "pvalue_0.05"}]
			value = "pvalue_0.05"

		return value, options

	#x and group by dropdowns boxplots
	@app.callback(
		Output("x_boxplot_dropdown", "options"),
		Output("group_by_boxplot_dropdown", "options"),
		Input("discrete_metadata_options", "data")
	)
	def get_x_values_boxplot_dropdowns(options_discrete):
		return options_discrete, options_discrete

	#expression or abundance y dropdown
	@app.callback(
		Output("y_boxplot_dropdown", "options"),
		Output("y_boxplot_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("continuous_metadata_options", "data"),
		State("y_boxplot_dropdown", "options"),
	)
	def get_y_values_boxplot_dropdowns(feature_dataset_dropdown, continuous_metadata_options_data, y_boxplots_dropdown):
		if feature_dataset_dropdown is None:
			raise PreventUpdate
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		if trigger_id == "continuous_metadata_options.data" or y_boxplots_dropdown is None:
			y_boxplots_dropdown = continuous_metadata_options_data
		
		if feature_dataset_dropdown in ["human", "mouse"] or "genes" in feature_dataset_dropdown:
			y_boxplots_dropdown[0] = {"label": "Log2 expression", "value": "log2_expression"}
			value = "log2_expression"
		else:
			y_boxplots_dropdown[0] = {"label": "Log2 abundance", "value": "log2_abundance"}
			value = "log2_abundance"

		return y_boxplots_dropdown, value

	#filter x axis boxplots
	@app.callback(
		Output("x_filter_boxplot_dropdown", "options"),
		Output("x_filter_boxplot_dropdown", "value"),
		Input("x_boxplot_dropdown", "value"),
		Input("y_boxplot_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_filter_x_values_boxplots_dropdowns(selected_x, selected_y, feature_dataset, path):
		
		options, x_values = functions.get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset, path)

		return options, x_values

	### profiling dropdowns ###

	## heatmap ##

	#get options heatmap annotations
	@app.callback(
		Output("heatmap_annotation_dropdown", "options"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("heatmap_annotation_dropdown_options", "data")
	)
	def get_options_heatmap_annotation(selected_tab, annotation_dropdown_options):
		return annotation_dropdown_options

	#search genes for heatmap
	@app.callback(
		Output("feature_heatmap_dropdown", "value"),
		Output("genes_not_found_heatmap_div", "children"),
		Output("genes_not_found_heatmap_div", "hidden"),
		Output("heatmap_text_area", "value"),
		Output("update_heatmap_plot_button", "n_clicks"),
		Input("heatmap_search_button", "n_clicks"),
		Input("go_plot_graph", "clickData"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("analysis_dropdown", "value"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("heatmap_text_area", "value"),
		State("feature_dataset_dropdown", "value"),
		State("feature_heatmap_dropdown", "value"),
		State("genes_not_found_heatmap_div", "hidden"),
		State("genes_not_found_heatmap_div", "children"),
		State("update_heatmap_plot_button", "n_clicks"),
		State("add_gsea_switch", "value")
	)
	def serach_genes_in_text_area_heatmap(n_clicks_search, go_plot_click, contrast, stringency_info, path, tab_value, text, expression_dataset, selected_features, log_hidden_status, log_div, n_clicks_update_plot, add_gsea_switch):
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		selected_features, log_div, log_hidden_status, text = functions.search_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, selected_features, add_gsea_switch, 15, path)

		return selected_features, log_div, log_hidden_status, text, n_clicks_update_plot

	#features heatmap dropdown options
	@app.callback(
		Output("feature_heatmap_dropdown", "options"),
		Output("feature_heatmap_dropdown", "placeholder"),
		Input("feature_heatmap_dropdown", "search_value"),
		Input("feature_heatmap_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_options_heatmap_feature_dropdown(search_value, current_value, expression_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		#don't change the options when the search value is empty
		if not search_value and trigger_id == "feature_heatmap_dropdown.search_value":
			raise PreventUpdate
		
		#mock search when updating automatically
		if trigger_id == "feature_heatmap_dropdown.value":
			search_value = "ç"

		#get feature list and label
		features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

		#populate options based on user search
		options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "multi")

		return options, placeholder

	## multi-boxplots dropdowns ##

	#search genes for multiboxplots
	@app.callback(
		Output("feature_multi_boxplots_dropdown", "value"),
		Output("genes_not_found_multi_boxplots_div", "children"),
		Output("genes_not_found_multi_boxplots_div", "hidden"),
		Output("multi_boxplots_text_area", "value"),
		Output("update_multiboxplot_plot_button", "n_clicks"),
		Input("multi_boxplots_search_button", "n_clicks"),
		Input("go_plot_graph", "clickData"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("analysis_dropdown", "value"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("feature_dataset_dropdown", "value"),
		State("multi_boxplots_text_area", "value"),
		State("feature_multi_boxplots_dropdown", "value"),
		State("genes_not_found_multi_boxplots_div", "hidden"),
		State("add_gsea_switch", "value"),
		State("update_multiboxplot_plot_button", "n_clicks"),
	)
	def serach_genes_in_text_area_multiboxplots(n_clicks_search, go_plot_click, contrast, stringency_info, path, tab_value, expression_dataset, text, selected_features, log_hidden_status, add_gsea_switch, update_multiboxplot_plot_button):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		selected_features, log_div, log_hidden_status, text = functions.search_genes_in_textarea(trigger_id, go_plot_click, expression_dataset, stringency_info, contrast, text, selected_features, add_gsea_switch, 15, path)
		
		return selected_features, log_div, log_hidden_status, text, update_multiboxplot_plot_button

	#features multi-boxplots dropdown options
	@app.callback(
		Output("feature_multi_boxplots_dropdown", "options"),
		Output("feature_multi_boxplots_dropdown", "placeholder"),
		Input("feature_multi_boxplots_dropdown", "search_value"),
		Input("feature_multi_boxplots_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_options_multibox_feature_dropdown(search_value, current_value, expression_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		#don't change the options when the search value is empty
		if not search_value and trigger_id == "feature_multi_boxplots_dropdown.search_value":
			raise PreventUpdate
		
		#mock search when updating automatically
		if trigger_id == "feature_multi_boxplots_dropdown.value":
			search_value = "ç"

		#get feature list and label
		features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

		#populate options based on user search
		options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "multi")

		return options, placeholder

	#get x and group by options multiboxplot dropdown
	@app.callback(
		Output("x_multiboxplots_dropdown", "options"),
		Output("group_by_multiboxplots_dropdown", "options"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("discrete_metadata_options", "data")
	)
	def get_x_options_multiboxplots(selected_tab, discrete_options):
		return discrete_options, discrete_options

	#get y options multiboxplot dropdown
	@app.callback(
		Output("y_multiboxplots_dropdown", "options"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("continuous_metadata_options", "data")
	)
	def get_y_options_multiboxplots(selected_tab, continuous_options):
		return continuous_options

	#filter x axis multiboxplots
	@app.callback(
		Output("x_filter_multiboxplots_dropdown", "options"),
		Output("x_filter_multiboxplots_dropdown", "value"),
		Input("x_multiboxplots_dropdown", "value"),
		Input("y_multiboxplots_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_x_filter_values_multiboxplots(selected_x, selected_y, feature_dataset, path):

		options, x_values = functions.get_x_axis_elements_boxplots(selected_x, selected_y, feature_dataset, path)

		return options, x_values

	## correlation dropdowns ##

	#feature datasets and group by options and values
	@app.callback(
		Output("x_dataset_correlation_dropdown", "options"),
		Output("x_dataset_correlation_dropdown", "value"),
		Output("y_dataset_correlation_dropdown", "options"),
		Output("y_dataset_correlation_dropdown", "value"),
		Output("group_by_correlation_dropdown", "options"),
		Input({"type": "tabs", "id": "profiling_tabs"}, "value"),
		State("feature_dataset_dropdown", "options"),
		State("discrete_metadata_options", "data")
	)
	def update_dataset_and_group_by_dropdowns_correlation(selected_tab, feature_dataset_options, discrete_options):
		possible_dataset_values = []
		for dataset_option in feature_dataset_options:
			possible_dataset_values.append(dataset_option["value"])
		if "human" in possible_dataset_values:
			dataset_value = "human"
		else:
			dataset_value = possible_dataset_values[0]
		
		return feature_dataset_options, dataset_value, feature_dataset_options, dataset_value, discrete_options

	#features x correlation dropdown options
	@app.callback(
		Output("x_correlation_dropdown", "options"),
		Output("x_correlation_dropdown", "value"),
		Input("x_correlation_dropdown", "search_value"),
		Input("x_dataset_correlation_dropdown", "value"),
		State("x_correlation_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_options_x_correlation_feature_dropdown(search_value, expression_dataset, current_value, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#reset the feature if the dataset is changed
		if trigger_id == "x_dataset_correlation_dropdown.value":
			options = []
			value = None
		#change of search value
		else:
			value = current_value

			#don't change the options when the search value or the selected value are empty
			if not search_value:
				raise PreventUpdate

			#get feature list and label
			features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

			#populate options based on user search
			options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "single")

		return options, value

	#features y correlation dropdown options
	@app.callback(
		Output("y_correlation_dropdown", "options"),
		Output("y_correlation_dropdown", "value"),
		Input("y_correlation_dropdown", "search_value"),
		Input("y_dataset_correlation_dropdown", "value"),
		State("y_correlation_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_options_x_correlation_feature_dropdown(search_value, expression_dataset, current_value, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#reset the feature if the dataset is changed
		if trigger_id == "x_dataset_correlation_dropdown.value":
			options = []
			value = None
		#change of search value
		else:
			value = current_value

			#don't change the options when the search value or the selected value are empty
			if not search_value:
				raise PreventUpdate

			#get feature list and label
			features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

			#populate options based on user search
			options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "single")

		return options, value

	## diversity dropdowns ##

	#group by diversity dropdown
	@app.callback(
		Output("group_by_diversity_dropdown", "options"),
		Input({"type": "tabs", "id": "main_tabs"}, "value"),
		State("discrete_metadata_options", "data")
	)
	def update_diversity_group_by_dropdown(tab_value, discrete_metadata_options):
		return discrete_metadata_options

	### differential analysis dropdowns ###

	#features dge table dropdown options
	@app.callback(
		Output("multi_gene_dge_table_dropdown", "options"),
		Output("multi_gene_dge_table_dropdown", "placeholder"),
		Input("multi_gene_dge_table_dropdown", "search_value"),
		Input("multi_gene_dge_table_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def get_options_dge_table_feature_dropdown(search_value, current_value, expression_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		#don't change the options when the search value is empty
		if not search_value and trigger_id == "multi_gene_dge_table_dropdown.search_value":
			raise PreventUpdate
		
		#get feature list and label
		features, label, placeholder = functions.get_list_label_placeholder_feature_dropdown(path, expression_dataset)

		#populate options based on user search
		options = functions.get_options_feature_dropdown(expression_dataset, features, search_value, current_value, "multi")

		return options, placeholder

	#store dge tables values click
	@app.callback(
		Output("dge_table_click_data", "data"),
		Input("dge_table", "active_cell"),
		Input("dge_table_filtered", "active_cell"),
	)
	def save_dge_table_data_click(active_cell_full, active_cell_filtered):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#find out which active table to use
		if trigger_id == "dge_table.active_cell":
			active_cell = active_cell_full
		else:
			active_cell = active_cell_filtered
		if active_cell is None:
			raise PreventUpdate
		else:
			#prevent update for click on wrong column or empty gene
			if active_cell["column_id"] not in ["Gene", "Family", "Order", "Species"] or active_cell["column_id"] == "Gene" and active_cell["row_id"] == "":
				raise PreventUpdate
			#return values
			else:
				value = active_cell["row_id"]

		return value

	### mofa dropdowns ###

	#mofa contrast dropdown options
	@app.callback(
		Output("mofa_comparison_dropdown", "options"),
		Input({"type": "tabs", "id": "main_tabs"}, "value"),
		State("mofa_contrasts_options", "data"),
	)
	def update_mofa_contrasts_dropdown_options(tab_value, mofa_constrast_options):
		return mofa_constrast_options

	#mofa contrast dropdown value
	@app.callback(
		Output("mofa_comparison_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input({"type": "tabs", "id": "main_tabs"}, "value"),
		State("mofa_comparison_dropdown", "options"),
		State("analysis_dropdown", "value")
	)
	def set_mofa_contrast_dropdown_value(contrast, tab_value, mofa_contrasts_options, path):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#open metadata
		metadata = functions.download_from_github(path, "metadata.tsv")
		metadata = pd.read_csv(metadata, sep = "\t")

		#get hypotetical mofa contrast value from constrast dropdown
		groups = []
		for condition in contrast.split("-vs-"):
			metadata_filtered = metadata[metadata["condition"] == condition]
			if "group" in metadata_filtered.columns:
				group = metadata_filtered["group"].unique().tolist()
			else:
				group = metadata_filtered["condition"].unique().tolist()
			group = group[0]
			groups.append(group)

		#search in github data the selected mofa contrast
		group_contrast = "-vs-".join(groups)
		mofa_contrasts = functions.get_content_from_github(path, "mofa")
		#try the opposite contrast
		if not group_contrast in mofa_contrasts:
			group_contrast = groups[1] + "-vs-" + groups[0]
			#any mofa contrast is linked to constrast, use the first value
			if not group_contrast in mofa_contrasts:
				group_contrast = mofa_contrasts_options[0]["value"]

		return group_contrast

	## deconvolution dropdowns ##
	@app.callback(
		Output("split_by_1_deconvolution_dropdown", "options"),
		Output("split_by_2_deconvolution_dropdown", "options"),
		Output("data_sets_deconvolution_dropdown", "options"),
		Output("data_sets_deconvolution_dropdown", "value"),
		Input({"type": "tabs", "id": "main_tabs"}, "value"),
		State("discrete_metadata_options", "data"),
		State("deconvolution_datasets_options", "data")
	)
	def update_options_deconvolution_dropdowns(tab_value, options_discrete, deconvolution_datasets_options):
		dataset_value = deconvolution_datasets_options[0]["value"]

		return options_discrete, options_discrete, deconvolution_datasets_options, dataset_value

	### DOWNLOAD CALLBACKS ###

	#download metadata
	@app.callback(
		Output("download_metadata", "data"),
		Input("download_metadata_button", "n_clicks"),
		State("metadata_table", "data"),
		prevent_initial_call=True
	)
	def download_metadata(button_click, metadata_table):
		metadata_table = pd.DataFrame(metadata_table)
		
		with tempfile.TemporaryDirectory() as tmpdir:
			writer = pd.ExcelWriter(f"{tmpdir}/metadata.xlsx")

			#general format
			(max_row, max_col) = metadata_table.shape
			format_white = writer.book.add_format({"font_name": "Arial", "font_size": 10, "text_wrap": True, "align": "top"})
			metadata_table.to_excel(writer, sheet_name="Metadata", index=False, freeze_panes=(1, 1))
			sheet = writer.sheets["Metadata"]
		
			#write header with white formatting
			for col_num, value in enumerate(metadata_table.columns.values):
				sheet.write(0, col_num, value, format_white)
			
			#apply formatting to all the current sheet
			sheet.set_column(0, max_col, 17, format_white)
			
			#save tmp file
			writer.save()

			return dcc.send_file(f"{tmpdir}/metadata.xlsx")

	#download diffexp
	@app.callback(
		Output("download_diffexp", "data"),
		Input("download_diffexp_button", "n_clicks"),
		State("analysis_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("contrast_dropdown", "value"),
		State("stringency_dropdown", "value"),
		prevent_initial_call=True
	)
	def downlaod_diffexp_table(button_click, path, dataset, contrast, stringency):

		#download from GitHub
		df = functions.download_from_github(path, "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		#read the downloaded content and make a pandas dataframe
		df = pd.read_csv(df, sep="\t")
		df = df[["Gene", "Geneid", "log2FoldChange", "lfcSE", "pvalue", "padj", "baseMean"]]

		#clean features
		if "genes" not in dataset:
			if dataset not in ["human", "mouse"]:
				df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]
		else:
			clean_genes = []
			for x in df["Gene"]:
				gene_x = x.split("@")[0]
				beast_x = x.split("@")[1]
				beast_x = beast_x.replace("_", " ")
				x = gene_x + " - " + beast_x
				clean_genes.append(x)
			df["Gene"] = clean_genes

		return functions.dge_table_download_operations(df, dataset, contrast, stringency, False)

	#disabled status for download filtered diffexp
	@app.callback(
		Output("download_diffexp_partial_button", "disabled"),
		Input("multi_gene_dge_table_dropdown", "value")
	)
	def disable_status_download_filtered_diffexp_table(dropdown_values):
		if dropdown_values is None or dropdown_values == []:
			disabled_status = True
		else:
			disabled_status = False
		
		return disabled_status

	#download partial diffexp
	@app.callback(
		Output("download_diffexp_partial", "data"),
		Input("download_diffexp_partial_button", "n_clicks"),
		State("analysis_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("contrast_dropdown", "value"),
		State("stringency_dropdown", "value"),
		State("multi_gene_dge_table_dropdown", "value"),
		prevent_initial_call=True
	)
	def downlaod_diffexp_table_partial(button_click, path, dataset, contrast, stringency, dropdown_values):
		
		#download from GitHub
		df = functions.download_from_github(path, "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		df = pd.read_csv(df, sep="\t")
		df = df[["Gene", "Geneid", "log2FoldChange", "lfcSE", "pvalue", "padj", "baseMean"]]

		#filter selected genes
		if "genes" not in dataset:
			if dataset not in ["human", "mouse"]:
				df["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in df["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			else:
				dropdown_values = [value.replace("€", "/") for value in dropdown_values]
		else:
			clean_genes = []
			for x in df["Gene"]:
				gene_x = x.split("@")[0]
				beast_x = x.split("@")[1]
				beast_x = beast_x.replace("_", " ")
				x = gene_x + " - " + beast_x
				clean_genes.append(x)
			df["Gene"] = clean_genes
			#clean dropdown values
			clean_dropdown_values = []
			for x in dropdown_values:
				gene_x = x.split("@")[0]
				beast_x = x.split("@")[1]
				beast_x = beast_x.replace("_", " ")
				x = gene_x + " - " + beast_x
				clean_dropdown_values.append(x)
			dropdown_values = clean_dropdown_values.copy()
		df = df[df["Gene"].isin(dropdown_values)]

		return functions.dge_table_download_operations(df, dataset, contrast, stringency, True)

	#disabled status for download go buttons
	@app.callback(
		Output("download_go_button", "disabled"),
		Output("download_go_button_partial", "disabled"),
		Input("go_plot_filter_input", "value"),
		Input("feature_dataset_dropdown", "value")
	)
	def disable_status_download_filtered_diffexp_table(search_value, expression_dataset):
		#metatranscriptomics does not have any go
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			disabled = True
			disabled_partial = True
		else:
			disabled = False
			#find out if there is a filtered df
			if search_value is not None and search_value != "":
				disabled_partial = False
			else:
				disabled_partial = True
		
		return disabled, disabled_partial

	#download go
	@app.callback(
		Output("download_go", "data"),
		Input("download_go_button", "n_clicks"),
		State("analysis_dropdown", "value"),
		State("stringency_dropdown", "value"),
		State("contrast_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("add_gsea_switch", "value"),
		prevent_initial_call=True
	)
	def download_go_table(button_click, path, stringency, contrast, expression_dataset, add_gsea_switch):
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate

		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#download from GitHub
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]

		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			go_df = pd.concat([go_df, gsea_df])
		
		return functions.go_table_download_operations(go_df, expression_dataset, contrast, False)

	#download partial go
	@app.callback(
		Output("download_go_partial", "data"),
		Input("download_go_button_partial", "n_clicks"),
		State("contrast_dropdown", "value"),
		State("go_plot_filter_input", "value"),
		State("feature_dataset_dropdown", "value"),
		State("stringency_dropdown", "value"),
		State("add_gsea_switch", "value"),
		State("analysis_dropdown", "value"),
		prevent_initial_call=True
	)
	def download_partial_go_table(n_clicks, contrast, search_value, expression_dataset, stringency, add_gsea_switch, path):
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#define search query if present
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		#open df
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		
		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			go_df = pd.concat([go_df, gsea_df])

		#filtering
		processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)
		go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]

		return functions.go_table_download_operations(go_df, expression_dataset, contrast, True)
	
	#download boxplot statisatics table
	@app.callback(
		Output("download_multiboxplot_stats", "data"),
		Input("download_multiboxplot_stats_button", "n_clicks"),
		State("stats_multixoplots_table", "data"),
		State("feature_dataset_dropdown", "value"),
		State("stringency_dropdown", "value"),
		prevent_initial_call=True
	)
	def download_stats_multiboxplots(n_clicks, stats_table, expression_dataset, stringency):
		#read data
		stats_table = pd.DataFrame(stats_table)

		#find out colors for rows
		pvalue_type = stringency.split("_")[0]
		if pvalue_type == "padj":
			pvalue_type = "FDR"
		else:
			pvalue_type = "P-value"
		pvalue_value = stringency.split("_")[1]
		#not significant
		stats_table.loc[(stats_table[pvalue_type] > float(pvalue_value)), "color"] = "white"
		#up
		stats_table.loc[(stats_table[pvalue_type] <= float(pvalue_value)) & (stats_table["log2 FC"] > 0), "color"] = "#FFE6E6"
		#down
		stats_table.loc[(stats_table[pvalue_type] <= float(pvalue_value)) & (stats_table["log2 FC"] < 0), "color"] = "#E6F0FF"
		colors = stats_table["color"].tolist()

		#reorder columns and remove external resources and id column
		if expression_dataset in ["human", "mouse"]:
			base_mean_label = "Average expression"
			gene_column_name = "Gene"
		else:
			#base mean label
			if "genes" in expression_dataset:
				base_mean_label = "Average expression"
			else:
				base_mean_label = "Average abundance"
			#all other variables
			gene_column_name = expression_dataset.replace("_", " ").capitalize()
		stats_table = stats_table[["Comparison", gene_column_name, base_mean_label, "log2 FC", "log2 FC SE", "stat", "P-value", "FDR"]]
		
		#formatting numbers
		stats_table[["P-value", "FDR"]] = stats_table[["P-value", "FDR"]].replace("NA", np.nan)
		for column in stats_table.columns:
			if column in ["P-value", "FDR"]:
				stats_table[column] = stats_table[column].apply(lambda x: "%.2e" % x if not x.is_integer() else x).values.tolist()
			elif column in [base_mean_label, "log2 FC", "log2 FC SE", "stat"]: 
				stats_table[column] = stats_table[column].apply(lambda x: round(x, 1)).values.tolist()
		stats_table[["P-value", "FDR"]] = stats_table[["P-value", "FDR"]].replace("nan", "NA")

		#get colors for cells
		cell_colors = []
		for color in colors:
			color_row = []
			for col in range(0,len(stats_table.columns)):
				color_row.append(color)
			cell_colors.append(color_row)

		#hide axes
		ax = plt.subplot(111, frame_on=False)
		ax.xaxis.set_visible(False)
		ax.yaxis.set_visible(False)

		#creeate table
		tab=ax.table(cellText=stats_table.values.tolist(), colLabels=stats_table.columns, cellColours=cell_colors, loc="center", cellLoc="left")
		tab.auto_set_column_width(list(range(0,len(stats_table.columns))))
		
		#increase row height and set arial as font
		for r in range(0, len(stats_table.columns)):
			for i in range(0, len(stats_table.index)+1):
				cell = tab[i, r]
				cell.set_height(0.08)

		with tempfile.TemporaryDirectory() as tmpdir:
			#save file
			png = f"{tmpdir}/stats.png"
			plt.savefig(png, dpi=300, bbox_inches="tight")	

			#remove plot form memory
			plt.clf()

			return dcc.send_file(png)

	### TABLES ###

	#dge table filtered by multidropdown
	@app.callback(
		Output("dge_table_filtered", "columns"),
		Output("dge_table_filtered", "data"),
		Output("dge_table_filtered", "style_data_conditional"),
		Output("filtered_dge_table_div", "hidden"),
		Input("multi_gene_dge_table_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("target_prioritization_switch", "value"),
		State("analysis_dropdown", "value")
	)
	def display_filtered_dge_table(dropdown_values, contrast, dataset, fdr, target_prioritization, path):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		boolean_target_prioritization = functions.boolean_switch(target_prioritization)
		
		if dropdown_values is None or dropdown_values == [] or trigger_id == "feature_dataset_dropdown.value":
			hidden_div = True
			columns = []
			data = [{}]
			style_data_conditional = []
		else:
			hidden_div = False
			#open tsv
			table = functions.download_from_github(path, "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
			table = pd.read_csv(table, sep = "\t")

			#filter selected genes
			if dataset not in ["human", "mouse"]:
				table["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table["Gene"]]
				dropdown_values = [value.replace("_", " ").replace("[", "").replace("]", "") for value in dropdown_values]
			else:
				dropdown_values = [value.replace("€", "/")for value in dropdown_values]
			table = table[table["Gene"].isin(dropdown_values)]

			columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, fdr, boolean_target_prioritization, path)

		return columns, data, style_data_conditional, hidden_div

	#dge table full
	@app.callback(
		Output("dge_table", "columns"),
		Output("dge_table", "data"),
		Output("dge_table", "style_data_conditional"),
		Input("contrast_dropdown", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("target_prioritization_switch", "value"),
		State("analysis_dropdown", "value")
	)
	def display_dge_table(contrast, dataset, strincency, target_prioritization, path):
		#open tsv
		table = functions.download_from_github(path, "data/" + dataset + "/dge/" + contrast + ".diffexp.tsv")
		table = pd.read_csv(table, sep = "\t")
		
		boolean_target_prioritization = functions.boolean_switch(target_prioritization)
		
		columns, data, style_data_conditional = functions.dge_table_operations(table, dataset, strincency, boolean_target_prioritization, path)

		return columns, data, style_data_conditional

	#go table
	@app.callback(
		Output("go_table", "columns"),
		Output("go_table", "data"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("add_gsea_switch", "value"),
		State("analysis_dropdown", "value")
	)
	def display_go_table(contrast, stringency, search_value, expression_dataset, add_gsea_switch, path):
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			raise PreventUpdate
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"
		
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep="\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			gsea_df["Genes"] = gsea_df["Genes"].str.replace(";", "; ")
			go_df = pd.concat([go_df, gsea_df])

		#define search query if present
		if search_value is not None and search_value != "":
			processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)
			#filtering
			go_df = go_df[go_df["Process~name"].isin(processes_to_keep)]

		#add links to amigo for main organism or add spaces for lipids
		if expression_dataset in ["human", "mouse"]:
			go_df["Process~name"] = ["[{}](".format(process) + str("http://amigo.geneontology.org/amigo/term/") + process.split("~")[0] + ")" for process in go_df["Process~name"]]
			process_column = "GO biological process"
			feature_columm = "Genes"
			up_or_down_column = "DGE"
			diff_column = "DEGs"
			go_df = go_df.rename(columns={"Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment"})
		else:	
			go_df["Genes"] = go_df["Genes"].str.replace(";", "; ")
			go_df["Process~name"] = go_df["Process~name"].str.replace("_", " ")
			process_column = "Functional category"
			feature_columm = "Lipids"
			up_or_down_column = "DLE"
			diff_column = "LSEA DELs"
			go_df = go_df.rename(columns={"DGE": up_or_down_column, "Process~name": process_column, "num_of_Genes": diff_column, "gene_group": "Dataset genes", "percentage%": "Enrichment", "Genes": feature_columm})

		columns = [
			{"name": up_or_down_column, "id": up_or_down_column}, 
			{"name": feature_columm, "id": feature_columm},
			{"name": process_column, "id": process_column, "type": "text", "presentation": "markdown"},
			{"name": diff_column, "id": diff_column},
			{"name": "Dataset genes", "id":"Dataset genes"},
			{"name": "Enrichment", "id":"Enrichment", "type": "numeric", "format": Format(precision=2, scheme=Scheme.fixed)},
			{"name": "P-value", "id":"P-value", "type": "numeric", "format": Format(precision=2, scheme=Scheme.decimal_or_exponent)}
			]
		data = go_df.to_dict("records")

		return columns, data

	#multiboxplot statistics
	@app.callback(
		Output("stats_multiboxplots_switch", "options"),
		Output("stats_multiboxplots_switch", "value"),
		Output("multiboxplot_stats_div", "children"),
		Output("multiboxplot_stats_div", "hidden"),
		Output("multibox_stats_buttons_div", "hidden"),
		Input("stats_multiboxplots_switch", "value"),
		Input("comparison_only_multiboxplots_switch", "value"),
		Input("x_multiboxplots_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("update_multiboxplot_stats_button", "n_clicks"),
		State("multi_boxplots_graph", "figure"),
		State("feature_dataset_dropdown", "value"),
		State("y_multiboxplots_dropdown", "options"),
		State("stats_multiboxplots_switch", "options"),
		State("analysis_dropdown", "value")
	)
	def display_multibox_stats(stats_switch, comparison_only_switch, x, stringency, update_statistics_button, multiboxplot_graph, expression_dataset, y_options, switch_options, path):
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#statistics are only available for "condition" in x
		if trigger_id == "x_multiboxplots_dropdown.value":
			if x == "condition":
				switch_options = [{"label": "", "value": 1}]
				stats_switch = [1]
			else:
				switch_options = [{"label": "", "value": 1, "disabled": True}]
				stats_switch = []
		
		boolean_stats_switch = functions.boolean_switch(stats_switch)

		if boolean_stats_switch:
			hidden = False
			
			#get possible values for y axis annotation
			possible_y_titles = []
			for option in y_options:
				possible_y_titles.append(option["label"])

			#get genes in plot
			genes = []
			for annotation in multiboxplot_graph["layout"]["annotations"]:
				if annotation["text"] not in possible_y_titles:
					genes.append(annotation["text"])

			#get conditions in plot
			conditions = []
			for trace in multiboxplot_graph["data"]:
				if trace["visible"] == True:
					if trace["name"] not in conditions:
						conditions.append(trace["name"])
			
			#get contrasts which have both conditions in the selected conditions in the plot
			contrasts_df_list = []
			dge_folder = "data/" + expression_dataset + "/dge"
			dge_files = functions.get_content_from_github(path, dge_folder)
			for dge_file in dge_files:
				contrast = dge_file.split("/")[-1]
				contrast = contrast.split(".")[0]
				conditions_in_contrast = contrast.split("-vs-")
				condition_1 = conditions_in_contrast[0]
				condition_2 = conditions_in_contrast[1]
				if condition_1.replace("_", " ") in conditions and condition_2.replace("_", " ") in conditions:
					dge_table = functions.download_from_github(path, "data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
					dge_table = pd.read_csv(dge_table, sep = "\t")
					dge_table = dge_table.dropna(subset=["Gene"])
					
					#since feature names are clean, to filter the dge table we need to clean it
					if expression_dataset in ["human", "mouse"]:
						dge_table["clean_feature"] = [x.replace("€", "/") for x in dge_table["Gene"]]
					else:
						if "lipid" in expression_dataset:
							dge_table["clean_feature"] = dge_table["Gene"]
						elif "genes" in expression_dataset:
							clean_gen_column_name = []
							for x in dge_table["Gene"]:
								gene_x = x.split("@")[0]
								beast_x = x.split("@")[1]
								beast_x = beast_x.replace("_", " ")
								x = gene_x + " - " + beast_x
								clean_gen_column_name.append(x)
							dge_table["clean_feature"] = clean_gen_column_name.copy()
						else:
							dge_table["clean_feature"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in dge_table["Gene"]]

					dge_table = dge_table[dge_table["clean_feature"].isin(genes)]
					dge_table["Comparison"] = contrast.replace("-", " ").replace("_", " ")
					contrasts_df_list.append(dge_table)

			#concat all dfs
			if len(contrasts_df_list) > 1:
				merged_df = pd.concat(contrasts_df_list)
			#no need to concat
			elif len(contrasts_df_list) == 1:
				merged_df = dge_table
			#no any contrast for the selected conditions: create mock df
			else:
				if expression_dataset in ["human", "mouse"]:
					base_mean_label = "Average expression"
					gene_column_name = "Gene"
				else:
					#base mean label
					if "genes" in expression_dataset:
						base_mean_label = "Average expression"
					else:
						base_mean_label = "Average abundance"
					#all other variables
					gene_column_name = expression_dataset.replace("_", " ").capitalize()
				merged_df = pd.DataFrame(columns=["Comparison", gene_column_name, "Geneid", base_mean_label, "log2FoldChange", "lfcSE", "stat", "pvalue", "padj"])

			statistics_table_columns, statistics_table_data, style_data_conditional = functions.dge_table_operations(merged_df, expression_dataset, stringency, False, path)

			#table
			children = [
				
				html.Br(),
				
				dbc.Spinner(
					size="md",
					color="lightgray",
					children=dash_table.DataTable(
						id="stats_multixoplots_table",
						filter_action="native",
						style_filter={
							"text-align": "left"
						},
						style_table={
							"text-align": "left"
						},
						style_cell={
							"whiteSpace": "normal",
							"height": "auto",
							"fontSize": 12, 
							"font-family": "arial",
							"text-align": "left"
						},
						style_data_conditional=style_data_conditional,
						page_size=25,
						sort_action="native",
						style_header={
							"text-align": "left"
						},
						style_as_list_view=True,
						data=statistics_table_data,
						columns=statistics_table_columns,
						filter_options={"case": "insensitive"}
					)
				),
				html.Br()
			]
		else:
			hidden = True
			children = []

		return switch_options, stats_switch, children, hidden, hidden

	##### plots #####

	#mds metadata
	@app.callback(
		Output("mds_metadata", "figure"),
		Output("mds_metadata", "config"),
		Output("mds_metadata_div", "style"),
		Input("mds_dataset", "value"),
		Input("mds_type", "value"),
		Input("metadata_dropdown", "value"),
		Input("mds_expression", "relayoutData"),
		Input("comparison_only_mds_metadata_switch", "value"),
		Input("hide_unselected_mds_metadata_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("mds_metadata", "relayoutData"),
		Input("mds_metadata", "restyleData"),
		State("mds_metadata", "figure"),
		State("mds_expression", "figure"),
		State("color_mapping", "data"),
		State("label_to_value", "data"),
		State("analysis_dropdown", "value")
	)
	def plot_mds_metadata(mds_dataset, mds_type, metadata_to_plot, zoom_mds_expression, comparison_only_switch, hide_unselected_switch, contrast, legend_mds_metadata_click, zoom_mds_metadata, mds_metadata_fig, mds_expression_fig, color_mapping, label_to_value, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		height = 400

		#boolean switches
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		
		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False and mds_expression_fig is not None:
			raise PreventUpdate

		#open metadata
		metadata_df = functions.download_from_github(path, "metadata.tsv")
		metadata_df = pd.read_csv(metadata_df, sep = "\t")

		#change dataset or metadata: create a new figure from tsv
		if trigger_id in ["mds_type.value", "mds_dataset.value", "metadata_dropdown.value", "comparison_only_mds_metadata_switch.value", "contrast_dropdown.value"] or mds_metadata_fig is None:
			
			#preserve old zoom
			keep_old_zoom = False
			if mds_metadata_fig is not None and trigger_id not in ["mds_type.value", "mds_dataset.value", "comparison_only_mds_metadata_switch.value", "contrast_dropdown.value"]:
				xaxis_range = mds_metadata_fig["layout"]["xaxis"]["range"]
				yaxis_range = mds_metadata_fig["layout"]["yaxis"]["range"]
				keep_old_zoom = True

			#create figure from tsv
			mds_metadata_fig = go.Figure()
			if str(metadata_df.dtypes[metadata_to_plot]) == "object":
				mds_metadata_fig = functions.plot_mds_discrete(color_mapping, mds_type, mds_dataset, metadata_to_plot, mds_metadata_fig, height, label_to_value, boolean_comparison_only_switch, contrast, path)
			else:
				variable_to_plot = [metadata_to_plot]
				#get msd df
				mds_df = functions.download_from_github(path, "data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
				mds_df = pd.read_csv(mds_df, sep = "\t")
				#comparison only will filter the samples
				if boolean_comparison_only_switch:
					mds_df = mds_df[mds_df["condition"].isin(contrast.split("-vs-"))]
				color = functions.get_color(color_mapping, metadata_to_plot, "continuous")
				mds_metadata_fig = functions.plot_mds_continuous(mds_df, mds_type, variable_to_plot, color, mds_metadata_fig, height, label_to_value, path)

			#apply old zoom if present
			if keep_old_zoom:
				mds_metadata_fig["layout"]["xaxis"]["range"] = xaxis_range
				mds_metadata_fig["layout"]["yaxis"]["range"] = yaxis_range
				mds_metadata_fig["layout"]["xaxis"]["autorange"] = False
				mds_metadata_fig["layout"]["yaxis"]["autorange"] = False
		
		#change umap expression means just to update the zoom
		elif trigger_id == "mds_expression.relayoutData" and mds_expression_fig is not None:
			mds_metadata_fig = functions.synchronize_zoom(mds_metadata_fig, mds_expression_fig)
		
		#get number of displayed samples
		n_samples_mds_metadata = functions.get_displayed_samples(mds_metadata_fig)

		#labels for graph title
		if "lipid" in mds_dataset:
			omics = "lipidome"
			subdirs = functions.get_content_from_github(path, "data")
			if "human" in subdirs:
				mds_title = "human"
			elif "mouse" in subdirs:
				mds_title = "mouse"
		else:
			omics = "transcriptome"
		if mds_dataset in ["human", "mouse"]:
			mds_title = mds_dataset
		else:
			mds_title = mds_dataset.replace("_", " ")

		#apply title
		mds_metadata_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + mds_title + " " + omics + " MDS<br>colored by " + metadata_to_plot.replace("_", " ") + " metadata n=" + str(n_samples_mds_metadata)


		#hide unselected legend items
		if boolean_hide_unselected_switch:
			mds_metadata_fig["layout"]["legend"]["itemclick"] = False
			mds_metadata_fig["layout"]["legend"]["itemdoubleclick"] = False
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] == "legendonly":
					trace["visible"] = False
		else:
			mds_metadata_fig["layout"]["legend"]["itemclick"] = "toggle"
			mds_metadata_fig["layout"]["legend"]["itemdoubleclick"] = "toggleothers"
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] is False :
					trace["visible"] = "legendonly"

		#div style
		if str(metadata_df.dtypes[metadata_to_plot]) == "object":
			mds_metadata_div_style = {"width": "45%", "display": "inline-block"}
		else:
			mds_metadata_div_style = {"width": "33.5%", "display": "inline-block"}

		##### CONFIG OPTIONS ####
		config_mds_metadata = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "mds_{mds_metadata}_colored_by_{metadata}".format(mds_metadata = mds_dataset, metadata = metadata_to_plot)}, "edits": {"legendPosition": True, "titleText": True}, "doubleClickDelay": 1000}

		mds_metadata_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		mds_metadata_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
		mds_metadata_fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"

		return mds_metadata_fig, config_mds_metadata, mds_metadata_div_style

	#mds feature
	@app.callback(
		Output("mds_expression", "figure"),
		Output("mds_expression", "config"),
		Output("mds_expression_div", "style"),
		Input("mds_dataset", "value"),
		Input("mds_type", "value"),
		Input("feature_dataset_dropdown", "value"),
		Input("feature_dropdown", "value"),
		Input("mds_metadata", "relayoutData"),
		Input("mds_metadata", "restyleData"),
		Input("mds_metadata", "figure"),
		State("mds_expression", "figure"),
		State("color_mapping", "data"),
		State("label_to_value", "data"),
		State("analysis_dropdown", "value"),
		prevent_initial_call=True
	)
	def plot_mds_feature(mds_dataset, mds_type, expression_dataset, feature, zoom_mds_metadata, legend_click, mds_metadata_fig, mds_expression_fig, color_mapping, label_to_value, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		height = 400

		#do not plot if there is no feature
		if feature is None:
			raise PreventUpdate

		#change umap dataset, expression dataset or gene/species: create a new figure from tsv
		if trigger_id in ["mds_type.value", "mds_dataset.value", "feature_dataset_dropdown.value", "feature_dropdown.value", "mds_metadata.figure", "mds_metadata.restyleData"] or mds_expression_fig is None:

			#get samples to keep
			samples_to_keep = []
			#parse metadata figure data 
			for trace in mds_metadata_fig["data"]:
				if trace["visible"] is True:
					for dot in trace["customdata"]:
						#stores samples to keep after filtering
						samples_to_keep.append(dot[0])
			variable_to_plot = [expression_dataset, feature, samples_to_keep]
			#create figure
			mds_expression_fig = go.Figure()
			#get msd df
			mds_df = functions.download_from_github(path, "data/" + mds_dataset + "/mds/" + mds_type + ".tsv")
			mds_df = pd.read_csv(mds_df, sep = "\t")
			color = functions.get_color(color_mapping, "Log2 expression", "continuous")
			mds_expression_fig = functions.plot_mds_continuous(mds_df, mds_type, variable_to_plot, color, mds_expression_fig, height, label_to_value, path)

		#update zoom
		mds_metadata_fig = functions.synchronize_zoom(mds_expression_fig, mds_metadata_fig)

		#get number of displayed samples
		n_samples_mds_expression = functions.get_displayed_samples(mds_metadata_fig)

		#labels for graph title
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = " expression"
		else:
			expression_or_abundance = " abundance"

		#labels for graph title
		if "lipid" in mds_dataset:
			omics = "lipidome"
			subdirs = functions.get_content_from_github(path, "data")
			if "human" in subdirs:
				mds_title = "human"
			elif "mouse" in subdirs:
				mds_title = "mouse"
		else:
			omics = "transcriptome"
		if mds_dataset in ["human", "mouse"]:
			mds_title = mds_dataset
		else:
			mds_title = mds_dataset.replace("_", " ")

		#apply title
		if "genes" in expression_dataset:
			feature_gene = feature.split("@")[0]
			feature_beast = feature.split("@")[1]
			feature_beast = feature_beast.replace("_", " ")
			feature = feature_gene + " - " + feature_beast
			mds_expression_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + mds_title + " " + omics + " MDS colored by<br>" + feature + expression_or_abundance + " n=" + str(n_samples_mds_expression)
		else:
			mds_expression_fig["layout"]["title"]["text"] = "Sample dispersion within<br>the " + mds_title + " " + omics + " MDS<br>colored by " + feature.replace("_", " ").replace("[", "").replace("]", "").replace("€", "/") + expression_or_abundance + " n=" + str(n_samples_mds_expression)

		mds_expression_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		mds_expression_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"

		##### CONFIG OPTIONS ####
		config_mds_expression = {"doubleClick": "autosize", "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "mds_{mds_metadata}_colored_by_{gene_species}_{expression_abundance}".format(mds_metadata = mds_dataset, gene_species = feature, expression_abundance = expression_or_abundance)}, "edits": {"colorbarPosition": True, "titleText": True}}
		mds_expression_div_style = {"width": "34.5%", "display": "inline-block"}

		return mds_expression_fig, config_mds_expression, mds_expression_div_style

	#boxplots
	@app.callback(
		Output("boxplots_graph", "figure"),
		Output("boxplots_graph", "config"),
		Output("x_filter_dropdown_div", "hidden"),
		Output("hide_unselected_boxplot_switch", "value"),
		Output("comparison_only_boxplots_switch", "value"),
		Output("best_conditions_boxplots_switch", "value"),
		Output("boxplots_width_slider", "value"),
		Output("boxplots_height_slider", "value"),
		Input("feature_dropdown", "value"),
		Input("x_boxplot_dropdown", "value"),
		Input("x_filter_boxplot_dropdown", "value"),
		Input("group_by_boxplot_dropdown", "value"),
		Input("y_boxplot_dropdown", "value"),
		Input("comparison_only_boxplots_switch", "value"),
		Input("best_conditions_boxplots_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("hide_unselected_boxplot_switch", "value"),
		Input("show_as_boxplot_switch", "value"),
		Input("boxplots_width_slider", "value"),
		Input("boxplots_height_slider", "value"),
		State("feature_dataset_dropdown", "value"),
		State("boxplots_graph", "figure"),
		State("x_filter_dropdown_div", "hidden"),
		State("color_mapping", "data"),
		State("analysis_dropdown", "value")
	)
	def plot_boxplots(feature, x_metadata, selected_x_values, group_by_metadata, y_metadata, comparison_only_switch, best_conditions_switch, contrast, hide_unselected_switch, show_as_boxplot, width, height, expression_dataset, box_fig, hidden, color_mapping, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#boolean switch
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_best_conditions_switch = functions.boolean_switch(best_conditions_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		boolean_show_as_boxplot = functions.boolean_switch(show_as_boxplot)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False and box_fig is not None:
			raise PreventUpdate

		#labels
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			expression_or_abundance = "expression"
			log2_expression_or_abundance = "Log2 expression"
		else:
			expression_or_abundance = "abundance"
			log2_expression_or_abundance = "Log2 abundance"

		#slider resize
		if trigger_id in ["boxplots_height_slider.value", "boxplots_width_slider.value"]:
			box_fig["layout"]["height"] = height
			box_fig["layout"]["width"] = width
			if width < 600:
				if "abundance" in box_fig["layout"]["title"]["text"]:
					box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" abundance", "<br>abundance")
				else:
					box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" expression", "<br>expression")
		#new plot
		else:
			if trigger_id != "hide_unselected_boxplot_switch.value":
				#open metadata
				metadata_df = functions.download_from_github(path, "metadata.tsv")
				metadata_df = pd.read_csv(metadata_df, sep = "\t")

				#clean metadata
				metadata_df = metadata_df.fillna("NA")
				metadata_df = metadata_df.replace("_", " ", regex=True)

				#reset hide unselected switch
				hide_unselected_switch = []
				boolean_hide_unselected_switch = False
				
				#default reset values
				if trigger_id == "comparison_only_boxplots_switch.value" or box_fig is None and boolean_comparison_only_switch:
					width = 500
					height = 375
				elif trigger_id != "comparison_only_boxplots_switch.value" and boolean_comparison_only_switch is False:
					width = 900
					height = 375

				#comparison only and best conditions switches are mutually exclusive
				if trigger_id == "comparison_only_boxplots_switch.value" and boolean_best_conditions_switch is True:
					best_conditions_switch = []
					boolean_best_conditions_switch = False
				elif trigger_id == "best_conditions_boxplots_switch.value" and boolean_comparison_only_switch is True:
					comparison_only_switch = []
					boolean_comparison_only_switch = False

				#filter samples for comparison
				repo = functions.get_repo_name_from_path(path, repos)
				if boolean_comparison_only_switch:
					contrast = contrast.replace("_", " ")
					metadata_df = metadata_df[metadata_df["condition"].isin(contrast.split("-vs-"))]
				elif boolean_best_conditions_switch:
					best_contrasts = config["repos"][repo]["best_comparisons"]
					best_conditions = []
					for best_contrast in best_contrasts:
						best_contrast = best_contrast.replace("_", " ")
						best_conditions_in_best_contrast = best_contrast.split("-vs-")
						for best_condition in best_conditions_in_best_contrast:
							if best_condition not in best_conditions:
								best_conditions.append(best_condition)
					metadata_df = metadata_df[metadata_df["condition"].isin(best_conditions)]				

				#counts as y need external file with count values
				if y_metadata in ["log2_expression", "log2_abundance"]:
					counts = functions.download_from_github(path, "data/" + expression_dataset + "/counts/" + feature + ".tsv")
					counts = pd.read_csv(counts, sep = "\t")
					counts = counts.replace("_", " ", regex=True)
					#merge and compute log2 and replace inf with 0
					metadata_df = metadata_df.merge(counts, how="inner", on="sample")
					metadata_df[log2_expression_or_abundance] = np.log2(metadata_df["counts"])
					metadata_df[log2_expression_or_abundance].replace(to_replace = -np.inf, value = 0, inplace=True)

				#get trace names
				if x_metadata == group_by_metadata:
					column_for_filtering = x_metadata

					#user defined list of condition
					if x_metadata == "condition" and config["repos"][repo]["sorted_conditions"]  and boolean_comparison_only_switch is False and boolean_best_conditions_switch is False:
						metadata_fields_ordered = config["repos"][repo]["condition_list"]
						metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
					else:
						metadata_fields_ordered = metadata_df[x_metadata].unique().tolist()
						metadata_fields_ordered.sort()
				else:
					column_for_filtering = group_by_metadata
					metadata_fields_ordered = metadata_df[group_by_metadata].unique().tolist()
					metadata_fields_ordered.sort()
				#reset visible
				visible = {}
				for metadata in metadata_fields_ordered:
					visible[metadata] = True

				#grouped or not boxplot setup
				boxmode = "overlay"
				hidden = True
				#get values that will be on the x axis
				all_x_values = metadata_df[x_metadata].unique().tolist()
				for x_value in all_x_values:
					if boxmode != "group":
						#filter df for x_value and get his traces
						filtered_metadata = metadata_df[metadata_df[x_metadata] == x_value]
						values_column_for_filtering = filtered_metadata[column_for_filtering].unique().tolist()
						#if, for the same x, there is more than one trace, then should be grouped
						if len(set(values_column_for_filtering)) > 1:
							boxmode = "group"
							hidden = False
							#keep only selected x_values
							selected_x_values = [x_value.replace("_", " ") for x_value in selected_x_values]
							metadata_df = metadata_df[metadata_df[x_metadata].isin(selected_x_values)]
				
				#tmp
				if "genes" in expression_dataset:
					feature_gene = feature.split("@")[0]
					feature_beast = feature.split("@")[1]
					feature_beast = feature_beast.replace("_", " ")
					feature = feature_gene + " - " + feature_beast

				#create figure
				box_fig = go.Figure()
				for metadata in metadata_fields_ordered:
					#slice metadata
					filtered_metadata = metadata_df[metadata_df[column_for_filtering] == metadata]
					#only 2 decimals
					filtered_metadata = filtered_metadata.round(2)
					#get x and y
					if y_metadata in ["log2_expression", "log2_abundance"]:
						y_values = filtered_metadata[log2_expression_or_abundance]
						y_axis_title = "Log2 {}".format(expression_or_abundance)
						if "genes" in expression_dataset:
							title_text = feature + " {} profile per ".format(expression_or_abundance) + x_metadata.replace("_", " ").capitalize()
						else:
							title_text = feature.replace("_", " ").replace("[", "").replace("]", "").replace("€", "/") + " {} profile per ".format(expression_or_abundance) + x_metadata.replace("_", " ").capitalize()
					else:
						y_values = filtered_metadata[y_metadata]
						y_axis_title = y_metadata
						title_text = "{y_metadata} profile per {x_metadata}".format(y_metadata=y_metadata, x_metadata=x_metadata.replace("_", " ").capitalize())
					x_values = filtered_metadata[x_metadata]

					#create hovertext
					filtered_metadata["hovertext"] = ""
					for column in filtered_metadata.columns:
						if column not in ["control", "counts", "hovertext", "fq1", "fq2", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
							filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_metadata[column].astype(str) + "<br>"
					hovertext = filtered_metadata["hovertext"].tolist()

					#create traces
					marker_color = functions.get_color(color_mapping, column_for_filtering, metadata)
					
					if boolean_show_as_boxplot: 
						box_fig.add_trace(go.Box(y=y_values, x=x_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, visible=visible[metadata]))
					else:
						box_fig.add_trace(go.Violin(y=y_values, x=x_values, name=metadata, marker_color=marker_color, hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, visible=visible[metadata], points="all"))

				#figure layout
				if width < 600:
					#apply title if not present
					if box_fig["layout"]["title"]["text"] is None:
						box_fig["layout"]["title"]["text"] = title_text
					
					if "abundance" in box_fig["layout"]["title"]["text"]:
						box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" abundance", "<br>abundance")
					else:
						box_fig["layout"]["title"]["text"] = box_fig["layout"]["title"]["text"].replace(" expression", "<br>expression")
				if boolean_show_as_boxplot:
					box_fig.update_layout(title = {"text": title_text, "x": 0.5, "xanchor": "center", "xref": "paper", "font_size": 14, "y": 0.95}, legend_title_text=group_by_metadata.capitalize(), legend_yanchor="top", legend_y=1.2, yaxis_title=y_axis_title, xaxis_automargin=True, xaxis_tickangle=-90, yaxis_automargin=True, font_family="Arial", width=width, height=height, margin=dict(t=45, b=50, l=5, r=10), boxmode=boxmode, showlegend=True)
				else:
					box_fig.update_layout(title = {"text": title_text, "x": 0.5, "xanchor": "center", "xref": "paper", "font_size": 14, "y": 0.95}, legend_title_text=group_by_metadata.capitalize(), legend_yanchor="top", legend_y=1.2, yaxis_title=y_axis_title, xaxis_automargin=True, xaxis_tickangle=-90, yaxis_automargin=True, font_family="Arial", width=width, height=height, margin=dict(t=45, b=50, l=5, r=10), violinmode=boxmode, showlegend=True)
			else:
				box_fig = go.Figure(box_fig)

			#when the switch is true, the legend is no longer interactive
			if boolean_hide_unselected_switch:
				box_fig.update_layout(legend_itemclick=False, legend_itemdoubleclick=False)
				for trace in box_fig["data"]:
					if trace["visible"] == "legendonly":
						trace["visible"] = False
			else:
				box_fig.update_layout(legend_itemclick="toggle", legend_itemdoubleclick="toggleothers")
				for trace in box_fig["data"]:
					if trace["visible"] is False:
						trace["visible"] = "legendonly"

		#general config for boxplots
		config_boxplots = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "boxplots_with_{feature}_{expression_or_abundance}_colored_by_{metadata}".format(feature=feature.replace("€", "_"), expression_or_abundance=expression_or_abundance, metadata=x_metadata)}, "edits": {"legendPosition": True, "titleText": True}, "doubleClickDelay": 1000}

		box_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		box_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
		box_fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"

		return box_fig, config_boxplots, hidden, hide_unselected_switch, comparison_only_switch, best_conditions_switch, width, height

	#MA-plot
	@app.callback(
		Output("ma_plot_graph", "figure"),
		Output("ma_plot_graph", "config"),
		Input("feature_dataset_dropdown", "value"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("feature_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def plot_MA_plot(expression_dataset, contrast, stringency_info, feature, path):

		#stingency specs
		pvalue_type = stringency_info.split("_")[0]
		pvalue_value = stringency_info.split("_")[1]

		#labels
		if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
			if expression_dataset in ["human", "mouse"]:
				feature = feature.replace("€", "/")
			else:
				feature_gene = feature.split("@")[0]
				feature_beast = feature.split("@")[1]
				feature_beast = feature_beast.replace("_", " ")
				feature = feature_gene + " - " + feature_beast
			gene_or_species = "Gene"
			expression_or_abundance = expression_dataset.split("_")[0] + " gene expression"
			xaxis_title = "Log2 average expression"
		else:
			feature = feature.replace("_", " ").replace("[", "").replace("]", "")
			xaxis_title = "Log2 average abundance"
			gene_or_species = expression_dataset.replace("_", " ")
			expression_or_abundance = gene_or_species + " abundance"
			gene_or_species = gene_or_species

		#read table
		table = functions.download_from_github(path, "data/" + expression_dataset + "/dge/" + contrast + ".diffexp.tsv")
		table = pd.read_csv(table, sep = "\t")
		table["Gene"] = table["Gene"].fillna("NA")
		#log2 base mean
		table["log2_baseMean"] = np.log2(table["baseMean"])
		#clean gene/species name
		if "genes" in expression_dataset:
			clean_genes = []
			for x in table["Gene"]:
				x_gene = x.split("@")[0]
				x_beast = x.split("@")[1]
				x_beast = x_beast.replace("_", " ")
				x = x_gene + " - " + x_beast
				clean_genes.append(x)
			table["Gene"] = clean_genes
		else:
			table["Gene"] = [x.replace("_", " ").replace("[", "").replace("]", "") for x in table["Gene"]]

		#find DEGs and selected gene
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] > 0) & (table["Gene"] != feature), "DEG"] = "Up"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] < 0) & (table["Gene"] != feature), "DEG"] = "Down"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] > 0) & (table["Gene"] == feature), "DEG"] = "selected_Up"
		table.loc[(table[pvalue_type] <= float(pvalue_value)) & (table["log2FoldChange"] < 0) & (table["Gene"] == feature), "DEG"] = "selected_Down"
		table.loc[(table["DEG"].isnull()) & (table["Gene"] != feature), "DEG"] = "no_DEG"
		table.loc[(table["DEG"].isnull()) & (table["Gene"] == feature), "DEG"] = "selected_no_DEG"

		#replace nan values with NA
		table = table.fillna(value={pvalue_type: "NA"})

		#count DEGs
		up = table[table["DEG"] == "Up"]
		up = len(up["Gene"])
		up_selected = table[table["DEG"] == "selected_Up"]
		up += len(up_selected["Gene"])
		down = table[table["DEG"] == "Down"]
		down = len(down["Gene"])
		down_selected = table[table["DEG"] == "selected_Down"]
		down += len(down_selected["Gene"])

		#find out if the selected gene have more than 1 gene ID
		filtered_table = table[table["Gene"] == feature]
		number_of_geneids_for_gene = len(filtered_table["Gene"])

		#if there are more gene ID for the same gene, a warning should appear on the ceneter of the plot
		if number_of_geneids_for_gene > 1:
			max_x = table["log2_baseMean"].max()
			min_x = table["log2_baseMean"].min()
			mid_x = (max_x + min_x)/2 
			max_y = table["log2FoldChange"].max()
			min_y = table["log2FoldChange"].min()
			mid_y = (max_y + min_y)/2

		#colors for plot traces (gray, red, blue)
		colors_ma_plot = ["#636363", "#D7301F", "#045A8D", "#636363", "#D7301F", "#045A8D"]
		colors_ma_plot = {"no_deg": "#636363", "down": "#045A8D", "up": "#D7301F", "selected": "#D9D9D9"}
		#rename column if not human
		if expression_dataset not in ["human", "mouse"]:
			table = table.rename(columns={"Gene": gene_or_species})

		#plot
		ma_plot_fig = go.Figure()
		for deg_status in ["no_DEG", "Up", "Down", "selected_no_DEG", "selected_Up", "selected_Down"]:
			#params for trace
			if "selected" in deg_status:
				marker_size = 9
				marker_line = {"color": "#525252", "width": 2}
				color = colors_ma_plot["selected"]
			else:	
				marker_size = 5
				marker_line = {"color": None, "width": None}
				if "up" in deg_status.lower():
					color = colors_ma_plot["up"]
				elif "down" in deg_status.lower():
					color = colors_ma_plot["down"]
				else:
					color = colors_ma_plot["no_deg"]
			filtered_table = table[table["DEG"] == deg_status]
			#custom data and hover template
			custom_data = filtered_table[[gene_or_species, pvalue_type, "log2_baseMean", "log2FoldChange"]]
			custom_data = custom_data.fillna("NA")
			if pvalue_type == "padj":
				pvalue_type_for_labels = "FDR"
			else:
				pvalue_type_for_labels = "P-value"
			hover_template = gene_or_species.capitalize() + ": %{{customdata[0]}}<br>{pvalue_type}: %{{customdata[1]:.2e}}<br>{expression_or_abundance}: %{{x:.2e}}<br>Log2 fold change: %{{y:.2e}}<extra></extra>".format(expression_or_abundance=xaxis_title, pvalue_type=pvalue_type_for_labels)
			
			#add trace
			ma_plot_fig.add_trace(go.Scattergl(x=filtered_table["log2_baseMean"], y=filtered_table["log2FoldChange"], marker_opacity=1, marker_color=color, marker_symbol=2, marker_size=marker_size, marker_line=marker_line, customdata=custom_data, mode="markers", hovertemplate = hover_template))

		#update layout
		title_text = "Differential {expression_or_abundance}<br>".format(expression_or_abundance=expression_or_abundance) + contrast.replace("_", " ").replace("-", " ")
		
		ma_plot_fig.update_layout(title={"text": title_text, "xref": "paper", "x": 0.5, "font_size": 14}, xaxis_automargin=True, xaxis_title=xaxis_title, yaxis_zeroline=True, yaxis_automargin=True, yaxis_title="Log2 fold change", yaxis_domain=[0.25, 1], font_family="Arial", height=415, margin=dict(t=50, b=5, l=5, r=5), showlegend=False)

		#annotations
		stringency_annotation = [dict(text = "{pvalue_type} < {stringency}".format(pvalue_type=pvalue_type_for_labels, stringency = str(float(pvalue_value))), align="right", xref="paper", yref="paper", x=0.02, y=0.25, showarrow=False, font=dict(size=14, family="Arial"))]
		up_genes_annotation = [dict(text = str(up) + " higher in<br>" + contrast.split("-vs-")[0].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.98, showarrow=False, font=dict(size=14, color="#DE2D26", family="Arial"))]
		down_genes_annotation = [dict(text = str(down) + " higher in<br>" + contrast.split("-vs-")[1].replace("_", " "), align="right", xref="paper", yref="paper", x=0.98, y=0.25, showarrow=False, font=dict(size=14, color="#045A8D", family="Arial"))]
		annotaton_title = [dict(text = "Show annotations", align="center", xref="paper", yref="paper", x=0, y=0, showarrow=False, font_size=12)]
		if number_of_geneids_for_gene == 1:
			for i in [3, 4, 5]:
				if len(ma_plot_fig["data"][i]["x"]) == 1:
					feature_name = ma_plot_fig["data"][i]["customdata"][0][0]
					feature_fdr = ma_plot_fig["data"][i]["customdata"][0][1]
					if feature_fdr != "NA":
						feature_fdr = "{:.1e}".format(feature_fdr)
					feature_log2_base_mean = ma_plot_fig["data"][i]["customdata"][0][2]
					feature_log2fc = ma_plot_fig["data"][i]["customdata"][0][3]
					x = ma_plot_fig["data"][i]["x"][0]
					y = ma_plot_fig["data"][i]["y"][0]
					selected_gene_annotation = [dict(x=x, y=y, xref="x", yref="y", text=feature_name + "<br>Log2 avg expr: " +  str(round(feature_log2_base_mean, 1)) + "<br>Log2 FC: " +  str(round(feature_log2fc, 1)) + "<br>{pvalue_type}: ".format(pvalue_type=pvalue_type_for_labels) + feature_fdr, showarrow=True, font=dict(family="Arial", size=12, color="#252525"), align="center", arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor="#525252", ax=50, ay=50, bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.9)]
		else:
			selected_gene_annotation = [dict(x=mid_x, y=mid_y, text="Multiple transcripts with the same gene name.", showarrow=False, font=dict(family="Arial", size=12, color="#252525"), align="center", bordercolor="#525252", borderwidth=2, borderpad=4, bgcolor="#D9D9D9", opacity=0.9)]

		#add default annotations
		ma_plot_fig["layout"]["annotations"] = annotaton_title + stringency_annotation + up_genes_annotation + down_genes_annotation + selected_gene_annotation

		#buttons
		ma_plot_fig.update_layout(updatemenus=[dict(
			pad=dict(r=5),
			active=0,
			xanchor = "left",
			direction = "up",
			bgcolor = "#ffffff",
			x=0,
			y=0,
			buttons=[
				dict(label="All",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]
						},
						{"annotations": annotaton_title + stringency_annotation + up_genes_annotation + down_genes_annotation + selected_gene_annotation}]
				),
				dict(label="Differential analysis",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]
						},
						{"annotations": annotaton_title + stringency_annotation + up_genes_annotation + down_genes_annotation}]
				),
				dict(label="Selected {gene_or_species}".format(gene_or_species = gene_or_species.lower()),
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}},
									{"color": colors_ma_plot["selected"], "size": 9, "symbol": 2, "line": {"color": "#525252", "width": 2}}]
						},
						{"annotations": annotaton_title + selected_gene_annotation}]
				),
				dict(label="None",
					method="update",
					args=[
						{"marker": [{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}, 
									{"color": colors_ma_plot["no_deg"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["up"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}},
									{"color": colors_ma_plot["down"], "size": 5, "symbol": 2, "line": {"color": None, "width": None}}]
						},
						{"annotations": annotaton_title}]
				)
			])
		])

		config_ma_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}, "toImageButtonOptions": {"filename": "MA-plot_with_{contrast}_stringency_{pvalue_type}_{pvalue}".format(contrast = contrast, pvalue_type = pvalue_type.replace("padj", "FDR"), pvalue = pvalue_value)}, "edits": {"annotationPosition": True, "annotationTail": True, "annotationText": True, "titleText": True}}

		ma_plot_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		ma_plot_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
		
		return ma_plot_fig, config_ma_plot
	
	#deconvolution
	@app.callback(
		Output("deconvolution_graph", "figure"),
		Output("deconvolution_graph", "config"),
		Output("plots_per_row_deconvolution_dropdown", "value"),
		Input("split_by_1_deconvolution_dropdown", "value"),
		Input("split_by_2_deconvolution_dropdown", "value"),
		Input("plots_per_row_deconvolution_dropdown", "value"),
		Input("data_sets_deconvolution_dropdown", "value"),
		Input("analysis_dropdown", "value")
	)
	def plot_deconvolution(split_by, split_by_2, plot_per_row, deconvolution_dataset, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#open deconvolution df
		deconvolution_df = functions.download_from_github(path, f"deconvolution/{deconvolution_dataset}")
		deconvolution_df = pd.read_csv(deconvolution_df, sep = "\t", low_memory=False)

		#if there is no file, do not plot
		if deconvolution_df.empty:
			raise PreventUpdate

		#clean df
		deconvolution_df[split_by] = deconvolution_df[split_by].str.replace("_", " ")
		deconvolution_df = deconvolution_df.dropna(subset = [split_by])
		
		#get cell types
		cell_types = deconvolution_df["Cell type"].unique().tolist()

		#sum proportion for each selected value
		if split_by == split_by_2:
			#group by
			grouped_df = deconvolution_df.groupby([split_by]).sum()
			grouped_df = pd.DataFrame({"proportion_sum": grouped_df["Proportion"]})
			grouped_df = grouped_df.reset_index()

			#create x_values column
			grouped_df["x_values"] = grouped_df[split_by]
			deconvolution_df["x_values"] = deconvolution_df[split_by]
		else:
			if trigger_id == "split_by_2_deconvolution_dropdown.value":
				plot_per_row = 3
			
			#clean also the second column
			deconvolution_df = deconvolution_df.dropna(subset = [split_by_2])
			deconvolution_df[split_by_2] = deconvolution_df[split_by_2].str.replace("_", " ")
			
			#group by
			grouped_df = deconvolution_df.groupby([split_by, split_by_2]).sum()
			grouped_df = pd.DataFrame({"proportion_sum": grouped_df["Proportion"]})
			grouped_df = grouped_df.reset_index()

			#create x_values column with the two variables
			grouped_df["x_values"] = grouped_df[split_by] + " " + grouped_df[split_by_2]
			deconvolution_df["x_values"] = deconvolution_df[split_by] + " " + deconvolution_df[split_by_2]

		#get values that will be on the x axis of the subplots
		x_values = deconvolution_df["x_values"].unique().tolist()
		x_values.sort()
		grouped_df = grouped_df.set_index("x_values")

		#compute relative proportion by Cell type
		filtered_df_list = []
		for x_value in x_values:
			#get value to compute relative proportion
			sum_value = grouped_df.loc[x_value, "proportion_sum"]
			#filter df for x value and compute his relative proportion
			filtered_df = deconvolution_df[deconvolution_df["x_values"] == x_value]
			filtered_df["relative_proportion"] = filtered_df["Proportion"] / sum_value
			#sum values of the same Cell type
			filtered_df = filtered_df.groupby(["Cell type"]).sum()
			#reconstruct df
			filtered_df = pd.DataFrame({"relative_proportion": filtered_df["relative_proportion"]})
			filtered_df["x_values"] = x_value
			filtered_df = filtered_df.reset_index()
			#append to list
			filtered_df_list.append(filtered_df)

		#cat dfs
		proportion_df = pd.concat(filtered_df_list)
		proportion_df["percentage_relative_proportion"] = proportion_df["relative_proportion"] * 100

		#setup deconvolution color dict
		deconvolution_color_dict = {}
		i = 0
		for cell_type in cell_types:
			deconvolution_color_dict[cell_type] = colors[i]
			i += 1

		#create figure
		fig = go.Figure()

		#define number of rows
		if (len(x_values) % plot_per_row) == 0:
			n_rows = len(x_values)/plot_per_row
		else:
			n_rows = len(x_values)/plot_per_row + 1
		n_rows = int(n_rows)

		#define specs for subplot starting from the space for the legend
		specs = []

		#define specs for each plot row
		for i in range(0, n_rows):
			specs.append([])
			for y in range(0, plot_per_row):
				specs[i].append({})
		
		#in case of odd number of selected elements, some plots in the grid are None
		if (len(x_values) % plot_per_row) != 0:
			odd_elements_to_plot = len(x_values) - plot_per_row * (n_rows - 1)
			for i in range(1, ((plot_per_row + 1) - odd_elements_to_plot)):
				specs[-1][-i] = None

		#create subplot
		fig = make_subplots(rows=n_rows, cols=plot_per_row, specs=specs, shared_yaxes="all", y_title="Relative proportion")

		#get cell types and populate figure
		working_row = 1
		working_col = 1
		showlegend = True
		split_by_for_hover = split_by.capitalize().replace("_", " ")
		split_by_2_for_hover = split_by_2.capitalize().replace("_", " ")
		for x_value in x_values:
			filtered_df = proportion_df[proportion_df["x_values"] == x_value]
			filtered_df = filtered_df.set_index("Cell type")
			for cell_type in cell_types:
				if split_by == split_by_2:
					hovertemplate = f"{split_by_for_hover}: %{{x}}<br>Cell type: {cell_type}<br>Fraction: %{{y:.0f}}%<extra></extra>"
				else:
					filtered_deconvolution_df = deconvolution_df[deconvolution_df["x_values"] == x_value]
					x_1 = filtered_deconvolution_df[split_by].unique().tolist()
					x_1 = x_1[0]
					x_2 = filtered_deconvolution_df[split_by_2].unique().tolist()
					x_2 = x_2[0]
					hovertemplate = f"{split_by_for_hover}: {x_1}<br>{split_by_2_for_hover}: {x_2}<br>Cell type: {cell_type}<br>Fraction: %{{y:.0f}}%<extra></extra>"
				fig.add_trace(go.Bar(name=cell_type, x=[x_value], y=[filtered_df.loc[cell_type, "percentage_relative_proportion"]], showlegend=showlegend, legendgroup=cell_type, marker_color=deconvolution_color_dict[cell_type], hovertemplate=hovertemplate), row=working_row, col=working_col)
			
			#adjust row and col counts
			working_col += 1
			if working_col == plot_per_row + 1:
				working_row += 1
				working_col = 1

			#showlegend only on the first tracw
			if showlegend:
				showlegend = False

			#update layout
			height = (n_rows*100) + 200
			if height == 140:
				height = 240
			#get host for title
			host = functions.get_content_from_github(path, "data")
			if "human" in host:
				host = "human"
			else:
				host = "mouse"
			title_text = "Cell type compositions by {host} transcriptome deconvolution".format(host=host)
			fig.update_layout(margin=dict(t=40, l=70, r=0), font_family="Arial", font_size=11, height=height, title={"text": title_text, "x": 0.5, "y": 0.99, "yanchor": "top"}, legend_orientation="h")

			fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
			fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"

		config_deconvolution = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5}, "toImageButtonOptions": {"filename": title_text}, "edits": {"titleText": True, "legendPosition": True}}

		return fig, config_deconvolution, plot_per_row

	#GO-plot
	@app.callback(
		Output("go_plot_graph", "figure"),
		Output("go_plot_graph", "config"),
		Output("go_plot_div", "style"),
		Input("contrast_dropdown", "value"),
		Input("stringency_dropdown", "value"),
		Input("go_plot_filter_input", "value"),
		Input("add_gsea_switch", "value"),
		State("feature_dataset_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def plot_go_plot(contrast, stringency, search_value, add_gsea_switch, expression_dataset, path):

		#metatranscriptomics does not have go
		if expression_dataset not in ["human", "mouse", "lipid", "lipid_category"]:
			expression_dataset = "human"
			repo = functions.get_repo_name_from_path(path, repos)
			stringency = config["repos"][repo]["stringency"]
		
		#boolean switch
		boolean_add_gsea_switch = functions.boolean_switch(add_gsea_switch)

		#lipid category does not have GO, load the lipid one instead
		if expression_dataset == "lipid_category":
			expression_dataset = "lipid"

		#get pvalue type and value
		pvalue_type = stringency.split("_")[0]
		pvalue_type = pvalue_type.replace("padj", "FDR").replace("pvalue", "P-value")
		pvalue_threshold = stringency.split("_")[1]

		#omics type
		if "lipid" in expression_dataset:
			omics = "lipidome"
		else:
			omics = "transcriptome"

		#open df
		if expression_dataset in ["human", "mouse"]:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + stringency + "/" + contrast + ".merged_go.tsv")
		else:
			go_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "lo/" + contrast + ".merged_go.tsv")
		go_df = pd.read_csv(go_df, sep = "\t")
		go_df = go_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
		
		#concatenate gsea results if the switch is true
		if boolean_add_gsea_switch:
			gsea_df = functions.download_from_github(path, "data/{}/".format(expression_dataset) + "gsea/" + contrast + ".merged_go.tsv")
			gsea_df = pd.read_csv(gsea_df, sep = "\t")
			gsea_df["Genes"] = [gene.replace(";", "; ") for gene in gsea_df["Genes"]]
			gsea_df = gsea_df[["DGE", "Genes", "Process~name", "num_of_Genes", "gene_group", "percentage%", "P-value"]]
			go_df = pd.concat([go_df, gsea_df])

		hide_go_axis = False
		#empty gene ontology file
		if go_df.empty:
			go_df = go_df.rename(columns={"Process~name": "Process", "percentage%": "Enrichment", "P-value": "GO p-value"})
			go_df["enrichment_interpolated"] = []
			go_df_up = go_df
			go_df_down = go_df
			all_enrichments = [33, 66, 99]
			all_enrichments_interpolated = [6, 10.5, 15]
			computed_height = 500
			hide_go_axis = True
		#gene ontology is not empty
		else:
			#filter out useless columns
			go_df = go_df[["DGE", "Process~name", "P-value", "percentage%"]]

			#define search query if present
			if search_value is not None and search_value != "":
				processes_to_keep = functions.serach_go(search_value, go_df, expression_dataset, boolean_add_gsea_switch)
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
				processes.append(process.replace("_", " "))
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
				#take go categories
				go_categories = df["Process"].tolist()

				return go_categories

			#take most important GO up and down
			go_up_categories = select_go_categories(go_df_up)
			go_down_categories = select_go_categories(go_df_down)
			
			#unique list of go categories
			all_go_categories = list(set(go_up_categories + go_down_categories))

			#find if there are double go categories (up + down)
			unique_go_categories = []
			double_go_categories = []
			for go_category in all_go_categories:
				filtered_go_df = go_df[go_df["Process"] == go_category]
				dge_values = filtered_go_df["DGE"].tolist()
				if len(dge_values) == 2:
					double_go_categories.append(go_category)
				else:
					unique_go_categories.append(go_category)

			#interpolation for enrichment dimension
			if not go_df.empty:
				go_df.loc[go_df["Enrichment"] == go_df["Enrichment"].min(), "enrichment_interpolated"] = 6
				go_df.loc[go_df["Enrichment"] == go_df["Enrichment"].max(), "enrichment_interpolated"] = 15
				go_df = go_df.sort_values(by=["Enrichment"])
				go_df = go_df.set_index("Enrichment")
				go_df["enrichment_interpolated"] = go_df["enrichment_interpolated"].interpolate(method="index")
				go_df = go_df.reset_index()
			else:
				go_df["enrichment_interpolated"] = []

			#filter df by important unique categories
			filtered_go_df = go_df[go_df["Process"].isin(unique_go_categories)]

			#divide up and down GO categories and sort by enrichment
			go_df_up = filtered_go_df[filtered_go_df["DGE"] == "up"]
			go_df_up = go_df_up.sort_values(by=["Enrichment", "GO p-value"])
			go_df_down = filtered_go_df[filtered_go_df["DGE"] == "down"]
			go_df_down = go_df_down.sort_values(by=["Enrichment", "GO p-value"])

			#if there are double categories, these should not influence the sorting of the unique one
			if len(double_go_categories) > 0:
				filtered_go_df = go_df[go_df["Process"].isin(double_go_categories)]
				go_df_up = pd.concat([go_df_up, filtered_go_df[filtered_go_df["DGE"] == "up"].sort_values(by=["Enrichment", "GO p-value"])])
				go_df_down = pd.concat([go_df_down, filtered_go_df[filtered_go_df["DGE"] == "down"].sort_values(by=["Enrichment", "GO p-value"])])

			#get enrichments as lists
			all_enrichments = go_df_up["Enrichment"].tolist() + go_df_down["Enrichment"].tolist()
			all_enrichments_interpolated = go_df_up["enrichment_interpolated"].tolist() + go_df_down["enrichment_interpolated"].tolist()

			#compute figure height
			pixels_per_go_category = 21
			computed_height = len(all_enrichments) * pixels_per_go_category

			#min and max height
			if computed_height < 500:
				computed_height = 500
			elif computed_height > 700:
				computed_height = 700

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
		go_plot_fig.add_trace(go.Scatter(x=go_df_up["DGE"], y=go_df_up["Process"], marker_size=go_df_up["enrichment_interpolated"], marker_opacity=1, marker_color=go_df_up["GO p-value"], marker_colorscale=["#D7301F", "#FCBBA1"], marker_showscale=False, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext=hover_text, hoverinfo="text"), row=1, col=1)
		#down trace
		hover_text = create_hover_text(go_df_down)
		go_plot_fig.add_trace(go.Scatter(x=go_df_down["DGE"], y=go_df_down["Process"], marker_size=go_df_down["enrichment_interpolated"], marker_opacity=1, marker_color=go_df_down["GO p-value"], marker_colorscale=["#045A8D", "#C6DBEF"], marker_showscale=False, marker_cmax=0.05, marker_cmin=0, mode="markers", hovertext=hover_text, hoverinfo="text"), row=1, col=1)

		#legend colorbar trace
		go_plot_fig.add_trace(go.Scatter(x=[None], y=[None], marker_showscale=True, marker_color = [0], marker_colorscale=["#737373", "#D9D9D9"], marker_cmax=0.05, marker_cmin=0, marker_sizemode="area", marker_colorbar=dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=(computed_height/5), y=0.68, x=0.8, xpad=0, ypad=0, xanchor="center", yanchor="middle")), row=2, col=3)

		#enrichment legend trace
		if len(all_enrichments) >= 3:
			#dimension
			min_enrichment_interpolated = min(all_enrichments_interpolated)
			max_enrichment_interpolated = max(all_enrichments_interpolated)
			mid_enrichment_interpolated = np.average([min_enrichment_interpolated, max_enrichment_interpolated])
			legend_sizes = [min_enrichment_interpolated, mid_enrichment_interpolated, max_enrichment_interpolated]

			#text
			min_enrichment = min(all_enrichments)
			max_enrichment = max(all_enrichments)
			mid_enrichment = np.average([min_enrichment, max_enrichment])
			#check for small differences
			if (mid_enrichment - min_enrichment) < 1 or (max_enrichment - mid_enrichment) < 1 or min_enrichment < 1 or mid_enrichment < 1 or max_enrichment < 1:
				min_enrichment = round(min_enrichment, 2)
				mid_enrichment = round(mid_enrichment, 2)
				max_enrichment = round(max_enrichment, 2)
			else:
				min_enrichment = round(min_enrichment)
				mid_enrichment = round(mid_enrichment)
				max_enrichment = round(max_enrichment)
			legend_sizes_text = [min_enrichment, mid_enrichment, max_enrichment]

			#coordinates
			enrichment_legend_x = [1, 1, 1]
			enrichment_legend_y = [5, 40, 75]
		elif len(all_enrichments) == 2:
			#dimension
			min_enrichment_interpolated = min(all_enrichments_interpolated)
			max_enrichment_interpolated = max(all_enrichments_interpolated)
			legend_sizes = [min_enrichment_interpolated, max_enrichment_interpolated]

			#text
			min_enrichment = min(all_enrichments)
			max_enrichment = max(all_enrichments)
			if (max_enrichment - min_enrichment) < 1 or min_enrichment < 1 or max_enrichment < 1:
				min_enrichment = round(min_enrichment, 2)
				max_enrichment = round(max_enrichment, 2)
			else:
				min_enrichment = round(min_enrichment)
				max_enrichment = round(max_enrichment)
			legend_sizes_text = [min_enrichment, max_enrichment]

			#coordinates
			enrichment_legend_x = [1, 1]
			enrichment_legend_y = [20, 60]
		elif len(all_enrichments) == 1:
			legend_sizes = all_enrichments_interpolated
			if all_enrichments[0] < 1:
				legend_sizes_text = round(all_enrichments[0], 2)
			else:
				legend_sizes_text = round(all_enrichments[0])

			#coordinates
			enrichment_legend_x = [1]
			enrichment_legend_y = [50]
		else:
			#dimension
			legend_sizes = [6, 10.5, 15]
			legend_sizes_text = [33, 66, 99]
			
			#coordinates
			enrichment_legend_x = [1, 1, 1]
			enrichment_legend_y = [5, 40, 75]
		go_plot_fig.add_trace(go.Scatter(x=enrichment_legend_x, y=enrichment_legend_y, marker_size=legend_sizes, marker_color="#737373", mode="markers+text", text=legend_sizes_text, hoverinfo="text", hovertext=legend_sizes_text, textposition="top center"), row = 5, col = 3)

		#figure layout
		if expression_dataset in ["human", "mouse"]:
			title_text = "Gene ontology enrichment plot<br>{host} {omics} DGE {pvalue_type} < {pvalue_threshold}<br>".format(host=expression_dataset.capitalize(), omics=omics, pvalue_type=pvalue_type, pvalue_threshold=pvalue_threshold) + contrast.replace("_", " ").replace("-", " ")
		else:
			title_text = "Lipid ontology enrichment plot<br>".format(host=expression_dataset.capitalize(), omics=omics, pvalue_type=pvalue_type, pvalue_threshold=pvalue_threshold) + contrast.replace("_", " ").replace("-", " ")
		go_plot_fig.update_layout(title={"text": title_text , "x": 0.75, "xanchor": "center", "font_size": 14}, 
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

		go_plot_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		go_plot_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
		go_plot_fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"

		config_go_plot = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 10, "filename": f"GO-plot_with_{contrast}"}, "responsive": True, "edits": {"titleText": True}}

		return go_plot_fig, config_go_plot, {"width": "100%", "display": "inline-block", "height": computed_height}

	#heatmap
	@app.callback(
		Output("heatmap_graph", "figure"),
		Output("heatmap_graph", "config"),
		Output("hetamap_height_slider", "value"),
		Output("hetamap_height_slider", "max"),
		Output("hetamap_width_slider", "value"),
		Output("hetamap_width_slider", "disabled"),
		Output("hetamap_height_slider", "disabled"),
		Output("comparison_only_heatmap_switch", "value"),
		Output("best_conditions_heatmap_switch", "value"),
		Input("update_heatmap_plot_button", "n_clicks"),
		Input("clustered_heatmap_switch", "value"),
		Input("comparison_only_heatmap_switch", "value"),
		Input("best_conditions_heatmap_switch", "value"),
		Input("hide_unselected_heatmap_switch", "value"),
		Input("hetamap_height_slider", "value"),
		Input("hetamap_width_slider", "value"),
		State("feature_heatmap_dropdown", "value"),
		State("heatmap_annotation_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("heatmap_graph", "figure"),
		State("contrast_dropdown", "value"),
		#resize
		State("hetamap_height_slider", "max"),
		State("hetamap_width_slider", "max"),
		State("analysis_dropdown", "value"),
		State("label_to_value", "data"),
		State("color_mapping", "data")
	)
	def plot_heatmap(n_clicks, clustered_switch, comparison_only_switch, best_conditions_switch, hide_unselected_switch, height, width, features, annotations, expression_dataset, old_figure, contrast, max_height, width_max, path, label_to_value, color_mapping):
		# jak1 jak2 jak3 stat3 stat4 stat5a stat5b

		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#transform switch to boolean switch
		boolean_clustering_switch = functions.boolean_switch(clustered_switch)
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_best_conditions_switch = functions.boolean_switch(best_conditions_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate

		#resize
		if trigger_id in ["hetamap_height_slider.value", "hetamap_width_slider.value"]:
			if height <= max_height and height >= 200 and width <= width_max and width >= 200:
				old_figure["layout"]["height"] = height
				old_figure["layout"]["width"] = width
				height_fig = height
				width_fig = width
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
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
			#coerce features to list
			if features is None:
				features = []
			#annotations will have always condition by default and these will be at the top of the other annotations
			if annotations == None or annotations == []:
				annotations = ["condition"]
			else:
				annotations.insert(0, "condition")

			#plot only if at least 2 features are present
			if len(features) >= 2:
				#get counts dfs
				counts_df_list = []
				for feature in features:
					df = functions.download_from_github(path, "data/" + expression_dataset + "/counts/" + feature + ".tsv")
					df = pd.read_csv(df, sep = "\t")
					if "genes" in expression_dataset:
						feature_gene = feature.split("@")[0]
						featre_beast = feature.split("@")[1]
						featre_beast = featre_beast.replace("_", " ")
						feature = feature_gene + " - " + featre_beast
					else:
						feature = feature.replace("€", "/")
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
				metadata = functions.download_from_github(path, "metadata.tsv")
				metadata = pd.read_csv(metadata, sep="\t")
				metadata = metadata.replace("_", " ", regex=True)
				#remove samples for which we don't have counts
				metadata = metadata[metadata["sample"].isin(counts.index)]
				metadata = metadata.set_index("sample")
				metadata_with_NA = metadata.fillna("NA")
				
				#get repo
				repo = functions.get_repo_name_from_path(path, repos)

				#by default all conditions are visible
				if config["repos"][repo]["sorted_conditions"]:
					sorted_conditions = config["repos"][repo]["condition_list"]
					conditions = [condition.replace("_", " ") for condition in sorted_conditions]
				else:
					conditions = metadata["condition"].unique().tolist()
					conditions.sort()

				#comparison only and best conditions switches are mutually exclusive
				if trigger_id == "comparison_only_heatmap_switch.value" and boolean_best_conditions_switch is True:
					best_conditions_switch = []
					boolean_best_conditions_switch = False
				elif trigger_id == "best_conditions_heatmap_switch.value" and boolean_comparison_only_switch is True:
					comparison_only_switch = []
					boolean_comparison_only_switch = False

				#parse old figure if present to get conditions to plot
				if old_figure is None or len(old_figure["data"]) == 0:
					if boolean_comparison_only_switch:
						contrast = contrast.replace("_", " ")
						conditions_to_keep = contrast.split("-vs-")
					elif boolean_best_conditions_switch:
						best_contrasts = config["repos"][repo]["best_comparisons"]
						conditions_to_keep = []
						for best_contrast in best_contrasts:
							best_contrast = best_contrast.replace("_", " ")
							best_conditions_in_best_contrast = best_contrast.split("-vs-")
							for best_condition in best_conditions_in_best_contrast:
								if best_condition not in conditions_to_keep:
									conditions_to_keep.append(best_condition)
					else:
						conditions_to_keep = conditions
				else:
					#filter samples according to legend status
					conditions_to_keep = []
					#only comparison conditions are visible
					if boolean_comparison_only_switch:
						contrast = contrast.replace("_", " ")
						conditions_to_keep = contrast.split("-vs-")
					#best conditions
					elif boolean_best_conditions_switch:
						best_contrasts = config["repos"][repo]["best_comparisons"]
						conditions_to_keep = []
						for best_contrast in best_contrasts:
							best_contrast = best_contrast.replace("_", " ")
							best_conditions_in_best_contrast = best_contrast.split("-vs-")
							for best_condition in best_conditions_in_best_contrast:
								if best_condition not in conditions_to_keep:
									conditions_to_keep.append(best_condition)
					else:
						#find out if some conditions have to be removed
						for trace in old_figure["data"]:
							#clicking on the switch to false will turn all traces to true
							if trigger_id == "comparison_only_heatmap_switch.value":
								conditions_to_keep = conditions
							#get the previous legend selection
							else:
								#only traces with a name are legend traces
								if "name" in trace.keys():
									if trace["visible"] is True:
										conditions_to_keep.append(trace["name"])

				#filter metadata and get remaining samples
				metadata = metadata[metadata["condition"].isin(conditions_to_keep)]
				samples_to_keep = metadata.index.tolist()
				#filter counts for these samples
				counts = counts[counts.index.isin(samples_to_keep)]

				#create df with features as columns
				feature_df = counts
				#create df with samples as columns
				sample_df = counts.T

				#get a list of features and samples
				features = list(sample_df.index)
				samples = list(sample_df.columns)

				#dendrogram colors
				blacks = ["#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969", "#676969"]

				#the number of yaxis will be the number of annotations + 2 (main heatmap and dendrogram), keep track of the number of annotations
				number_of_annotations = len(annotations)

				#setup figure
				fig = go.Figure()

				#top dendrogram (samples) only if switch is true
				if boolean_clustering_switch:
					dendro_top = ff.create_dendrogram(feature_df, orientation="bottom", labels=samples, colorscale=blacks)
					#set as the last yaxis
					dendro_top.update_traces(yaxis="y" + str(number_of_annotations + 2), showlegend=False)
					
					#save top dendro yaxis
					top_dendro_yaxis = "yaxis" + str(number_of_annotations + 2)
					
					#add top dendrogram traces to figure
					for trace in dendro_top["data"]:
						fig.add_trace(trace)
					
					#get clustered samples
					clustered_samples = dendro_top["layout"]["xaxis"]["ticktext"]
				#sort samples by condition
				else:
					#custom sorting
					if config["repos"][repo]["sorted_conditions"]:
						df_slices = []
						for condition in conditions:
							df_slice = metadata[metadata["condition"] == condition]
							df_slices.append(df_slice)
						metadata = pd.concat(df_slices)
					#alphabetical sort
					else:
						metadata = metadata.sort_values(by=["condition"])
					clustered_samples = metadata.index.tolist()

				#right dengrogram (features)
				dendro_side = ff.create_dendrogram(sample_df.values, orientation="left", labels=features, colorscale=blacks)
				#set as xaxis2
				dendro_side.update_traces(xaxis="x2", showlegend=False)
				#add right dendrogram data to figure
				for data in dendro_side["data"]:
					fig.add_trace(data)

				#add annotations
				y_axis_number = 2
				all_annotations_yaxis = []
				for annotation in annotations:
					
					#y axis for condition annotation
					if annotation == "condition":
						#condition must be the annotation closer to the dendrogram
						current_y_axis_number = number_of_annotations + 1
						
						#save the yaxis for condition annotation
						condition_annotation_yaxis = "yaxis" + str(current_y_axis_number)

						#get elements with clustered order
						clustered_features = dendro_side["layout"]["yaxis"]["ticktext"]
					#y axis for any other annotation
					else:
						current_y_axis_number = y_axis_number
						#save all additional annotation yaxis in a list
						all_annotations_yaxis.append("yaxis" + str(current_y_axis_number))

					#get clustered annotation
					clustered_annotations = []
					for sample in clustered_samples:
						clustered_annotations.append(metadata_with_NA.loc[sample, annotation])
					
					#discrete annotation
					if str(metadata.dtypes[annotation]) == "object":
						hovertemplate = "{annotation}: ".format(annotation=annotation.capitalize()) + "%{customdata}<Br>Sample: %{x}<extra></extra>"
						if annotation == "condition" and config["repos"][repo]["sorted_conditions"]:
							values_for_discrete_color_mapping = conditions
						else:
							values_for_discrete_color_mapping = metadata_with_NA[annotation].unique().tolist()
							values_for_discrete_color_mapping.sort()

						#color mapping
						annotation_colors = []
						#link between condition and number for discrete color mapping
						annotation_number_mapping = {}
						i = 0
						for value in values_for_discrete_color_mapping:
							#give a number to the condition
							annotation_number_mapping[value] = i
							#map a color to this number
							annotation_colors.append(functions.get_color(color_mapping, annotation, value))
							#increase incrementals
							i += 1

						#translate clustered conditions in numbers
						z = []
						for value in clustered_annotations:
							z.append(annotation_number_mapping[value])
						zmin = 0
						zmax = i-1
						if zmax == 0:
							zmax = 1
							annotation_colors = annotation_colors + annotation_colors
					#continuous annotation
					else:
						hovertemplate = "{annotation}: ".format(annotation=annotation.capitalize()) + "%{z}<Br>Sample: %{x}<extra></extra>"
						annotation_colors = ["#FFFFFF", functions.get_color(color_mapping, annotation, "continuous")]
						z = []
						for sample in clustered_samples:
							z.append(metadata.loc[sample, annotation])
						zmin = min(z)
						zmax = max(z)

					#create annotation heatmap
					annotation_heatmap = go.Heatmap(z=[z], x=clustered_samples, y=[label_to_value[annotation]], colorscale=annotation_colors, customdata=[clustered_annotations], showscale=False, hovertemplate=hovertemplate, hoverlabel_bgcolor="lightgrey", zmin=zmin, zmax=zmax)
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
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					feature = "Gene"
					colorbar_title = "gene expression"
					space_for_legend = 80
				else:
					feature = expression_dataset.replace("_", " ").capitalize()
					colorbar_title = expression_dataset.replace("_", " ") + " abundance"
					space_for_legend = 200

				#create main heatmap
				heatmap = go.Heatmap(x=clustered_samples, y=clustered_features, z=heat_data, colorscale="Reds", hovertemplate="Sample: %{{x}}<br>{feature}: %{{y}}<extra></extra>".format(feature=feature), hoverlabel_bgcolor="lightgrey", colorbar_title="Row scaled " + colorbar_title, colorbar_title_side="right", colorbar_title_font_family="Arial", colorbar_thicknessmode="pixels", colorbar_thickness=20, colorbar_lenmode="pixels", colorbar_len=100)
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
				max_height = dendro_top_height + 50*30 + heigth_multiplier*number_of_annotations + 50
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

				#legend click behaviour
				if boolean_hide_unselected_switch:
					legend_itemclick = False
					legend_itemdoubleclick = False
				else:
					legend_itemclick = "toggle"
					legend_itemdoubleclick = "toggleothers"
				#add traces for legend
				for condition in conditions:
					if condition in conditions_to_keep:
						visible = True
					else:
						if boolean_hide_unselected_switch:
							visible = False
						else:
							visible = "legendonly"
					fig.add_trace(go.Scatter(x=[None], y=[None], marker_color=functions.get_color(color_mapping, "condition", condition), marker_size=8, mode="markers", showlegend=True, name=condition, visible=visible))

				#update layout
				fig.update_layout(title_text=colorbar_title.capitalize() + " heatmap" + clustered_or_sorted, title_font_family="arial", title_font_size=14, title_x=0.5, title_y = 0.98, plot_bgcolor="rgba(0,0,0,0)", legend_title="Condition", legend_title_side="top", legend_orientation="h", legend_tracegroupgap=0.05, margin_t=30, margin_b=0, margin_l=0, margin_r=0, legend_x=0, legend_y=0, legend_yanchor="top", legend_xanchor="left", legend_itemclick=legend_itemclick, legend_itemdoubleclick=legend_itemdoubleclick, width=width_fig, height=height_fig)
				
				config_filename_title = colorbar_title + " heatmap" + clustered_or_sorted
				disabled = False
				max_height = height_fig + 200
				
				fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
				fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
				fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"
			else:
				fig = go.Figure()
				fig.add_annotation(text="Please select at least two features to plot the heatmap.", showarrow=False)
				width_fig = 885
				height_fig = 450
				max_height = height_fig
				config_filename_title = "empty_heatmap"
				fig.update_layout(xaxis_linecolor="rgb(255,255,255)", yaxis_linecolor="rgb(255,255,255)", xaxis_showticklabels=False, yaxis_showticklabels=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_ticks="", yaxis_ticks="")
				disabled = True

		config_fig = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "width": width_fig, "height": height_fig, "scale": 5, "filename": config_filename_title}, "edits": {"colorbarPosition": True, "legendPosition": True, "titleText": True}}

		return fig, config_fig, height_fig, max_height, width_fig, disabled, disabled, comparison_only_switch, best_conditions_switch

	#heatmap annotation legend
	@app.callback(
		Output("heatmap_legend_div", "children"),
		Output("heatmap_legend_div", "hidden"),
		Input("heatmap_graph", "figure"),
		State("heatmap_annotation_dropdown", "value"),
		State("color_mapping", "data"),
		State("analysis_dropdown", "value")
	)
	def plot_heatmap_annotation_legend(heatmap_fig, annotations, color_mapping, path):
		#setup empty children
		children = []

		#no annotations
		if len(annotations) == 0:
			hidden = True
		#any number of annotation
		else:
			hidden = False
			#open metadata
			metadata = functions.download_from_github(path, "metadata.tsv")
			metadata = pd.read_csv(metadata, sep="\t")
			metadata = metadata.replace("_", " ", regex=True)
			metadata_with_NA = metadata.fillna("NA")

			#filter metadata for selected conditions in the heatmap condition legend
			if len(heatmap_fig["data"]) > 0:
				conditions_to_keep = []
				for trace in heatmap_fig["data"]:
					#find out if there is the legend in the trace
					if "name" in trace:
						if trace["visible"] is True:
							conditions_to_keep.append(trace["name"])
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
					for i in range(1, 6):
						if i <= number_of_missing_elements:
							last_row.append({})
						else:
							last_row.append(None)
					specs.append(last_row)
				#any non-last row will be filled by plots
				else:
					specs.append([{}, {}, {}, {}, {}])
					specs_done += 5
			
			#find out how many categories will have each annotation and use the one with the most categories as a reference
			max_categories = 0
			discrete_annotation_count = 1
			#order names for subplots: first discrete, then continue
			discrete_annotations = []
			continuous_annotations = []
			for annotation in annotations:
				if str(metadata.dtypes[annotation]) == "object":
					discrete_annotations.append(annotation.capitalize())
					categories = metadata[annotation].unique().tolist()
					number_of_categories = len(categories)
					#the continue annotations will be after the discrete, 
					#so count the number of discrete annotations to see where will be the first continue x and y axes
					discrete_annotation_count += 1
				else:
					continuous_annotations.append(annotation)
					number_of_categories = 5
				
				#update the number of max categories
				if number_of_categories > max_categories:
					max_categories = number_of_categories

			#make subplot
			fig = make_subplots(rows=rows, cols=5, specs=specs, subplot_titles=discrete_annotations + continuous_annotations, shared_yaxes=True, horizontal_spacing=0)

			#setup loop
			discrete_legends = []
			continue_legends = []
			#loop over annotations
			for annotation in annotations:		
				#discrete annotation
				if str(metadata.dtypes[annotation]) == "object":
					#get unique categories for legend creation
					categories_for_legend = metadata_with_NA[annotation].unique().tolist()
					categories_for_legend.sort()

					#the starting point depends on the number of categories related to the legend with more categories
					y = 1
					if len(categories_for_legend) < max_categories:
						y += max_categories - len(categories_for_legend)
					#add traces to legend
					discrete_legend = []
					for category in categories_for_legend:
						trace = go.Scatter(x=[1], y=[y], marker_color=functions.get_color(color_mapping, annotation, category), marker_size=8, mode="markers+text", name=category, text= "   " + category, textposition="middle right", hoverinfo="none")
						discrete_legend.append(trace)
						y += 1
					#transparent trace to move the colored markes on the left of the area
					trace = go.Scatter(x=[3], y=[1, max_categories], marker_color="rgb(255,255,255)", hoverinfo="none")
					discrete_legend.append(trace)
					discrete_legends.append(discrete_legend)
				
				#continuous annotation
				else:
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
					trace = go.Scatter(x = [None], y = [None], marker_showscale=True, marker_color=metadata[annotation], marker_colorscale=["#FFFFFF", functions.get_color(color_mapping, annotation, "continuous")], marker_colorbar=dict(thicknessmode="pixels", thickness=20, lenmode="pixels", len=80, x=colorbar_x, y=colorbar_y, xanchor="right"))
					continue_legend.append(trace)

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
					if working_col == 6:
						working_col = 1
						working_row += 1

			#update axes
			fig.update_xaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_yaxes(linecolor="rgb(255,255,255)", showticklabels=False, fixedrange=True, ticks="")
			fig.update_annotations(font_size=12, xanchor="left")
			#move legend titles to the left so that they line up with markers
			for annotation in fig["layout"]["annotations"]:
				current_x = annotation["x"]
				annotation["x"] = current_x - 0.102
				current_y = annotation["y"]
				annotation["y"] = current_y
			#compute height
			category_height = 20
			subplot_title_height = 30
			row_height = (category_height*max_categories) + subplot_title_height
			height = (row_height*rows)
			#update layout
			fig.update_layout(width=900, height=height, showlegend=False, margin=dict(t=30, b=10, l=0, r=0, autoexpand=False))

			#add figure to children
			children.append(dcc.Graph(figure=fig, config={"modeBarButtonsToRemove": ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "hoverClosestGl2d", "hoverClosestPie", "toggleHover", "sendDataToCloud", "toggleSpikelines", "resetViewMapbox", "hoverClosestCartesian", "hoverCompareCartesian"], "toImageButtonOptions": {"format": "png", "width": 885, "height": height, "scale": 5, "filename": "heatmap_legend_for_" + "_".join(annotations)}}))

			fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
			fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
			fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"
			
		return children, hidden

	#multiboxplots
	@app.callback(
		Output("multi_boxplots_graph", "figure"),
		Output("multi_boxplots_graph", "config"),
		Output("multi_boxplots_div", "hidden"),
		Output("multiboxplot_div", "style"),
		Output("x_filter_dropdown_multiboxplots_div", "hidden"),
		Output("comparison_only_multiboxplots_switch", "value"),
		Output("best_conditions_multiboxplots_switch", "value"),
		Output("hide_unselected_multiboxplots_switch", "value"),
		Output("multiboxplots_height_slider", "value"),
		Output("multiboxplots_width_slider", "value"),
		Output("update_multiboxplot_stats_button", "n_clicks"),
		Input("update_multiboxplot_plot_button", "n_clicks"),
		Input("x_multiboxplots_dropdown", "value"),
		Input("group_by_multiboxplots_dropdown", "value"),
		Input("y_multiboxplots_dropdown", "value"),
		Input("comparison_only_multiboxplots_switch", "value"),
		Input("best_conditions_multiboxplots_switch", "value"),
		Input("hide_unselected_multiboxplots_switch", "value"),
		Input("show_as_multiboxplot_switch", "value"),
		Input("x_filter_multiboxplots_dropdown", "value"),
		Input("plot_per_row_multiboxplots_dropdown", "value"),
		Input("multiboxplots_height_slider", "value"),
		Input("multiboxplots_width_slider", "value"),
		State("contrast_dropdown", "value"),
		State("feature_multi_boxplots_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("multi_boxplots_graph", "figure"),
		State("multi_boxplots_div", "hidden"),
		State("x_filter_dropdown_multiboxplots_div", "hidden"),
		State("analysis_dropdown", "value"),
		State("color_mapping", "data"),
		State("update_multiboxplot_stats_button", "n_clicks"),
	)
	def plot_multiboxplots(n_clicks_multiboxplots, x_metadata, group_by_metadata, y_metadata, comparison_only_switch, best_conditions_switch, hide_unselected_switch, show_as_boxplot_switch, selected_x_values, plot_per_row, height, width, contrast, selected_features, expression_dataset, box_fig, hidden_status, x_filter_div_hidden, path, color_mapping, n_clicks_update_multiboxplot_stats):
		# MEN1; CIT; NDC80; AURKA; PPP1R12A; XRCC2; ENSA; AKAP8; BUB1B; TADA3; DCTN3; JTB; RECQL5; YEATS4; CDK11B; RRM1; CDC25B; CLIP1; NUP214; CETN2
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]

		#boolean swithces
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_best_conditions_switch = functions.boolean_switch(best_conditions_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)
		boolean_show_as_boxplot_switch = functions.boolean_switch(show_as_boxplot_switch)

		#do not update the plot for change in contrast if the switch is off
		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate

		#title text
		if expression_dataset in ["human", "mouse"]:
			title_text = "{host} gene expression profiles per ".format(host=expression_dataset.capitalize()) + x_metadata.replace("_", " ").capitalize()
		elif "genes" in expression_dataset:
			title_text = "{} expression profiles per".format(expression_dataset.replace("_genes", " gene").capitalize())
		else:
			title_text = "{} abundance profiles per ".format(expression_dataset.replace("_", " ").replace("archaea", "archaeal").replace("bacteria", "bacterial").capitalize()) + x_metadata.replace("_", " ").capitalize()

		#open metadata
		metadata_df_full = functions.download_from_github(path, "metadata.tsv")
		metadata_df_full = pd.read_csv(metadata_df_full, sep = "\t")

		#clean metadata
		metadata_df_full = metadata_df_full.fillna("NA")
		metadata_df_full = metadata_df_full.replace("_", " ", regex=True)
		
		#empty dropdown
		if selected_features is None or selected_features == []:
			hidden_status = True
			x_filter_div_hidden = True
		#filled dropdown
		else:
			if trigger_id not in ["hide_unselected_multiboxplots_switch.value", "multiboxplots_height_slider.value", "multiboxplots_height_slider.value"]:

				#if there is a change in the plot, hide unselected must be false
				hide_unselected_switch = []
				boolean_hide_unselected_switch = False

				#comparison only and best conditions switches are mutually exclusive
				if trigger_id == "comparison_only_multiboxplots_switch.value" and boolean_best_conditions_switch is True:
					best_conditions_switch = []
					boolean_best_conditions_switch = False
				elif trigger_id == "best_conditions_multiboxplots_switch.value" and boolean_comparison_only_switch is True:
					comparison_only_switch = []
					boolean_comparison_only_switch = False

				#filter samples for comparison or for best conditions
				if boolean_comparison_only_switch:
					contrast = contrast.replace("_", " ")
					metadata_df_full = metadata_df_full[metadata_df_full["condition"].isin(contrast.split("-vs-"))]
				elif boolean_best_conditions_switch:
					repo = functions.get_repo_name_from_path(path, repos)
					best_contrasts = config["repos"][repo]["best_comparisons"]
					best_conditions = []
					for best_contrast in best_contrasts:
						best_contrast = best_contrast.replace("_", " ")
						best_conditions_in_best_contrast = best_contrast.split("-vs-")
						for best_condition in best_conditions_in_best_contrast:
							if best_condition not in best_conditions:
								best_conditions.append(best_condition)
					metadata_df_full = metadata_df_full[metadata_df_full["condition"].isin(best_conditions)]

				#create figure
				box_fig = go.Figure()
				
				#define number of rows
				if (len(selected_features) % plot_per_row) == 0:
					n_rows = len(selected_features)/plot_per_row
				else:
					n_rows = int(len(selected_features)/plot_per_row) + 1
				n_rows = int(n_rows)

				#define specs for subplot starting from the space for the legend
				specs = []

				#define specs for each plot row
				for i in range(0, n_rows):
					specs.append([])
					for y in range(0, plot_per_row):
						specs[i].append({})
				
				#in case of odd number of selected elements, some plots in the grid are None
				if (len(selected_features) % plot_per_row) != 0:
					odd_elements_to_plot = len(selected_features) - plot_per_row * (n_rows - 1)
					for i in range(1, ((plot_per_row + 1) - odd_elements_to_plot)):
						specs[-1][-i] = None
				
				#compute height
				height = 250 + n_rows*220
				row_height = 1/n_rows
				row_heights = []
				for i in range(0, n_rows):
					row_heights.append(row_height)

				#labels
				if expression_dataset in ["human", "mouse"] or "genes" in expression_dataset:
					expression_or_abundance = "expression"
					log2_expression_or_abundance = "Log2 expression"
				else:
					expression_or_abundance = "abundance"
					log2_expression_or_abundance = "Log2 abundance"

				if y_metadata in ["log2_expression", "log2_abundance"]:
					y_axis_title = "Log2 {}".format(expression_or_abundance)
				else:
					y_axis_title = y_metadata

				#make subplots
				subplot_titles = []
				for feature in selected_features:
					if "genes" in expression_dataset:
						feature_gene = feature.split("@")[0]
						feature_beast = feature.split("@")[1]
						feature_beast = feature_beast.replace("_", " ")
						feature = feature_gene + " - " + feature_beast
					else:
						feature = feature.replace("[", "").replace("]", "").replace("_", " ").replace("€", "/")
					subplot_titles.append(feature)
				box_fig = make_subplots(rows=n_rows, cols=plot_per_row, specs=specs, subplot_titles=subplot_titles, shared_xaxes=True, vertical_spacing=(0.25/(n_rows)), y_title=y_axis_title, row_heights=row_heights)

				#loop 1 plot per gene
				working_row = 1
				working_col = 1
				showlegend = True
				for feature in selected_features:
					#counts as y need external file with count values
					if y_metadata in ["log2_expression", "log2_abundance"]:
						counts = functions.download_from_github(path, "data/" + expression_dataset + "/counts/" + feature + ".tsv")
						counts = pd.read_csv(counts, sep = "\t")
						counts = counts.replace("_", " ", regex=True)
						#merge and compute log2 and replace inf with 0
						metadata_df = metadata_df_full.merge(counts, how="inner", on="sample")
						metadata_df[log2_expression_or_abundance] = np.log2(metadata_df["counts"])
						metadata_df[log2_expression_or_abundance].replace(to_replace = -np.inf, value = 0, inplace=True)
					else:
						metadata_df = metadata_df_full.copy()

					#setup traces
					if x_metadata == group_by_metadata:
						column_for_filtering = x_metadata
						
						repo = functions.get_repo_name_from_path(path, repos)
						
						#user defined list of traces
						if x_metadata == "condition" and config["repos"][repo]["sorted_conditions"] and boolean_comparison_only_switch is False and boolean_best_conditions_switch is False:
							metadata_fields_ordered = config["repos"][repo]["condition_list"]
							metadata_fields_ordered = [condition.replace("_", " ") for condition in metadata_fields_ordered]
						else:
							metadata_fields_ordered = metadata_df[x_metadata].unique().tolist()
							metadata_fields_ordered.sort()
					else:
						column_for_filtering = group_by_metadata
						metadata_fields_ordered = metadata_df[group_by_metadata].unique().tolist()
						metadata_fields_ordered.sort()

					#grouped or not boxplot setup
					boxmode = "overlay"
					x_filter_div_hidden = True
					#get values that will be on the x axis
					all_x_values = metadata_df[x_metadata].unique().tolist()
					for x_value in all_x_values:
						if boxmode != "group":
							#filter df for x_value and get his traces
							filtered_metadata = metadata_df[metadata_df[x_metadata] == x_value]
							values_column_for_filtering = filtered_metadata[column_for_filtering].unique().tolist()
							#if, for the same x, there is more than one trace, then should be grouped
							if len(set(values_column_for_filtering)) > 1:
								boxmode = "group"
								x_filter_div_hidden = False
								#keep only selected x_values
								selected_x_values = [x_value.replace("_", " ") for x_value in selected_x_values]
								metadata_df = metadata_df[metadata_df[x_metadata].isin(selected_x_values)]

					#plot
					for metadata in metadata_fields_ordered:
						#slice metadata
						filtered_metadata = metadata_df[metadata_df[column_for_filtering] == metadata]
						#only 2 decimals
						filtered_metadata = filtered_metadata.round(2)
						#get x and y
						if y_metadata in ["log2_expression", "log2_abundance"]:
							y_values = filtered_metadata[log2_expression_or_abundance]
						else:
							y_values = filtered_metadata[y_metadata]
						x_values = filtered_metadata[x_metadata]

						#create hovertext
						filtered_metadata["hovertext"] = ""
						for column in filtered_metadata.columns:
							if column not in ["control", "counts", "hovertext", "fq1", "fq2", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
								filtered_metadata["hovertext"] = filtered_metadata["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_metadata[column].astype(str) + "<br>"
						hovertext = filtered_metadata["hovertext"].tolist()

						#create traces
						marker_color = functions.get_color(color_mapping, column_for_filtering, metadata)
						if boolean_show_as_boxplot_switch:
							box_fig.add_trace(go.Box(x=x_values, y=y_values, name=metadata, marker_color=marker_color, boxpoints="all", hovertext=hovertext, hoverinfo="text", legendgroup=metadata, showlegend=showlegend, offsetgroup=metadata, marker_size=3, line_width=4, visible=True), row=working_row, col=working_col)
						else:
							box_fig.add_trace(go.Violin(x=x_values, y=y_values, name=metadata, marker_color=marker_color, points="all", hovertext=hovertext, hoverinfo="text", legendgroup=metadata, showlegend=showlegend, offsetgroup=metadata, marker_size=3, line_width=4, visible=True), row=working_row, col=working_col)

					#just one legend for trece showed is enough
					if showlegend is True:
						showlegend = False

					#row and column count
					working_col += 1
					#reset count
					if working_col > plot_per_row:
						working_col = 1
						working_row += 1
				
				#update layout
				box_fig.update_xaxes(tickangle=-90)
				if boolean_show_as_boxplot_switch:
					box_fig.update_layout(height=height, width=width, title={"text": title_text, "x": 0.5, "y": 0.99, "yanchor": "top"}, font_size=14, font_family="Arial", boxmode=boxmode, legend_title_text=group_by_metadata.capitalize(), legend_y=1, legend_tracegroupgap=5, showlegend=True)
				else:
					box_fig.update_layout(height=height, width=width, title={"text": title_text, "x": 0.5, "y": 0.99, "yanchor": "top"}, font_size=14, font_family="Arial", violinmode=boxmode, legend_title_text=group_by_metadata.capitalize(), legend_y=1, legend_tracegroupgap=5, showlegend=True)
			else:
				box_fig = go.Figure(box_fig)
				if trigger_id in ["multiboxplots_height_slider.value", "multiboxplots_height_slider.value"]:
					box_fig.update_layout(height=height, width=width)
			
			#when the switch is true, the legend is no longer interactive
			if boolean_hide_unselected_switch:
				box_fig.update_layout(legend_itemclick=False, legend_itemdoubleclick=False)
				for trace in box_fig["data"]:
					if trace["visible"] == "legendonly":
						trace["visible"] = False
			else:
				box_fig.update_layout(legend_itemclick="toggle", legend_itemdoubleclick="toggleothers")
				for trace in box_fig["data"]:
					if trace["visible"] is False :
						trace["visible"] = "legendonly"

			#hidden div status
			hidden_status = False

			#transparent figure
			box_fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
			box_fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
			box_fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"

		config_multi_boxplots = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "multiboxplots_{title_text}".format(title_text = title_text.replace(" ", "_") + x_metadata)}, "edits": {"legendPosition": True, "titleText": True}}

		multiboxplot_div_style = {"height": height, "width": "100%", "display":"inline-block"}

		return box_fig, config_multi_boxplots, hidden_status, multiboxplot_div_style, x_filter_div_hidden, comparison_only_switch, best_conditions_switch, hide_unselected_switch, height, width, n_clicks_update_multiboxplot_stats
	
	#correlation plot
	@app.callback(
		Output("feature_correlation_plot", "figure"),
		Output("feature_correlation_plot", "config"),
		Output("correletion_stats", "data"),
		Output("hide_unselected_correlation_switch", "options"),
		Output("correlation_width_slider", "value"),
		Output("correlation_height_slider", "value"),
		Input("x_correlation_dropdown", "value"),
		Input("y_correlation_dropdown", "value"),
		Input("group_by_correlation_dropdown", "value"),
		Input("comparison_only_correlation_switch", "value"),
		Input("contrast_dropdown", "value"),
		Input("hide_unselected_correlation_switch", "value"),
		Input("correlation_width_slider", "value"),
		Input("correlation_height_slider", "value"),
		State("x_dataset_correlation_dropdown", "value"),
		State("y_dataset_correlation_dropdown", "value"),
		State("color_mapping", "data"),
		State("feature_correlation_plot", "figure"),
		State("hide_unselected_correlation_switch", "options"),
		State("correletion_stats", "data"),
		State("label_to_value", "data"),
		State("analysis_dropdown", "value")
	)
	def plot_feature_correlation(x, y, group_by_column, comparison_only_switch, contrast, hide_unselected_switch, width_fig, height_fig, dataset_x, dataset_y, color_mapping, fig, hide_unselected_switch_options, statistics_data, label_to_value, path):
		x = "TNF"
		y = "ALOX5"
		group_by_column = "condition"
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		
		#boolean switches
		boolean_comparison_only_switch = functions.boolean_switch(comparison_only_switch)
		boolean_hide_unselected_switch = functions.boolean_switch(hide_unselected_switch)

		if trigger_id == "contrast_dropdown.value" and boolean_comparison_only_switch is False:
			raise PreventUpdate
		
		#size changes
		if trigger_id in ["correlation_width_slider.value", "correlation_height_slider.value"]:
			fig["layout"]["height"] = height_fig
			fig["layout"]["width"] = width_fig
		#new plot
		else:
			#open metadata
			metadata_df = functions.download_from_github(path, "metadata.tsv")
			metadata_df = pd.read_csv(metadata_df, sep = "\t")
			#comparison only will filter the samples
			if boolean_comparison_only_switch:
				metadata_df = metadata_df[metadata_df["condition"].isin(contrast.split("-vs-"))]
			metadata_df = metadata_df.replace("_", " ", regex=True)
			
			#empty plot
			if x is None or y is None:
				fig = go.Figure()
				fig.add_annotation(text="Please select x and y", showarrow=False, font_size=16)
				width_fig = 600
				height_fig = 450
				config_filename_title = "empty_correlation"
				fig.update_layout(xaxis_linecolor="rgb(255,255,255)", yaxis_linecolor="rgb(255,255,255)", xaxis_showticklabels=False, yaxis_showticklabels=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_ticks="", yaxis_ticks="")
			#plot
			else:
				#same feature on x an y
				if x == y:
					counts = functions.download_from_github(path, "data/" + dataset_x + "/counts/" + x + ".tsv")
					counts = pd.read_csv(counts, sep = "\t")
				
					#expression or abundance for x
					if dataset_x in ["human", "mouse"] or "genes" in dataset_x:
						expression_or_abundance = "expression"
					else:
						expression_or_abundance = "abundance"
					expression_or_abundance_x = f"Log2 {expression_or_abundance} {x}"

					#log2
					counts[expression_or_abundance_x] = np.log2(counts["counts"])
					merged_df = counts.rename(columns={"Gene": f"{x}"})

					#x and y are the same
					expression_or_abundance_y = expression_or_abundance_x

				#different features on x and y
				else:
					#get counts
					counts_x = functions.download_from_github(path, "data/" + dataset_x + "/counts/" + x + ".tsv")
					counts_x = pd.read_csv(counts_x, sep = "\t")
					#expression or abundance for x
					if dataset_x in ["human", "mouse"] or "genes" in dataset_x:
						expression_or_abundance = "expression"
					else:
						expression_or_abundance = "abundance"
					expression_or_abundance_x = f"Log2 {expression_or_abundance} {x}"
					#log2
					counts_x[expression_or_abundance_x] = np.log2(counts_x["counts"])
					counts_x = counts_x.rename(columns={"Gene": f"{x}"})

					counts_y = functions.download_from_github(path, "data/" + dataset_y + "/counts/" + y + ".tsv")
					counts_y = pd.read_csv(counts_y, sep = "\t")
					#expression or abundance for y
					if dataset_y in ["human", "mouse"] or "genes" in dataset_y:
						expression_or_abundance = "expression"
					else:
						expression_or_abundance = "abundance"
					expression_or_abundance_y = f"Log2 {expression_or_abundance} {y}"
					#log2
					counts_y[expression_or_abundance_y] = np.log2(counts_y["counts"])
					counts_y = counts_y.rename(columns={"Gene": f"{y}"})

					#merge counts
					merged_df = counts_x.merge(counts_y, how="inner", on="sample")

				#merge with metadata
				merged_df = merged_df.merge(metadata_df, how="inner", on="sample")
				
				#prepare for hover data
				metadata_columns = []
				for column in label_to_value:
					metadata_columns.append(label_to_value[column])
				merged_df = merged_df.rename(columns=label_to_value)
				merged_df[metadata_columns] = merged_df[metadata_columns].fillna("NA")

				#plot figure without group by
				if group_by_column is None:
					fig = px.scatter(merged_df, x=expression_or_abundance_x, y=expression_or_abundance_y, hover_data=metadata_columns, trendline="ols", trendline_color_override="black")
					fig.update_traces(marker_color="darkgray")

					#get statistics
					statistics_results = px.get_trendline_results(fig)
					#format scientific notation for pvalue
					pvalue_f = f"{statistics_results.px_fit_results.iloc[0].f_pvalue:.1e}".replace("e-0", "e-")
					#get rsquared
					r_squared = round(statistics_results.px_fit_results.iloc[0].rsquared, 1)

					#check if the slope is negative
					line_slope = re.match(r".+\s=\s(.+)\s\*", fig["data"][1]["hovertemplate"]).group(1)
					if float(line_slope) < 0:
						r_squared = -r_squared

					#add annotation and change hovertemplate
					correlation_statistics = f"R<sup>2</sup>={r_squared} p={pvalue_f}"
					fig.add_annotation(text=correlation_statistics, showarrow=False, font=dict(family="Arial", size=12, color="black"), xref="paper", yref="paper", x=0.1, y=0.1)
					fig["data"][0]["hovertemplate"] = fig["data"][0]["hovertemplate"].replace("=", ": ")
					fig["data"][1]["hovertemplate"] = correlation_statistics
				
				#plot figure with group by
				else:
					original_group_by_column = group_by_column
					group_by_column = label_to_value[group_by_column]
					#find out if some of the groups have only 1 sample, which make it impossible to compute correlation
					group_count = merged_df[group_by_column].value_counts()
					group_count = pd.DataFrame(group_count)
					group_count = group_count[group_count[group_by_column] != 1]
					#filter keep good groups
					merged_df = merged_df[merged_df[group_by_column].isin(list(group_count.index))]
					
					#sort metadata by group column
					merged_df = merged_df.sort_values(by=[group_by_column])
					
					#get colors from metadata
					groups = merged_df[group_by_column].unique().tolist()
					group_colors = []
					for group in groups:
						group_colors.append(functions.get_color(color_mapping, original_group_by_column, group))
					
					#same feature on both axis
					fig = px.scatter(merged_df, x=expression_or_abundance_x, y=expression_or_abundance_y, color=group_by_column, color_discrete_sequence=group_colors, trendline="ols", hover_data=metadata_columns,)
					fig.update_traces(visible=True)
					fig.update_layout(legend_title=group_by_column.capitalize(), legend_orientation="h", legend_yanchor="top", legend_y=-0.2)

					#add statistics to plot
					statistics_results = px.get_trendline_results(fig)

					#save correlation statistics, check slope and update line hovertemplate
					statistics_data = {}
					for trace in fig["data"]:
						if trace["mode"] == "lines":
							#get group
							group = trace["name"]
							
							#extract results
							group_results = statistics_results.query(f"{group_by_column} == '{group}'").px_fit_results.iloc[0]
							#format scientific notation for pvalue
							pvalue_f = f"{group_results.f_pvalue:.1e}".replace("e-0", "e-")
							#get rsquared
							r_squared = round(group_results.rsquared, 1)

							#check if the slope is negative
							line_slope = re.match(r".+\s=\s(.+)\s\*", trace["hovertemplate"]).group(1)
							if float(line_slope) < 0:
								r_squared = -r_squared

							#save annotation text so that it can be used again later on legend update
							annotation_text = f"R<sup>2</sup>={r_squared} p={pvalue_f}"
							statistics_data[group] = annotation_text

							#update hover template for line
							trace["hovertemplate"] = statistics_data[group]
						#update hover template for markers
						elif trace["mode"] == "markers":
							trace["hovertemplate"] = trace["hovertemplate"].replace("=", ": ")

				#update layout and config variables
				width_fig = 400
				height_fig = 450
				fig.update_layout(font_family="Arial", title_text="Pearson correlation", title_xanchor="center", title_x=0.5, width=width_fig, height=height_fig, margin_r=0)
		
		#transparent background
		fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"
		fig["layout"]["legend_bgcolor"] = "rgba(0,0,0,0)"

		#config
		config_filename_title = f"{x}_{y}_correlation"
		config_fig = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": config_filename_title}, "edits": {"colorbarPosition": True, "legendPosition": True, "titleText": True, "annotationPosition": True}}

		#hide unselected legend items
		if group_by_column is None:
			hide_unselected_switch_options = [{"label": "", "value": [], "disabled": True}]
		else:
			hide_unselected_switch_options = [{"label": "", "value": []}]
			if boolean_hide_unselected_switch:
				fig["layout"]["legend"]["itemclick"] = False
				fig["layout"]["legend"]["itemdoubleclick"] = False
				for trace in fig["data"]:
					if trace["visible"] == "legendonly":
						trace["visible"] = False
			else:
				fig["layout"]["legend"]["itemclick"] = "toggle"
				fig["layout"]["legend"]["itemdoubleclick"] = "toggleothers"
				for trace in fig["data"]:
					if trace["visible"] is False :
						trace["visible"] = "legendonly"

		return fig, config_fig, statistics_data, hide_unselected_switch_options, width_fig, height_fig

	#statistics correlation plot
	@app.callback(
		Output("statistics_feature_correlation_plot", "figure"),
		Output("statistics_feature_correlation_plot", "config"),
		Output("statistics_feature_correlation_plot_div", "hidden"),
		Input("correletion_stats", "data"),
		Input("feature_correlation_plot", "figure"),
		Input("feature_correlation_plot", "restyleData"),
		State("group_by_correlation_dropdown", "value"),
		State("color_mapping", "data"),
	)
	def update_statistics_correlation(statistics_data, correlation_fig, legend_click, group_by_column, color_mapping):

		#hide div if any group by column is specified
		if group_by_column is None:
			hidden = True
			fig = go.Figure()
		else:
			hidden = False
			
			#get visible groups from trace visibility status
			visible_groups = []
			i = 0
			for trace in correlation_fig["data"]:
				#count only markers and not lines
				if trace["mode"] == "markers":
					if trace["visible"] == True:
						visible_groups.append(trace["name"])
					i += 1
			
			#create fig
			fig = go.Figure()
			fig.update_layout(xaxis_linecolor="rgb(255,255,255)", yaxis_linecolor="rgb(255,255,255)", xaxis_showticklabels=False, yaxis_showticklabels=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_ticks="", yaxis_ticks="", margin=dict(l=0, r=0, t=0, b=0))
			
			#setup loop and coordinates
			annotation_x = 0.05
			annotation_y = 1
			for group in visible_groups:
				#retrive statistics text from data
				annotation_text = statistics_data[group]
				
				#add annotation
				fig.add_annotation(text=annotation_text, showarrow=False, font=dict(family="Arial", size=12, color=functions.get_color(color_mapping, group_by_column, group)), xref="paper", yref="paper", xanchor="left", yanchor="top", x=annotation_x, y=annotation_y, name=group, hovertext=group.capitalize())

				#move coordinates for the next annotation
				annotation_y -= 0.05

		#transparent background
		fig["layout"]["paper_bgcolor"] = "rgba(0,0,0,0)"
		fig["layout"]["plot_bgcolor"] = "rgba(0,0,0,0)"

		#config
		config_fig = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "correlation_stats"}}

		return fig, config_fig, hidden

	#diversity plot
	@app.callback(
		Output("diversity_graph", "figure"),
		Output("diversity_graph", "config"),
		Input("group_by_diversity_dropdown", "value"),
		State("feature_dataset_dropdown", "value"),
		State("color_mapping", "data"),
		State("analysis_dropdown", "value")
	)
	def plot_species_diversity(group_by, expression_dataset, color_mapping, path):
		
		#make subplots
		#plots = ["Species diversity<br>by Shannon index", "Species dominance<br>by Simpson index", "Species dominance<br>by Inverse Simpson index"]
		#fig = make_subplots(rows=1, cols=3, subplot_titles=plots, y_title="Index")
		plots = ["Species diversity<br>by Shannon index", "Species dominance<br>by Simpson index"]
		fig = make_subplots(rows=1, cols=2, subplot_titles=plots, y_title="Index")

		#populate subplots
		col = 1
		showlegend = True
		for plot in plots:

			#define which file to open
			if plot == "Species diversity<br>by Shannon index":
				file_name = "shannon"
				index_column = "Shannon_index"
			elif plot == "Species dominance<br>by Simpson index":
				file_name = "simpson"
				index_column = "Simpson_index"
			elif plot == "Species dominance<br>by Inverse Simpson index":
				file_name = "invsimpson"
				index_column = "Inversed_Simpson_index"

			#open df
			diversity_df = functions.download_from_github(path, f"diversity/{expression_dataset}/{file_name}.tsv")
			diversity_df = pd.read_csv(diversity_df, sep = "\t")
			diversity_df = diversity_df.replace("_", " ", regex=True)

			#get x values
			x_values = diversity_df[group_by].unique().tolist()
			x_values.sort()

			#add traces for each x value
			for x_value in x_values:
				filtered_diversity_df = diversity_df[diversity_df[group_by] == x_value]
				marker_color = functions.get_color(color_mapping, group_by, x_value)

				#create hovertext
				filtered_diversity_df["hovertext"] = ""
				for column in filtered_diversity_df.columns:
					if column not in ["control", "counts", "hovertext", "fq1", "fq2", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
						filtered_diversity_df["hovertext"] = filtered_diversity_df["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_diversity_df[column].astype(str) + "<br>"
				hovertext = filtered_diversity_df["hovertext"].tolist()

				fig.add_trace(go.Violin(x=filtered_diversity_df[group_by], y=filtered_diversity_df[index_column], name=x_value, marker_color=marker_color, hoverinfo="text", marker_size=3, line_width=4, hovertext=hovertext, legendgroup=x_value, showlegend=showlegend, points="all"), row=1, col=col)

			#next subplot
			if showlegend:
				showlegend=False
			col += 1
		
		#update final layout
		fig.update_layout(legend_orientation="h", height=500, legend_yanchor="bottom", legend_y=1.25)
		fig.update_xaxes(tickangle=-90)

		#add tab with figure
		config = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": f"{expression_dataset}_diversity"}, "edits": {"legendPosition": True, "annotationText": True}}

		return fig, config
	
	##### mofa callbacks #####

	#data overview
	@app.callback(
		Output("mofa_data_overview", "figure"),
		Output("mofa_data_overview", "config"),
		Input("mofa_comparison_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def plot_data_overview_mofa(group_contrast, path):
		
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == ".":
			raise PreventUpdate

		#get groups from mofa contrast
		groups = group_contrast.split("-vs-")

		#open df
		data_overview_df = functions.download_from_github(path, f"mofa/{group_contrast}/data_overview.tsv")
		data_overview_df = pd.read_csv(data_overview_df, sep = "\t")

		##get titles
		subplot_titles = []
		for group in groups:
			group_data_overview_df = data_overview_df[data_overview_df["group"] == group]
			n = group_data_overview_df["ntotal"].unique().tolist()
			n = n[0]
			n = n.replace("N", "n")
			clean_group = group.replace("_", " ")
			title = f"{clean_group} {n}"
			subplot_titles.append(title)

		#create figure
		fig = make_subplots(rows=2, cols=1, subplot_titles=subplot_titles)

		#define colorscale
		colorscale = [[0, na_color], [1, "#02818a"]]

		#loop over groups
		row=1
		for group in groups:
			group_data_overview_df = data_overview_df[data_overview_df["group"] == group]

			#heatmap x and y
			x = group_data_overview_df["sample"].unique().tolist()
			group_data_overview_df["y"] = group_data_overview_df["view"].str.replace("_", " ") + "<br>" + group_data_overview_df["ptotal"].str.replace("D", "n")
			y = group_data_overview_df["y"].unique().tolist()

			#get z for each level in y
			z = []
			levels = group_data_overview_df["view"].unique().tolist()
			for level in levels:
				#translate true/false in numbers for z
				z_for_level = []
				level_group_data_overview_filtered = group_data_overview_df[group_data_overview_df["view"] == level]
				values = level_group_data_overview_filtered["value"].tolist()
				for value in values:
					if value:
						z_for_level.append(1)
					else:
						z_for_level.append(0)
				z.append(z_for_level)

			#create heatmap
			fig.add_trace(go.Heatmap(x=x, y=y, z=z, zmax=1, colorscale=colorscale, showscale=False, hovertemplate="Sample: %{x}<extra></extra>"), row=row, col=1)

			#change row
			row +=1

		#compute height
		height = 80+(35*len(levels)*2)
		if height < 250:
			height = 250

		#update layout
		fig.update_xaxes(visible=False)
		fig.update_layout(height=height, margin_t=80, margin_b=0, margin_r=0, title={"text": "Data overview", "font_size": 20, "x": 0.5, "xanchor": "center"})

		#config
		config = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": f"data_overview_{group_contrast}"}, "edits": {"titleText": True, "annotationText": True}}

		return fig, config

	#variance hetmap
	@app.callback(
		Output("mofa_variance_heatmap", "figure"),
		Output("mofa_variance_heatmap", "config"),
		Input("mofa_comparison_dropdown", "value"),
		State("analysis_dropdown", "value")
	)
	def plot_variance_heatmap(group_contrast, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == ".":
			raise PreventUpdate
		
		#get groups from mofa contrast
		groups = group_contrast.split("-vs-")
		groups = [group.replace("_", " ") for group in groups]

		#open df
		variance_heatmap_df = functions.download_from_github(path, f"mofa/{group_contrast}/variance_explained_heatmap.tsv")
		variance_heatmap_df = pd.read_csv(variance_heatmap_df, sep = "\t")
		variance_heatmap_df = variance_heatmap_df.replace([np.inf, -np.inf], None)
		variance_heatmap_df = variance_heatmap_df.replace("_", " ", regex=True)
		variance_heatmap_df.columns = variance_heatmap_df.columns.str.replace("_", " ")

		#get zmax and zmin
		zmax = None
		zmin = None
		for column in variance_heatmap_df.columns:
			if column not in ["factor", "group"]:
				column_max = variance_heatmap_df[column].max()
				column_min = variance_heatmap_df[column].min()
				if zmax is None or column_max > zmax:
					zmax = column_max
				if zmin is None or column_min < zmin:
					zmin = column_min

		#create subplots
		fig = make_subplots(rows=1, cols=2, subplot_titles=groups, shared_yaxes=True)

		#loop over groups
		col = 1
		for group in groups:
			filtered_df = variance_heatmap_df[variance_heatmap_df["group"] == group]
			filtered_df = filtered_df.drop(["group"], axis=1)
			filtered_df = pd.melt(filtered_df, id_vars="factor")

			#get x and y
			x = filtered_df["variable"].unique().tolist()
			y = filtered_df["factor"].unique().tolist()

			#get z for each y (factor)
			z = []
			for factor in y:
				factor_filtered_df = filtered_df[filtered_df["factor"] == factor]
				z.append(factor_filtered_df["value"].tolist())

			#show colorbar only once
			if col == 1:
				showscale = True
			else:
				showscale = False

			#add heatmap
			fig.add_trace(go.Heatmap(x=x, y=y, z=z, zmax=zmax, zmin=zmin, zauto=False, colorscale=["white", "#02818a"], showscale=showscale, colorbar_title="Variance explained", colorbar_title_side="right", colorbar_ticksuffix="%", colorbar_thickness=15, hovertemplate="Layer: %{x}<br>Factor: %{y}<br>Variance explained: %{z:.0f}%<extra></extra>", hoverongaps=False), row=1, col=col)

			#change subplot
			col += 1				

		#update layout
		fig.update_layout(height=200+(20*len(y)), margin_t=75, margin_b=0, title={"text": "Multi-layer signatures", "font_size": 20, "x": 0.5, "xanchor": "center"}, plot_bgcolor="#d9d9d9")
		fig.update_xaxes(tickangle=-90)

		#config
		config = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": f"mofa_signatures_{group_contrast}"}, "edits": {"titleText": True, "annotationText": True}}

		return fig, config

	#factor plot
	@app.callback(
		Output("mofa_factor_plot", "figure"),
		Output("mofa_factor_plot", "config"),
		Input("mofa_comparison_dropdown", "value"),
		Input("mofa_variance_heatmap", "clickData"),
		State("analysis_dropdown", "value")
	)
	def plot_factor_plot(group_contrast, click_data, path):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == ".":
			raise PreventUpdate

		#default plot is the one which explain more variance
		if trigger_id == "mofa_comparison_dropdown.value":
			variance_heatmap_df = functions.download_from_github(path, f"mofa/{group_contrast}/variance_explained_heatmap.tsv")
			variance_heatmap_df = pd.read_csv(variance_heatmap_df, sep = "\t")
			
			#get max variance explained
			max_variance = None
			for column in variance_heatmap_df.columns:
				if column not in ["factor", "group"]:
					column_max = variance_heatmap_df[column].max()
					if max_variance is None or column_max > max_variance:
						view = column
						max_variance = column_max
			
			#given vew and max, get factor
			variance_heatmap_df = variance_heatmap_df[variance_heatmap_df[view] == max_variance]
			factor = variance_heatmap_df["factor"].tolist()
			factor = factor[0]
		#click on heatmap
		else:
			factor = click_data["points"][0]["y"]
			view = click_data["points"][0]["x"]
			view = view.replace(" ", "_")

		#open weights df
		weights_df = functions.download_from_github(path, f"mofa/{group_contrast}/weights.tsv")
		weights_df = pd.read_csv(weights_df, sep = "\t")
		
		#filter by factor and value and then sort by value
		weights_df = weights_df[weights_df["factor"] == factor]
		weights_df = weights_df[weights_df["view"] == view]

		#get first 10 (and the others which have the same value as the 10th)
		weights_df["abs_value"] = weights_df["value"].abs()
		weights_df = weights_df.sort_values(by=["abs_value"], ascending=False)
		#get top 10 df
		top_10_df = weights_df.head(10)
		#find lower value of top 10
		top_10_last_value = top_10_df["abs_value"].unique().tolist()
		top_10_last_value = min(top_10_last_value)
		#get all features with the lower value
		features_with_top_10_last_value = weights_df[weights_df["abs_value"] == top_10_last_value]
		features_with_top_10_last_value = features_with_top_10_last_value["feature"].tolist()
		#concat if there are multiple features with the same lower value
		if len(features_with_top_10_last_value) > 1:
			weights_df = weights_df[weights_df["feature"].isin(features_with_top_10_last_value)]
			weights_df = pd.concat(top_10_df, weights_df)
		else:
			weights_df = top_10_df

		#sort by value so that positive numbers will be on the top
		weights_df = weights_df.sort_values(by=["value"], ascending=True)

		#clean features
		clean_features = []
		for index, row in weights_df.iterrows():
			view = row["view"]
			feature = row["feature"]
			if view in feature:
				feature = feature.split("_")[0]
			feature = feature.replace("[", "").replace("]", "")
			clean_features.append(feature)
		weights_df["feature"] = clean_features

		#create figure with dots
		fig = go.Figure(go.Scatter(x=weights_df["value"], y=weights_df["feature"], marker_color="#02818a", marker_size=8, showlegend=False, mode="markers", hovertemplate="Feature: %{y}<br>Weight: %{x:.1f}<extra></extra>"))
		
		#add lines
		weights_df = weights_df.reset_index()
		for i in range(0, len(weights_df)):
			fig.add_shape(type='line', x0=0, y0=i, x1=weights_df["value"][i], y1=i, line=dict(color="#02818a", width=3))

		#update layout
		view = view.replace("_", " ")
		fig.update_layout(title={"text": f"Top features per {factor} in {view}", "font_size": 16, "x": 0.5, "xanchor": "center"}, xaxis_title_text="Weight", yaxis_title_text="Feature", margin_t=40)
		fig.update_xaxes(zeroline=True)
		fig.update_yaxes(showline=False)

		#config
		config = {"modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "mofa_factor"}, "edits": {"titleText": True, "annotationText": True}}

		return fig, config

	#all factors plot
	@app.callback(
		Output("mofa_all_factors_values", "figure"),
		Output("mofa_all_factors_values", "config"),
		Input("mofa_comparison_dropdown", "value"),
		Input("group_condition_switch_mofa", "value"),
		State("analysis_dropdown", "value"),
		State("color_mapping", "data")
	)
	def plot_all_factor_values(group_contrast, switch_value, path, color_mapping):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == ".":
			raise PreventUpdate

		#get which metadata variable to use for x axis
		if len(switch_value) == 0:
			metadata_column = "group"
		else:
			metadata_column = "condition"

		#get groups from mofa contrast
		groups = group_contrast.split("-vs-")

		#open weights df
		factors_df = functions.download_from_github(path, f"mofa/{group_contrast}/factors.tsv")
		factors_df = pd.read_csv(factors_df, sep = "\t")
		factors_df = factors_df.replace("_", " ", regex=True)

		#get all factors
		factors = factors_df["factor"].unique().tolist()
		factors.sort()

		#create figure
		fig = make_subplots(rows=1, cols=len(factors), subplot_titles=factors, horizontal_spacing=0.4/len(factors))

		#populate subplots
		col = 1
		for factor in factors:
			filtered_factor_df = factors_df[factors_df["factor"] == factor]
			
			#get groups
			groups = filtered_factor_df[metadata_column].unique().tolist()
			groups.sort(reverse=True)

			#add groups violins
			for group in groups:
				group_df = filtered_factor_df[filtered_factor_df[metadata_column] == group]
				x_values = group_df[metadata_column].tolist()
				y_values = group_df["value"].tolist()
				marker_color = functions.get_color(color_mapping, metadata_column, group)

				#create hovertext
				group_df["hovertext"] = ""
				for column in group_df.columns:
					if column not in ["control", "counts", "hovertext", "fq1", "fq2", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
						group_df["hovertext"] = group_df["hovertext"] + column.replace("_", " ").capitalize() + ": " + group_df[column].astype(str) + "<br>"
				hovertext = group_df["hovertext"].tolist()

				fig.add_trace(go.Violin(x=x_values, y=y_values, name=group, marker_color=marker_color, hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, points="all", showlegend=False), row=1, col=col)
				if col == 1:
					fig.update_yaxes(title_text="Factor score", title_standoff=5, row=1, col=col)

			#new subplot
			col += 1
		
		#update layout
		fig.update_layout(margin_l=10, margin_r=0, margin_t=40, height=225)
		fig.update_annotations(font_size=14)

		#config
		config = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": "factor_score_distribution"}}

		return fig, config

	#feature expression or abundance
	@app.callback(
		Output("mofa_factor_expression_abundance", "figure"),
		Output("mofa_factor_expression_abundance", "config"),
		Input("mofa_factor_plot", "figure"),
		Input("mofa_factor_plot", "clickData"),
		Input("group_condition_switch_mofa", "value"),
		State("mofa_comparison_dropdown", "value"),
		State("analysis_dropdown", "value"),
		State("color_mapping", "data")
	)
	def plot_factor_feature(factor_figure, click_data, switch_value, group_contrast, path, color_mapping):
		#define contexts
		ctx = dash.callback_context
		trigger_id = ctx.triggered[0]["prop_id"]
		if trigger_id == ".":
			raise PreventUpdate

		#get which metadata variable to use for x axis
		if len(switch_value) == 0:
			metadata_column = "group"
		else:
			metadata_column = "condition"

		#get mofa level to understand which feature list to use for searching
		level = factor_figure["layout"]["title"]["text"]
		level = re.match(r"Top features per Factor\d in (Archaea|Bacteria|Fungi|Human|Mouse|Protozoa|Viral) \w+", level).group(1)
		level = level.lower()
		if level in ["human", "mouse"]:
			features_df = "data/" + level + "/counts/genes_list.tsv"
			log2_expression_or_abundance = "Log2 expression"
		else:
			level = level + "_species"
			features_df = "data/" + level + "/counts/feature_list.tsv"
			log2_expression_or_abundance = "Log2 abundance"

		#get features and their clean version
		features_df = functions.download_from_github(path, features_df)
		features_df = pd.read_csv(features_df, sep = "\t", header=None, names=["feature"])
		features_df["clean_feature"] = features_df["feature"].str.replace("_", " ", regex=False).str.replace("[", "", regex=False).str.replace("]", "", regex=False).str.replace("€", "/", regex=False)

		#setup
		if trigger_id in ["mofa_factor_plot.figure", "group_condition_switch_mofa.value"]:
			df = pd.DataFrame({"feature": factor_figure["data"][0]["y"], "weight": factor_figure["data"][0]["x"]})
			df["abs_weight"] = df["weight"].abs()
			max_weight = df["abs_weight"].max()
			df = df[df["abs_weight"] == max_weight]
			clean_feature = df["feature"].tolist()
			clean_feature = clean_feature[0]
		#user click
		else:
			clean_feature = click_data["points"][0]["y"]

		#search feature counts
		feature = features_df[features_df["clean_feature"] == clean_feature]
		feature = feature["feature"].tolist()
		feature = feature[0]

		counts = functions.download_from_github(path, "data/" + level + "/counts/" + feature + ".tsv")
		counts = pd.read_csv(counts, sep = "\t")
		counts = counts.replace("_", " ", regex=True)
		
		#open metadata
		metadata = functions.download_from_github(path, "metadata.tsv")
		metadata = pd.read_csv(metadata, sep = "\t")

		#filter metadata, keep only conditions which contain the groups
		groups = group_contrast.split("-vs-")
		metadata = metadata[metadata["group"].isin(groups)]

		#clean metadata
		metadata = metadata.fillna("NA")
		metadata = metadata.replace("_", " ", regex=True)

		#merge and compute log2 and replace inf with 0
		metadata = metadata.merge(counts, how="inner", on="sample")
		metadata[log2_expression_or_abundance] = np.log2(metadata["counts"])
		metadata[log2_expression_or_abundance].replace(to_replace = -np.inf, value = 0, inplace=True)

		#plot per condition
		conditions = metadata[metadata_column].unique().tolist()
		conditions.sort()
		
		#setup plot
		fig = go.Figure()
		for condition in conditions:
			filtered_df = metadata[metadata[metadata_column] == condition]

			x_values = filtered_df[metadata_column].tolist()
			y_values = filtered_df[log2_expression_or_abundance].tolist()
			marker_color = functions.get_color(color_mapping, metadata_column, condition)

			#create hovertext
			filtered_df["hovertext"] = ""
			for column in filtered_df.columns:
				if column not in ["control", "counts", "hovertext", "fq1", "fq2", "analysis_path", "host", "metatranscriptomics", "immune_profiling"]:
					filtered_df["hovertext"] = filtered_df["hovertext"] + column.replace("_", " ").capitalize() + ": " + filtered_df[column].astype(str) + "<br>"
			hovertext = filtered_df["hovertext"].tolist()

			#add trace
			fig.add_trace(go.Violin(x=x_values, y=y_values, name=condition, marker_color=marker_color, hovertext=hovertext, hoverinfo="text", marker_size=3, line_width=4, points="all"))

		#update layout
		fig.update_layout(title={"text": f"{clean_feature}", "font_size": 16, "x": 0.5, "xanchor": "center"}, yaxis_title=log2_expression_or_abundance, height=142, margin_t=30, margin_b=0, margin_l=0)
		fig.update_xaxes(showticklabels=False)

		#general config for boxplots
		config = {"doubleClickDelay": 1000, "modeBarButtonsToRemove": ["select2d", "lasso2d", "hoverClosestCartesian", "hoverCompareCartesian", "resetScale2d", "toggleSpikelines"], "toImageButtonOptions": {"format": "png", "scale": 5, "filename": f"{clean_feature}_profiling"}, "edits": {"legendPosition": True, "titleText": True}}

		return fig, config
