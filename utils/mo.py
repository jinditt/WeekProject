import time

from requests.exceptions import MissingSchema
from streamlit.runtime.media_file_storage import MediaFileStorageError
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster
import pandas as pd
import numpy as np
from streamlit_pills import pills
import requests
from bs4 import BeautifulSoup
from matplotlib import font_manager, rc
import platform
import re

# font_path = 'C:/Windows/Fonts/malgun.ttf'
# font_name2 = font_manager.FontProperties(fname=font_path).get_name()
# font_name = 'NanumGothic.ttf'
# rc('font', family=font_name)

if platform.system() == 'Darwin':  # 맥OS
    rc('font', family='AppleGothic')
elif platform.system() == 'Windows':  # 윈도우
    font_name = "c:/Windows/Fonts/malgun.ttf"
    path = font_manager.FontProperties(fname=font_name).get_name()
    rc('font', family=path)
else:
    font_name = 'NanumGothic.ttf'
    rc('font', family=font_name)


def wordcloud(data, count):
    word_freq = dict(zip(data['Unnamed: 1'], data['freq']))
    # word_freq = data['freq'].to_dict()
    wc = WordCloud(font_path=font_name, max_words=count, width=800, height=400,
                   background_color='white').generate_from_frequencies(word_freq)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt.gcf())


def year_chart(df, place):
    st.subheader(f'{place} 연간 관광객수')
    da = df[(df['관광지'] == place) & (df['내/외국인'] == '합계')].loc[:, '2018년':'2023년'].values.tolist()
    da.append(['2018', '2019', '2020', '2021', '2022', '2023'])
    # streamlit에서 line_chart형식(열이름을 써줘야되서 데이터 재구조화)
    spot_df = pd.DataFrame({'headcount': da[0], 'year': da[1]}, index=['a', 'b', 'c', 'd', 'e', 'f'])
    st.line_chart(spot_df, x='year', color='#F90000')


def tab1_select(categories):
    select = st.multiselect(
        '확인하고 싶은 유형을 고르세요👇',
        categories, categories)
    name_str = ', '.join(select)
    # st.write('You selected:', name_str)
    return select


# 사용자가 선택한 시도와 범주 리스트
def load_location(map, df, select, sido):
    # loc_list 리스트 생성
    loc_list = []
    time.sleep(3)
    # 각 범주에 해당하는 딕셔너리 생성
    for category in select:
        # 해당 조건에 맞는 데이터프레임 필터링
        filtered_df = df[(df['시도'] == sido) & (df['범주'] == category)]

        # 딕셔너리 생성
        site_loc = {}

        # 데이터프레임을 순회하면서 딕셔너리에 추가
        for idx, row in filtered_df.iterrows():
            site_loc[row['관광지']] = [row['위도'], row['경도']]

        # 딕셔너리를 loc_list에 추가
        loc_list.append(site_loc)

    # 아이콘 색상 리스트
    icon_colors = icon_colors = ['darkblue', 'red', 'green', 'purple', 'orange', 'lightgray',
                                 'lightblue', 'black', 'lightred', 'darkpurple', 'lightgreen']

    for idx, site_loc_dict in enumerate(loc_list):
        # 범주에 대한 아이콘 색상과 종류 선택
        icon_color = icon_colors[idx]

        # 선택한 범주에 따라 해당 위치에 마커 추가
        for site, pos in site_loc_dict.items():
            folium.Marker(location=pos,
                          popup=folium.Popup(site, max_width=150),
                          icon=folium.Icon(color=icon_color, icon='circle', prefix='fa')).add_to(map)
    st_folium(map, width=500, height=500)


