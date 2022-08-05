#import packages
from dash import html, dcc
from dash import dash_table
import dash_bootstrap_components as dbc
from functions import config, multiple_analysis, repos_options
import info_text

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
					)], style={"width": "100%"}, className="dropdown-luigi"),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_analysis_dropdown)],
						target="analysis_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left", "font-size": "12px"}, hidden=multiple_analysis),

				#expression dataset dropdown
				html.Div([
					html.Label(["Expression/Abundance",
						dcc.Dropdown(
							id="feature_dataset_dropdown",
							clearable=False,
					)], style={"width": "100%"}, className="dropdown-luigi"),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_expression_dropdown)],
						target="feature_dataset_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),

				#feature dropdown
				html.Div([
					html.Label(id = "feature_label", children = ["Loading...",
						dcc.Dropdown(
							id="feature_dropdown",
							clearable=False
					)], style={"width": "100%"}, className="dropdown-luigi"),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_feature_dropdown)],
						target="feature_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "40%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"})
			], style={"width": "100%", "display": "inline-block"}),

			#second row
			html.Div([								
				#comparison filter
				html.Label(["Filter comparison by",
					dbc.Input(id="comparison_filter_input", type="search", placeholder="Type here to filter comparisons", debounce=True, style={"font-family": "Arial", "font-size": 12, "height": 36}),
				], style={"width": "20%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),				
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_comparison_filter_dropdown)],
					target="comparison_filter_input",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				),

				#contrast dropdown
				html.Label(["Comparison", 
					dcc.Dropdown(
						id="contrast_dropdown",
						clearable=False
				)], className="dropdown-luigi", style={"width": "35%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_comparison_dropdown)],
					target="contrast_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				),

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
					], style={"textAlign": "center"}),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_best_comparison_switch)],
						target="best_comparisons_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					),
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),

				#stringecy dropdown
				html.Label(["Stringency", 
					dcc.Dropdown(
						id="stringency_dropdown",
						clearable=False
				)], className="dropdown-luigi", style={"width": "10%", "display": "inline-block", "margin-left": "auto", "margin-right": "auto", "vertical-align": "middle", "textAlign": "left"}),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_stringency_dropdown)],
					target="stringency_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
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
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_dataset_dropdown_mds)],
						target="mds_dataset",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#mds type dropdown
				html.Div([
					html.Label(["MDS type", 
						dcc.Dropdown(
							id="mds_type",
							clearable=False
					)], style={"width": "100%", "textAlign": "left"}),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_type_dropdown_mds)],
						target="mds_type",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

				#color by dropdown
				html.Div([
					html.Label(["Color by", 
						dcc.Dropdown(
							id="metadata_dropdown_mds",
							clearable=False,
							value="condition"
					)], style={"width": "100%", "textAlign": "left"}),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_color_by_dropdown_mds)],
						target="metadata_dropdown_mds",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto"}),

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
					], style={"textAlign": "center"}),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_comparison_only_switch)],
						target="comparison_only_mds_metadata_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
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
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
						target="hide_unselected_mds_metadata_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"})
			], style={"width": "100%", "font-size": "12px", "display": "inline-block"}),

			#mds graph
			html.Div([
				dbc.Spinner(
					children = dcc.Graph(id="mds_graph"),
					size = "md",
					color = "lightgray"
				),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_plot_mds)],
					target="mds_graph",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
			], style={"width": "80%", "display": "inline-block"})
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
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_x_violins)],
							target="x_boxplot_dropdown",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
					#y dropdown
					html.Label(["y", 
						dcc.Dropdown(
							id="y_boxplot_dropdown",
							clearable=False,
							value="log2_expression",
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_y_violins)],
							target="y_boxplot_dropdown",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
					#group by dropdown
					html.Label(["Group by", 
						dcc.Dropdown(
							id="group_by_boxplot_dropdown",
							clearable=False,
							value="condition"
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_group_by)],
							target="group_by_boxplot_dropdown",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], className="dropdown-luigi", style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"})
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
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_comparison_only_switch)],
								target="comparison_only_boxplots_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#best conditions switch
					html.Div([
						html.Label(["Best conditions",
							dbc.Checklist(
								options=[{"label": "", "value": 1}],
								value=[],
								id="best_conditions_boxplots_switch",
								switch=True
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_best_conditions_switch)],
								target="best_conditions_boxplots_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#hide unselected switch
					html.Div([
						html.Label(["Hide unselected",
							dbc.Checklist(
								options=[{"label": "", "value": 1}],
								value=[],
								id="hide_unselected_boxplot_switch",
								switch=True
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
								target="hide_unselected_boxplot_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#show as boxplot switch
					html.Div([
						html.Label(["Show as boxplots",
							dbc.Checklist(
								options=[{"label": "", "value": 1, "disabled": False}],
								value=[],
								id="show_as_boxplot_switch",
								switch=True
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_show_as_boxplots)],
								target="show_as_boxplot_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#stats switch
					html.Div([
						html.Label(["Statistics",
							dbc.Checklist(
								options=[{"label": "", "value": 1}],
								value=[1],
								id="stats_boxplots_switch",
								switch=True
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_statistics_switch_violins)],
								target="stats_boxplots_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"textAlign": "center"}),
					], style={"width": "10%", "display": "inline-block", "vertical-align": "middle"}),
					#height slider
					html.Div([
						html.Label(["Height",
							dcc.Slider(id="boxplots_height_slider", min=200, max=750, step=1, marks=None)
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
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_x_filter_dropdown_violins)],
						target="x_filter_boxplot_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "100%", "textAlign": "left"}),
			], style={"width": "80%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

			#plot
			html.Div([
				html.Div(id="boxplot_div", children=[
					dbc.Spinner(
						children = dcc.Graph(id="boxplots_graph"),
						size = "md",
						color = "lightgray"
					)
				])
			], style={"width": "100%", "display": "inline-block", "justify-content":"center", "display":"flex"})
		], style={"width": "100%", "display": "inline-block"}),

		html.Br(),
		html.Br(),

		#MA-plot + go plot
		html.Div([
			#MA-plot
			html.Div([
				#annotation dropdown
				html.Div([
					html.Label(["Annotation",
						dcc.Dropdown(
							id="ma_plot_annotation_dropdown",
							clearable=False,
							options=[{"label": "All", "value": "all"}, {"label": "Differential analysis", "value": "differential_analtsis"}, {"label": "Selected feature", "value": "selected_feature"}, {"label": "None", "value": "none"}],
							value="differential_analtsis"
					)], style={"width": "100%"}, className="dropdown-luigi"),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_annotations_ma_plot)],
						target="ma_plot_annotation_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "85%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left", "font-size": "12px"}, hidden=multiple_analysis),
				#MA-plot
				html.Div([
					dbc.Spinner(
						id = "loading_ma_plot",
						children = dcc.Graph(id="ma_plot_graph"),
						size = "md",
						color = "lightgray"
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_ma_plot)],
						target="ma_plot_graph",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"width": "85%", "display": "inline-block"}),
			], style={"width": "30%", "display": "inline-block", "font-size": "12px"}),

			#go plot
			html.Div([
				#search bar go plot
				html.Div([
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
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_add_gsea_switch)],
								target="add_gsea_switch",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
							)
						], style={"width": "100%", "display": "inline-block", "vertical-align": "middle", "text-align": "center"})
					], style={"width": "15%", "display": "inline-block", "font-size": "12px"}),

					#spacer
					html.Div([], style={"width": "1%", "display": "inline-block"}),

					#search bar
					html.Div([
						dbc.Input(
							id="go_plot_filter_input", 
							type="search", 
							placeholder="Type here to filter GO gene sets", 
							size="30", 
							debounce=True, 
							style={"font-family": "Arial", "font-size": 12}
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_go_plot_search_bar)],
							target="go_plot_filter_input",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
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
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_go_plot)],
						target="go_plot_graph",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
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
		html.Div(id="tab_content_div", style={"width": "100%", "display": "inline-block"}),

		#footer
		html.Footer([
			html.Hr(),
			dcc.Markdown(config["footer"])
		], style={"font-size": 11})

	], style={"width": 1200, "font-family": "Arial"})
], style={"width": "100%", "justify-content":"center", "display":"flex", "textAlign": "center"})

#sunkey tab layout
sankey_tab_layout = html.Div([
	html.Br(),

	#workflow if present
	html.Div(id="workflow_div", hidden=True),

	#graph
	dbc.Spinner(
		children = [dcc.Graph(id="sankey_graph")],
		size = "md",
		color = "lightgray"
	),
	dbc.Tooltip(
		children=[dcc.Markdown(info_text.info_sankey_plot)],
		target="sankey_graph",
		placement="right",
		style={"font-family": "arial", "font-size": 14}
	)
])

#metadata table tab layout
metadata_table_tab_layout = html.Div([
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
			
			#update plot button
			html.Div([
				#update plot button
				html.Div([
					dbc.Button("Update plot", id="update_heatmap_plot_button", style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", "color": "black"}),
				], style={"width": "40%", "display": "inline-block", "vertical-align": "middle"}),
			]),
			
			html.Br(),

			#dropdowns
			html.Label(["Annotations", 
				dcc.Dropdown(id="heatmap_annotation_dropdown", 
					multi=True,
					value=[], 
					style={"textAlign": "left", "font-size": "12px"}
				),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_heatmap_annotation_dropdown)],
					target="heatmap_annotation_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			html.Label(["Features",
				dcc.Dropdown(id="feature_heatmap_dropdown", 
					multi=True, 
					placeholder="Select features", 
					style={"textAlign": "left", "font-size": "12px"}
				),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_features_dropdown)],
					target="feature_heatmap_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			#text area
			dbc.Textarea(id="heatmap_text_area", style={"height": 300, "resize": "none", "font-size": "12px"}),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_features_search_area)],
				target="heatmap_text_area",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			),

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
			
			#swithces and custom hetmap dimension
			html.Div([
				#cluster heatmap switch
				html.Div([
					html.Label(["Clustered samples",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[1],
							id="clustered_heatmap_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_heatmap_clustered_samples_switch)],
							target="clustered_heatmap_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
				], style={"width": "14%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

				#comparison only heatmap switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[1],
							id="comparison_only_heatmap_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_comparison_only_switch)],
							target="comparison_only_heatmap_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"width": "100%", "display": "inline-block", "vertical-align": "middle"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle", "font-size": "12px"}),

				#best conditions heatmap switch
				html.Div([
					html.Label(["Best conditions",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[],
							id="best_conditions_heatmap_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_best_conditions_switch)],
							target="best_conditions_heatmap_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
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
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
							target="hide_unselected_heatmap_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
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
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_heatmap_plot)],
				target="heatmap_graph",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
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
			
			#pdate plot button
			html.Div([
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
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_features_dropdown)],
					target="feature_multi_boxplots_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
			], className="dropdown-luigi", style={"width": "100%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			html.Br(),

			#text area
			dbc.Textarea(id="multi_boxplots_text_area", style={"width": "100%", "height": 300, "resize": "none", "font-size": "12px"}),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_features_search_area)],
				target="multi_boxplots_text_area",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			),

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
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_x_violins)],
						target="x_multiboxplots_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#group by dropdown
				html.Label(["Group by", 
					dcc.Dropdown(
						id="group_by_multiboxplots_dropdown",
						clearable=False,
						value="condition"
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_group_by)],
						target="group_by_multiboxplots_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
				#plot per row
				html.Label(["Plot per row", 
					dcc.Dropdown(
						id="plot_per_row_multiboxplots_dropdown",
						clearable=False,
						value=3,
						options=[{"label": n, "value": n} for n in [1, 2, 3]]
					)
				], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),
			], style={"width": "100%", "display": "inline-block"}),
			
			#switches and sliders
			html.Div([
				#comparison_only switch
				html.Div([
					html.Label(["Comparison only",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[1],
							id="comparison_only_multiboxplots_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_comparison_only_switch)],
							target="comparison_only_multiboxplots_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#best conditions switch
				html.Div([
					html.Label(["Best conditions",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[],
							id="best_conditions_multiboxplots_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_best_conditions_switch)],
							target="best_conditions_multiboxplots_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
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
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
							target="hide_unselected_multiboxplots_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#show as boxplot switch
				html.Div([
					html.Label(["Show as boxplots",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[],
							id="show_as_multiboxplot_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_show_as_boxplots)],
							target="show_as_multiboxplot_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#stats switch
				html.Div([
					html.Label(["Statistics",
						dbc.Checklist(
							options=[{"label": "", "value": 1}],
							value=[1],
							id="stats_multiboxplots_switch",
							switch=True
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_multiviolins_statistics_switch)],
							target="stats_multiboxplots_switch",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"textAlign": "center"}),
				], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
				#custom dimension
				html.Div([
					#height slider
					html.Label(["Height",
						dcc.Slider(id="multiboxplots_height_slider", min=200, step=1, max=3250, marks=None)
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
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_x_filter_dropdown_violins)],
						target="x_filter_multiboxplots_dropdown",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], className="dropdown-luigi", style={"width": "100%", "textAlign": "left"}),
			], style={"width": "90%", "display": "inline-block", "textAlign": "left", "font-size": "12px"}),

			#graph
			html.Div(id="multiboxplot_graph_div", children=[
				dbc.Spinner(size = "md", color = "lightgray", children=[
					html.Div(
						id="multi_boxplots_div",
						children=[
							dbc.Spinner(
								children = [dcc.Graph(id="multi_boxplots_graph", figure={})],
								size = "md",
								color = "lightgray")
						], hidden=True
					)
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
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_correlation_x_dataset_dropdown)],
				target="x_dataset_correlation_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#x correlation dropdown
		html.Div([
			html.Label(["x",
				dcc.Dropdown(
					id="x_correlation_dropdown",
					placeholder="Search a feature"
			)], style={"width": "100%"}, className="dropdown-luigi"),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_correlation_x_dropdown)],
				target="x_correlation_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#y dataset correlation dropdown
		html.Div([
			html.Label(["y dataset",
				dcc.Dropdown(
					id="y_dataset_correlation_dropdown",
					clearable=False,
			)], style={"width": "100%"}, className="dropdown-luigi"),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_correlation_y_dataset_dropdown)],
				target="y_dataset_correlation_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#y correlation dropdown
		html.Div([
			html.Label(["y",
				dcc.Dropdown(
					id="y_correlation_dropdown",
					placeholder="Search a feature"
			)], style={"width": "100%"}, className="dropdown-luigi"),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_correlation_y_dropdown)],
				target="y_correlation_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "50%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#group by correlation dropdown
		html.Div([
			html.Label(["Group by",
				dcc.Dropdown(
					id="group_by_correlation_dropdown",
			)], style={"width": "100%"}, className="dropdown-luigi"),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_group_by)],
				target="group_by_correlation_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "35%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left"}),
		#switches
		html.Div([
			#comparison_only switch
			html.Div([
				html.Label(["Comparison only",
					dbc.Checklist(
						options=[{"label": "", "value": 1}],
						value=[1],
						id="comparison_only_correlation_switch",
						switch=True
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_comparison_only_switch)],
						target="comparison_only_correlation_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"textAlign": "center"})
			], style={"width": "32%", "display": "inline-block", "vertical-align": "middle"}),

			#hide unselected switch
			html.Div([
				html.Label(["Hide unselected",
					dbc.Checklist(
						options=[{"label": "", "value": 1, "disabled": True}],
						value=[],
						id="hide_unselected_correlation_switch",
						switch=True
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
						target="hide_unselected_correlation_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"textAlign": "center"}),
			], style={"width": "32%", "display": "inline-block", "vertical-align": "middle"}),

			#sort correlation by significance
			html.Div([
				html.Label(["Sort by significance",
					dbc.Checklist(
						options=[{"label": "", "value": 1}],
						value=[1],
						id="sort_by_significance_correlation_switch",
						switch=True
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_correlation_sort_by_significance)],
						target="sort_by_significance_correlation_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
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
		),
		dbc.Tooltip(
			children=[dcc.Markdown(info_text.info_correlation_statistics_plot)],
			target="statistics_feature_correlation_plot",
			placement="right",
			style={"font-family": "arial", "font-size": 14}
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
				),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_group_by)],
					target="group_by_diversity_dropdown",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
				)
			], style={"width": "15%", "vertical-align": "middle", "textAlign": "left"}, className="dropdown-luigi"),
			#hide unselected switch
			html.Div([
				html.Label(["Hide unselected",
					dbc.Checklist(
						options=[{"label": "", "value": 1}],
						value=[],
						id="hide_unselected_diversity_switch",
						switch=True
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_hide_unselected_switch)],
						target="hide_unselected_diversity_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
					)
				], style={"textAlign": "center"}),
			], style={"width": "11%", "display": "inline-block", "vertical-align": "middle"}),
			#statistics switch
			html.Div([
				html.Label(["Statistics",
					dbc.Checklist(
						options=[{"label": "", "value": 1}],
						value=[1],
						id="statistics_diversity_switch",
						switch=True
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_diversity_statistics_switch)],
						target="statistics_diversity_switch",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
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
		], style={"width": "75%", "display": "inline-block"})
	], style={"width": "100%", "display": "inline-block"})
])

#dge tab layout
dge_tab_layout = html.Div([
	html.Br(),
	#title dge table
	html.Div(id="dge_table_title", children=[], style={"width": "100%", "display": "inline-block", "textAlign": "center", "font-size": "14px"}),
	html.Br(),
	html.Br(),

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
			style={"textAlign": "left", "font-size": "12px"}
		),
		dbc.Tooltip(
			children=[dcc.Markdown(info_text.info_dge_table_feature_filter_dropdown)],
			target="multi_gene_dge_table_dropdown",
			placement="right",
			style={"font-family": "arial", "font-size": 14}
		)
	], className="dropdown-luigi", style={"width": "25%", "display": "inline-block", "font-size": "12px", "vertical-align": "middle"}),

	#target priorization switch
	html.Div(id = "target_prioritization_switch_div", hidden=True, children=[
		html.Label(["Target prioritization",
			dbc.Checklist(
				options=[{"label": "", "value": 1}],
				value=[],
				id="target_prioritization_switch",
				switch=True
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_dge_table_target_prioritization_switch)],
				target="target_prioritization_switch",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
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
		html.Label(["Comparison",
			dcc.Dropdown(
				id="mofa_comparison_dropdown",
				clearable=False,
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_mofa_group_contrast_dropdown)],
				target="mofa_comparison_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], style={"width": "100%"}, className="dropdown-luigi"),
	], style={"width": "20%", "display": "inline-block", "vertical-align": "middle", "textAlign": "left", "font-size": "12px"}),
	
	#plots
	html.Div([
		#mofa data overview
		html.Div([
			dbc.Spinner(
				children = dcc.Graph(id="mofa_data_overview"),
				size = "md",
				color = "lightgray"
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_mofa_data_overview_plot)],
				target="mofa_data_overview",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
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
				),
				dbc.Tooltip(
					children=[dcc.Markdown(info_text.info_mofa_variance_heatmap_plot)],
					target="mofa_variance_heatmap",
					placement="right",
					style={"font-family": "arial", "font-size": 14}
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
					),
					dbc.Tooltip(
						children=[dcc.Markdown(info_text.info_mofa_top_features_for_factor_plot)],
						target="mofa_factor_plot",
						placement="right",
						style={"font-family": "arial", "font-size": 14}
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
								options=[{"label": "", "value": 1}],
								value=[1],
								id="group_condition_switch_mofa",
								switch=True
							),
							dbc.Tooltip(
								children=[dcc.Markdown(info_text.info_mofa_group_condition_switch)],
								target="group_condition_switch_mofa",
								placement="right",
								style={"font-family": "arial", "font-size": 14}
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
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_mofa_factor_scores_plot)],
							target="mofa_all_factors_values",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
						)
					], style={"width": "100%", "display": "inline-block"}),
					#feature expression or abundance
					html.Div([
						dbc.Spinner(
							children = dcc.Graph(id="mofa_factor_expression_abundance"),
							size = "md",
							color = "lightgray"
						),
						dbc.Tooltip(
							children=[dcc.Markdown(info_text.info_mofa_feature_expression_abundance_plot)],
							target="mofa_factor_expression_abundance",
							placement="right",
							style={"font-family": "arial", "font-size": 14}
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
		#split_by dropdown
		html.Label(["Split by",
			dcc.Dropdown(
			id="split_by_1_deconvolution_dropdown",
			clearable=False,
			value="condition",
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_deconvolution_split_by_dropdown)],
				target="split_by_1_deconvolution_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#second split_by dropdown
		html.Label(["and by",
			dcc.Dropdown(
			id="split_by_2_deconvolution_dropdown",
			clearable=False,
			value="condition",
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_deconvolution_and_by_2_dropdown)],
				target="split_by_2_deconvolution_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#third split_by dropdown
		html.Label(["and by",
			dcc.Dropdown(
			id="split_by_3_deconvolution_dropdown",
			clearable=False,
			value="condition",
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_deconvolution_and_by_3_dropdown)],
				target="split_by_3_deconvolution_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#plot per row dropdown
		html.Label(["Plots per row",
			dcc.Dropdown(
				id="plots_per_row_deconvolution_dropdown",
				clearable=False,
				options=[{"label": "1", "value": 1}, {"label": "2", "value": 2}, {"label": "3", "value": 3}, {"label": "4", "value": 4}, {"label": "5", "value": 5}],
				value=4
			)
		], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#dataset dropdown
		html.Label(["Data sets",
			dcc.Dropdown(
			id="data_sets_deconvolution_dropdown",
			clearable=False,
			),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_deconvolution_data_sets_dropdown)],
				target="data_sets_deconvolution_dropdown",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
		], className="dropdown-luigi", style={"width": "15%", "display": "inline-block", "vertical-align": "middle", "margin-left": "auto", "margin-right": "auto", "textAlign": "left"}),

		#reset labels button
		html.Div([
			dbc.Button("Reset labels", id="reset_labels_deconvolution_button", disabled=True, style={"font-size": 12, "text-transform": "none", "font-weight": "normal", "background-image": "linear-gradient(-180deg, #FFFFFF 0%, #D9D9D9 100%)", 'color': 'black'}),
			dbc.Tooltip(
				children=[dcc.Markdown(info_text.info_deconvolution_reset_labels_button)],
				target="reset_labels_deconvolution_button",
				placement="right",
				style={"font-family": "arial", "font-size": 14}
			)
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
