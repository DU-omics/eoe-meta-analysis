#import packages
from dash import html, dcc
import dash_bootstrap_components as dbc
from functions import multiple_analysis, repos_options

#app layout
layout = html.Div([
	html.Div([
		html.Br(),
		#title
		html.Div(id="header_div"),

		#store components
		dcc.Store(id="color_mapping"),
		dcc.Store(id="label_to_value"),
		dcc.Store(id="metadata_table_store"),
		dcc.Store(id="annotation_dropdown_options"),
		dcc.Store(id="discrete_metadata_options"),
		dcc.Store(id="continuous_metadata_options"),

		#common options dropdowns
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
							id="metadata_dropdown",
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
					value="condition"
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#y dropdown
				html.Label(["y", 
							dcc.Dropdown(
								id="y_boxplot_dropdown",
								clearable=False,
								value="log2_expression",
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#group by dropdown
				html.Label(["Group by", 
							dcc.Dropdown(
								id="group_by_boxplot_dropdown",
								clearable=False,
								value="condition"
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
				], style={"width": "9%", "display": "inline-block", "vertical-align": "middle"}),
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
				], style={"width": "9%", "display": "inline-block", "vertical-align": "middle"}),
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
				], style={"width": "9%", "display": "inline-block", "vertical-align": "middle"}),
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
				], style={"width": "9%", "display": "inline-block", "vertical-align": "middle"}),
				#height slider
				html.Div([
					html.Label(["Height",
						dcc.Slider(id="boxplots_height_slider", min=200, max=400, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "14.5%", "display": "inline-block", "vertical-align": "middle"}),
				#width slider
				html.Div([
					html.Label(["Width",
						dcc.Slider(id="boxplots_width_slider", min=200, max=1000, step=1)
					], style={"width": "100%", "height": "30px", "display": "inline-block"})
				], style={"width": "14.5%", "display": "inline-block", "vertical-align": "middle"}),
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
			], style={"width": "50%", "display": "inline-block", "font-size": "12px"}),

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
			], style={"width": "50%", "display": "inline-block", "font-size": "12px", "vertical-align": "top"})
		], style = {"width": "100%", "display": "inline-block"}),

		#tabs
		html.Br(),
		html.Br(),

		html.Div(children=[
			dcc.Tabs(id="site_tabs", value="metadata_tab", style={"height": 40}),
		], style = {"width": "100%", "display": "inline-block"})
	], style={"width": 1200, "font-family": "Arial"})
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})
