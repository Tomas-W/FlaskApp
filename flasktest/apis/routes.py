import time
import os

from flask import render_template, request, flash, session, Blueprint
from flask_login import login_required

from flasktest.models import APIData
from flasktest.apis.forms import SearchPUBGForm, SearchCPIForm
from flasktest.apis.utils import get_player_id, get_seasons, get_all_season_stats, \
    create_dataframe, create_kills_bar, create_damage_bar, create_distance_bar, \
    load_old_pubg_data, get_pubg_cooldown_message, update_pubg_api_data, save_cpi_graph, \
    get_cpi_categories, rename_graphs, count_cpi_graphs, get_cpi_graph_paths, \
    check_user_folder_exists
from flasktest.apis.apis_settings import PUBG_IMAGE_PATH, PUBG_IMAGE_PATH_RELATIVE, PUBG_DATA_PATH

apis = Blueprint("apis", __name__)


# ------------------------------------------------------------- #
# ------------------------- PUBG ------------------------------ #
@apis.route("/api/pubg", methods=["POST", "GET"])
@login_required
def pubg():
    pubg_form = SearchPUBGForm()
    kills_img = f"{PUBG_IMAGE_PATH_RELATIVE}example_kills.png"
    damage_img = f"{PUBG_IMAGE_PATH_RELATIVE}example_damage.png"
    distance_img = f"{PUBG_IMAGE_PATH_RELATIVE}example_distance.png"
    df_path = f"{PUBG_DATA_PATH}df_"
    pubg_data = APIData.query.filter_by(api_name="pubg").first()

    if request.method == "GET":
        # Check if user generated stats this session
        if os.path.isfile(f"{PUBG_IMAGE_PATH}{session['id']}-current_distance.png"):
            # Graphs found
            kills_img = f"{PUBG_IMAGE_PATH_RELATIVE}{session['id']}-current_kills.png"
            damage_img = f"{PUBG_IMAGE_PATH_RELATIVE}{session['id']}-current_damage.png"
            distance_img = f"{PUBG_IMAGE_PATH_RELATIVE}{session['id']}-current_distance.png"

        # No graphs generated yet so serve examples
        return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                               damage_img=damage_img, distance_img=distance_img, page="pubg")

    if pubg_form.validate_on_submit():
        name = pubg_form.name.data
        game_mode = pubg_form.game_mode.data + pubg_form.perspective.data
        save_mode = game_mode.replace("-", "_")

        # Check for existing data before contacting API
        if os.path.exists(f"{df_path}{name}_{save_mode}.csv"):
            # User has been searched already so old DataFrame can be loaded
            kills_img, damage_img, distance_img = \
                load_old_pubg_data(df_path, name, game_mode, save_mode, session["id"])

            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        # No data found - contact API
        # Check API availability
        if (pubg_data.last_used + 60) > time.time():
            # API used in last 60 seconds
            flash_message = get_pubg_cooldown_message()
            flash(flash_message)
            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        # Codes mentioned below are described in the called functions docstring
        id_code, id_response = get_player_id(name)

        if not id_code == 200:
            # Unsuccessful request
            if id_code == 429:
                # Request limit reached
                update_pubg_api_data()

            # Get flash() message corresponding to the request status code
            flash_message = id_response
            flash(flash_message)
            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        player_id = id_response
        # Player ID retrieved successfully
        seasons_code, seasons_response = get_seasons()
        if not seasons_code == 200:
            # Unsuccessful request
            # Get flash() message corresponding to the request status code
            flash_message = seasons_response
            if seasons_code == 429:
                # Request limit reached
                update_pubg_api_data()

            flash(flash_message)
            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        valid_seasons = seasons_response
        # Valid seasons retrieved successfully
        stats_code, stats_response = get_all_season_stats(player_id, valid_seasons, game_mode)
        if not stats_code == 200:
            # Unsuccessful request
            # Get flash() message corresponding to the request status code
            flash_message = stats_response
            if stats_code == 429:
                # Request limit reached
                update_pubg_api_data()

            flash(flash_message)
            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        player_stats = stats_response
        # Player stats retrieved successfully
        if len(player_stats[0]) < 2:
            # Check if player was active in at least 2 seasons, else draw no graph
            flash("Player has insufficient stats to generate graph")
            return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                                   damage_img=damage_img, distance_img=distance_img,
                                   scrollToAnchor="graph-section", page="pubg")

        # Success
        new_df = create_dataframe(player_stats, name, save_mode)
        kills_img = create_kills_bar(new_df, name, game_mode, session["id"])
        damage_img = create_damage_bar(new_df, name, game_mode, session["id"])
        distance_img = create_distance_bar(new_df, name, game_mode, session["id"])
        # Update api db with timestamp
        update_pubg_api_data()
        return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                               damage_img=damage_img, distance_img=distance_img,
                               scrollToAnchor="graph-section", page="pubg")

    # Form not validated
    return render_template("/api/pubg.html", pubg_form=pubg_form, kills_img=kills_img,
                           damage_img=damage_img, distance_img=distance_img,
                           scrollToAnchor="graph-section", page="pubg")


