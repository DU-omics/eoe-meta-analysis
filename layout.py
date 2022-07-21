#import packages
from dash import html, dcc
from dash import dash_table
import dash_bootstrap_components as dbc
from functions import multiple_analysis, repos_options, tab_style, tab_selected_style

#main app layout
main_layout = html.Div([
	html.Div([
		html.Br(),
		#title
		html.Div(id="header_div"),

		#store components
		dcc.Store(id="color_mapping"),
		dcc.Store(id="label_to_value"),
		dcc.Store(id="metadata_table_store"),
		dcc.Store(id="metadata_columns_store"),
		dcc.Store(id="heatmap_annotation_dropdown_options"),
		dcc.Store(id="discrete_metadata_options"),
		dcc.Store(id="continuous_metadata_options"),
		dcc.Store(id="mofa_contrasts_options"),
		dcc.Store(id="deconvolution_datasets_options"),
		
		#store components for variable data
		dcc.Store(id="profiling_tab_label_data"),
		dcc.Store(id="differential_analysis_tab_label_data"),
		dcc.Store(id="dge_table_click_data"),

		#main options dropdowns
		html.Div([
			#first row
			html.Div([
				#analysis dropdown
				html.Div([
					html.Label(["Analysis",
						dcc.Dropdown(
							id="analysis_dropdown",
							clearable=False,
							options=repos_options,
							value=repos_options[0]["value"]
					)], style={"width": "100%"}, className="dropdown-luigi")
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left", "font-size": "12px"}, hidden=multiple_analysis),

				#expression dataset dropdown
				html.Div([
					html.Label(["Expression/Abundance",
						dcc.Dropdown(
							id="feature_dataset_dropdown",
							clearable=False,
					)], style={"width": "100%"}, className="dropdown-luigi"),
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

				#feature dropdown
				html.Div([
					html.Label(id = "feature_label", children = ["Loading...",
						dcc.Dropdown(
							id="feature_dropdown",
							clearable=False
					)], style={"width": "100%"}, className="dropdown-luigi"),
				], style={"width": "40%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"})
			], style={"width": "100%", "display": "inline-block"}),

			#second row
			html.Div([								
				#comparison filter
				html.Label(["Filter comparison by",
					dbc.Input(id="comparison_filter_input", type="search", placeholder="Type here to filter comparisons", debounce=True, style={"font-family": "Arial", "font-size": 12, "height": 36}),
				], style={"width": "20%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),

				#contrast dropdown
				html.Label(["Comparison", 
					dcc.Dropdown(
						id="contrast_dropdown",
						clearable=False
				)], className="dropdown-luigi", style={"width": "35%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),

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

				#best comparisons switch
				html.Div([
					html.Label(["Best comparisons",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[1],
							id="best_comparisons_switch",
							switch=True
						)
					], style={"textAlign": "center"})
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

				#stringecy dropdown
				html.Label(["Stringency", 
					dcc.Dropdown(
						id="stringency_dropdown",
						clearable=False
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"})
			], style={"width": "100%", "display": "inline-block"}),
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
							clearable=False
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
							id="metadata_dropdown_mds",
							clearable=False,
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

			#mds graph
			html.Div([
				dbc.Spinner(
					children = dcc.Graph(id="mds_graph"),
					size = "md",
					color = "lightgray"
				)
			], style={"width": "80%", "display": "inline-block"}),
		], style={"width": "100%", "display": "inline-block"}),
		
		html.Br(),

		#boxplots
		html.Br(),
		html.Div([
			#boxplots options
			html.Div([
				#first row
				html.Div([	
					#x dropdown
					html.Label(["x",
						dcc.Dropdown(
						id="x_boxplot_dropdown",
						clearable=False,
						value="condition"
					)], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
					#y dropdown
					html.Label(["y", 
						dcc.Dropdown(
							id="y_boxplot_dropdown",
							clearable=False,
							value="log2_expression",
					)], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
					#group by dropdown
					html.Label(["Group by", 
						dcc.Dropdown(
							id="group_by_boxplot_dropdown",
							clearable=False,
							value="condition"
					)], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
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
					], style={"width": "5%", "display": "inline-block", "vertical-align": "middle"})
				], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),
				
				html.Br(),

				#second row
				html.Div([	
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
					#best conditions switch
					html.Div([
						html.Label(["Best conditions",
							dbc.Checklist(
								options=[
									{"label": "", "value": 1},
								],
								value=[],
								id="best_conditions_boxplots_switch",
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
					#stats switch
					html.Div([
						html.Label(["Statistics",
							dbc.Checklist(
								options=[
									{"label": "", "value": 1},
								],
								value=[1],
								id="stats_boxplots_switch",
								switch=True
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#height slider
					html.Div([
						html.Label(["Height",
							dcc.Slider(id="boxplots_height_slider", min=200, max=400, step=1, marks=None)
						], style={"width": "100%", "height": "30px", "display": "inline-block"})
					], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),
					#width slider
					html.Div([
						html.Label(["Width",
							dcc.Slider(id="boxplots_width_slider", min=200, max=1000, step=1, marks=None)
						], style={"width": "100%", "height": "30px", "display": "inline-block"})
					], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"})
				], style={"width": "100%", "font-size": "12px", "display": "inline-block"})
			], style={"width": "80%", "display": "inline-block"}),
			
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
				html.Div(id="boxplot_div", children=[
					dbc.Spinner(
						children = dcc.Graph(id="boxplots_graph"),
						size = "md",
						color = "lightgray"
					),
				])
			], style={"width": "100%", "display": "inline-block", "justify-content":"center", "display":"flex"})
		], style={"width": "100%", "display": "inline-block"}),

		html.Br(),
		html.Br(),

		#MA-plot + go plot
		html.Div([
			#MA-plot
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
				], style={"width": "85%", "display": "inline-block"}),
				#MA-plot
				html.Div([
					dbc.Spinner(
						id = "loading_ma_plot",
						children = dcc.Graph(id="ma_plot_graph"),
						size = "md",
						color = "lightgray"
					)
				], style={"width": "85%", "display": "inline-block"}),
			], style={"width": "30%", "display": "inline-block", "font-size": "12px"}),

			#go plot
			html.Div([
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
					html.Div(id="add_gsea_switch_div", hidden=True, children=[
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
			], style={"width": "50%", "display": "inline-block", "font-size": "12px", "vertical-align": "top"})
		], style = {"width": "100%", "display": "inline-block"}),

		#tabs
		html.Br(),
		html.Br(),

		html.Div(children=[
			dcc.Tabs(id={"type": "tabs", "id": "main_tabs"}, value="metadata_tab", style={"height": 40}),
		], style = {"width": "100%", "display": "inline-block"}),

		#tab content
		html.Div(id="tab_content_div", style={"width": "100%", "display": "inline-block"})
	], style={"width": 1200, "font-family": "Arial"})
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})

#metadata table data & columns
#mofa contrasts options
#deconvolution discrete options & datasets options

#metadata tab layout
metadata_tab_layout = html.Div([
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
				filter_options={"case": "insensitive"},
			)
		)
	], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
	html.Br(),
	html.Br()
])

#heatmap tab
heatmap_tab_layout = html.Div([
	html.Div([
		html.Br(),
		
		#heatmap input
		html.Div([
			
			#info + update plot button
			html.Div([
				
				#info
				html.Div([
					html.Div(id="info_heatmap",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto", "text-align": "center"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							##### Heatmap showing row scaled log2 expression/abundance profiles
							
							Use the __feature__ dropdown and form to select the features to be displayed.
							
							Use the __annotations__ dropdown to decorate the heatmap with metadata.
							
							Click a GO plot __balloon__ to display in the heatmap the genes responsible for its enrichment.
							
							Use the __clustered samples__ switch to perform unsupervised hierarchical clustering along the x-axis.
							
							Use the __comparison only__ switch to display only the samples belonging to the two conditions of interest.
							
							Use the __legend__ to hide a group of samples. Use the __hide unselected__ switch to clear the legend from undisplayed samples.
							
							Use __height__ and __width__ sliders to resize the entire plot.
							""")
						],
						target="info_heatmap",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),

				#update plot button
				html.Div([
					dbc.Button("Update plot", id="update_heatmap_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),
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

			#dropdowns
			html.Label(["Annotations", 
				dcc.Dropdown(id="heatmap_annotation_dropdown", 
					multi=True,
					value=[], 
					style={"textAlign": "left", "font-size": "12px"})
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			html.Label(["Features",
				dcc.Dropdown(id="feature_heatmap_dropdown", 
					multi=True, 
					placeholder="Select features", 
					style={"textAlign": "left", "font-size": "12px"})
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			#text area
			dbc.Textarea(id="heatmap_text_area", style={"height": 300, "resize": "none", "font-size": "12px"}),

			html.Br(),

			#search button
			dbc.Button("Search", id="heatmap_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),

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
				], style={"width": "14%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

				#comparison only heatmap switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[1],
							id="comparison_only_heatmap_switch",
							switch=True
						)
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

				#best conditions heatmap switch
				html.Div([
					html.Label(["Best conditions",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="best_conditions_heatmap_switch",
							switch=True
						)
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

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
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),
				
				#height slider
				html.Label(["Height",
					dcc.Slider(id="hetamap_height_slider", min=200, step=1, marks=None)
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"}),
				#width slider
				html.Label(["Width",
					dcc.Slider(id="hetamap_width_slider", min=200, max=885, step=1, marks=None)
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle"})
			], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),

			#graph
			dbc.Spinner(
				children = [dcc.Graph(id="heatmap_graph")],
				size = "md",
				color = "lightgray"
			),
			#legend
			html.Div(id="heatmap_legend_div", hidden=True)
		], style = {"width": "74%", "display": "inline-block"})
	], style = {"width": "100%", "height": 800, "display": "inline-block"})
])

#multi violin tab
multi_violin_tab_layout = html.Div([
	html.Div(id="multiboxplot_div", children=[
		
		html.Br(),
		
		#input section
		html.Div([
			
			#info + update plot button
			html.Div([
				
				#info
				html.Div([
					html.Div(id="info_multiboxplots",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto", "text-align": "center"}),
					dbc.Tooltip(
						children=[dcc.Markdown(
							"""
							Use the __features__ dropdown and form to select the features to be displayed.
							
							Use __x__ and __y__, or the __group by__ dropdowns to select the data or facet the plot, respectively.
							
							Use the __plot per row__ dropdown to choose how many features to be displayed per row.
							
							Use the __comparison only__ switch to display only the groups belonging to the two conditions of interest.
							
							Use the appropriate switch to __show as boxplots__.
							
							Use __height__ and __width__ sliders to resize the entire plot.
							
							Use the __legend__ to hide a group. Use the __hide unselected__ switch to clear the legend from undisplayed groups.
							
							A maximum of 20 features has been set.

							""")
						],
						target="info_multiboxplots",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

				#update plot button
				html.Div([
					dbc.Button("Update plot", id="update_multiboxplot_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"})
				], style={"width": "30%", "display": "inline-block", "vertical-align": "middle"}),
			]),
			
			html.Br(),

			#dropdown
			html.Label(["Features",
				dcc.Dropdown(id="feature_multi_boxplots_dropdown", 
					multi=True, 
					placeholder="Select features",
					style={"textAlign": "left", "font-size": "12px"}
				),
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			#text area
			dbc.Textarea(id="multi_boxplots_text_area", style={"width": "100%", "height": 300, "resize": "none", "font-size": "12px"}),

			html.Br(),

			#search button
			dbc.Button("Search", id="multi_boxplots_search_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),

			html.Br(),

			#genes not found area
			html.Div(id="genes_not_found_multi_boxplots_div", children=[], hidden=True, style={"font-size": "12px", "text-align": "center"}), 

			html.Br()
		], style={"width": "25%", "display": "inline-block", "vertical-align": "top"}),

		#multiboxplots options and graph
		html.Div([
			#dropdowns
			html.Div([
				#x dropdown
				html.Label(["x",
					dcc.Dropdown(
					id="x_multiboxplots_dropdown",
					clearable=False,
					value="condition"
				)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#group by dropdown
				html.Label(["Group by", 
					dcc.Dropdown(
						id="group_by_multiboxplots_dropdown",
						clearable=False,
						value="condition"
				)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#plot per row
				html.Label(["Plot per row", 
					dcc.Dropdown(
						id="plot_per_row_multiboxplots_dropdown",
						clearable=False,
						value=3,
						options=[{"label": n, "value": n} for n in [1, 2, 3]]
				)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
			], style={"width": "100%", "display": "inline-block"}),
			
			#switches and sliders
			html.Div([
				#comparison_only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[1],
							id="comparison_only_multiboxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#best conditions switch
				html.Div([
					html.Label(["Best conditions",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="best_conditions_multiboxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#hide unselected switch
				html.Div([
					html.Label(["Hide unselected",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="hide_unselected_multiboxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#show as boxplot switch
				html.Div([
					html.Label(["Show as boxplots",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[],
							id="show_as_multiboxplot_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#stats switch
				html.Div([
					html.Label(["Statistics",
						dbc.Checklist(
							options=[
								{"label": "", "value": 1},
							],
							value=[1],
							id="stats_multiboxplots_switch",
							switch=True
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#custom hetmap dimension
				html.Div([
					#height slider
					html.Label(["Height",
						dcc.Slider(id="multiboxplots_height_slider", min=200, step=1, max=2000, marks=None)
					], style={"width": "49.5%", "display": "inline-block"}),
					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),
					#width slider
					html.Label(["Width",
						dcc.Slider(id="multiboxplots_width_slider", min=200, max=900, value=900, step=1, marks=None)
					], style={"width": "49.5%", "display": "inline-block"})
				], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
			], style={"width": "100%", "display": "inline-block"}),

			#x filter dropdown
			html.Div(id="x_filter_dropdown_multiboxplots_div", hidden=True, children=[
				html.Label(["x filter", 
					dcc.Dropdown(
						id="x_filter_multiboxplots_dropdown",
						multi=True,
				)], className="dropdown-luigi", style={"width": "100%", "textAlign": "left"}),
			], style={"width": "90%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			#graph
			html.Div(id="multiboxplot_graph_div", children=[
				dbc.Spinner(size = "md", color = "lightgray", children=[
					html.Div(
						id="multi_boxplots_div",
						children=[dbc.Spinner(
							children = [dcc.Graph(id="multi_boxplots_graph", figure={})],
							size = "md",
							color = "lightgray")
					], hidden=True)
				])
			], style={"width": "100%", "display": "inline-block", "vertical-align": "top"}),

		], style={"width": "75%", "font-size": "12px", "display": "inline-block"}),
		
		html.Br(),
		html.Br(),

		#div that can contain statistics table
		html.Br(),
		dbc.Spinner(
			size = "md",
			color = "lightgray",
			children = html.Div(
				id="multiboxplot_stats_div",
				hidden=True,
				style={"width": "100%", "display": "inline-block"},
				className="luigi-dash-table",
				children=[
					#download statistics
					dbc.Button("Download statistics", id="download_multiboxplot_stats_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),
					dcc.Download(id="download_multiboxplot_stats"),
					
					#table
					html.Br(),
					html.Br(),
					dash_table.DataTable(
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
						page_size=25,
						sort_action="native",
						style_header={
							"text-align": "left"
						},
						style_as_list_view=True,
						filter_options={"case": "insensitive"}
					),
					html.Br()
				]
			)
		),
		html.Br()
	], style={"width": "100%", "display": "inline-block"})
])

#correlation tab
correlation_tab_layout = html.Div([
	dcc.Store(id="correletion_stats"),
	html.Br(),
	
	#dropdowns and switches
	html.Div([
		#x dataset correlation dropdown
		html.Div([
			html.Label(["x dataset",
				dcc.Dropdown(
					id="x_dataset_correlation_dropdown",
					clearable=False,
			)], style={"width": "100%"}, className="dropdown-luigi"),
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#x correlation dropdown
		html.Div([
			html.Label(["x",
				dcc.Dropdown(
					id="x_correlation_dropdown",
					placeholder="Search a feature"
			)], style={"width": "100%"}, className="dropdown-luigi"),
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#y dataset correlation dropdown
		html.Div([
			html.Label(["y dataset",
				dcc.Dropdown(
					id="y_dataset_correlation_dropdown",
					clearable=False,
			)], style={"width": "100%"}, className="dropdown-luigi"),
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#y correlation dropdown
		html.Div([
			html.Label(["y",
				dcc.Dropdown(
					id="y_correlation_dropdown",
					placeholder="Search a feature"
			)], style={"width": "100%"}, className="dropdown-luigi"),
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#group by correlation dropdown
		html.Div([
			html.Label(["Group by",
				dcc.Dropdown(
					id="group_by_correlation_dropdown",
			)], style={"width": "100%"}, className="dropdown-luigi"),
		], style={"width": "35%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#switches
		html.Div([
			#comparison_only switch
			html.Div([
				html.Label(["Comparison only",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[1],
						id="comparison_only_correlation_switch",
						switch=True
					)
				], style={"textAlign": "center"})
			], style={"width": "32%", "display": "inline-block", "vertical-align": "middle"}),

			#hide unselected switch
			html.Div([
				html.Label(["Hide unselected",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1, "disabled": True},
						],
						value=[],
						id="hide_unselected_correlation_switch",
						switch=True
					)
				], style={"textAlign": "center"}),
			], style={"width": "32%", "display": "inline-block", "vertical-align": "middle"}),

			#sort correlation by significance
			html.Div([
				html.Label(["Sort by significance",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[],
						id="sort_by_significance_correlation_switch",
						switch=True
					)
				], style={"textAlign": "center"}),
			], style={"width": "36%", "display": "inline-block", "vertical-align": "middle"})
	], style={"width": "65%", "display": "inline-block"}),
		#width slider
		html.Div([
			html.Label(["Width",
				dcc.Slider(id="correlation_width_slider", min=300, max=600, step=1, marks=None)
			], style={"width": "100%", "height": "30px", "display": "inline-block"})
		], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
		#height slider
		html.Div([
			html.Label(["Height",
				dcc.Slider(id="correlation_height_slider", min=300, max=1000, step=1, marks=None)
			], style={"width": "100%", "height": "30px", "display": "inline-block"})
		], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"})
	],  style={"width": "40%", "display": "inline-block", "font-size": "12px", "vertical-align": "top"}),

	#statistics plot
	html.Div(id="statistics_feature_correlation_plot_div", hidden=True, children=[
		dbc.Spinner(
			children = dcc.Graph(id="statistics_feature_correlation_plot"),
			size = "md",
			color = "lightgray"
		)
	], style={"width": "10%", "display": "inline-block", "vertical-align": "top"}),

	#main plot
	html.Div([
		dbc.Spinner(
			children = dcc.Graph(id="feature_correlation_plot"),
			size = "md",
			color = "lightgray"
		)
	], style={"width": "50%", "display": "inline-block"}),

	html.Br(),
	html.Br()
])

#diversity tab
diversity_tab_layout = html.Div([
	html.Div([
		html.Br(),

		#dropdown and switch
		html.Div([
			#dropdown
			html.Label(["Group by",
				dcc.Dropdown(
					id="group_by_diversity_dropdown",
					clearable=False,
					value="condition"
			)], style={"width": "15%", "vertical-align": "middle", "textAlign": "left"}, className="dropdown-luigi"),
			#hide unselected switch
			html.Div([
				html.Label(["Hide unselected",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[],
						id="hide_unselected_diversity_switch",
						switch=True
					)
				], style={"textAlign": "center"}),
			], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
			#statistics switch
			html.Div([
				html.Label(["Statistics",
					dbc.Checklist(
						options=[
							{"label": "", "value": 1},
						],
						value=[1],
						id="statistics_diversity_switch",
						switch=True
					)
				], style={"textAlign": "center"}),
			], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
		], style={"width": "100%", "display": "inline-block", "font-size": "12px"}),
		
		#graph
		html.Div([
			dbc.Spinner(
				id = "loading_mds_metadata",
				children = dcc.Graph(id="diversity_graph"),
				size = "md",
				color = "lightgray"
			)
		], style={"width": "100%", "display": "inline-block"})
	], style={"width": "100%", "display": "inline-block"})
])

#dge tab layout
dge_tab_layout = html.Div([
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
		dcc.Dropdown(id="multi_gene_dge_table_dropdown", 
			multi=True, 
			placeholder="", 
			style={"textAlign": "left", "font-size": "12px"})
	], className="dropdown-luigi", style={"width": "25%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"}),

	#target priorization switch
	html.Div(id = "target_prioritization_switch_div", hidden=True, children=[
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
			size="md",
			color="lightgray",
			children=dash_table.DataTable(
				id="dge_table_filtered",
				filter_action="native",
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
				style_as_list_view=True,
				filter_options={"case": "insensitive"}
			)
		)
	], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}, hidden=True),

	#full dge table
	html.Div([
		html.Br(),
		dbc.Spinner(
			size="md",
			color="lightgray",
			children=dash_table.DataTable(
				id="dge_table",
				filter_action="native",
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
				style_as_list_view=True,
				filter_options={"case": "insensitive"}
			)
		)
	], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
	html.Br()
])

#go tab layout
go_tab_layout = html.Div([
	
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
				filter_action="native",
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
				style_as_list_view=True,
				filter_options={"case": "insensitive"}
			)
		)
	], className="luigi-dash-table", style={"width": "100%", "font-family": "arial"}),
	html.Br()
])

#mofa tab layout
mofa_tab_layout = html.Div([
	html.Br(),
	
	#mofa contrast dropdown
	html.Div([
		html.Label(["MOFA comparison",
			dcc.Dropdown(
				id="mofa_comparison_dropdown",
				clearable=False,
		)], style={"width": "100%"}, className="dropdown-luigi"),
	], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left", "font-size": "12px"}),
	
	#plots
	html.Div([
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
		], style={"width": "65%", "display": "inline-block", "vertical-align": "top"}),
	], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

	html.Br()
])

#deconvolution tab layout
deconvolution_tab_layout = html.Div([
	html.Br(),

	html.Div(id="deconvolution_div", children=[
		#info deconvolution
		html.Div([
			html.Div(id="info_deconvolution",  children="ℹ", style={"border": "2px solid black", "border-radius": 20, "width": 20, "height": 20, "font-family": "courier-new", "font-size": "15px", "font-weight": "bold", "line-height": 16, "margin": "auto"}),
			dbc.Tooltip(
				children=[dcc.Markdown(
					"""
					TODO
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
			value="condition",
		)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#second split_by dropdown
		html.Label(["and by",
			dcc.Dropdown(
			id="split_by_2_deconvolution_dropdown",
			clearable=False,
			value="condition",
		)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#third split_by dropdown
		html.Label(["and by",
			dcc.Dropdown(
			id="split_by_3_deconvolution_dropdown",
			clearable=False,
			value="condition",
		)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#plot per row dropdown
		html.Label(["Plots per row",
			dcc.Dropdown(
			id="plots_per_row_deconvolution_dropdown",
			clearable=False,
			options=[{"label": "1", "value": 1}, {"label": "2", "value": 2}, {"label": "3", "value": 3}, {"label": "4", "value": 4}, {"label": "5", "value": 5}],
			value=4
		)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#dataset dropdown
		html.Label(["Data sets",
			dcc.Dropdown(
			id="data_sets_deconvolution_dropdown",
			clearable=False,
		)], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#reset labels button
		html.Div([
			dbc.Button("Reset labels", id="reset_labels_deconvolution_button", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'})
		], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", 'color': 'black'}),

		#deconvolution plot
		html.Div([
			dbc.Spinner(
				id = "loading_deconvolution",
				children = dcc.Graph(id="deconvolution_graph"),
				size = "md",
				color = "lightgray"
			)
		], style={"width": "50%", "display": "inline-block"})
	], style={"width": "100%", "display": "inline-block", "font-size": "12px"})
])
