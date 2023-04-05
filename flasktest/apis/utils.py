import os
import time
import requests
import pandas as pd
import math

# savefig needs this
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import plotly.express as px  # noqa: E402

from flasktest import db  # noqa: E402
from flasktest.models import APIData  # noqa: E402
from flasktest.apis.apis_settings import *  # noqa: E402


pd.options.display.float_format = "{:,.4f}".format


# ------------------------------------------------------------- #
# ------------------------- PUBG ------------------------------ #
def get_player_id(player_name):
    """
    Contact PUBG API to retrieve a player's id.

    :param player_name: Steam name (str) of player.

    :return: API status code (int) & API message (str).
    Either:
    200, player_id
    404, "Player not found!"
    429, API cooldown flash() message
    other, "Unexpected error"
    """
    response = requests.get(
        f"{PUBG_PLAYER_ID_URL}{player_name}",
        headers=PUBG_API_HEADER,
        timeout=TIMEOUT,
    )
    status_code = response.status_code

    if status_code == 200:
        # Successful request
        json_response = response.json()
        player_id = json_response["data"][0]["id"]
        return status_code, player_id

    if status_code == 404:
        # Player not found
        return status_code, "Player not found!"

    if status_code == 429:
        # Too many requests
        # Update PUBG API database log
        update_pubg_api_data()
        pubg_data = APIData.query.filter_by(api_name="pubg").first()
        return status_code, f"API on cooldown." \
                            f" {(pubg_data.last_used + 60) - math.floor(time.time())} seconds left."

    # Unexpected error
    return status_code, "Unexpected error."


def get_seasons():
    """
    Contact PUBG API to retrieve all available seasons (starting after full launch).

    :return: API status code (int) & API message (str).
    Either:
    200, valid_seasons (list)
    429, API cooldown flash() message
    other, "Unexpected error"
    """
    response = requests.get(
        PUBG_SEASONS_URL,
        headers=PUBG_API_HEADER,
        timeout=TIMEOUT,
    )
    status_code = response.status_code

    if status_code == 200:
        # Successful request
        json_response = response.json()
        all_seasons = [x["id"] for x in json_response["data"]]
        valid_seasons = [x for x in all_seasons if "pc-" in x][::-1]
        return status_code, valid_seasons

    if status_code == 429:
        # Too many requests
        # Update PUBG API database log
        update_pubg_api_data()
        pubg_data = APIData.query.filter_by(api_name="pubg").first()
        return status_code, f"API on cooldown." \
                            f" {(pubg_data.last_used + 60) - math.floor(time.time())} seconds left."

    # Unexpected error
    return status_code, "Unexpected error."


def get_all_season_stats(player_id, valid_seasons, game_mode):
    """
    Contact PUBG API to retrieve all stats for requested seasons with
    a minimum of 5 played games.

    :param player_id: Player id taken from get_player_id() (str).
    :param valid_seasons: Seasons taken from get_seasons() (list).
    :param game_mode: Requested game mode from SearchPUBGForm to query (str).

    :return: API status code (int) & list all available player stats (list).
    Either:
    200, stats (nested list)
    429, API cooldown flash() message
    other, "Unexpected error"
    """
    assists = []
    damage = []
    kills = []
    headshots = []
    most_kills = []
    distance = []
    top10s = []
    games = []
    wins = []
    seasons = []
    checked = 0

    for season in valid_seasons:
        # Sleep in case of too many requests
        if checked in (7, 15):
            time.sleep(60)

        checked += 1
        response = requests.get(
            f"https://api.pubg.com/shards/steam/players/{player_id}/seasons/{season}?filter["
            f"gamepad]=false",
            headers=PUBG_API_HEADER,
            timeout=TIMEOUT,
        )
        status_code = response.status_code

        if status_code == 200:
            # Successful
            try:
                data_json = response.json()
                stats = data_json["data"]["attributes"]["gameModeStats"][game_mode]
            except KeyError:
                return status_code, "Internal error!"

        elif response.status_code == 429:
            # Too many requests
            # Update PUBG API database log
            update_pubg_api_data()
            pubg_data = APIData.query.filter_by(api_name="pubg").first()
            return status_code, \
                f"API on cooldown." \
                f"{(pubg_data.last_used + 60) - math.floor(time.time())} seconds left."

        else:
            # Unexpected error
            return status_code, "Unexpected error."

        if stats["roundsPlayed"] > 4:
            assists.append(stats["assists"])
            damage.append(stats["damageDealt"])
            kills.append(stats["kills"])
            headshots.append(stats["headshotKills"])
            most_kills.append(stats["roundMostKills"])
            distance.append(stats["rideDistance"])
            top10s.append(stats["top10s"])
            games.append(stats["roundsPlayed"])
            wins.append(stats["wins"])
            seasons.append("s." + season.split(".")[-1].split("-")[-1])
            # TODO: Create loading feedback for user on the webpage
            print(f"{season} added")
        else:
            print(f"{season} skipped")

        # Stop requests when NR_OF_BARS is reached
        if len(games) == NR_OF_BARS:
            return status_code, [assists, damage, kills, headshots, most_kills,
                                 distance, top10s, games, wins, seasons]

    # Unexpected error
    status_code = 404
    # TODO: Handle logic for empty results (player has no games played)
    return status_code, [assists, damage, kills, headshots, most_kills,
                         distance, top10s, games, wins, seasons]


