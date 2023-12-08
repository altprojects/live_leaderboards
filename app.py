import streamlit as st
import pandas as pd
import requests
import numpy as np
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objs as go

st.title("Share 2 Win LeaderBoards")


@st.cache_data()
def fetch_player_stats(player_tag):
    # Make API call for each player's detailed stats
    player_stats_url = f"https://api.clashking.xyz/player/%20%23{player_tag}/stats"
    player_stats_response = requests.get(player_stats_url)

    if player_stats_response.status_code == 200:
        player_stats_data = player_stats_response.json()

        # Extracting relevant information from player_stats_data
        name = player_stats_data.get("name", "")
        tag = player_stats_data.get("tag", "")
        townhall = player_stats_data.get("townhall", "")

        # Extracting donations information
        donations = player_stats_data.get("donations", {})
        last_donation_key = sorted(donations.keys())[-1] if donations else None
        last_donation = donations.get(last_donation_key, {}) if last_donation_key else {}

        donated = last_donation.get("donated", 0)
        received = last_donation.get("received", 0)

        # Extracting activity information
        activity = player_stats_data.get("activity", {})
        last_activity_key = sorted(activity.keys())[-1] if activity else None
        last_activity_value = activity.get(last_activity_key, 0) if last_activity_key else 0

        # Extracting trophies
        trophies = player_stats_data.get("trophies", 0)

        # Extracting clan_tag
        clan_tag = player_stats_data.get("clan_tag", "")

        return name, tag, townhall, donated, received, last_activity_value, trophies, clan_tag
    else:
        print(f"Error: Unable to fetch data for player {player_tag}. Status code: {player_stats_response.status_code}")
        return "", "", 0, 0, 0, 0, 0, ""


@st.cache_data()
def fetch_clan_donations(clan_urls):
    # Initialize an empty DataFrame to store the combined data
    df_donations = pd.DataFrame()

    # Loop through each clan URL
    for url in clan_urls:
        # Make the request
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON content
            json_data = response.json()
            clan_tag = json_data.get("tag", "")
            # Extract member data
            members_data = json_data.get("memberList", [])

            # Create lists to store extracted data
            names = []
            tags = []
            trophies = []
            player_tags = []

            # Iterate through each member in the "memberList"
            for member in members_data:
                names.append(member.get("name", ""))
                tags.append(member.get("tag", ""))
                trophies.append(member.get("trophies", 0))

                # Extract player tag without '#'
                player_tag = member.get("tag", "").replace("#", "")
                player_tags.append(player_tag)

            # Fetch player stats sequentially without threading
            results = [fetch_player_stats(player_tag) for player_tag in player_tags]

            # Unpack results
            name_list, tag_list, townhall_list, donated_list, received_list, last_activity_list, trophies_list, clan_tag_list = zip(*results)

            # Create a DataFrame from the lists
            df_clan = pd.DataFrame({
                "Name": name_list,
                "Tag": tag_list,
                "Townhall": townhall_list,
                "Donated": donated_list,
                "Received": received_list,
                "Activity": last_activity_list,
                "Trophies": trophies_list,
                "Clan Tag": clan_tag_list
            })

            # Append the clan DataFrame to the combined DataFrame
            df_donations = pd.concat([df_donations, df_clan], ignore_index=True)

    # Sort the combined DataFrame by donations in descending order
    df_donations = df_donations.sort_values(by="Donated", ascending=False)
    df_donations.to_excel("donations.xlsx")

    return df_donations


# List of clan URLs
clan_urls = [
    "https://api.clashking.xyz/clan/%23UCR0Y2G/basic",
    "https://api.clashking.xyz/clan/%232LYP2J2L/basic",
    "https://api.clashking.xyz/clan/%23YVUPY0R/basic",
    "https://api.clashking.xyz/clan/%232Y28P8QV0/basic",
    "https://api.clashking.xyz/clan/%239UJCC2QJ/basic",
]

# Call the function with the specified clan URLs and store the result in donations_df
donations_df = fetch_clan_donations(clan_urls)


