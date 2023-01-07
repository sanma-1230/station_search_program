#  -*- coding: utf-8 -*-
import sys
import copy
import folium
import sqlite3
import webbrowser

# 入力例：python my.py 2400205 2500308




def get_neighborhood(cd):
    lat_lon = cur.execute(f"select lat, lon from m_station where station_cd={cd}").fetchall()
    if lat_lon:
        lat = lat_lon[0][0]
        lon = lat_lon[0][1]

        sta2 = cur.execute(f"select station_name, station_cd, line_cd from m_station where (lat between {lat-0.005} and {lat+0.005}) and (lon between {lon-0.005} and {lon+0.005})").fetchall()

        for i in range(len(sta2)):
            if cd == sta2[i][1]:
                save = i
        sta2.pop(save)
        return sta2

def get_join_list(cd1):
    join_list = []
    next_sta1 = cur.execute(f"select station_cd1 from m_station_join where station_cd2={cd1}").fetchall()
    next_sta2 = cur.execute(f"select station_cd2 from m_station_join where station_cd1={cd1}").fetchall()
    nei_sta = get_neighborhood(cd1)

    if next_sta1:
        next_sta1 = next_sta1[0][0]
        join_list.append(next_sta1)
    if next_sta2:
        next_sta2 = next_sta2[0][0]
        join_list.append(next_sta2)
    if nei_sta:
        for i in range(len(nei_sta)):
            join_list.append(nei_sta[i][1])

    return join_list

def search_station_2(lists, count, save_station_list):
        if count<25:
            for sta_cd in lists:
                save_station_list_copy = copy.copy(save_station_list)
                save_station_list_copy.append(sta_cd)
                cd_lists_2 = get_join_list(sta_cd)
                if cd2 in cd_lists_2:
                    save_station_list_copy.append(cd2)
                    match_linecd_list.append(save_station_list_copy)

                else:
                    rem_lists = []
                    for i in cd_lists_2:
                        if i in save_station_list:
                            rem_lists.append(i)
                    for i in rem_lists:
                        cd_lists_2.remove(i)
                    if cd_lists_2:
                        count += 1
                        search_station_2(cd_lists_2, count, save_station_list_copy)

def show_info_fromcd(lists):
    for i in lists:
        tmp = cur.execute(f"select station_name, station_cd, m_station.line_cd, line_name from m_station left outer join m_line on m_station.line_cd=m_line.line_cd where station_cd={i}").fetchall()
        print(tmp)

def plot_route(lists):
    loc = []
    lat_list = []
    lon_list = []
    m = folium.Map()
    for n, i in enumerate(lists):
        if n==0 or n==len(lists)-1:
            tmp = cur.execute(f"select lat,lon from m_station where station_cd={i}").fetchall()
            name = cur.execute(f"select station_name from m_station where station_cd={i}").fetchall()
            loc.append(tmp[0])
            folium.Marker(location=tmp[0],
                             popup=name[0][0],
                             icon=folium.Icon(color='red')
                             ).add_to(m)
        else:
            tmp = cur.execute(f"select lat,lon from m_station where station_cd={i}").fetchall()
            name = cur.execute(f"select station_name from m_station where station_cd={i}").fetchall()
            loc.append(tmp[0])
            folium.Marker(location=tmp[0],
                                     popup=name[0][0]
                                     ).add_to(m)

    line= folium.vector_layers.PolyLine(
                locations=loc,
                color='blue',
                weight=2)
    m.add_child(line)

    for i in loc:
        lat_list.append(i[0])
        lon_list.append(i[1])
    m.fit_bounds([[min(lat_list),min(lon_list)], [max(lat_list),max(lon_list)]])

    return m

def show_line(cd1, cd2):
    cd_lists = get_join_list(cd1)

    save_station_list = []
    save_station_list.append(cd1)
    save_station_list_copy = copy.copy(save_station_list)
    search_station_2(cd_lists, 0, save_station_list_copy)

    if match_linecd_list:
        minimum = 100
        for i in range(len(match_linecd_list)):
            n = len(match_linecd_list[i])
            if n < minimum:
                num = i
        show_info_fromcd(match_linecd_list[num])
        m = plot_route(match_linecd_list[num])
        m.save('map.html')
        webbrowser.open('map.html')
        
    else:
        print('見つかりませんでした。')

# station_cdから名前を表示
def cd_to_name(cd_):
    tmp = cur.execute(f"select station_name from m_station where station_cd={cd_}").fetchall()
    return tmp[0][0]

def name_to_cd(na):
    return cur.execute("select station_name, station_cd from m_station where station_name=?", (na,)).fetchall()




if __name__ == '__main__':
    args = sys.argv
    database_path = 'database.sqlite'
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    match_linecd_list = []
    cd1 = int(args[1])
    cd2 = int(args[2])
    show_line(cd1,cd2)

    cur.close()
    conn.close()