def create_dataframe(player_stats, player_name, game_mode):
    """
    Creates and saves a DataFrame with the stats collected by get_all_season_stats(),
    the players name and the requested game mode.

    :param player_stats: Nested list containing stats per category.
    :param player_name: Players name received from the SearchPUBGForm (str).
    :param game_mode: Requested game mode from SearchPUBGForm to query (str).

    :return: DataFrame (DataFrame)
    """
    game_mode = game_mode.replace("-", "_")
    df_player = pd.DataFrame()

    df_player["Season"] = player_stats[9]
    df_player["Games"] = player_stats[7]

    df_player["Wins"] = player_stats[8]
    df_player["Wins_g"] = df_player.Wins / df_player.Games

    df_player["Top10s"] = player_stats[8]
    df_player["Top10s_g"] = df_player.Top10s / df_player.Games

    df_player["Damage"] = player_stats[1]
    df_player["Damage_g"] = df_player.Damage / df_player.Games

    df_player["Kills"] = player_stats[2]
    df_player["Kills_g"] = df_player.Kills / df_player.Games

    df_player["Headshots"] = player_stats[3]
    df_player["Headshots_g"] = df_player.Headshots / df_player.Games

    df_player["Assists"] = player_stats[0]
    df_player["Assists_g"] = df_player.Assists / df_player.Games

    df_player["Most_Kills"] = player_stats[4]
    df_player["Most_Kills_g"] = df_player.Assists / df_player.Games

    df_player["Distance"] = player_stats[5]
    df_player["Distance_g"] = df_player.Distance / df_player.Games

    df_player.to_csv(f"{PUBG_DATAFRAME_PATH}df_{player_name}_{game_mode}.csv",
                     index=False)

    return df_player


def create_kills_bar(dataframe, player_name, game_mode, user_id):
    """
    Creates and saves a plotly express KILLS bar graph with requested info from SearchPUBGForm.

    :param dataframe: Dataframe created by create_dataframe().
    :param player_name: Players name received from the SearchPUBGForm (str).
    :param game_mode: Requested game mode from SearchPUBGForm (str).
    :param user_id: User id from current_user or session["id"] (str or int).

    :return: Relative path to the saved bar graph to be sent to jinja (str).
    """
    kills_bar = px.bar(
        data_frame=dataframe,
        x="Season",
        y="Kills_g",
        title=f"Kills per game vs season | {player_name} {game_mode}",
    )
    kills_bar.update_traces(
        marker_color=PUBG_BAR_COLOR,
        marker_line_width=None,
        opacity=None,
    )

    kills_bar.update_layout(
        xaxis_title="Season",
        yaxis_title="Kills per game",
        paper_bgcolor=PUBG_BAR_BG_COLOR,
        plot_bgcolor=PUBG_BAR_BG_COLOR,
        font=PUBG_BAR_FONT,
    )
    kills_bar.write_image(f"{PUBG_IMAGE_PATH}{user_id}-current_kills.png",
                          scale=2)
    return f"{PUBG_IMAGE_PATH_RELATIVE}{user_id}-current_kills.png"


def create_damage_bar(dataframe, player_name, game_mode, user_id):
    """
    Creates and saves a plotly express DAMAGE bar graph with requested info from SearchPUBGForm.

    :param dataframe: Dataframe created by create_dataframe().
    :param player_name: Players name received from the SearchPUBGForm (str).
    :param game_mode: Requested game mode from SearchPUBGForm (str).
    :param user_id: User id from current_user or session["id"] (str or int).

    :return: Relative path to the saved bar graph to be sent to jinja (str).
    """
    damage_bar = px.bar(
        data_frame=dataframe,
        x="Season",
        y="Damage_g",
        title=f"Damage per game vs season | {player_name} {game_mode}",
    )
    damage_bar.update_traces(
        marker_color=PUBG_BAR_COLOR,
        marker_line_width=None,
        opacity=None,
    )

    damage_bar.update_layout(
        xaxis_title="Season",
        yaxis_title="Damage per game",
        paper_bgcolor=PUBG_BAR_BG_COLOR,
        plot_bgcolor=PUBG_BAR_BG_COLOR,
        font=PUBG_BAR_FONT,
    )

    damage_bar.write_image(f"{PUBG_IMAGE_PATH}{user_id}-current_damage.png",
                           scale=2)

    return f"{PUBG_IMAGE_PATH_RELATIVE}{user_id}-current_damage.png"