def all_location(map, loc_df, select):
    loc_list = []

    # 각 범주에 해당하는 딕셔너리 생성
    for category in select:
        # 해당 조건에 맞는 데이터프레임 필터링
        filtered_df = loc_df[loc_df['범주'] == category]

        # 딕셔너리 생성
        site_loc = {}

        # 데이터프레임을 순회하면서 딕셔너리에 추가
        for idx, row in filtered_df.iterrows():
            site_loc[row['관광지']] = [row['위도'], row['경도']]

        # 딕셔너리를 loc_list에 추가
        loc_list.append(site_loc)

    # 아이콘 색상 리스트
    icon_colors = icon_colors = ['darkblue', 'red', 'green', 'purple', 'orange', 'lightgray',
                                 'lightblue', 'black', 'lightred', 'darkpurple', 'lightgreen']
    marker_cluster = MarkerCluster().add_to(map)
    for idx, site_loc_dict in enumerate(loc_list):
        # 범주에 대한 아이콘 색상과 종류 선택
        icon_color = icon_colors[idx]

        # 선택한 범주에 따라 해당 위치에 마커 추가
        for site, pos in site_loc_dict.items():
            folium.Marker(location=pos,
                          popup=folium.Popup(site, max_width=150),
                          icon=folium.Icon(color=icon_color, icon='circle', prefix='fa')).add_to(marker_cluster)
    st_folium(map, width=500, height=500)


def place_ranking(df, sido, color='#8c00f9'):
    sido_df_sum = df[(df['내/외국인'] == '합계') & (df['시도'] == sido)].sort_values(['총계'], ascending=False)[:10]
    text = ""
    for idx, word in enumerate(sido_df_sum['관광지'].iloc[:3].values):
        idx += 1
        text += f'{idx}위 . {word} / '
    st.caption(text)
    # select = pills("Top3",Top3_list, ["1️⃣", "2️⃣", "3️⃣"])
    st.bar_chart(sido_df_sum, x='관광지', y='총계', color=color)


def all_place_ranking(df, tabint, tabname, color='#8c00f9'):
    with tabint:
        sido_df_sum = df[df['내/외국인'] == tabname].sort_values(['총계'], ascending=False)[:10]
        text = ""
        for idx, word in enumerate(sido_df_sum['관광지'].iloc[:3].values):
            idx += 1
            text += f'{idx}위 . {word} / '
        st.caption(text)
        # select = pills("Top3",Top3_list, ["1️⃣", "2️⃣", "3️⃣"])
        st.bar_chart(sido_df_sum, x='관광지', y='총계', color=color)


def visit_sido(df, tabname, tabint):
    data = df.pivot_table(index='시도', columns='내/외국인', values='총계', aggfunc=['mean'])
    visited_people = data.droplevel(level=0, axis=1)
    # 합계,내국인,외국인 순위 나타내기 위해서 사용
    visited_people_sorted = visited_people.sort_values(tabname, ascending=False)
    with tabint:
        text = ""
        for idx, word in enumerate(visited_people_sorted.iloc[:3].index):
            idx += 1
            text += f'{idx}위 . {word} / '
        st.caption(text)
        st.bar_chart(visited_people[tabname][:10], color='#f5eae1')


def star_ranking(df, color='#FFBC00'):
    text = ""
    for idx, word in enumerate(df['name'].iloc[:3].values):
        idx += 1
        text += f'{idx}위 . {word} / '
    st.caption(text)
    st.bar_chart(df, x='name', y='rating', color=color)




def tab2_review(select, data, low_data, high_data, tabname):
    with tabname:
        co12_1, co12_2 = st.columns([2, 1])
        with co12_1:
            st.subheader('**전체 리뷰 Wordcloud📝**')
            st.set_option('deprecation.showPyplotGlobalUse', False)
            try:
                all_data = data.loc[select]
                all20_df = all_data.rename(columns={'Unnamed: 1': '단어 빈도순', 'freq': '합계'}).iloc[:20]
                wordcloud(all_data, 50)
                with co12_2:
                    st.markdown('단어 순위')
                    try:
                        st.dataframe(all20_df, width=250, height=280, hide_index=True)
                    except:
                        pass
            except:
                st.header('리뷰가 0개입니다:cry:')
        st.write('---')
        co12_3, co12_4 = st.columns(2)
        with co12_3:
            st.markdown('**낮은평점 리뷰:confused:**')
            try:
                low_df = low_data.loc[select]
                wordcloud(low_df, 50)

            except:
                st.caption('낮은평점이 없습니다😀')
        with co12_4:
            st.markdown('**높은평점 리뷰:blush:**')
            try:
                high_df = high_data.loc[select]
                wordcloud(high_df, 50)
            except:
                st.caption('높은평점이 없습니다😥')