@st.cache_data()
def war(url):
    # Make the request
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON content
        json_data = response.json()

        # Initialize lists to store extracted data
        names = []
        tags = []
        total_attacks_random_list = []
        total_stars_random_list = []
        total_destruction_random_list = []
        three_stars_random_list = []
        two_stars_random_list = []
        one_stars_random_list = []
        zero_stars_random_list = []
        hitrate_random_list = []

        # Iterate through each player in the "items" list
        for player in json_data["items"]:
            name = player["name"]
            tag = player["tag"]

            # Initialize variables to store data for each player
            total_attacks_random = None
            total_stars_random = None
            total_destruction_random = None
            three_stars_random = None
            two_stars_random = None
            one_stars_random = None
            zero_stars_random = None
            hitrate_random = None

            # Iterate through hit_rates to find specific types
            for hit_rate in player["hit_rates"]:
                if hit_rate["type"] == "war_type" and hit_rate["value"] == "random":
                    total_attacks_random = hit_rate["total_attacks"]
                    total_stars_random = hit_rate.get("total_stars", None)
                    total_destruction_random = hit_rate.get("total_destruction", None)
                    three_stars_random = hit_rate.get("three_stars", None)
                    two_stars_random = hit_rate.get("two_stars", None)
                    one_stars_random = hit_rate.get("one_stars", None)
                    zero_stars_random = hit_rate.get("zero_stars", None)
                    hitrate_random = hit_rate["hitrate"]

            # Check if there is data for "war_type" with "value" equal to "random"
            if total_attacks_random is not None:
                # Append the extracted data to the lists
                names.append(name)
                tags.append(tag)
                total_attacks_random_list.append(total_attacks_random)
                total_stars_random_list.append(total_stars_random)
                total_destruction_random_list.append(total_destruction_random)
                three_stars_random_list.append(three_stars_random)
                two_stars_random_list.append(two_stars_random)
                one_stars_random_list.append(one_stars_random)
                zero_stars_random_list.append(zero_stars_random)
                hitrate_random_list.append(hitrate_random)

        # Create a DataFrame from the lists
        war_df = pd.DataFrame({
            "Name": names,
            "Tag": tags,
            "Total Attacks": total_attacks_random_list,
            "Total Stars": total_stars_random_list,
            "Total Destruction": total_destruction_random_list,
            "Three Stars": three_stars_random_list,
            "Two Stars": two_stars_random_list,
            "One Stars": one_stars_random_list,
            "Zero Stars": zero_stars_random_list,
            "Hitrate": hitrate_random_list,
        })

        # Write the DataFrame to an Excel file
        excel_file_path = "war_stats.xlsx"
        war_df = war_df.sort_values(by="Total Stars", ascending=False)
        war_df.drop_duplicates(inplace=True)
        war_df["Missed Hits"] = war_df["Total Attacks"] - war_df["Three Stars"] - war_df["Two Stars"] - war_df["One Stars"] - war_df["Zero Stars"]
        war_df.to_excel(excel_file_path, index=False)

        print(f"Data has been written to: {excel_file_path}")

        return war_df

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}")


# Specify the URL
url = """https://api.clashking.xyz/war-stats?clans=%23UCR0Y2G&clans=%232LYP2J2L&clans=%23YVUPY0R&clans=%232Y28P8QV0&sort_field=hit_rates.hitrate&tied_only=true&descending=true&limit=200"""

# Call the function with the specified URL and store the result in war_df
war_df = war(url)

df_combined = pd.merge(donations_df, war_df, on="Tag", how="outer")
df_combined = df_combined.drop(columns=["Name_y"])
df_combined = df_combined.rename(columns={"Name_x": "Name"})
df_combined.drop_duplicates(inplace=True)
allowed_clan_tags = ["#UCR0Y2G", "#2LYP2J2L", "#YVUPY0R", "#2Y28P8QV0", "#9UJCC2QJ"]
df_combined = df_combined[df_combined['Clan Tag'].isin(allowed_clan_tags)]

# Mapping of Clan Tags to Clan Names
clan_tag_to_name = {
    "#UCR0Y2G": "Share 2 Win",
    "#2LYP2J2L": "Share 2 Win 2",
    "#YVUPY0R": "Share 2 Win 3",
    "#2Y28P8QV0": "Share 2 Win 4",
    "#9UJCC2QJ": "Share 2 War",
}

