import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from PIL import Image
import datetime
import base64

st.set_page_config(
    page_title="Groundwater Monitoring",
    page_icon="✅",
    layout="wide"
)

# Read data from a CSV file
dataset_url = "https://raw.githubusercontent.com/cgwatertech/PySimpleGUI/master/cgwt.csv"
@st.experimental_memo
def get_data() -> pd.DataFrame:
    return pd.read_csv(dataset_url)

df = get_data()

# Dashboard title
st.title("영등포 양평의 지하수위 관측")

# Top-level filters
job_filter = st.selectbox("관측공의 위치 선택", pd.unique(df.columns), index=df.columns.get_loc('Test02'))

st.markdown("### 지하수위 그래프")
df["Time"] = pd.to_datetime(df["Time"])
fig1 = px.line(
    x=df["Time"], y=df[job_filter], data_frame=df)
fig1.update_xaxes(title_text="X 축 (mmm dd)")
fig1.update_yaxes(title_text="Y 축 (m)")
st.write(fig1)

# Date and time filtering
start_date = st.date_input('Enter start date', value=datetime.datetime(2023, 9, 26))
end_date = st.date_input('Enter end date', value=datetime.datetime(2023, 10, 10))
start_time = st.time_input('Enter start time', datetime.time(8, 45))
end_time = st.time_input('Enter end time', datetime.time(8, 46))

# Define the desired hour using a slider
custom_hour = st.slider("원하는 시간을 선택하세요 (24시간 형식)", 1, 24, 15)

# Filter data based on selected job and date/time range
filtered_df = df[['Time', job_filter]]
filtered_df["Time"] = pd.to_datetime(filtered_df["Time"])

# Find the closest timestamp to the custom hour for each selected date
filtered_df['CustomHour'] = filtered_df['Time'].apply(lambda x: x.replace(hour=custom_hour, minute=0, second=0, microsecond=0))
filtered_df = filtered_df[(filtered_df['Time'] - filtered_df['CustomHour']).abs() == (filtered_df['Time'] - filtered_df['CustomHour']).abs().min()]

# Define your custom y-axis range here
custom_y_range = st.slider("Y-축 범위 조절 (cm)", min_value=-200, max_value=0, value=(-150, -90), step=1)  # Use a step of 10

# Convert the slider values to a scale of -20.0 to 0.0
scaled_y_range = (custom_y_range[0] / 10.0, custom_y_range[1] / 10.0)

# fig2 - 특정 시간대의 지하수위 그래프
fig2 = px.line(
    x=filtered_df["Time"], y=filtered_df[job_filter])
fig2.update_xaxes(title_text="X 축 (mmm dd)")
fig2.update_yaxes(title_text="Y 축 (m)")
fig2.update_yaxes(range=scaled_y_range)

# Create a new window for fig2
st.markdown("### 특정 시간대의 지하수위 그래프 (새 창)")
st.plotly_chart(fig2)

# Image upload
uploaded_file = st.file_uploader("업로드할 이미지를 선택하세요.", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image)

# Download filtered data as CSV
if st.button("CSV로 다운로드"):
    csv = filtered_df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="filtered_data.csv">다운로드 CSV 파일</a>'
    st.markdown(href, unsafe_allow_html=True)

st.markdown("### Detailed Data View")
# Show detailed data for the selected job_filter
st.dataframe(filtered_df)
