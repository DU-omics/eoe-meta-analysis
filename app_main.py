#import python packages
import dash
import dash_bootstrap_components as dbc
import dash_auth
import plotly.io as pio

from functions import config

#default template
pio.templates.default = "simple_white"

#assign objects to app
app = dash.Dash(__name__, title=config["header"]["text"], external_stylesheets=[dbc.themes.FLATLY])
server = app.server

#layout
from layout import layout
app.layout = layout

#pass
credentials_dict = {config["credentials"]["username"]: config["credentials"]["pass"]}
VALID_USERNAME_PASSWORD_PAIRS = credentials_dict
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

#google analytics tag
app.index_string = '''
	<!DOCTYPE html>
	<html>
		<head>
			<!-- Global site tag (gtag.js) - Google Analytics --><script async src="https://www.googletagmanager.com/gtag/js?id=G-RQFC90MDCS"></script><script> window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);} gtag('js', new Date()); gtag('config', 'G-HL81GG80X2'); </script>
			<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2280852393527019" crossorigin="anonymous"></script>
		{%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
		</head>
		<body>
			<div></div>
			{%app_entry%}
			<footer>
				{%config%}
				{%scripts%}
				{%renderer%}
			</footer>
			<div></div>
		</body>
	</html>
'''

#callbacks
from callbacks import define_callbacks
define_callbacks(app)

if __name__ == "__main__":

	#run app
	import os.path
	if os.path.isfile(".vscode/settings.json"):
		app.run_server(debug=True, host = "10.39.173.120", port = "8052")
	else:
		app.run_server()