# ------------------------------------------------------------ #
# ------------------------- CPI ------------------------------ #
@apis.route("/api/cpi", methods=["POST", "GET"])
@login_required
def cpi():
    cpi_form = SearchCPIForm()

    if request.method == "GET":
        # Check to see if user has generated graphs in the past
        # If so, get the relative paths
        total_graphs = count_cpi_graphs(session["id"])
        graph_paths = get_cpi_graph_paths(session["id"],
                                          total_graphs)

        return render_template("/api/cpi.html",
                               cpi_form=cpi_form,
                               page="cpi",
                               total_graphs=total_graphs,
                               graph_paths=graph_paths)

    if not cpi_form.validate_on_submit():
        # Form is not validated
        # Check to see if user has generated graphs in the past
        # If so, get the relative paths
        total_graphs = count_cpi_graphs(session["id"])
        graph_paths = get_cpi_graph_paths(session["id"],
                                          total_graphs)

        return render_template("/api/cpi.html",
                               cpi_form=cpi_form,
                               page="cpi",
                               total_graphs=total_graphs,
                               graph_paths=graph_paths)

    # Form is validated
    # Check if dates are chronological
    if not cpi_form.start_year.data < cpi_form.stop_year.data:
        # Start and end date not chronological
        flash("Selected years not valid")
        # Check to see if user has generated graphs in the past
        # If so, get the relative paths
        total_graphs = count_cpi_graphs(session["id"])
        graph_paths = get_cpi_graph_paths(session["id"],
                                          total_graphs)
        return render_template("/api/cpi.html",
                               cpi_form=cpi_form,
                               page="cpi",
                               total_graphs=total_graphs,
                               graph_paths=graph_paths)

    # Submission accepted
    # Get list of selected categories
    categories = get_cpi_categories(cpi_form.data)

    # Check input
    if not len(categories) > 0:
        # Form is submitted without and selections
        # Check to see if user has generated graphs in the past
        # If so, get the relative paths
        flash("PLease select at lease 1 category")
        total_graphs = count_cpi_graphs(session["id"])
        graph_paths = get_cpi_graph_paths(session["id"],
                                          total_graphs)

        return render_template("/api/cpi.html",
                               cpi_form=cpi_form,
                               page="cpi",
                               total_graphs=total_graphs,
                               graph_paths=graph_paths)

    # Rename old graphs recursively & create new graph
    check_user_folder_exists(session["id"])
    rename_graphs(session["id"])
    save_cpi_graph(categories=categories,
                   start_date=cpi_form.start_year.data,
                   end_date=cpi_form.stop_year.data,
                   user_id=session["id"])

    # Check to see how many graphs user has generated in the past
    # If so, get the relative paths
    total_graphs = count_cpi_graphs(session["id"])
    graph_paths = get_cpi_graph_paths(session["id"],
                                      total_graphs)

    return render_template("/api/cpi.html",
                           cpi_form=cpi_form,
                           page="cpi",
                           total_graphs=total_graphs,
                           graph_paths=graph_paths)
