#import packages
import pandas as pd
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_table
import urllib.parse
import functions
from functions import config

#metadata dropdown and table
metadata = functions.download_from_github("metadata.tsv")
metadata = pd.read_csv(metadata, sep = "\t")
metadata = metadata.replace("_", " ", regex=True)
tissues = metadata["tissue"].unique().tolist()
tissues.sort()
metadata_options = [{"label": "Condition", "value": "condition"}]
annotation_options = []
label_to_value = {"sample": "Sample", "condition": "Condition"}
columns_to_keep = []
for column in metadata.columns:
	#color by and heatmap annotation dropdowns
	if column not in ["sample", "fq1", "fq2", "condition", "control", "raw_counts", "kraken2", "immune_profiling_vdj"]:
		#dict used for translating colnames
		label_to_value[column] = column.capitalize().replace("_", " ")
		if len(metadata[column].unique().tolist()) < 21:
			metadata_options.append({"label": column.capitalize().replace("_", " "), "value": column})
			annotation_options.append({"label": column.capitalize().replace("_", " "), "value": column})
	#metadata teble columns
	if column not in [ "fq1", "fq2", "control", "raw_counts", "kraken2", "immune_profiling_vdj"]:
		columns_to_keep.append(column)
#shape metadata table
metadata_table = metadata[columns_to_keep]
metadata_table = metadata_table.rename(columns=label_to_value)
metadata_table_columns = []
for column in metadata_table.columns:
	metadata_table_columns.append({"name": column.capitalize().replace("_", " "), "id": column})
metadata_table_data = metadata_table.to_dict("records")
metadata_table_link = metadata_table.to_csv(index=False, encoding="utf-8", sep="\t")
metadata_table_link = "data:text/tsv;charset=utf-8," + urllib.parse.quote(metadata_table_link)

#get all subdir to populate expression dataset
subdirs = functions.get_content_from_github("data")
expression_datasets_options = []
mds_dataset_options = []
for dir in subdirs:
	if dir in ["human", "mouse"]:
		organism = dir
		expression_datasets_options.append({"label": dir.capitalize(), "value": dir})
		mds_dataset_options.append({"label": dir.capitalize(), "value": dir})	
	else:
		kingdom = dir.split("_")[0]
		lineage = dir.split("_")[1]
		expression_datasets_options.append({"label": kingdom.capitalize() + " by " + lineage, "value": dir})
		if "species" in dir:
			metatranscriptomics_content = functions.get_content_from_github("data/" + dir)
			#check if there is mds for each metatranscriptomics
			if "mds" in metatranscriptomics_content:
				mds_dataset_options.append({"label": kingdom.capitalize(), "value": dir})

#evidences
old_evidence_options = [
	{"label": "TODO", "value": "TODO"},
	{"label": "TODO_2", "value": "TODO_2"}
]

new_evidence_options = [
	{"label": "TODO", "value": "TODO"},
	{"label": "TODO_2", "value": "TODO_2"}
]

#styles for tabs and selected tabs
tab_style = {
	"padding": 6, 
	"backgroundColor": "#FAFAFA"
}

tab_selected_style = {
    "padding": 6
}

#header type
if config["header"]["logo"] == "NA":
	header_content = html.Div(config["header"]["text"], style={"font-size": 50})
else:
	header_content = html.Img(src=config["header"]["logo"], alt="logo", style={"width": "70%", "height": "70%"}, title=config["header"]["text"])