def create_distance_bar(dataframe, player_name, game_mode, user_id):
    """
    Creates and saves a plotly express DISTANCE bar graph with requested info from SearchPUBGForm.

    :param dataframe: Dataframe created by create_dataframe().
    :param player_name: Players name received from the SearchPUBGForm (str).
    :param game_mode: Requested game mode from SearchPUBGForm (str).
    :param user_id: User id from current_user or session["id"] (str or int).

    :return: Relative path to the saved bar graph to be sent to jinja (str).
    """
    distance_bar = px.bar(
        data_frame=dataframe,
        x="Season",
        y="Distance_g",
        title=f"Distance per game vs season | {player_name} {game_mode}",
    )
    distance_bar.update_traces(
        marker_color=PUBG_BAR_COLOR,
        marker_line_width=None,
        opacity=None,
    )

    distance_bar.update_layout(
        xaxis_title="Season",
        yaxis_title="Distance per game",
        paper_bgcolor=PUBG_BAR_BG_COLOR,
        plot_bgcolor=PUBG_BAR_BG_COLOR,
        font=PUBG_BAR_FONT,
    )

    distance_bar.write_image(f"{PUBG_IMAGE_PATH}{user_id}-current_distance.png",
                             scale=2)

    return f"{PUBG_IMAGE_PATH_RELATIVE}{user_id}-current_distance.png"


def remove_pubg_images(user_id):
    """
    Deletes users generated bar graphs when logging out.

    :param user_id: User id from current_user or session["id"] (str or int).
    """
    if os.path.isfile(f"{PUBG_IMAGE_PATH}{user_id}-current_kills.png"):
        os.remove(f"{PUBG_IMAGE_PATH}{user_id}-current_kills.png")

    if os.path.isfile(f"{PUBG_IMAGE_PATH}{user_id}-current_damage.png"):
        os.remove(f"{PUBG_IMAGE_PATH}{user_id}-current_damage.png")

    if os.path.isfile(f"{PUBG_IMAGE_PATH}{user_id}-current_distance.png"):
        os.remove(f"{PUBG_IMAGE_PATH}{user_id}-current_distance.png")


def load_old_pubg_data(df_path, player_name, game_mode, save_mode, user_id):
    """
    Generates and saved bar graphs for PUBG page when the searched player has had their
    stats searched for in the past and thus their stats have been saved already.

    :param df_path: Path to folder containing the dataframe (str).
    :param player_name: Players name received from the SearchPUBGForm (str).
    :param game_mode: Requested game mode from SearchPUBGForm (str).
    :param save_mode: Modified game_mode param for better format (str).
    :param user_id: User id from current_user or session["id"] (str or int).

    :returns: Three relative paths to the requested graphs (str).
    """
    old_df = pd.read_csv(f"{df_path}{player_name}_{save_mode}.csv")
    kills_img = create_kills_bar(old_df, player_name, game_mode, user_id)
    damage_img = create_damage_bar(old_df, player_name, game_mode, user_id)
    distance_img = create_distance_bar(old_df, player_name, game_mode, user_id)

    return kills_img, damage_img, distance_img


def update_pubg_api_data():
    """
    Stores the current time.time() in the APIData database.
    This is later checked whe new requests are made to display cooldown flash() messages.
    """
    pubg_data = APIData.query.filter_by(api_name="pubg").first()
    pubg_data.last_used = math.floor(time.time())
    db.session.commit()


def get_pubg_cooldown_message():
    """
    Returns a string containing the api cooldown timer and the connected flash() message.
    """
    pubg_data = APIData.query.filter_by(api_name="pubg").first()

    return f"API on cooldown. {(pubg_data.last_used + 60) - math.floor(time.time())} seconds left."


# ------------------------------------------------------------ #
# ------------------------- CPI ------------------------------ #
def get_cpi_categories(form_data):
    """
    Generates a list of category items from the SearchCPIForm.

    :param form_data: List of tuples from the SearchCPIForm (list tuple str).

    :return:  List of category items (list str).
    """
    categories = []
    for k, v in form_data.items():
        if k in CPI_CATEGORIES:
            for x in v:
                categories.append(x)
    return categories


