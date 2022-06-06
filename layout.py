#import packages
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash import dash_table
from functions import config, organism, expression_datasets_options, mds_dataset_options, metadata_options, discrete_metadata_options, continuous_metadata_options, metadata_table_data, metadata_table_columns, tab_style, tab_selected_style, mofa_analysis


#header type
if config["header"]["logo"] == "NA":
	header_content = html.Div(config["header"]["text"], style={"width": "100%", "font-size": 50, "text-align": "center"})
else:
	header_content = html.Img(src=config["header"]["logo"], alt="logo", style={"width": "70%", "height": "70%"}, title=config["header"]["text"])

## main tabs ##
#metadata tab
metadata_tab = dcc.Tab(label="Metadata", value="metadata_tab", children=[

	html.Br(),

	#download metadata button
	html.Div([
		dbc.Spinner(
			size = "md",
			color = "lightgray",
			children=[
				dbc.Button("Download metadata", id="download_metadata_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
				dcc.Download(id="download_metadata")
			]
		)
	], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),
	
	#table
	html.Div([
		html.Br(),
		dbc.Spinner(
			size="md",
			color="lightgray",
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
				style_data_conditional=[
					{
						"if": {"state": "selected"},
						"backgroundColor": "rgba(44, 62, 80, 0.2)",
						"border": "1px solid #597ea2",
					},
				],
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
	], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
	html.Br(),
	html.Br()
], style=tab_style, selected_style=tab_selected_style)
#expression/abundance profiling
expression_abundance_profiling_tab = dcc.Tab(id="expression_abundance_profiling", value="expression_abundance", children=[
	dcc.Tabs(id="expression_abundance_profiling_tabs", value="heatmap", style= {"height": 40})
], style=tab_style, selected_style=tab_selected_style)
#differential analysis tab
differential_analysis_tab = dcc.Tab(label="Differential analysis", value="differential_analysis", children=[
	dcc.Tabs(id="differential_analysis_tabs", value="dge_tab", children=[
		#dge table tab
		dcc.Tab(id="dge_table_tab", label="DGE table", value="dge_tab", children=[
			
			html.Br(),
			#title dge table
			html.Div(id="dge_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
			html.Br(),
			html.Br(),

			#info dge table
			html.Div([
				html.Div(id="info_dge_table",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto", "text-align": "center"}),
				dbc.Tooltip(
					children=[dcc.Markdown(
						"""
						##### Table showing the differential analysis statistics for the comparison chosen in the __comparison__ dropdown (uppermost menù)
						
						Use the __search bar__ to display a filtered table with the selected features.
						
						Click a __feature name__ (first column) within the table to highlight it in the MA plot.
						
						Use the __icons__ in the last column to access external resources.
						""")
					],
					target="info_dge_table",
					style={"font-family": "arial", "font-size": 14}
				),
			], style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

			#download full table button diffexp
			html.Div([
				dbc.Spinner(
					size = "md",
					color = "lightgray",
					children=[
						dbc.Button("Download full table", id="download_diffexp_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
						dcc.Download(id="download_diffexp")
					]
				)
			], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

			#download partial button diffexp
			html.Div([
				dbc.Spinner(
					size = "md",
					color = "lightgray",
					children=[
						dbc.Button("Download filtered table", id="download_diffexp_partial_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
						dcc.Download(id="download_diffexp_partial")
					]
				)
			], style={"width": "25%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

			#dropdown
			html.Div([
				dcc.Dropdown(id="multi_gene_dge_table_selection_dropdown", 
					multi=True, 
					placeholder="", 
					style={"textAlign": "left", "font-size": "12px"})
			], className="dropdown-luigi", style={"width": "25%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"}),

			#target priorization switch
			html.Div(id = "target_prioritization_switch_div", hidden = True, children = [
				html.Label(["Target prioritization",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[],
						id="target_prioritization_switch",
						switch=True
					)
				], style={"textAlign": "center"})
			], style={"width": "16%", "display": "inline-block", "vertical-align": "middle"}),

			#filtered dge table
			html.Div(id="filtered_dge_table_div", children=[
				html.Br(),
				dbc.Spinner(
					id="loading_dge_table_filtered",
					size="md",
					color="lightgray",
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
							}
						],
						style_data_conditional=[],
						style_as_list_view=True
					)
				)
			], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}, hidden=True),

			#full dge table
			html.Div([
				html.Br(),
				dbc.Spinner(
					id="loading_dge_table",
					size="md",
					color="lightgray",
					children=dash_table.DataTable(
						id="dge_table",
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
							}
						],
						style_data_conditional=[],
						style_as_list_view=True
					)
				)
			], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
			html.Br()
		], style=tab_style, selected_style=tab_selected_style),
		#go table tab
		dcc.Tab(id="go_table_tab", label="GO table", value="go_table_tab", children=[
			
			html.Br(),
			#title go table
			html.Div(id="go_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
			html.Br(),
			html.Br(),

			#info go table
			html.Div([
				html.Div(id="info_go_table",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto", "text-align": "center"}),
				dbc.Tooltip(
					children=[dcc.Markdown(
						"""
						##### Table showing the functional enrichment statistics for the comparison chosen in the __comparison__ dropdown (uppermost menù)
						
						Use the GO plot __search bar__ to display a filtered table with the selected gene sets.
						
						Click a __gene set name__ to see its specifications within the AmiGO 2 database.
						""")
					],
					target="info_go_table",
					style={"font-family": "arial", "font-size": 14}
				),
			], style={"width": "12%", "display": "inline-block", "vertical-align": "middle", "textAlign": "center"}),

			#download go button
			html.Div([
				dbc.Spinner(
					size = "md",
					color = "lightgray",
					children=[
						dbc.Button("Download full table", id="download_go_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
						dcc.Download(id="download_go")
					]
				)
			], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

			#download button partial
			html.Div([
				dbc.Spinner(
					size = "md",
					color = "lightgray",
					children=[
						dbc.Button("Download filtered table", id="download_go_button_partial", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
						dcc.Download(id="download_go_partial")
					]
				)
			], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

			#go table
			html.Div([
				html.Br(),
				dbc.Spinner(
					id="loading_go_table",
					size="md",
					color="lightgray",
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
								"if": {"column_id": "Lipids"},
								"textAlign": "left",
								"width": "50%"
							},
							{
								"if": {"column_id": "GO biological process"},
								"textAlign": "left",
								"width": "15%"
							},
							{
								"if": {"column_id": "Functional category"},
								"textAlign": "left",
								"width": "15%"
							}
						],
						style_data_conditional=[
							{
								"if": {"filter_query": "{{DGE}} = {}".format("up")},
								"backgroundColor": "#FFE6E6"
							},
							{
								"if": {"filter_query": "{{DGE}} = {}".format("down")},
								"backgroundColor": "#E6F0FF"
							},
							{
								"if": {	"filter_query": "{{DLE}} = {}".format("up")},
								"backgroundColor": "#FFE6E6"
							},
							{
								"if": {"filter_query": "{{DLE}} = {}".format("down")},
								"backgroundColor": "#E6F0FF"
							},
							{
								"if": {"state": "selected"},
								"backgroundColor": "rgba(44, 62, 80, 0.2)",
								"border": "1px solid #597ea2",
							}
						],
						style_as_list_view=True
					)
				)
			], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
			html.Br()
		], style=tab_style, selected_style=tab_selected_style)
	], style= {"height": 40})
], style=tab_style, selected_style=tab_selected_style)

#save main tabs in a list to use as children
all_tabs = [metadata_tab] + [expression_abundance_profiling_tab] + [differential_analysis_tab]

## additional tabs ##
if mofa_analysis:
	mofa_tab = dcc.Tab(label="Multi-omics signatures", value="mofa_tab", children=[
		#mofa data overview
		html.Div([
			dbc.Spinner(
				children = dcc.Graph(id="mofa_data_overview"),
				size = "md",
				color = "lightgray"
			)
		], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),
		#heatmap and factor plot
		html.Div([
			#heatmap
			html.Div([
				dbc.Spinner(
					children = dcc.Graph(id="mofa_variance_heatmap"),
					size = "md",
					color = "lightgray"
				)
			], style={"width": "100%", "display": "inline-block"}),
			#factor + factor values + feature expression/abundance
			html.Div([
				#factor
				html.Div([
					dbc.Spinner(
						children = dcc.Graph(id="mofa_factor_plot"),
						size = "md",
						color = "lightgray"
					)
				], style={"width": "50%", "display": "inline-block", "vertical-align": "top"}),
				#factor values and feature expression/abundance
				html.Div([
					#group/condition switch
					html.Div([
						#left description
						html.Div([
							"Groups"
						], style={"width": "15%", "display": "inline-block", "text-align": "left"}),
						html.Div([], style={"width": "5%", "display": "inline-block"}),
						#switch
						html.Div([
							dbc.Checklist(
								options=[
									{"label": "", "value": 1},
								],
								value=[],
								id="group_condition_switch_mofa",
								switch=True
							)
						], style={"width": "1%", "display": "inline-block"}),
						#right description
						html.Div([], style={"width": "5%", "display": "inline-block"}),
						html.Div([
							"Conditions"
						], style={"width": "15%", "display": "inline-block", "text-align": "right"})
					], style={"width": "100%", "display": "inline-block"}),
					
					#all factors values
					html.Div([
						dbc.Spinner(
							children = dcc.Graph(id="mofa_all_factors_values"),
							size = "md",
							color = "lightgray"
						),
					], style={"width": "100%", "display": "inline-block"}),
					#feature expression or abundance
					html.Div([
						dbc.Spinner(
							children = dcc.Graph(id="mofa_factor_expression_abundance"),
							size = "md",
							color = "lightgray"
						)
					], style={"width": "100%", "display": "inline-block"})
				], style={"width": "50%", "display": "inline-block", "vertical-align": "top"})
			], style={"width": "100%", "display": "inline-block", "vertical-align": "top"})
		], style={"width": "65%", "display": "inline-block", "vertical-align": "top"})
	], style=tab_style, selected_style=tab_selected_style)
	all_tabs = [metadata_tab] + [mofa_tab] + [expression_abundance_profiling_tab] + [differential_analysis_tab]

#app layout
layout = html.Div([
	html.Div([
		html.Br(),
		#title
		html.Div(header_content),

		#common options dropdown
		html.Div([
			
			#expression dataset dropdown
			html.Div([
				html.Label(["Expression/Abundance",
					dcc.Dropdown(
						id="feature_dataset_dropdown",
						clearable=False,
						options=expression_datasets_options,
						value=organism
				)], style={"width": "100%"}, className="dropdown-luigi"),
			], style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

			#feature dropdown
			html.Div([
				html.Label(id = "feature_label", children = ["Loading...",
					dcc.Dropdown(
						id="feature_dropdown",
						clearable=False
				)], style={"width": "100%"}, className="dropdown-luigi"),
			], style={"width": "30%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

			#info comparison filter
			html.Div([
				html.Div(id="info_comparison_filter",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
				dbc.Tooltip(
					children=[dcc.Markdown(
						"""
						On the left, choose the __expression/abundance matrix__ and the __feature to plot__.

						On the right, choose the __comparison__ between two conditions and the __stringency__ to be used for differential analyses.

						Use the __filter comparison__ form to restrict the possibilities in the comparison dropdown.
						""")
					],
					target="info_comparison_filter",
					style={"font-family": "arial", "font-size": 14}
				),
			], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),
			
			#comparison filter
			html.Label(["Filter comparison by",
				dbc.Input(id="comparison_filter_input", type="search", placeholder="Type here to filter comparisons", debounce=True, style={"font-family": "Arial", "font-size": 12, "height": 36}),
			], style={"width": "17%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),
			
			#contrast dropdown
			html.Label(["Comparison", 
				dcc.Dropdown(
					id="contrast_dropdown",
					clearable=False
			)], className="dropdown-luigi", style={"width": "19%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),

			#stringecy dropdown
			html.Label(["Stringency", 
				dcc.Dropdown(
					id="stringency_dropdown",
					clearable=False
			)], className="dropdown-luigi", style={"width": "9%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"})

		], style={"width": "100%", "font-size": "12px"}),
		
		html.Br(),

		#mds
		html.Div([
			#mds options and info
			html.Div([
								
				#mds dataset dropdown
				html.Div([
					html.Label(["MDS dataset", 
						dcc.Dropdown(
							id="mds_dataset",
							clearable=False,
							options=mds_dataset_options,
							value=organism
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#mds type dropdown
				html.Div([
					html.Label(["MDS type", 
						dcc.Dropdown(
							id="mds_type",
							clearable=False
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#metadata dropdown
				html.Div([
					html.Label(["Color by", 
						dcc.Dropdown(
							id="metadata_dropdown",
							clearable=False,
							options=metadata_options,
							value="condition"
					)], style={"width": "100%", "textAlign": "left"}),
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#info mds
				html.Div([
					html.Div(id="info_mds",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							##### Multidimensional scaling (MDS) visualization by low-dimensional embedding of high-dimensional data
							
							On the left, select the MDS __dataset__ and __type__ to be shown. Use the __color by__ dropdown to color the samples by specific features in the left plot.

							Use the __comparison only__ switch to display only the samples belonging to the two conditions of interest.
							
							Use the __legend__ to hide a group of samples. Use the __hide unselected__ switch to clear the legend from undisplayed samples.
							""")
						],
						target="info_mds",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),

				#comparison_only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="comparison_only_mds_metadata_switch",
							switch=True
						)
					], style={"textAlign": "center"})
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

				#hide unselected switch
				html.Div([
					html.Label(["Hide unselected",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="hide_unselected_mds_metadata_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"})
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),

			#mds metadata
			html.Div(id="mds_metadata_div", children=[
				dbc.Spinner(
					id = "loading_mds_metadata",
					children = dcc.Graph(id="mds_metadata"),
					size = "md",
					color = "lightgray"
				)
			], style={"width": "48%", "display": "inline-block"}),

			#mds expression
			html.Div(id="mds_expression_div", children=[
				dbc.Spinner(
					id = "loading_mds_expression",
					children = dcc.Graph(id="mds_expression"),
					size = "md",
					color = "lightgray"
				)
			], style={"width": "35%", "display": "inline-block"}),
		], style={"width": "100%", "display": "inline-block"}),
		
		html.Br(),

		#boxplots
		html.Br(),
		html.Div([
			#boxplots options
			html.Div([
				#x dropdown
				html.Label(["x",
					dcc.Dropdown(
					id="x_boxplot_dropdown",
					clearable=False,
					options=discrete_metadata_options,
					value="condition"
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#y dropdown
				html.Label(["y", 
							dcc.Dropdown(
								id="y_boxplot_dropdown",
								clearable=False,
								value="log2_expression",
								options=continuous_metadata_options
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#group by dropdown
				html.Label(["Group by", 
							dcc.Dropdown(
								id="group_by_boxplot_dropdown",
								clearable=False,
								value="condition",
								options=discrete_metadata_options
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#info boxplots
				html.Div([
					html.Div(id="info_boxplots",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							On the left, select the data for __x__- and __y__-axis, and use the __group by__ dropdown to facet the plot.

							Use the __comparison only__ switch to display only the groups belonging to the two conditions of interest.

							Use the appropriate switch to __show as boxplots__.

							Use __height__ and __width__ sliders to resize the entire plot.

							Use the __legend__ to hide a group. Use the __hide unselected__ switch to clear the legend from undisplayed groups.
							""")
						],
						target="info_boxplots",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"}),
				#comparison only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[1],
							id="comparison_only_boxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#hide unselected switch
				html.Div([
					html.Label(["Hide unselected",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="hide_unselected_boxplot_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#show as boxplot switch
				html.Div([
					html.Label(["Show as boxplots",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="show_as_boxplot_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
				#height slider
				html.Div([
					html.Label(["Height",
						dcc.Slider(id="boxplots_height_slider", min=200, max=400, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "15%", "display": "inline-block", "vertical-align": "middle"}),
				#width slider
				html.Div([
					html.Label(["Width",
						dcc.Slider(id="boxplots_width_slider", min=200, max=1000, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "15%", "display": "inline-block", "vertical-align": "middle"}),
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),
			
			#x filter dropdown
			html.Div(id="x_filter_dropdown_div", hidden=True, children=[
				html.Label(["x filter", 
					dcc.Dropdown(
						id="x_filter_boxplot_dropdown",
						multi=True
				)], className="dropdown-luigi", style={"width": "100%", "textAlign": "left"}),
			], style={"width": "80%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

			#plot
			html.Div([
				dbc.Spinner(
					id = "loading_boxplots",
					children = dcc.Graph(id="boxplots_graph"),
					size = "md",
					color = "lightgray"
				),
			], style={"width": "80%", "display": "inline-block"})
		], style={"width": "100%", "display": "inline-block"}),

		html.Br(),
		html.Br(),

		#MA-plot + go plot + deconvolution
		html.Div([
			#MA-plot + go plot
			html.Div([
				#info MA-plot
				html.Div([
					html.Div(id="info_ma_plot",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							##### MA plot showing the differential expression analysis results
							
							Use the __features__ dropdown (uppermost menù) to select a feature of interest. Click on a specific feature (__points__ inside the plot) to change the feature of interest.
							
							Use the __show annotations__ dropdown to choose whether to display the statistics.
							
							Use the __stringency__ dropdown to change the number of the differential features reaching statistical significance.
							""")
						],
						target="info_ma_plot",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "100%", "display": "inline-block"}),
				#MA-plot
				html.Div([
					dbc.Spinner(
						id = "loading_ma_plot",
						children = dcc.Graph(id="ma_plot_graph"),
						size = "md",
						color = "lightgray"
					)
				], style={"width": "52%", "display": "inline-block"}),

				#info and search bar go plot
				html.Div([
					#info
					html.Div([
						html.Div(id="info_go_plot",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto", "text-align": "center"}),
						dbc.Tooltip(
							children=[dcc.Markdown(
								"""
								Use the __comparison__ or the __stringency__ dropdowns (uppermost menù) to change the results.
								
								Use the __search bar__ form to plot the enrichment of specific biological process categories. Separate the different entries with spaces.
								
								Clicking a __balloon__ will send the genes responsible for the enrichment of that gene set to the __multi-violin__ or __heatmap__ sections.
								""")
							],
							target="info_go_plot",
							style={"font-family": "arial", "font-size": 14}
						),
					], style={"width": "15%", "display": "inline-block"}),
					
					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),

					#add gsea switch
					html.Div(id="add_gsea_switch_div", children=[
						html.Label(["Add GSEA",
							dbc.Checklist(
								options=[
									{"label": "", "value": 1},
								],
								value=[],
								id="add_gsea_switch",
								switch=True
							)
						], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "center"})
					], style={"width": "15%", "display": "inline-block", "font-size": "12px"}),

					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),

					#search bar
					html.Div([
						dbc.Input(id="go_plot_filter_input", type="search", placeholder="Type here to filter GO gene sets", size="30", debounce=True, style={"font-family": "Arial", "font-size": 12}),
					], style={"width": "35%", "display": "inline-block", "vertical-align": "middle"})
				], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "right"}),
				#plot
				html.Div(id="go_plot_div", children=[
					dbc.Spinner(
						id = "loading_go_plot",
						children = [html.Br(), dcc.Graph(id="go_plot_graph")],
						size = "md",
						color = "lightgray", 
					),
				], style={"width": "100%", "display": "inline-block"})
				
			], style={"width": "50%", "display": "inline-block", "font-size": "12px"}),

			#deconvolution
			html.Div(id="deconvolution_div", children=[
				#info deconvolution
				html.Div([
					html.Div(id="info_deconvolution",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Coming soon...
							""")
						],
						target="info_deconvolution",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "100%", "display": "inline-block"}),
				
				#split_by dropdown
				html.Label(["Split by",
					dcc.Dropdown(
					id="split_by_1_deconvolution_dropdown",
					clearable=False,
					options=discrete_metadata_options,
					value="condition"
				)], className="dropdown-luigi", style={"width": "30%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

				#second split_by dropdown
				html.Label(["Split also by",
					dcc.Dropdown(
					id="split_by_2_deconvolution_dropdown",
					clearable=False,
					options=discrete_metadata_options,
					value="condition"
				)], className="dropdown-luigi", style={"width": "30%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

				#plot per row dropdown
				html.Label(["Plots per row",
					dcc.Dropdown(
					id="plots_per_row_deconvolution_dropdown",
					clearable=False,
					options=[{"label": "1", "value": 1}, {"label": "2", "value": 2}, {"label": "3", "value": 3}, {"label": "4", "value": 4}, {"label": "5", "value": 5}],
					value=4
				)], className="dropdown-luigi", style={"width": "30%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

				#deconvolution plot
				html.Div([
					dbc.Spinner(
						id = "loading_deconvolution",
						children = dcc.Graph(id="deconvolution_graph"),
						size = "md",
						color = "lightgray"
					)
				], style={"width": "100%", "display": "inline-block"})
			], style={"width": "50%", "display": "inline-block", "vertical-align": "top", "font-size": "12px"})
		], style = {"width": "100%", "display": "inline-block"}),

		#tabs
		html.Br(),
		html.Br(),

		html.Div(children=[
			dcc.Tabs(id="site_tabs", value="metadata_tab", children=all_tabs, style= {"height": 40}),
		], style = {"width": "100%", "display": "inline-block"})
	], style={"width": 1200, "font-family": "Arial"})
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})
