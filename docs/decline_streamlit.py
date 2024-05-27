import datetime

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import time

import plotly.graph_objects as go

import streamlit as st

from prodpy import timeview as tv

from prodpy import decline as dc

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = tv.Session(st.session_state).set()
st.session_state = dc.Session(st.session_state).set()

with st.sidebar:

	st.header(
		body = 'Input Data',
		)

	file = st.file_uploader(
		label = 'Upload your input excel file',
		type = ['csv','xlsx'],
		)

	data = tv.Update.load_data(file)

	st.header(
		body = 'Feature Selection',
		)

	datehead = st.selectbox(
		label = "Choose Date Column:",
		options = data.datetimes,
		index = None,
		key = 'datehead',
		)

	if datehead is not None:
		data = data(datehead=datehead)

	ratehead = st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		key = 'ratehead',
		)

	nominals = st.multiselect(
		label = "Choose Groupby Columns:",
		options = data.nominals,
		key = 'nominals',
		)

	table = tv.Update.load_table(st.session_state,data)

	st.header(
		body = 'Item Selection:',
		)

	itemname = st.selectbox(
		label = 'Select Item:',
		options = table.items,
		index = None,
		key = 'itemname'
		)

	view = tv.Update.load_view(st.session_state,table)

	st.header(
		body = 'Timeseries View',
		)

	viewlist = st.multiselect(
		label = 'Add to the Plot:',
		options = data.minors(st.session_state.ratehead),
		key = 'viewlist',
		)

displayColumn, modelColumn = st.columns([0.7,0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	analysis = dc.Update.load_analysis(st.session_state)

	st.slider(
		label = "Time Interval:",
		min_value = view.limit[0],
		max_value = view.limit[1],
		key = 'estimate',
		on_change = dc.Update.slider,
		args = (st.session_state,),
		)

	opacity = dc.Update.load_opacity(st.session_state,analysis(view.frame))

	st.selectbox(
		label = "Decline Mode",
		options = dc.Model.options,
		key = 'mode',
		on_change = dc.Update.mode,
		args = (st.session_state,),
		)

	st.number_input(
		label = 'Decline Exponent %',
		min_value = 0,
		max_value = 100,
		key = 'exponent',
		step = 5,
		on_change = dc.Update.exponent,
		args = (st.session_state,),
		)

	FitGroupButton = st.button(
		label = "Fit Group",
		help = "Optimize all group items.",
		use_container_width = True,
		)

	if FitGroupButton:

		st.session_state.models = {}

		progress_text = "Optimization in progress. Please wait."

		bar = st.progress(0.,text=progress_text)
		
		for index,scene in enumerate(table,start=1):

			model = dc.Update.best_model(
				st.session_state,analysis(scene.frame)
				)

			st.session_state.models[scene.items[0]] = model

			bar.progress(value=index/table.num,text=progress_text)

		time.sleep(1)
	
		bar.empty()

	dc.Update.load_model(st.session_state,analysis(view.frame))

	st.text_input(
		label = 'Initial Rate',
		key = 'rate0',
		on_change = dc.Update.attributes,
		args = (st.session_state,),
		)

	st.text_input(
		label = 'Initial Decline Rate',
		key = 'decline0',
		on_change = dc.Update.attributes,
		args = (st.session_state,),
		)

	estimate_curve = dc.Update.load_estimate_curve(st.session_state)

	SaveModelEditButton = st.button(
		label = "Save Edits",
		help = "Save decline attribute edits for the item.",
		use_container_width = True,
		)

	if SaveModelEditButton:

		if len(st.session_state.models)==0:
			st.warning("Click Fit Group first.")
		else:
			try:
				st.session_state.models[itemname] = dc.Update.user_model(st.session_state)
			except Exception as message:
				st.warning(message)
			else:
				st.success(f"The model for {itemname} is updated.")

	st.markdown("""---""")

	forecast_show = st.checkbox(
		label = "Display Forecasted Rates",
		)

	if forecast_show:
		xaxis_range = [
			min(st.session_state.forecast[0],view.limit[0]),
			max(st.session_state.forecast[1],view.limit[1])
			]
	else:
		xaxis_range = list(view.limit)

	nextyear = datetime.datetime.now().year+1

	forecast = st.date_input(
		"Forecast Interval",
		value = (datetime.date(nextyear,1,1),datetime.date(nextyear,12,31)),
		key = 'forecast',
		format="MM.DD.YYYY",
	)

	forecast_frequency = st.selectbox(
		label = 'Forecast Frequency:',
		options = ("Daily","Monthly","Yearly"),
		key = 'frequency'
		)

	forecast_curve = dc.Update.load_forecast_curve(st.session_state)

	if False:
		output = dc.Update.load_download(st.session_state)
	else:
		output = None

	DownloadButton = st.download_button(
		label = 'Download Forecast',
		data = '',
		help = "Download rates for all group items.",
		file_name = f"{table.leadhead}_forecast.csv",
		mime = 'text/csv',
		use_container_width = True,
		)

	# if DownloadButton:

	# 	progress_text = "Forecast in progress. Please wait."

	# 	bar2 = st.progress(0.,text=progress_text)
		
	# 	for index,view in enumerate(table,start=1):

	# 		model = dc.Update.best_model(st.session_state,analysis(view.frame))

	# 		st.session_state.models[view.items[0]] = model

	# 		bar2.progress(value=index/table.num,text=progress_text)

	# 	time.sleep(1)
	
	# 	bar2.empty()

with displayColumn:

	if not view.frame.empty:

		st.header(f'{itemname} Rates')

		fig1 = go.Figure()

		observed_plot = go.Scatter(
			x = view.frame[datehead],
			y = view.frame[ratehead],
			mode = 'markers',
			marker = dict(opacity=opacity),
			)

		fig1.add_trace(observed_plot)

		if estimate_curve is not None:

			estimate_plot = go.Scatter(
				x = estimate_curve['dates'],
				y = estimate_curve['predicted'],
				mode = 'lines',
				line = dict(color="black"),
				)

			fig1.add_trace(estimate_plot)

		if forecast_show and forecast_curve is not None:
			forecast_plot = go.Scatter(
				x = forecast_curve['dates'],
				y = forecast_curve['predicted'],
				mode = 'lines',
				line = dict(color="red"),
				)

			fig1.add_trace(forecast_plot)

		fig1.update_xaxes(range=xaxis_range)

		fig1.update_layout(
			title = f'{st.session_state.ratehead}',
			showlegend = False,
	        )

		st.plotly_chart(fig1,use_container_width=True)

		for ratename in viewlist:

			figI = go.Figure()

			data_vis = go.Scatter(
				x = view.frame[datehead],
				y = view.frame[ratename],
				mode = 'markers',
				marker = dict(opacity=opacity),
				)

			figI.add_trace(data_vis)

			figI.update_xaxes(range=xaxis_range)

			figI.update_layout(
				title = ratename,
				)

			st.plotly_chart(figI,use_container_width=True)