# Add a new column "Clan Name" based on the mapping
df_combined['Clan Name'] = df_combined['Clan Tag'].map(clan_tag_to_name)

grouped_df = df_combined.groupby('Clan Tag')


@st.cache_data()
def preprocess_group(group):
    group['Activity'].fillna(group['Activity'].min(), inplace=True)
    group['Donated'].fillna(0, inplace=True)
    group['Received'].fillna(0, inplace=True)
    group['Three Stars'].fillna(0, inplace=True)
    group['Two Stars'].fillna(0, inplace=True)
    group['One Stars'].fillna(0, inplace=True)
    group['Zero Stars'].fillna(0, inplace=True)
    group['Missed Hits'].fillna(0, inplace=True)
    group['Total Destruction'].fillna(group['Total Destruction'].min(), inplace=True)
    group['Total Stars'].fillna(group['Total Stars'].min(), inplace=True)
    group['Total Attacks'].fillna(group['Total Attacks'].min(), inplace=True)
    group['Hitrate'].fillna(0, inplace=True)

    # Calculate 'War Score' with division handling
    denominator_war = group['Total Stars'].quantile(0.75) - group['Total Stars'].quantile(0.25)
    group["War Score"] = np.where(denominator_war != 0, 0.6 * (group["Total Stars"] - group['Total Stars'].quantile(0.25)) * 10.0 / denominator_war, 0)

    # Calculate 'Donation Score' with division handling
    denominator_donation = group['Donated'].quantile(0.75) - group['Donated'].quantile(0.25)
    group["Donation Score"] = np.where(denominator_donation != 0, 0.3 * (group["Donated"] - group['Donated'].quantile(0.25)) * 10.0 / denominator_donation, 0)

    # Calculate 'Activity Score' with division handling
    denominator_activity = group['Activity'].quantile(0.75) - group['Activity'].quantile(0.25)
    group["Activity Score"] = np.where(denominator_activity != 0, 0.1 * (group["Activity"] - group['Activity'].quantile(0.25)) * 10.0 / denominator_activity, 0)

    group["Missed Score"] = group["Missed Hits"] ** 2
    # Calculate 'Season Score'
    group["Season Score"] = group["War Score"] + group["Donation Score"] + group["Activity Score"] - group["Missed Score"]

    return group


preprocessed_dfs = [preprocess_group(group) for _, group in grouped_df]
df_combined = pd.concat(preprocessed_dfs, ignore_index=True)

data = df_combined.reset_index(drop=True)
# st.write(data)


selected_metric = st.selectbox("Select Metric:", ["Total Stars", "Donations", "Activity", "Trophies", "Top Member"])
if selected_metric == "Total Stars":
    st.write("Top 5 Members by War Stars:")
    st.write(data[["Name", "Tag", "Clan Name","Total Stars","Total Attacks","Hitrate","Three Stars","War Score"]].sort_values(by="Total Stars", ascending=False).head(5).reset_index(drop=True))
    fig=go.Figure()
    fig=px.bar(data.sort_values(by="Total Stars",ascending=False).head(),x=data.sort_values(by="Total Stars",ascending=False).head().Name,y='Total Stars',color="Total Stars",hover_data=["Total Stars"],hover_name="Name",text='Total Stars',title='Best War Performers',height=500,width=700,color_continuous_scale='YlOrRd')
    fig.update_traces(texttemplate='%{text:.3s}',textposition='outside')
    st.plotly_chart(fig)


if selected_metric == "Activity":
    st.write("Top 5 Members by Activity:")
    st.write(data[["Name", "Tag","Clan Name", "Activity"]].sort_values(by="Activity", ascending=False).head(5).reset_index(drop=True))
    fig=go.Figure()
    fig=px.bar(data.sort_values(by="Activity",ascending=False).head(),x=data.sort_values(by="Activity",ascending=False).head().Name,y='Activity',color="Activity",hover_data=["Activity"],hover_name="Name",text='Activity',title='Most Active Players',height=500,width=700,color_continuous_scale='YlOrRd')
    fig.update_traces(texttemplate='%{text:.3s}',textposition='outside')
    st.plotly_chart(fig)

