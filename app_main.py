#import python packages
import dash
from dash import html
import dash_bootstrap_components as dbc
import dash_auth
import plotly.io as pio
from functions import config
from layout import main_layout, metadata_table_tab_layout, sankey_tab_layout, heatmap_tab_layout, multi_violin_tab_layout, correlation_tab_layout, diversity_tab_layout, dge_tab_layout, go_tab_layout, mofa_tab_layout, deconvolution_tab_layout

#default template
pio.templates.default = "simple_white"

#assign objects to app
app = dash.Dash(__name__, title=config["browser_tab_name"], external_stylesheets=[dbc.themes.FLATLY])
app.config.suppress_callback_exceptions=True
server = app.server

#layout
app.layout = main_layout

#validate layout with tabs
app.validation_layout = html.Div([
    main_layout, 
	metadata_table_tab_layout,
	sankey_tab_layout,
	heatmap_tab_layout,
	multi_violin_tab_layout,
	correlation_tab_layout,
	diversity_tab_layout,
	dge_tab_layout,
	go_tab_layout,
	mofa_tab_layout,
	deconvolution_tab_layout
])

#pass
if config["credentials"]["use_credentials"]:
	credentials_dict = {config["credentials"]["username"]: config["credentials"]["pass"]}
	VALID_USERNAME_PASSWORD_PAIRS = credentials_dict
	auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

#callbacks
from callbacks import define_callbacks
define_callbacks(app)

if __name__ == "__main__":

	#run app
	if config["local"]:
		app.run_server(debug=True, host = "172.21.17.26", port = "8052")
	else:
		app.run_server()
