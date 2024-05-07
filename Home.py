import streamlit as st

st.set_page_config(
    page_title='Korea Historic Sites',
    page_icon='🗿',
    layout='wide',
    initial_sidebar_state='expanded')

st.title('Historic Sites in South Korea')
st.subheader('대한민국 **역사 명소** 방문자를 위한 가이드', divider='rainbow')


def centered_text(text):
   st.markdown(f"<div style='text-align: center;'>{text}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
   centered_text("<b>지역/유형별 유적지 검색<b>")
   #st.write("지역별/유형별 유적지 검색")
   st.image('data/그림1.png',width=250)

with col2:
   centered_text("<b>리뷰를 한눈에<b>")
   #st.write("리뷰를 한눈에")
   st.image('data/그림2.png',width=250)

# with col3:
#    centered_text('''<b>리뷰 키워드로 유적지 추천<b>''')
#    #st.write("리뷰키워드를 중심으로 추천 서비스 제공")
#    #st.image('그림3.png')

#center>가운데</center>


st.write('---')
st.subheader('바로가기')
st.page_link('pages/01_전국별.py', label='***전국의 역사 명소 정보***', icon='🗺️')
st.page_link('pages/02_지역별.py', label='***각 지역 역사 명소 정보***', icon='🏛️')