if selected_metric == "Donations":
    st.write("Top 5 Members by Donations:")
    st.write(data[["Name", "Tag", "Clan Name", "Donated", "Received"]].sort_values(by="Donated", ascending=False).head(5).reset_index(drop=True))
    fig=go.Figure()
    fig=px.bar(data.sort_values(by="Donated",ascending=False).head(),x=data.sort_values(by="Donated",ascending=False).head().Name,y='Donated',color="Donated",hover_data=["Donated","Received","Donation Score"],hover_name="Name",text='Donated',title='Top Donators',height=500,width=700,color_continuous_scale='YlOrRd')
    fig.update_traces(texttemplate='%{text:.4s}',textposition='outside')
    st.plotly_chart(fig)

if selected_metric == "Trophies":
    st.write("Top 5 Members by Trophies:")
    st.write(data[["Name", "Tag", "Clan Name", "Trophies"]].sort_values(by="Trophies", ascending=False).head(5).reset_index(drop=True))
    fig=go.Figure()
    fig=px.bar(data.sort_values(by="Trophies",ascending=False).head(),x=data.sort_values(by="Trophies",ascending=False).head().Name,y='Trophies',color="Trophies",hover_data=["Trophies"],hover_name="Name",text='Trophies',title='Top Trophy Pushers',height=500,width=700,color_continuous_scale='YlOrRd')
    fig.update_traces(texttemplate='%{text:.4s}',textposition='outside')
    st.plotly_chart(fig)

if selected_metric == "Top Member":
    st.write("Top 5 Members by Season Score:")
    st.write(data[["Name", "Tag", "Clan Name", "War Score", "Donation Score", "Activity Score", "Season Score"]].sort_values(by="Season Score", ascending=False).head(5).reset_index(drop=True))
    fig=go.Figure()
    fig=px.bar(data.sort_values(by="Season Score",ascending=False).head(),x=data.sort_values(by="Season Score",ascending=False).head().Name,y='Season Score',color="Season Score",hover_data=["War Score","Donation Score","Activity Score","Season Score"],hover_name="Name",text='Season Score',title='Top Performers',height=500,width=700,color_continuous_scale='YlOrRd')
    fig.update_traces(texttemplate='%{text:.3s}',textposition='outside')
    st.plotly_chart(fig)

average_metrics_table = data.groupby(['Clan Tag', 'Clan Name']).agg({
    'Donated': 'mean',
    'Total Stars': 'mean',
    'Activity': 'mean'
}).reset_index()

# Display the average metrics table
st.write("Average Metrics by Clan:")
st.write(average_metrics_table)


# import plotly.express as px

# Group by 'Clan Tag' and 'Clan Name' and extract selected metrics
grouped_data = data.groupby(['Clan Tag', 'Clan Name'])

# Create boxplots for 'Donated', 'Total Stars', and 'Activity'
# Create boxplots for 'Donated', 'Total Stars', and 'Activity'
fig_donated = px.box(data, x='Clan Name', y='Donated', color='Clan Tag', points="all", title='Donated Distribution by Clan Name', hover_data=["Name","Clan Name"], facet_col_spacing=0.2, boxmode='overlay')
fig_stars = px.box(data, x='Clan Name', y='Total Stars', color='Clan Tag', points="all", title='Total Stars Distribution by Clan Name', hover_data=["Name","Clan Name"], facet_col_spacing=0.2, boxmode='overlay')
fig_activity = px.box(data, x='Clan Name', y='Activity', color='Clan Tag', points="all", title='Activity Distribution by Clan Name', hover_data=["Name","Clan Name"], facet_col_spacing=0.2, boxmode='overlay')

# Display the boxplots
st.plotly_chart(fig_donated)
st.plotly_chart(fig_stars)
st.plotly_chart(fig_activity)


download_data=data.sort_values(by="Season Score",ascending=False).reset_index(drop=True)
if st.button("Download DataFrame as Excel"):
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                download_data.to_excel(writer, sheet_name="Sheet1", index=False)


    # Set up the download link using an HTML anchor tag
            excel_buffer.seek(0)
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(excel_buffer.read()).decode()}" download="final_merged_data.xlsx">Click here to download the Excel file</a>'
            st.markdown(href, unsafe_allow_html=True)