def place_select(select, tabname,dataframe):
    if select == '충청북도':
        categories = ['고택/생가/민속마을', '유명사찰', '유명사적/유적지']
        map = folium.Map(location=[36.63598216, 128.0035026], zoom_start=8)
        with tabname:
            options = ['구인사', '배론성지', '정방사', '탄금대', '반야사', '육영수생가', '용암사', '동학농민혁명기념공원', '선병국가옥',
                       '삼년산성', '임충민공충렬사', '길상사', '김유신장군탄생지']

            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '충청남도':
        categories = ['고택/생가/민속마을', '왕릉/고분', '유명사찰',
                      '유명사적/유적지', '서원/향교/서당', '성/성터']
        map = folium.Map(location=[36.51924941, 126.937105], zoom_start=8)
        with tabname:
            options = ['장곡사', '공주한옥마을', '황새바위성지', '한용운선생생가', '무량사', '김좌진장군생가', '충청수영성',
                       '돈암서원', '맹씨행단', '유관순열사생가', '관촉사', '해미순교성지', '문당환경농업마을', '각원사', '향천사',
                       '송국리유적', '논산명재고택', '현충사', '공세리성당', '거북이마을', '문헌서원', '수리치골성지',
                       '공주무령왕릉과왕릉원', '개심사', '간월암', '문수사', '유관순열사사적지', '아산외암마을', '금산보석사',
                       '칠백의총', '사계고택', '공산성', '능산리고분군왕릉', '윤보선전대통령생가', '서산용현리마애여래삼존상',
                       '정림사지', '홍산동헌', '내포보부상촌', '수덕사', '부여기와마을', '다락골줄무덤', '청양고추문화마을',
                       '이종일생가지', '부소산성', '모덕사', '마곡사']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '서울특별시':
        categories = ['고택/생가/민속마을', '왕릉/고분', '궁궐/종묘']
        map = folium.Map(location=[37.5744031, 126.9943842], zoom_start=10)
        with tabname:
            options = ['경복궁', '헌릉인릉', '태릉강릉조선왕릉전시관', '창덕궁', '덕수궁', '창경궁', '선릉정릉',
                       '남산골한옥마을', '종묘']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '경기도':
        categories = ['고택/생가/민속마을', '유명사찰', '유명사적/유적지', '왕릉/고분', '성/성터', '비/탑/문/각']
        map = folium.Map(location=[37.63058213, 127.0140502], zoom_start=8)
        with tabname:
            options = ['명성황후생가', '정약용유적지', '융건릉', '광릉', '서오릉', '영모재', '안성성당', '파주장릉', '신라경순왕릉', '연천당포성',
                       '미리내성지', '장릉', '남한산성행궁', '생금집', '화성', '신륵사', '연천전곡리유적', '서삼릉', '화성행궁', '숭의전지',
                       '동구릉', '대원사템플스테이', '청룡사', '홍유릉', '영릉세종대왕', '백련사템플스테이', '황희선생유적지', '행주산성',
                       '농촌체험마을', '율곡선생유적지', '미리내마을', '헤이리예술마을', '나룻배마을', '연천호로고루', '칠장사', '파주삼릉', '너리굴문화마을']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '인천광역시':
        categories = ['유명사적/유적지']
        map = folium.Map(location=[37.66482327, 126.6044201], zoom_start=10)
        with tabname:
            options = ['강화전적지개소', '검단선사박물관']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '울산광역시':
        categories = ['고택/생가/민속마을', '유명사적/유적지', '유명사찰']
        map = folium.Map(location=[35.58932921, 129.2491987], zoom_start=10)
        with tabname:
            options = ['석남사', '두동면천전리각석', '장생포고래문화마을', '반구대암각화', '외솔생가및기념관', '울산동헌및내아']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '세종특별자치시':
        categories = ['유명사찰']
        map = folium.Map(location=[36.47361982, 127.2278358], zoom_start=10)
        with tabname:
            options = ['영평사템플스테이']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '대구광역시':
        categories = ['고택/생가/민속마을', '유명사적/유적지', '서원/향교/서당', '유명사찰', '왕릉/고분']
        map = folium.Map(location=[35.85839707, 128.5416148], zoom_start=10)
        with tabname:
            options = ['신숭겸장군유적지', '모명재', '대구불로고분군', '녹동서원', '노태우전대통령생가', '대구옻골마을', '병암서원',
                       '도동서원', '사육신기념관', '남평문씨본리세거지', '용연사', '마비정', '선사유적공원']
            selected = pills("Label", label_visibility='collapsed', options=options)
            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '광주광역시':
        categories = ['고택/생가/민속마을', '유명사적/유적지', '서원/향교/서당']
        map = folium.Map(location=[35.15754361, 126.8714588], zoom_start=10)
        with tabname:
            options = ['월봉서원빙월당', '충장사', '포충사', '이장우가옥']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '강원특별자치도':
        categories = ['고택/생가/민속마을', '왕릉/고분', '유명사적/유적지', '유명사찰']
        map = folium.Map(location=[37.65405827, 128.4952541], zoom_start=8)

        with tabname:
            options = ['법흥사적멸보궁', '죽서루', '화암사', '청평사관광지', '김삿갓유적지', '개미들마을', '김유정문학마을', '선교장',
                       '농촌체험마을냇강마을', '청령포', '낙산사', '단종장릉', '청간정', '백두대간약초나라']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '경상남도':
        categories = ['고택/생가/민속마을', '유명사찰', '유명사적/유적지', '왕릉/고분',
                      '비/탑/문/각', '국보', '보물', '서원/향교/서당']
        map = folium.Map(location=[35.31439628, 128.520725], zoom_start=8)

        with tabname:
            options = ['충익사', '지리산쌍계사', '평리산대추마을', '다대어촌체험마을', '만어사', '애국지사산돌손양원목사기념관', '진주성',
                       '가남정보화마을', '거기애사과마을', '고려동유적지', '이수도어촌체험마을', '서변정보화마을', '통영충렬사', '노무현대통령생가',
                       '홍룡사', '숲옛마을', '쌍근어촌체험마을', '남계서원', '표충비각', '삼성궁', '목면시배유지', '내원사', '수로왕릉', '한산도제승당',
                       '창원의집', '임경대', '군항문화탐방', '사명대사유적지', '통제영지세병관', '대성동고분박물관', '도장포어촌체험마을', '솔향기돌담마을',
                       '김영삼전대통령생가기록전시관', '영암사지', '밀양영남루', '지곡개평한옥마을', '표충사', '통도사', '하늘비단마을']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '경상북도':
        categories = ['고택/생가/민속마을', '유명사찰', '유명사적/유적지', '왕릉/고분',
                      '비/탑/문/각', '천연기념물', '보물', '서원/향교/서당', '성/성터']
        map = folium.Map(location=[36.40462551, 128.75298], zoom_start=8)

        with tabname:
            options = ['경주동궁과월지', '농암종택', '회연서원', '예마을', '무열왕릉', '분황사', '하회마을', '김유신장군묘', '기성리어촌체험마을',
                       '불국사', '고운사', '박대통령생가', '태사묘', '무섬마을', '오어사', '안동군자마을', '서우재마을', '봉평신라비전시관',
                       '덕동문화마을', '경주감은사지', '백암온천마을', '봉정사', '운문사', '도산서원', '박열의사기념관', '기림사', '괴시리전통마을',
                       '선암서원', '만취당', '낙동승곡마을', '신리마을', '소수서원', '예움터마을', '개실마을', '만휴정', '불영사', '안동임청각', '한개마을',
                       '석굴암', '포석정', '대곡사', '왕피거리고마을', '보경사', '이화만리녹색농촌체험마을', '대릉원', '임고서원', '은해사', '경주양동마을',
                       '세종대왕자태실', '통일전', '왕산허위선생기념관', '가산산성', '천생산성', '송소고택', '옛날솜씨마을', '직지사', '경주오릉', '산주마을',
                       '부석사']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '전라남도':
        categories = ['고택/생가/민속마을', '국보', '유명사찰', '유명사적/유적지', '비/탑/문/각', '서원/향교/서당', '성/성터']
        map = folium.Map(location=[34.94685128, 126.8603411], zoom_start=8)

        with tabname:
            options = ['김환기고택', '도림사', '백제불교최초도래지', '윤동주유고보존정병욱가옥', '운림산방', '남도진성', '송광사', '충의사',
                       '진남관', '정암조광조선생적려유허비', '태안사', '영랑생가', '해동사', '가톨릭목포성지', '윤선도유적지', '남미륵사',
                       '운조루유물전시관', '낙안읍성민속마을', '매간당고택', '무위사', '쌍봉사', '고금충무사', '성륜사', '용장성', '원불교영산성지',
                       '보림사', '유마사', '다산초당', '금성산성', '내산서원', '대흥사', '장도청해진유적지', '불회사입구', '천주교순교지', '향일암',
                       '영벽정', '필암서원', '흥국사', '내장산국립공원백양사', '나주목사내아', '도갑사', '영광향교', '매천황현선생생가', '백운동별서정원',
                       '동본원사', '김시식지', '선암사', '섬진강기차마을', '식영정', '명옥헌원림', '초의선사유적지', '금성관', '백련사',
                       '강진 고려청자 요지', '소쇄원', '전라병영성하멜표류지', '우수영', '쌍충사', '미황사달마고도', '운주사', '고산윤선도유적지']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '전라북도':
        categories = ['고택/생가/민속마을', '보물', '유명사찰', '유명사적/유적지', '천연기념물']
        map = folium.Map(location=[35.66065408, 127.1453867], zoom_start=8)

        with tabname:
            options = ['논개논개생가지', '무성서원', '미륵사지', '변산반도국립공원개암사', '만인의총', '무장읍성', '훈몽재', '경기전',
                       '고창읍성', '적상산사고지', '고창고인돌유적', '무주향교', '원불교익산성지', '논개의암사논개사당', '김명관고택',
                       '소충사', '실상사', '광한루원', '백제왕궁박물관', '피향정']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    elif select == '제주특별자치도':
        categories = ['유명사적/유적지', '비/탑/문/각']
        map = folium.Map(location=[33.43500382, 126.4490168], zoom_start=8)

        with tabname:
            options = ['제주목관아지', '항몽유적지', '삼양선사유적지', '제주추사관']
            selected = pills("Label", label_visibility='collapsed', options=options)

            url = dataframe.loc[dataframe['장소'] == selected, 'url'].iloc[0]

    return selected, map, categories, url

def tab2_place(url, chartdf, place, tabname):
    with tabname:
        try:
            # URL에서 GET 요청하여 응답 받기
            result = requests.get(url)
            # 응답을 XML로 파싱하기
            soup = BeautifulSoup(result.text, 'xml')
        except:
            pass

        try:
            for item in soup.findAll('item'):
                title = item.find('title').text
                addr = item.find('addr1').text
                overview = item.find('overview').text
                image1 = item.find('firstimage').text
                
                try:
                    st.image(image1)
                except MediaFileStorageError:
                    st.write('**이미지 없음**')
                st.write('이름 : ', title)
                st.write('주소 : ', addr)
                over_text = re.sub(r'<.*?>', '', overview)
                st.write(over_text)
        except:
            st.caption('장소에 대한 정보가 없습니다😥')



        year_chart(chartdf, place)
