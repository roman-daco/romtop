import requests
from bs4 import BeautifulSoup
import json
import streamlit as st

ROOTPAGE = "https://www.radiotrib.ro/radiotrib/romtop/arhiva?itemId=Romtop_Edition:"


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def get_edition(n):
    return requests.get(ROOTPAGE + str(n))

def read_and_parse_from_html():
    romtop_data = []
    file_path = 'C:/Users/Eugen/PycharmProjects/rt/rt_editions/'
    for ed in range(503):
        file_name = "editia_" + str(ed) + ".html"
        with open(file_path+file_name, "r", encoding="utf-8") as file:
            content = file.read()
        edition_soup = BeautifulSoup(content, "html.parser")
        # parse the week and edition number
        wk_tags = []
        for wk_tag in edition_soup.find_all("h2", {"class": "week"}):
            wk_tags.append(wk_tag.text)
        if len(wk_tags) == 1:
            wk_tag = wk_tags[0]
            wk_elems = wk_tag.split()
            if len(wk_elems) == 4:
                dd = int(wk_elems[0])
                mm = wk_elems[1]
                yy = int(wk_elems[2])
                ed_no = wk_elems[3].split("(")[-1].split(")")[0]
                if yy >= 2015:
                    # parse top entries
                    top_data = []
                    for divtag in edition_soup.find_all("div", {"class": "list article-blog"}):
                        for ptag in divtag.find_all("p"):
                            section = ptag.text
                        for litag in divtag.find_all("li", {"class": "vot"}):
                            for spantag in litag.find_all("span", {"class": "nr"}):
                                place = spantag.text
                            for spantag in litag.find_all("span", {"class": "song-name"}):
                                song_name = spantag.text
                            for spantag in litag.find_all("span", {"class": "artist"}):
                                artist = spantag.text
                            if artist != "N/A" and song_name != "N/A":
                                top_data.append({
                                    "place": int(place),
                                    "song-name": song_name,
                                    "artist": artist,
                                    "entry_type": section
                                })
                                if section == "Lista Cantece" and place == "1":
                                    print(artist, "---", song_name, "| edition", ed_no, "| date", dd, mm, yy, "| file ",
                                          ed)
                    # add entries to romtop database
                    if top_data:
                        romtop_data.append({
                            "edition_number": ed_no,
                            "day": dd,
                            "month": mm,
                            "year": yy,
                            "top_entries": top_data
                        })
                # print(json.dumps(top_data, indent=2))
                # entry_types = list(set([top_entry["entry_type"] for top_entry in top_data]))
                # print("entry types:", entry_types)
    # grimushi = [str(a["place"]) + ":" + a["song-name"] + ", " + a["entry_type"] for a in top_data if a["artist"] == "Grimus"]
    # print ("Grimus data:")
    # print(json.dumps(grimushi, indent=2))
    file_name = "romtop_data.json"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(json.dumps(romtop_data, indent=2))

def aggregated_top(year):
    with open("romtop_data.json") as romtop_file:
        romtop_data = json.load(romtop_file)
    romtop_year_agg = [romtop_entry for romtop_entry in romtop_data if romtop_entry["year"] == year]
    print(len(romtop_year_agg))
    romtop_aggregate_year = {}
    for romtop_edition in romtop_year_agg:
        top_entries = [top_entry for top_entry in romtop_edition["top_entries"] if top_entry["entry_type"] == "Lista Cantece"]
        for top_entry in top_entries:
            entry_id = top_entry["artist"] + "|" + top_entry["song-name"]
            entry_place = top_entry["place"]
            if entry_id not in romtop_aggregate_year:
                romtop_aggregate_year[entry_id] = {
                    "artist": top_entry["artist"],
                    "song-name": top_entry["song-name"],
                    "weeks": 1,
                    "weeks_at_no1": 0,
                    "highest_pos": entry_place,
                    "points": 31 - entry_place
                }
                if entry_place == 1:
                    romtop_aggregate_year[entry_id]["weeks_at_no1"] = 1
            else:
                romtop_aggregate_year[entry_id]["weeks"] += 1
                if entry_place == 1:
                    romtop_aggregate_year[entry_id]["weeks_at_no1"] += 1
                romtop_aggregate_year[entry_id]["highest_pos"] = min(romtop_aggregate_year[entry_id]["highest_pos"], entry_place)
                romtop_aggregate_year[entry_id]["points"] += 31 - entry_place
    for entry_id in romtop_aggregate_year:
        romtop_aggregate_year[entry_id]["avg_points"] = int(float(romtop_aggregate_year[entry_id]["points"])/romtop_aggregate_year[entry_id]["weeks"]*100)/100.0
    romtop_agg_list = sorted([romtop_aggregate_year[id] for id in romtop_aggregate_year], key=lambda x: x["points"], reverse=True)
    place = 0
    for final_entry in romtop_agg_list:
        place += 1
        print(place,
              final_entry["artist"],
              "-",
              final_entry["song-name"],
              final_entry["points"],
              final_entry["avg_points"],
              final_entry["weeks"],
              final_entry["highest_pos"],
              final_entry["weeks_at_no1"])
    romtop_agg_list = sorted([romtop_aggregate_year[id] for id in romtop_aggregate_year], key=lambda x: x["avg_points"], reverse=True)
    place = 0
    for final_entry in romtop_agg_list:
        place += 1
        print(place,
              final_entry["artist"],
              "-",
              final_entry["song-name"],
              final_entry["points"],
              final_entry["avg_points"],
              final_entry["weeks"],
              final_entry["highest_pos"],
              final_entry["weeks_at_no1"])

def run():
    st.title('RomTop yearly aggregator')
    st.write('Introduce the year to aggregate')

    # User input
    year = st.number_input('Year (YYYY)',
                           min_value=2015,
                           max_value=2024,
                           value=2024)
    if st.button('Generate top'):
        # Generate yearly top
        aggregated_top(year)
        # Show generated top
        st.success('Top was generated!')
    
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()
    # download editions from the site
    # for ed in range(503):
    #     print("Editia ", str(ed))
    #     curr_ed = get_edition(ed).text
    #     file_name = "editia_" + str(ed) + ".html"
    #     with open(file_name, "w", encoding="utf-8") as file:
    #         file.write(curr_ed)

    # create aggregating json
    # read_and_parse_from_html()

    #generate year aggregated top
    # aggregated_top(2024)


# data = [{"place": 1,
#          "artist": "Blazzaj",
#          "song-name": "PLUSUNU",
#          "entry_type": "Top30"}
# ]
