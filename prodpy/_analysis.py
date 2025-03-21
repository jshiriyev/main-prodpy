import datetime

import pandas

from .decline._arps import Arps
from ._timespan import TimeSpan

class Analysis():

	def fit(self,frame:pandas.DataFrame,*args,date0:datetime.date=None,**kwargs):
		"""Returns optimized model that fits the frame and fit-score (optionally)"""

		dates = TimeSpan(frame[self.datehead])

		rates = frame[self.ratehead].to_numpy()

		bools = dates.iswithin(*args)

		dates,rates = dates[bools],rates[bools]

		date0 = dates.mindate if date0 is None else date0

		days  = dates.days(date0)

		return Optimize(**kwargs).fit(days,rates,date0)

	def mfit(self,view,*args,**kwargs):
		"""Returns optimized model dictionary that fits the frames."""

		return {item:self.ufit(frame,*args,**kwargs) for item,frame in view}

	def run(self,model:Model,*args,**kwargs):
		"""Forecasts the rates based on the model, and for the pandas.date_range parameters."""

		dates = TimeSpan.get(*args,**kwargs)

		days  = dates.days(model.date0)

		curve = Curve(model).run(days)

		curve.set(dates=dates.series,heads=self.heads)

		return curve

	def mrun(self,models:dict,*args,**kwargs):

		dates = TimeSpan.get(*args,**kwargs)

		for index,(key,model) in enumerate(models.items(),start=1):

			days  = dates.days(model.date0)

			curve = Curve(model).run(days)

			curve.set(dates=dates.series,heads=self.heads)

			frame = curve.frame.copy() if index==1 else pandas.concat([frame,curve.frame])

		return frame.reset_index(drop=True)

if __name__ == "__main__":

	import pandas as pd

	df = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

	print(df)

	print(df.columns)

	# print(df.groupby('Date').sum('Actual Oil, Mstb/d'))

	# print(df.columns)

	# print(df['Well'].unique())

	# print(df[df['Well']=='D32'])

	# print((df['Date']-df['Date'][0])*5)

	# print(df.head)

	# print(dir(df))

	# print(
	# 	Curve.days(5)
	# 	)

	# print(
	# 	Curve.days(datetime.date(2022,2,3),datetime.date(2022,2,7))
	# 	)

	# print(
	# 	Curve.days(datetime.date(2022,2,3),datetime.date(2022,2,7),12)
	# 	)