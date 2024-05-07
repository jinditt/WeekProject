import time

from utils.mo import *


tab1, tab2 = st.tabs(['지도','Top10 순위🏆'])


with tab1:
    col1, col2 = st.columns([2, 1])
    with col2:
        categories = ['고택/생가/민속마을', '유명사찰', '유명사적/유적지', '왕릉/고분',
              '비/탑/문/각', '국보', '천연기념물','보물', '서원/향교/서당', '궁궐/종묘','성/성터']
        select = tab1_select(categories)

    with col1:
        @st.cache_data
        def loc_data(file_path):
            loc_df = pd.read_csv(file_path)
            return loc_df


        loc_df = loc_data('data/전국관광지위치정보.csv')
        map = folium.Map(location=[36.66482327, 127.6044201], zoom_start=6)

        all_location(map, loc_df, select)


    st.markdown('선택한 유형별 전국 역사명소 개수')


    @st.cache_data
    def load_data(file_path):
        df = pd.read_excel(file_path)
        return df


    df = load_data('data/주요관광지점입장객(전국).xlsx')

    da = df.groupby(['시도', '범주']).count()[['군구']].unstack().fillna(0).droplevel(axis=1, level=0).reset_index()
    st.bar_chart(da, x='시도', y=select)




with tab2:
    # st.subheader('Top10 순위🏆')
    st.write()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('📌평균 방문율이 높은 지역')

        tab1, tab2, tab3 = st.tabs(['합계', '내국인', '외국인'])

        visit_sido(df,'합계', tab1)
        visit_sido(df,'내국인', tab2)
        visit_sido(df,'외국인', tab3)

    with col2:
        st.markdown('📌방문객수가 많은 장소')
        tab4, tab5, tab6 = st.tabs(['합계', '내국인', '외국인'])
        # 전국 방문객 장소별 ( 합계, 내국인, 외국인)
        all_place_ranking(df, tab4, '합계', color='#E5C1C5')
        all_place_ranking(df, tab5, '내국인',color='#E5C1C5')
        all_place_ranking(df, tab6, '외국인',color='#E5C1C5')

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('📌별점 평균이 높은 지역')
        @st.cache_data
        def star_sido(file_path):
            sido_df = pd.read_csv(file_path)
            return sido_df


        sido_df = star_sido(f'data/star/전국_시도_별점순위.csv')
        star_ranking(sido_df.iloc[:10],color='#C3E2DD')
    with col4:
        st.markdown('📌별점 평균이 높은 장소')

        @st.cache_data
        def star_data(file_path):
            star_df = pd.read_csv(file_path)
            return star_df


        star_df = star_data(f'data/star/전국_장소_별점순위.csv')
        star_ranking(star_df.iloc[:10],color='#6ECEDA')