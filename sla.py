import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

#upload data 
file_path = 'C:\\Users\\moham\\Downloads\\sla_handled.xlsx'
data = pd.read_excel(file_path)

#calculation To get The meet Sla Response and Sla Resolution
data['Actual_Response_Hours'] = (data['Response_Time'] - data['Reported_Time']) / timedelta(hours=1)
data['Actual_Resolution_Hours'] = (data['Resolution_Time'] - data['Reported_Time']) / timedelta(hours=1)

data['Meets_SLA_Response'] = data['Actual_Response_Hours'] <= data['SLA_Response_Hours']
data['Meets_SLA_Resolution'] = data['Actual_Resolution_Hours'] <= data['SLA_Resolution_Hours']

#Get The percentage of reached operation that meet sla response hour and sla resolution hour 
percent_meeting_sla_response = data['Meets_SLA_Response'].mean() * 100
percent_meeting_sla_resolution = data['Meets_SLA_Resolution'].mean() * 100

#grouped issue type with meet sla response and sla resolution 
sla_compliance_by_issue_type = data.groupby('Issue_Type').agg({
    'Meets_SLA_Response': 'mean',
    'Meets_SLA_Resolution': 'mean'
}).reset_index()
#grouped priority with meet sla response and sla resolution 
sla_compliance_by_priority = data.groupby('Priority').agg({
    'Meets_SLA_Response': 'mean',
    'Meets_SLA_Resolution': 'mean'
}).reset_index()

st.title('SLA Compliance Dashboard')


st.header('SLA Compliance Rates')
fig_response_rate_gauge, fig_resolution_rate_gauge= st.columns(2)
fig_response_rate_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=percent_meeting_sla_response,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "SLA Response Compliance Rate"},
))
st.plotly_chart(fig_response_rate_gauge)




fig_resolution_rate_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=percent_meeting_sla_resolution,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "SLA Resolution Compliance Rate"},
))
st.plotly_chart(fig_resolution_rate_gauge)
    



st.header('SLA Compliance Visualizations')

fig_issue_type = px.bar(sla_compliance_by_issue_type, x='Issue_Type', y=['Meets_SLA_Response', 'Meets_SLA_Resolution'],
                        title="SLA Compliance by Issue Type", barmode='group')
st.plotly_chart(fig_issue_type)

fig_priority = px.bar(sla_compliance_by_priority, x='Priority', y=['Meets_SLA_Response', 'Meets_SLA_Resolution'],
                      title="SLA Compliance by Priority", barmode='group')
st.plotly_chart(fig_priority)

# Assuming 'Reported_Time' is the column to use for trend analysis
data['Reported_Month'] = data['Reported_Time'].dt.to_period('M')

# Calculate SLA Compliance Rate
sla_compliance = data.groupby('Reported_Month').apply(lambda x: np.mean(x['Meets_SLA_Resolution'])).reset_index(name='SLA_Compliance_Rate')
sla_compliance['Reported_Month'] = sla_compliance['Reported_Month'].astype(str)

# Calculate SLA Resolution Rate (fixing variable name and calculation)
sla_resolution = data.groupby('Reported_Month').apply(lambda x: np.mean(x['Meets_SLA_Response'])).reset_index(name='Sla_Resolution_Rate')
sla_resolution['Reported_Month'] = sla_resolution['Reported_Month'].astype(str)

# Merge SLA Compliance and Resolution Rates into a single DataFrame
trend_data = pd.merge(sla_compliance, sla_resolution, on='Reported_Month')

# Plotting both metrics on the same figure
fig_trend = px.line(trend_data, x='Reported_Month', 
                    y=['SLA_Compliance_Rate', 'Sla_Resolution_Rate'], 
                    title='SLA Metrics Trend Over Time', 
                    labels={'value': 'Rate', 'Reported_Month': 'Reported Month', 'variable':'Metrics'}, 
                    markers=True)

st.plotly_chart(fig_trend)
#  Top Three Issue Types with the Highest Breach in SLA
breach_rates = data.groupby('Issue_Type').apply(lambda x: np.mean(x['Meets_SLA_Resolution'] == False)).reset_index(name='Breach_Rate')
top_three_breaches = breach_rates.nlargest(3, 'Breach_Rate')
st.subheader('Top Three Issue Types with the Highest Breach in SLA Meet resolution')
st.write(top_three_breaches)

breach_rates_resp = data.groupby('Issue_Type').apply(lambda x: np.mean(x['Meets_SLA_Response'] == False)).reset_index(name='Breach_Rate')
top_three_breaches_resp = breach_rates_resp.nlargest(3, 'Breach_Rate')
st.subheader('Top Three Issue Types with the Highest Breach in SLA Meet response')
st.write(top_three_breaches_resp)


