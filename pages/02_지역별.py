import streamlit

from utils.mo import *
from utils import mo
import time

with st.sidebar:
    select1= st.radio("🔍**지역을 고르세요**",
        ('서울특별시','경기도','인천광역시','울산광역시', '세종특별자치시','대구광역시','광주광역시','강원특별자치도',
         '충청남도', '충청북도','경상남도', '경상북도','전라남도', '전라북도','제주특별자치도',)
        )
st.subheader(f'◽ {select1}')
tab1, tab2 = st.tabs(['지도', '장소별'])


@st.cache_data
def API_data(file_path):
    API_df = pd.read_excel(file_path)
    return API_df


API_df = API_data(f'data/TourAPI_id_url.xlsx')

selected, map, categories, url = place_select(select1,tab2,API_df)

@st.cache_data
def all_load_data(file_path):
    try:
        df = pd.read_csv(file_path, index_col='문서이름')
        return df
    except:
        pass


@st.cache_data
def low_load_data(file_path):
    try:
        df = pd.read_csv(file_path, index_col='문서이름')
        return df
    except:
        pass


@st.cache_data
def high_load_data(file_path):
    try:
        df = pd.read_csv(file_path, index_col='문서이름')
        return df
    except:
        pass


all_data = all_load_data(f'data/review/{select1}.csv')
low_data = low_load_data(f'data/review/{select1}_low.csv')
high_data = high_load_data(f'data/review/{select1}_high.csv')


@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df


df = load_data('data/주요관광지점입장객(전국).xlsx')



with tab1:
    @st.cache_data
    def loc_data(file_path):
        loc_df = pd.read_csv(file_path)
        return loc_df


    loc_df = loc_data('data/전국관광지위치정보.csv')


    col1, col2 = st.columns([0.6, 0.4])
    with col2:
        select = tab1_select(categories)
    with col1:
        load_location(map, loc_df, select, select1)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('**📍 장소별 방문객(합계) 순위 Top10** ')

        place_ranking(df, select1)

    with col4:
        st.markdown('**📍 별점 높은 장소**')


        @st.cache_data
        def star_data(file_path):
            star_df = pd.read_csv(file_path)
            return star_df


        star_df = star_data(f'data/star/{select1}_별점.csv')
        star_ranking(star_df)


with tab2:
    tab2_1, tab2_2 = st.tabs(['장소별분석', '리뷰분석'])



    # url = API_df.loc[API_df['장소'] == selected, 'url'].iloc[0]

    tab2_place(url, df, selected, tab2_1)
    mo.tab2_review(selected, all_data, low_data, high_data, tab2_2)