#app layout
layout = html.Div([			
	html.Div([
		#logo
		html.Div([
			html.Img(src="assets/logo.png", alt="logo", style={"width": "70%", "height": "70%"}, title="Tamma means talking drum in West Africa, where it’s also known as _dundun_. It is a small drum, played with a curved stick and having a membrane stretched over one end or both ends of a narrow-waisted wooden frame by cords whose tension can be manually altered to vary the drum's tonality as it is played. This image has been designed using resources from Flaticon.com."
			),
		]),

		#main content
		html.Div([
			#menù
			html.Div([html.Img(src="assets/menu.png", alt="menu", style={"width": "100%", "height": "100%"})
			], style = {"width": "100%", "display": "inline-block"}),

			#general options dropdowns
			html.Div([
				#mds dataset dropdown
				html.Label(["Cluster by", 
					dcc.Dropdown(
						id="mds_dataset",
						clearable=False,
						options=mds_dataset_options,
						value=organism
				)], style={"width": "7%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

				#metadata dropdown
				html.Label(["Color by", 
							dcc.Dropdown(
								id="metadata_dropdown",
								clearable=False,
								options=metadata_options,
								value="condition"
				)], style={"width": "9%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),

				#expression dataset dropdown
				html.Label(["Expression", 
							dcc.Dropdown(
								id="expression_dataset_dropdown",
								clearable=False,
								options=expression_datasets_options,
								value="human"
				)], style={"width": "11%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),

				#gene/specie dropdown
				html.Div([
					html.Label(id = "gene_species_label", children = ["Loading...", 
						dcc.Dropdown(
							id="gene_species_dropdown",
							clearable=False
						)
					], style={"width": "100%"}),
				], style={"width": "28%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),

				#tissue filter for contrast dropdown
				html.Label(["Filter comparisons by",
							dcc.Dropdown(
								value="All",
								id="comparison_filter_dropdown",
								clearable=False,
				)], style={"width": "14%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),

				#contrast dropdown
				html.Label(["Comparison", 
							dcc.Dropdown(
								value="Ileum_CD-vs-Ileum_Control",
								id="contrast_dropdown",
								clearable=False,
				)], style={"width": "25%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),

				#stringecy dropdown
				html.Label(["FDR", 
							dcc.Dropdown(
								id="stringency_dropdown",
								clearable=False
				)], style={"width": "6%", "display": "inline-block", 'margin-left': 'auto', 'margin-right': 'auto', "textAlign": "left"}),
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),

			#legend
			html.Div([
				#update button + contrast only switch
				html.Div([
					#button
					html.Br(),
					html.Div([
						dbc.Button("Update plots", id="update_legend_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})
					], style={"width": "100%", "display": "inline-block"}),
					
					#contrast only switch
					html.Br(),
					html.Br(),
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="contrast_only_switch",
							switch=True
						)
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"})
				], style={"width": "10%", "display": "inline-block", "vertical-align": "top"}),

				#legend
				html.Div([
					dcc.Loading(
						children = html.Div([
							dcc.Graph(id="legend", config={"displayModeBar": False}),
						], id="legend_div", hidden=True),
						type = "dot",
						color = "#33A02C"
					)
				], style={"width": "85%", "display": "inline-block", "margin-bottom": -180}),
			], style={"width":"100%", "display": "inline-block", "position":"relative", "z-index": -1}),

			#mds metadata
			html.Div(id="mds_metadata_div", children=[
				#info mds metadata
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_mds_metadata", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Low-dimensional embedding of high-dimensional data (e.g., 55k genes in the human transcriptome) by Uniform Manifold Approximation and Projection (UMAP).  
							
							Click the ___legend___ to choose which group you want to display.  
							Click the ___MDS dataset___ dropdown to change multidimensional scaling.  
							Click the ___Color by___ dropdown to change sample colors.  
							Click the ___Comparison only___ button to display only the samples from the two comparisons.

							Click the ___Show legend___ button to display the legend under the plot as well.
							""")
						],
						target="info_mds_metadata",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "height": 40}),
				#show legend switch
				html.Label(["Show legend",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[],
						id="show_legend_metadata_switch",
						switch=True
					)
				], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "height": 40}),
				#plot
				dcc.Loading(
					id = "loading_mds_metadata",
					children = dcc.Graph(id="mds_metadata"),
					type = "dot",
					color = "#33A02C"
				)
			], style={"width": "46.5%", "display": "inline-block"}),

			#mds expression
			html.Div(id="mds_expression_div", children=[
				#info mds expression
				html.Div([
					html.Img(src="assets/info.png", alt="info", id="info_mds_expression", style={"width": 20, "height": 20}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Low-dimensional embedding of high-dimensional data (e.g., 55k genes in the human transcriptome) by Uniform Manifold Approximation and Projection (UMAP).  
							
							Click the ___Host gene___ / ___Species___ / ___Family___ / ___Order___ dropdown to change the expression/abundance profile.
							""")
						],
						target="info_mds_expression",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "height": 40}),
				#plot
				dcc.Loading(
					id = "loading_mds_expression",
					children = dcc.Graph(id="mds_expression"),
					type = "dot",
					color = "#33A02C"
				)
			], style={"width": "53.5%", "display": "inline-block"}),

			#MA-plot + boxplots + go plot
			html.Div([
				#MA-plot + boxplots
				html.Div([
					#info MA-plot
					html.Div([
						html.Img(src="assets/info.png", alt="info", id="info_ma_plot", style={"width": 20, "height": 20}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Differential expression/abundance visualization by MA plot, with gene/species/family/order dispersion in accordance with the fold change between conditions and their average expression/abundance.
								
								Click on the ___Comparison___ dropdown to change the results.
								Click on the ___FDR___ dropdown to change visualization in accordance with the stringency.

								Click on the ___Show gene stats___ button to display its statistics.  
								Click a dot inside the plot to change the gene/species/family/order of interest.
								""")
							],
							target="info_ma_plot",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "100%", "display": "inline-block", "text-align":"center"}),

					#MA-plot
					html.Div([
						dcc.Loading(
							id = "loading_ma_plot",
							children = dcc.Graph(id="ma_plot_graph"),
							type = "dot",
							color = "#33A02C"
						)
					], style={"width": "100%", "display": "inline-block"}),

					#info boxplots
					html.Div([
						html.Img(src="assets/info.png", alt="info", id="info_boxplots", style={"width": 20, "height": 20}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Box plots showing gene/species/family/order expression/abundance in the different groups.
								
								Click the ___UMAP legend___ to choose which group you want to display.  
								Click the ___Comparison only___ button to display only the samples from the two conditions in comparison.
								""")
							],
							target="info_boxplots",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "22%", "display": "inline-block", "vertical-align": "middle"}),

					#group by "tissue"
					html.Label(["Group by tissue",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1, "disabled": True},
							],
							value=[],
							id="group_by_group_boxplots_switch",
							switch=True
						)
					], style={"width": "22%", "display": "inline-block", "vertical-align": "middle"}),

					#tissue checkbox for when the switch is on
					html.Div(id="tissue_checkboxes_div", hidden=False, children=[
						html.Br(),
						dbc.FormGroup(
							[
								dbc.Checklist(
									options=[{"label": tissue.replace("_", " "), "value": tissue} for tissue in tissues],
									value=tissues,
									id="tissue_checkboxes",
									inline=True
								),
							]
						)
					], style={"width": "56%", "display": "inline-block", "vertical-align": "middle", "font-size": 11}),

					#boxplots 
					html.Div([
						html.Br(),
						dcc.Loading(
							id = "loading_boxplots",
							children = dcc.Graph(id="boxplots_graph"),
							type = "dot",
							color = "#33A02C"
						),
						html.Br()
					], style={"width": "100%", "display": "inline-block", "position":"relative", "z-index": 1}),
				], style={"width": "40%", "display": "inline-block"}),

				#go plot
				html.Div([
					
					#info and search bar
					html.Div([
						#info
						html.Div([
							html.Img(src="assets/info.png", alt="info", id="info_go_plot", style={"width": 20, "height": 20}),
							dbc.Tooltip(
								children=[dcc.Markdown(
									"""
									Balloon plot showing top 15 up and top 15 down differentially enriched gene ontology biological processes between the two conditions in the selected comparison (differential gene expression FDR<1e-10), unless filtered otherwise.

									Click on the ___Comparison___ dropdown to change the results.
									""")
								],
								target="info_go_plot",
								style={"font-family": "arial", "font-size": 14}
							),
						], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "right"}),

						#spacer
						html.Div([], style={"width": "15%", "display": "inline-block"}),

						#search bar
						html.Div([
							dbc.Input(id="go_plot_filter_input", type="search", placeholder="Type here to filter GO gene sets", size="30", debounce=True, style={"font-size": "12px"}),
						], style={"width": "35%", "display": "inline-block", "vertical-align": "middle"})
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "right"}),

					#plot
					dcc.Loading(
						id = "loading_go_plot",
						children = dcc.Graph(id="go_plot_graph"),
						type = "dot",
						color = "#33A02C", 
					),
				], style={"width": "60%", "display": "inline-block", "vertical-align": "top"})
			], style = {"width": "100%", "height": 1000, "display": "inline-block"}),
		], style={"width": "100%", "display": "inline-block"}),

		#tabs
		html.Div([
			dcc.Tabs(id="site_tabs", value="summary_tab", children=[
				#summary and metadata tab
				dcc.Tab(label="Summary and metadata", value="summary_tab", children =[
					html.Br(),
					#graphical abstract
					html.Div([html.Img(src="assets/workflow.png", alt="graphical_abstract", style={"width": "60%", "height": "60%"}, title="FASTQ reads from 3,853 RNA-Seq data from different tissues, namely ileum, colon, rectum, mesenteric adipose tissue, peripheral blood, and stools, were mined from NCBI GEO/SRA and passed the initial quality filter. All files were mapped to the human reference genome and initial gene quantification was performed. Since these data came from 26 different studies made in different laboratories, we counteract the presumptive bias through a batch correction in accordance with source and tissue of origin. Once the gene counts were adjusted, samples were divided into groups in accordance with the tissue of origin and patient condition prior to differential expression analysis and gene ontology functional enrichment. Finally, the reads failing to map to the human genome were subjected to metatranscriptomics profiling by taxonomic classification using exact k-mer matching either archaeal, bacterial, eukaryotic, or viral genes. This image has been designed using resources from https://streamlineicons.com")
					], style={"width": "100%", "display": "inline-block"}),
					
					html.Br(),
					html.Br(),

					#info metadata table
					html.Div([
						html.Img(src="assets/info.png", alt="info", id="info_metadata_table", style={"width": 20, "height": 20}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Sample metadata table showing all variables used in TaMMA.
								Batch correction was performed using the study as possible source of variation (batch effect), and the Tissue of origin as source of covariation.

								Click on headers/subheaders to reorder/filter the table, respectively.

								Click on a study ID to see its specifications within its native hosting repository.
								""")
							],
							target="info_metadata_table",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "12%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

					#download button
					html.Div([
						dcc.Loading(
							type = "circle",
							color = "#33A02C",
							children=[html.A(
								id="download_metadata",
								href=metadata_table_link,
								download="TaMMa_metadata.xls",
								target="_blank",
								children = [dbc.Button("Download full table", id="download_metadata_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
								)
							]
						)
					], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),
					
					#table
					html.Div([
						html.Br(),
						dcc.Loading(
							type="dot",
							color="#33A02C",
							children=dash_table.DataTable(
								id="metadata_table",
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
								page_size=25,
								sort_action="native",
								style_header={
									"text-align": "left"
								},
								style_as_list_view=True,
								data = metadata_table_data,
								columns = metadata_table_columns
							)
						)
					], style={"width": "100%", "font-family": "arial"}),
					html.Br(),
					html.Br()
				], style=tab_style, selected_style=tab_selected_style),
				#expression/abundance profiling
				dcc.Tab(id="expression_abundance_profiling", value="expression_abundance", children=[
					dcc.Tabs(id="expression_abundance_profiling_tabs", value="heatmap", children=[
						
						#heatmap
						dcc.Tab(disabled = False, label="Heatmap", value="heatmap", children=[
							html.Div([
								html.Br(),
								
								#heatmap input
								html.Div([
									
									#info + update plot button
									html.Div([
										
										#info
										html.Div([
											html.Img(src="assets/info.png", alt="info", id="info_heatmap", style={"width": 20, "height": 20}),
											dbc.Tooltip(
												children=[dcc.Markdown(
													"""
													Heatmap showing gene/species/family/order expression/abundance in the different conditions. Expression/abundance data is log2 row scaled. By default, are showed the top 15 up and down genes which are statistically differentially expressed in the selected comparison and that shows the higher log2 fold change. 
													
													To select features to plot is possible to search them manualy using the ___Features___ dropdown and the relative search area or in alternative by clicking on any GO plot dot. 
													Switches allow the user to have the control over sample clustering and condition selection/hiding in the legend. 
													Annotations can be added to the heatmap using the ___Annotations___ dropdown.
													""")
												],
												target="info_heatmap",
												style={"font-family": "arial", "font-size": 14}
											),
										], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),

										#update plot button
										html.Div([
											dbc.Button("Update plot", id="update_heatmap_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black", "color": "black"}),
											#warning popup
											dbc.Popover(
												children=[
													dbc.PopoverHeader(children=["Warning!"], tag="div", style={"font-family": "arial", "font-size": 14}),
													dbc.PopoverBody(children=["Plotting more than 10 features is not allowed."], style={"font-family": "arial", "font-size": 12})
												],
												id="popover_plot_heatmap",
												target="update_heatmap_plot_button",
												is_open=False,
												style={"font-family": "arial"}
											),
										], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
									]),
									
									html.Br(),

									#cluster heatmap switch
									html.Div([
										html.Label(["Clustered samples",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[1],
												id="clustered_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle"}),

									#comparison only heatmap switch
									html.Div([
										html.Label(["Comparison only",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="comparison_only_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle"}),

									#hide unselected legend heatmap switch
									html.Div([
										html.Label(["Hide unselected",
											dbc.Checklist(
												options=[
													{"label": "", "value": 1},
												],
												value=[],
												id="hide_unselected_heatmap_switch",
												switch=True
											)
										], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle"}),

									#dropdowns
									html.Label(["Annotations", 
										dcc.Dropdown(id="annotation_dropdown", multi=True, options=annotation_options, value=[], style={"textAlign": "left", "font-size": "12px"})
									], style={"width": "100%", "display": "inline-block", "textAlign": "left"}),

									html.Br(),

									html.Label(["Features",
										dcc.Dropdown(id="gene_species_heatmap_dropdown", multi=True, placeholder="Select features", style={"textAlign": "left", "font-size": "12px"})
									], style={"width": "100%", "display": "inline-block", "textAlign": "left"}),

									html.Br(),

									#text area
									dbc.Textarea(id="heatmap_text_area", style={"height": 300, "resize": "none", "font-size": "12px"}),

									html.Br(),

									#search button
									dbc.Button("Search", id="heatmap_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black", "color": "black"}),

									html.Br(),

									#genes not found area
									html.Div(id="genes_not_found_heatmap_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"}), 

									html.Br()
								], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#spacer
								html.Div([], style={"width": "1%", "display": "inline-block"}),

								#heatmap graph and legend
								html.Div(children=[
									
									#custom hetmap dimension
									html.Div([
										html.Label(["Height",
											dbc.Input(id="hetamap_height_input", type="number", min=200, step=1, style={"font-family": "Arial", "font-size": 12, "height": 32})
										], style={"width": "30%", "display": "inline-block"}),
										#spacer
										html.Div([], style={"width": "3%", "display": "inline-block"}),
										html.Label(["Width",
											dbc.Input(id="hetamap_width_input", type="number", min=200, max=885, step=1, style={"font-family": "Arial", "font-size": 12, "height": 32})
										], style={"width": "30%", "display": "inline-block"}),
										#spacer
										html.Div([], style={"width": "3%", "display": "inline-block"}),
										dbc.Button("Resize heatmap", id="heatmap_resize_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black", "color": "black"}),
										], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
									
									#graph
									dcc.Loading(
										children = [dcc.Graph(id="heatmap_graph")],
										type = "dot",
										color = "#33A02C"
									),
									#legend
									html.Div(id="heatmap_legend_div", hidden=True)
								], style = {"width": "74%", "display": "inline-block"})
							], style = {"width": "100%", "height": 1200, "display": "inline-block"})
						], style=tab_style, selected_style=tab_selected_style, disabled_style={"padding": 6, "color": "#d6d6d6"}),
						
						#multiboxplots
						dcc.Tab(label="Boxplots", value="boxplots", children=[
							
							html.Div(id="multiboxplot_div", children=[
								
								html.Br(),
								
								#input section
								html.Div([
									
									#info + update plot button
									html.Div([
										
										#info
										html.Div([
											html.Img(src="assets/info.png", alt="info", id="info_multiboxplots", style={"width": 20, "height": 20}),
											dbc.Tooltip(
												children=[dcc.Markdown(
													"""
													Box plots showing host gene/species/family/order expression/abundance in the different groups.
													
													Click the ___legend___ on the top of the page to choose which group you want to display.  
													Click the ___Comparison only___ button to display only the samples from the two comparisons.
													Is not possible to plot more than 10 elements.
													""")
												],
												target="info_multiboxplots",
												style={"font-family": "arial", "font-size": 14}
											),
										], style={"width": "50%", "display": "inline-block", "vertical-align": "middle"}),
										
										#update plot button
										html.Div([
											dbc.Button("Update plot", id="update_multixoplot_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black", "color": "black"}),
											#warning popup
											dbc.Popover(
												children=[
													dbc.PopoverHeader(children=["Warning!"], tag="div", style={"font-family": "arial", "font-size": 14}),
													dbc.PopoverBody(children=["Plotting more than 20 features is not allowed."], style={"font-family": "arial", "font-size": 12})
												],
												id="popover_plot_multiboxplots",
												target="update_multixoplot_plot_button",
												is_open=False,
												style={"font-family": "arial"}
											),
										], style={"width": "50%", "display": "inline-block", "vertical-align": "middle"}),
									]),
									
									html.Br(),

									#dropdown
									dcc.Dropdown(id="gene_species_multi_boxplots_dropdown", multi=True, placeholder="", style={"textAlign": "left", "font-size": "12px"}),

									html.Br(),

									#text area
									dbc.Textarea(id="multi_boxplots_text_area", style={"width": "100%", "height": 300, "resize": "none", "font-size": "12px"}),

									html.Br(),

									#search button
									dbc.Button("Search", id="multi_boxplots_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black", "color": "black"}),

									html.Br(),

									#genes not found area
									html.Div(id="genes_not_found_multi_boxplots_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"}), 

									html.Br(),

									#group by "tissue" switch
									html.Label(["Group by tissue",
										dbc.Checklist(
											options=[
												{"label": "", "value": 1, "disabled": True},
											],
											value=[],
											id="group_by_group_multiboxplots_switch",
											switch=True
										)
									], style={"width": "33%", "display": "inline-block", "vertical-align": "middle"}),

									#tissue checkbox for when the switch is on
									html.Div(id="tissue_checkboxes_multiboxplots_div", hidden=False, children=[
										html.Br(),
										dbc.FormGroup(
											[
												dbc.Checklist(
													options=[{"label": tissue.replace("_", " "), "value": tissue} for tissue in tissues],
													value=tissues,
													id="tissue_checkboxes_multiboxplots",
													inline=True
												),
											]
										)
									], style={"width": "67%", "display": "inline-block", "vertical-align": "middle", "font-size": 11})

								], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#graph
								html.Div(id="multiboxplot_graph_div", children=[
									dcc.Loading(type = "dot", color = "#33A02C", children=[
										html.Div(
											id="multi_boxplots_div",
											children=[dcc.Loading(
												children = [dcc.Graph(id="multi_boxplots_graph", figure={})],
												type = "dot",
												color = "#33A02C")
										], hidden=True)
									])
								], style={"width": "75%", "display": "inline-block", "vertical-align": "top"})
							], style={"height": 1150, "width": "100%", "display":"inline-block"})
						], style=tab_style, selected_style=tab_selected_style),
					], style= {"height": 40})
				], style=tab_style, selected_style=tab_selected_style),
				#differential analysis tab
				dcc.Tab(label="Differential analysis", value="differential_analysis", children=[
					dcc.Tabs(id="differential_analysis_tabs", value="dge_tab", children=[
						
						#dge table tab
						dcc.Tab(label="DGE table", value="dge_tab", children=[
							
							html.Br(),
							#title dge table
							html.Div(id="dge_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
							html.Br(),
							html.Br(),

							#info dge table
							html.Div([
								html.Img(src="assets/info.png", alt="info", id="info_dge_table", style={"width": 20, "height": 20}),
								dbc.Tooltip(
									id="dge_table_tooltip",
									children=[],
									target="info_dge_table",
									style={"font-family": "arial", "font-size": 14}
								),
							], style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

							#download full table button diffexp
							html.Div([
								dcc.Loading(
									id = "loading_download_diffexp",
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_diffexp",
										href="",
										target="_blank",
										children = [dbc.Button("Download full table", id="download_diffexp_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
										)
									]
								)
							], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

							#download partial button diffexp
							html.Div([
								dcc.Loading(
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_diffexp_partial",
										href="",
										target="_blank",
										children = [dbc.Button("Download filtered table", id="download_diffexp_button_partial", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
										)
									]
								)
							], style={"width": "25%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

							#dropdown
							html.Div([
								dcc.Dropdown(id="multi_gene_dge_table_selection_dropdown", multi=True, placeholder="", style={"textAlign": "left", "font-size": "12px"})
							], style={"width": "25%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"}),

							#target priorization switch
							html.Label(["Target prioritization",
								dbc.Checklist(
									options=[
										{"label": "", "value": 1, "disabled": True},
									],
									value=[],
									id="target_prioritization_switch",
									switch=True
								)
							], style={"width": "16%", "display": "inline-block", "vertical-align": "middle"}),

							#filtered dge table
							html.Div(id="filtered_dge_table_div", children=[
								html.Br(),
								dcc.Loading(
									id="loading_dge_table_filtered",
									type="dot",
									color="#33A02C",
									children=dash_table.DataTable(
										id="dge_table_filtered",
										style_cell={
											"whiteSpace": "normal",
											"height": "auto",
											"fontSize": 12, 
											"font-family": "arial",
											"textAlign": "center"
										},
										page_size=25,
										sort_action="native",
										style_header={
											"textAlign": "center"
										},
										style_cell_conditional=[
											{
												"if": {"column_id": "External resources"},
												"width": "12%"
											},
											{
												"if": {"column_id": "expression_in_tissue_cell_types"},
												"textAlign": "left",
												"width": "45%",
											},
											{
												"if": {"column_id": "FDR"},
												"textAlign": "left",
												"width": "4.5%",
											},
											{
												"if": {"column_id": "total_drug_count"},
												"textAlign": "left",
												"width": "2.5%",
											},
											{
												"if": {"column_id": "IBD_drugs"},
												"textAlign": "left",
												"width": "3.5%",
											},
											{
												"if": {"column_id": "GWAS"},
												"textAlign": "left",
												"width": "3.5%",
											},
											{
												"if": {"column_id": "protein_expression_in_cell_compartment"},
												"textAlign": "left",
												"width": "8%",
											},
										],
										style_data_conditional=[],
										style_as_list_view=True,
										merge_duplicate_headers=True
									)
								)
							], style={"width": "100%", "font-family": "arial"}, hidden=True),

							#full dge table
							html.Div([
								html.Br(),
								dcc.Loading(
									id="loading_dge_table",
									type="dot",
									color="#33A02C",
									children=dash_table.DataTable(
										id="dge_table",
										style_cell={
											"whiteSpace": "pre-line",
											"height": "auto",
											"fontSize": 12, 
											"font-family": "arial",
											"textAlign": "center"
										},
										page_size=25,
										style_header={
											"textAlign": "center"
										},
										style_cell_conditional=[
											{
												"if": {"column_id": "External resources"},
												"width": "12%"
											},
											{
												"if": {"column_id": "expression_in_tissue_cell_types"},
												"textAlign": "left",
												"width": "45%",
											},
											{
												"if": {"column_id": "FDR"},
												"textAlign": "left",
												"width": "4.5%",
											},
											{
												"if": {"column_id": "total_drug_count"},
												"textAlign": "left",
												"width": "2.5%",
											},
											{
												"if": {"column_id": "IBD_drugs"},
												"textAlign": "left",
												"width": "3.5%",
											},
											{
												"if": {"column_id": "GWAS"},
												"textAlign": "left",
												"width": "3.5%",
											},
											{
												"if": {"column_id": "protein_expression_in_cell_compartment"},
												"textAlign": "left",
												"width": "8%",
											},
										],
										style_data_conditional=[],
										style_as_list_view=True,
										merge_duplicate_headers=True
									)
								)
							], style={"width": "100%", "font-family": "arial"}),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style),
						
						#go table tab
						dcc.Tab(label="GO table", value="go_table_tab", children=[
							
							html.Br(),
							#title go table
							html.Div(id="go_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
							html.Br(),
							html.Br(),

							#info go table
							html.Div([
								html.Img(src="assets/info.png", alt="info", id="info_go_table", style={"width": 20, "height": 20}),
								dbc.Tooltip(
									children=[dcc.Markdown(
										"""
										Table showing the differentially enriched gene ontology biological processes between the two conditions, unless filtered otherwise.

										Use the ___search bar___ above the GO plot to filter the processes.

										Click on headers to reorder the table.
										Click on a GO dataset name to see its specifics in AmiGO 2 (___Ashburner et al. 2000, PMID 10802651___).
										""")
									],
									target="info_go_table",
									style={"font-family": "arial", "font-size": 14}
								),
							], style={"width": "12%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

							#download button
							html.Div([
								dcc.Loading(
									id = "loading_download_go",
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_go",
										href="",
										target="_blank",
										children = [dbc.Button("Download full table", id="download_go_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
										)
									]
								)
							], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),

							#download button partial
							html.Div([
								dcc.Loading(
									type = "circle",
									color = "#33A02C",
									children=[html.A(
										id="download_go_partial",
										href="",
										target="_blank",
										children = [dbc.Button("Download shown table", id="download_go_button_partial", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})],
										)
									]
								)
							], style={"width": "20%", "display": "inline-block", "textAlign": "left", "vertical-align": "middle", 'color': 'black'}),

							#go table
							html.Div([
								html.Br(),
								dcc.Loading(
									id="loading_go_table",
									type="dot",
									color="#33A02C",
									children=dash_table.DataTable(
										id="go_table",
										style_cell={
											"whiteSpace": "normal",
											"height": "auto",
											"fontSize": 12, 
											"font-family": "arial",
											"textAlign": "center"
										},
										page_size=10,
										sort_action="native",
										style_header={
											"textAlign": "center"
										},
										style_cell_conditional=[
											{
												"if": {"column_id": "Genes"},
												"textAlign": "left",
												"width": "50%"
											},
											{
												"if": {"column_id": "GO biological process"},
												"textAlign": "left",
												"width": "15%"
											}
										],
										style_data_conditional=[
											{
												"if": {
													"filter_query": "{{DGE}} = {}".format("up")
												},
												"backgroundColor": "#FFE6E6"
											},
											{
												"if": {
													"filter_query": "{{DGE}} = {}".format("down")
												},
												"backgroundColor": "#E6F0FF"
											}
										],
										style_as_list_view=True
									)
								)
							], style={"width": "100%", "font-family": "arial"}),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style)
					], style= {"height": 40})
				], style=tab_style, selected_style=tab_selected_style),
				#evidence tab 
				dcc.Tab(label="Insights", value="evidence_tab", children=[
					dcc.Tabs(id="evidence_tabs", value="old_evidence_tab", children=[
						#old
						dcc.Tab(label="Old evidence from the literature confirmed by TaMMA", value="old_evidence_tab", children=[
							html.Br(),
							html.Div([
								#input section
								html.Div([
									html.Br(),
									#dropdown
									dcc.Dropdown(id="validation_dropdown", placeholder="Search evidence", options=old_evidence_options, style={"textAlign": "left", "font-size": "12px"}),
								], style={"height": 350, "width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#spacer
								html.Div([], style={"width": "1.5%", "display": "inline-block"}),

								#graphs
								html.Div(id="evidence_div", children=[
									dcc.Loading(
										id="evidence_div_loading",
										type="dot",
										color="#33A02C",
										children=[]
									)
								], style={"height": 600, "width": "70%", "display": "inline-block"}),

								#spacer
								html.Div([], style={"width": "1.5%", "display": "inline-block"}),
							]),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style),
						#new
						dcc.Tab(label="New evidence by TaMMA", value="new_evidence_tab", children=[
							html.Br(),
							html.Div([
								#input section
								html.Div([
									html.Br(),
									#dropdown
									dcc.Dropdown(id="new_evidence_dropdown", placeholder="Search evidence", options=new_evidence_options, style={"textAlign": "left", "font-size": "12px"}),
								], style={"height": 350, "width": "25%", "display": "inline-block", "vertical-align": "top"}),

								#spacer
								html.Div([], style={"width": "1.5%", "display": "inline-block"}),

								#graphs
								html.Div(id="new_evidence_div", children=[
									dcc.Loading(
										id="new_evidence_div_loading",
										type="dot",
										color="#33A02C",
										children=[]
									)
								], style={"height": 600, "width": "70%", "display": "inline-block"}),

								#spacer
								html.Div([], style={"width": "1.5%", "display": "inline-block"}),
							]),
							html.Br()
						], style=tab_style, selected_style=tab_selected_style),
					], style= {"height": 40})
				], style=tab_style, selected_style=tab_selected_style),
			], style= {"height": 40}),
		], style={"width": "100%", "display": "inline-block"}),
		
		#footer
		html.Footer([
			html.Hr(),
			html.Div([
				"© Copyright 2021 ", 
				html.A("Luca Massimino", href="https://scholar.google.com/citations?user=zkPRE9oAAAAJ&hl=en", target="_blank"), ", ",
				html.A("Luigi Antonio Lamparelli", href="https://scholar.google.com/citations?hl=en&user=D4JB6sQAAAAJ", target="_blank"), ", ",
				html.A("Federica Ungaro", href="https://scholar.google.com/citations?user=CYfM7wsAAAAJ&hl=en", target="_blank"), ", ",
				html.A("Silvio Danese", href="https://scholar.google.com/citations?hl=en&user=2ia1nGUAAAAJ", target="_blank"), "  -  ",
				html.A("Manual", href="https://ibd-tamma.readthedocs.io/", target="_blank"), "  -  ",
				html.A("Report a bug", href="https://github.com/Danese-Omics-Web-Apps/eoe_tamma/issues", target="_blank"), "  -  ",
				html.A("Suggestions", href="https://github.com/Danese-Omics-Web-Apps/eoe_tamma/issues", target="_blank"), "  -  ",
				html.A("Data", href="https://github.com/Danese-Omics-Web-Apps/eoe_tamma_data", target="_blank"),  "  -  ",
				html.A("NGS dark matter", href="https://dataverse.harvard.edu/dataverse/tamma-dark-matter", target="_blank"),  "  -  ",
				html.A("How to cite us", href="https://www.nature.com/articles/s43588-021-00114-y", target="_blank")
			]),
			html.Br()
		], style={"width": "100%", "display": "inline-block"})
	], style={"width": 1200, "font-family": "Arial"}),
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})