def get_cpi_series(category_item, start_date, end_date):
    """
    Takes SearchCPIForm input and returns the corresponding Pandas Series from
     the df_cpi_netherlands DataFrame.

    :param category_item: Category item from input from SearchCPIForm input.
    :param start_date: Start date received from SearchCPIForm input.
    :param end_date: End date received from SearchCPIForm input.

    :return: Pandas Series (Series).
    """
    df_all = pd.read_csv(f"{CPI_DATA_FOLDER}df_cpi_netherlands.csv",
                         parse_dates=["period_dt"],
                         index_col="period_dt")

    df = df_all[(df_all.cat == category_item) &
                (df_all.index.year >= start_date) &
                (df_all.index.year <= end_date)]

    return df.cpi


def save_cpi_graph(categories, start_date, end_date, user_id):
    """
    Takes list of Pandas Series taken from get_cpi_series(),
    start & end years from SearchCPIForm input and saves them in 1 line graph
    to return its relative path to be rendered with jinja.

    :param categories: List of Pandas Series (list).
    :param start_date: SearchCPIForm start_date input (int).
    :param end_date: SearchCPIForm stop_date input (int).
    :param user_id: User id from current_user or session["id"] (str or int).

    :return: Relative path to the saved line graph (str).
    """
    for x in categories:
        series = get_cpi_series(x, start_date, end_date)
        plt.plot(series, label=x)

    plt.title("Consumer Price Index (2006=100)", fontsize=19)
    plt.xlabel("Period", fontsize=17)
    plt.ylabel("CPI", fontsize=17)
    plt.grid()
    plt.legend()
    plt.xticks(rotation=45, fontsize=13)
    plt.yticks(fontsize=13)

    plt.savefig(f"{CPI_IMAGE_PATH}{user_id}\\graph1.png",
                bbox_inches="tight",
                facecolor=CPI_BG_COLOR,
                edgecolor=CPI_BG_COLOR,
                pad_inches=0.3)
    plt.clf()
    return f"{CPI_IMAGE_PATH_RELATIVE}{user_id}/graph1.png"


def check_user_folder_exists(user_id):
    """
    Checks if a user solder exists in the CPI_IMAGE_PATH to store the CPI line graph.
    If it does not exist it is created.

    :param user_id: User id from current_user or session["id"] (str or int).
    """
    if not os.path.exists(f"{CPI_IMAGE_PATH}{user_id}"):
        # Create user folder is non-existent
        os.makedirs(f"{CPI_IMAGE_PATH}{user_id}")


def count_cpi_graphs(user_id):
    """
    Checks the number of graphs the user has generated.
    Needed for recursive renaming to keep the maximum to the 4 latest graphs.

    :param user_id: User id from current_user or session["id"] (str or int).

    :return: The number of files in the users CPI image folder (int).
    """
    file_count = sum(len(files) for _, _, files in os.walk(f"{CPI_IMAGE_PATH}{user_id}"))

    return file_count if file_count is not None else 0


def get_cpi_graph_paths(user_id, file_count):
    """
    Creates relative paths to the users generated graphs if any were found with count_cpi_graphs().

    :param user_id: User id from current_user or session["id"] (str or int).
    :param file_count: Number of files in users CPI image folder from count_cpi_graphs() (int).

    :return: List with relative paths to user generated CPI images to be used with jinja (list str).
    """
    base_path = f"{CPI_IMAGE_PATH_RELATIVE}{user_id}/"
    graph_paths = [f"{base_path}graph{i + 1}.png" for i in range(0, file_count)]

    return graph_paths


def rename_graphs(user_id):
    """
    Recursively renames user generated graphs to keep the maximum to the 4 latest.

    :param user_id: User id from current_user or session["id"] (str or int).
    """
    if os.path.isfile(f"{CPI_IMAGE_PATH}{user_id}/graph3.png"):
        os.replace(f"{CPI_IMAGE_PATH}{user_id}/graph3.png",
                   f"{CPI_IMAGE_PATH}{user_id}/graph4.png")

    if os.path.isfile(f"{CPI_IMAGE_PATH}{user_id}/graph2.png"):
        os.replace(f"{CPI_IMAGE_PATH}{user_id}/graph2.png",
                   f"{CPI_IMAGE_PATH}{user_id}/graph3.png")

    if os.path.isfile(f"{CPI_IMAGE_PATH}{user_id}/graph1.png"):
        os.replace(f"{CPI_IMAGE_PATH}{user_id}/graph1.png",
                   f"{CPI_IMAGE_PATH}{user_id}/graph2.png")
