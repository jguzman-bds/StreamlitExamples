global System, DataTable, AMO, ADOMD

import pandas as pd
import ssas_api as ssas
import seaborn as sns
import streamlit as st
import altair as alt

import matplotlib.pyplot as plt
import numpy as np

sns.set_style("whitegrid")
blue, = sns.color_palette("muted", 1)

import sys
import os
sys.path.insert(0,os.path.abspath(' ./' ))
import clr
clr.AddReference('System.Data' )
r = clr.AddReference(r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.Tabular\v4.0_15.0.0.0__89845dcd8080cc91\Microsoft.AnalysisServices.Tabular.dll")
r = clr.AddReference(r"C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.AnalysisServices.AdomdClient\v4.0_15.0.0.0__89845dcd8080cc91\Microsoft.AnalysisServices.AdomdClient.dll")
from System import Data
from System import Converter
from System.Data import DataTable
import Microsoft.AnalysisServices.Tabular as TOM
import Microsoft.AnalysisServices.AdomdClient as ADOMD

conn = ssas.set_conn_string(
        server=server,
        db_name='MyFirstPowerBIModel',
        username=username,
        password=password
        )

Month = st.select_slider(
    'Select a month',
    options=['January', 'February', 'March', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])

Year = st.select_slider(
    'Select a year',
    options=['2016', '2017', '2018'])

st.write('The selected month is', Month, "/", Year)

dax_SumRevenueF ='''
DEFINE
  VAR YearSele = '''
dax_SumRevenueF += Year
dax_SumRevenueF += '''
  VAR MonthSele = "'''
dax_SumRevenueF += Month
dax_SumRevenueF += '''"
  VAR __DS0FilterTable =
    TREATAS({MonthSele}, 'LocalDateTable_fb5f29ac-cec2-4987-9024-27d8b168a3bf'[Month])

  VAR __DS0FilterTable2 =
    TREATAS({YearSele}, 'LocalDateTable_fb5f29ac-cec2-4987-9024-27d8b168a3bf'[Year])

  VAR __DS0FilterTable3 =
    TREATAS({"Urban"}, 'Product'[Category])

  VAR __DS0FilterTable4 =
    TREATAS({"Top Competitors",
      "VanArsdel"}, 'Manufacturer'[Manufacturer (groups)])

  VAR __DS0Core =
    SUMMARIZECOLUMNS(
      'Geography'[Country],
      __DS0FilterTable,
      __DS0FilterTable2,
      __DS0FilterTable3,
      __DS0FilterTable4,
      "SumRevenue", CALCULATE(SUM('Sales'[Revenue])),
      "CountState", CALCULATE(COUNTA('Geography'[State]))
    )

  VAR __DS0PrimaryWindowed =
    TOPN(1001, __DS0Core, [SumRevenue], 0, 'Geography'[Country], 1)

EVALUATE
  __DS0PrimaryWindowed

ORDER BY
  [SumRevenue] DESC, 'Geography'[Country]
'''

df_SumRevenueF = (ssas.get_DAX(
                   connection_string=conn,
                   dax_string=dax_SumRevenueF)
              )

RevenueValue = df_SumRevenueF['[SumRevenue]'].copy()
RevenueCountry = df_SumRevenueF['Geography[Country]']

for i in range (0, len(df_SumRevenueF['[SumRevenue]'])):
  RevenueValue[i] = int(str(df_SumRevenueF['[SumRevenue]'][i]))
  i=i+1

source = pd.DataFrame({
     'Value':RevenueValue,
     'Country':RevenueCountry
     })

if False:
	fig_SumRevenueF, axs_SumRevenueF = plt.subplots(figsize=(9, 3), sharey=True)
	axs_SumRevenueF.bar(RevenueCountry, RevenueValue)
	axs_SumRevenueF.tick_params(axis='x', labelrotation = 90)

	fig_SumRevenueF.suptitle('Sum of the revenue filtered by month')

	st.pyplot(fig_SumRevenueF)

	bar_chart = alt.Chart(source).mark_bar().encode(
		y='Value',
		x='Country',
		)

	st.altair_chart(bar_chart, use_container_width=True)

st.bar_chart(source,y='Value',x='Country')

#st.bar_chart(chart_data)

#chart_SumRevenueF = st.bar_chart(data=RevenueValue, x=RevenueCountry,use_container_width=True)

#st.bar_chart(chart_SumRevenueF)
