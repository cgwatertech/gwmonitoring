import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime, timedelta

# Sample data
df = pd.read_csv("https://raw.githubusercontent.com/gwmonitoring/main/cgwt_nnhn.csv")

# Sidebar (왼쪽 프레임)
st.sidebar.title("위치 리스트")

# 'Time'을 제외한 컬럼들을 선택 박스에 넣음
selected_location = st.sidebar.selectbox("위치 선택", df.columns[1:])

# Time 열을 DateTime 객체로 변환
df['Time'] = pd.to_datetime(df['Time'])

# 시작 날짜와 끝 날짜 선택
start_date = st.sidebar.date_input("시작 날짜 선택", min_value=df['Time'].min(), max_value=df['Time'].max(), value=df['Time'].max() - timedelta(days=7))
# 시간 선택
start_time = st.sidebar.selectbox("시작 시간 선택", options=pd.date_range("00:00:00", "23:00:00", freq="H").strftime("%H:%M:%S"), index=0)

end_date = st.sidebar.date_input("끝 날짜 선택", min_value=df['Time'].min(), max_value=df['Time'].max(), value=df['Time'].max())
# 시간 선택
end_time = st.sidebar.selectbox("끝 시간 선택", options=pd.date_range("00:00:00", "23:00:00", freq="H").strftime("%H:%M:%S"), index=len(pd.date_range("00:00:00", "23:00:00", freq="H")) - 1)

# datetime 객체로 변환
start_datetime = datetime.combine(start_date, datetime.strptime(start_time, "%H:%M:%S").time())
end_datetime = datetime.combine(end_date, datetime.strptime(end_time, "%H:%M:%S").time())

# 선택하는 시간 선택
selected_hour = st.sidebar.selectbox("선택하는 시간", range(25))

# 슬라이더로 범위 크기 조절
rng_cmn = st.sidebar.slider("범위 크기", min_value=1, max_value=20, value=5, step=1)

# 시작 날짜와 끝 날짜 사이의 데이터 필터링 및 시간 필터링
if selected_hour == 24:
    filtered_data = df[(df['Time'] >= start_datetime) & (df['Time'] <= end_datetime)]
else:
    filtered_data = df[(df['Time'] >= start_datetime) & (df['Time'] <= end_datetime) & (df['Time'].dt.hour == selected_hour)]

# 최신 자료가 먼저 표시되도록 정렬
filtered_data = filtered_data.sort_values(by='Time', ascending=False)

# Main content (오른쪽 프레임)
st.title("지하수위 관측 웹페이지")

# 이미지 표시
st.image("https://raw.githubusercontent.com/cgwatertech/gwmonitoring/main/Yujin_nonhyun.png", use_column_width=True)

# Plot (오른쪽 아래 프레임)
st.subheader(f"{selected_location} 위치의 지하수위 변화 ({start_datetime}부터 {end_datetime})")

# 선택한 위치에 대한 평균 값을 계산
avg_value = filtered_data[selected_location].mean()
mx_value = filtered_data[selected_location].max()
mn_value = filtered_data[selected_location].min()
rng_value = (mx_value - mn_value) * rng_cmn
rng_vale = rng_value / 2

# 평균 값으로 새로운 데이터 프레임을 만듦
avg_df = pd.DataFrame({'Time': filtered_data['Time'], selected_location: avg_value})
# 그래프 그리기
fig = px.line(filtered_data, x="Time", y=selected_location, title=f"{selected_location} 위치의 지하수위 변화 ({start_datetime}부터 {end_datetime})")

# y 축 리미트 설정
fig.update_layout(yaxis=dict(range=[avg_value - rng_vale, avg_value + rng_vale]))

# x 축 tick 및 라벨 설정
tickvals = filtered_data['Time'].iloc[::len(filtered_data) // 5]  # 5 ticks로 나누기
ticktext = [val.strftime('%Y-%m-%d %H:%M') for val in tickvals]
fig.update_layout(xaxis=dict(tickvals=tickvals, ticktext=ticktext))

# 반응형으로 그래프 표시
st.plotly_chart(fig, use_container_width=True)

# 선택한 그래프의 시간과 데이터 다운로드 버튼
selected_data = filtered_data[['Time', selected_location]]
csv_selected_data = selected_data.to_csv(index=False)
b64_selected_data = base64.b64encode(csv_selected_data.encode()).decode()
st.markdown(f'<a href="data:file/csv;base64,{b64_selected_data}" download="selected_data.csv">선택 그래프 데이터 다운로드</a>', unsafe_allow_html=True)

# 전체 데이터 다운로드 버튼
csv_all_data = df.to_csv(index=False)
b64_all_data = base64.b64encode(csv_all_data.encode()).decode()
st.markdown(f'<a href="data:file/csv;base64,{b64_all_data}" download="all_data.csv">전체 자료 다운로드</a>', unsafe_allow_html=True)

# 선택 결과를 새로운 창에서 보여주기
selected_data_preview = filtered_data[['Time', selected_location]].copy()

# 인덱스를 감춤
selected_data_preview.set_index('Time', inplace=True)

# 왼쪽 프레임에 데이터를 미리보는 창
st.sidebar.subheader("선택된 자료 미리보기")
st.sidebar.write(selected_data_preview.sort_index().head(15))
