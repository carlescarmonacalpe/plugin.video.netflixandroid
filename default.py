# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Kodi Add-on for netflix integration in AndroidTV
# Version 1.0.0
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Based on code & idea of pelisalacarta/plugintools scripts
#------------------------------------------------------------
# Changelog:
# 1.0.0
# - First release
#---------------------------------------------------------------------------

import os
import sys
import plugintools
import json
import math
import xbmc
import xbmcgui
import xbmcplugin
import HTMLParser
parser = HTMLParser.HTMLParser()

# Global variables
dir_path_tv_shows = "/storage/sdcard1/Netflix/Series/"
dir_path_movies = "/storage/sdcard1/Netflix/Pelis/"

# Dialog process
def dialog_progress(heading, line1, line2=" ", line3=" "):
    dialog = xbmcgui.DialogProgress()
    dialog.create(heading, line1, line2, line3)
    return dialog


def dialog_progress_bg(heading, message=""):
    try:
        dialog = xbmcgui.DialogProgressBG()
        dialog.create(heading, message)
        return dialog
    except:
        return dialog_progress(heading, message)


# Entry point
def run():
    """
    If code parameter is not passed, the plugin scrapes all the content of the Spanish Netflix provider an create
    an strm file for each content.
    """
    plugintools.log("NetflixAndroid.run")

    # Get params
    params = plugintools.get_params()

    if params.get("code") is not None:
        play(params.get("code"))
    else:
        update_library()

    plugintools.close_item_list()


# Main menu
def update_library():
    plugintools.log("NetflixAndroid.update_library")

    # TvShows scraper
    num_tv_shows = tvshows_scraper()

    # Movies scraper
    num_movies = movies_scraper()

    plugintools.message("Total Scraped Items", "Movies:"+num_movies, "TvShows:"+num_tv_shows)


def tvshows_scraper():
    """
    Scrapes the tv shows from netflix that are available in the Spain
    :return: Number of scrapped Tv shows.
    """

    # Scrapper TvShows
    headers = []
    headers.append(["referer", "http://unogs.com/video/"])
    source, headers2 = plugintools.read_body_and_headers(
        url="http://unogs.com/cgi-bin/nf.cgi?u=saruciope1a5l7snqcnhnt1085&q=-!1900,2016-!0,5-!0,10-!0,10-!Any-!Series-!Any-!Any-!I%20Don&t=ns&cl=270&st=adv&ob=Relevance&p=1&l=10000&inc=&ao=and",
        headers=headers)
    tvshows = json.loads(source)["ITEMS"]

    # Create dialog
    heading = 'Update library [TvShows] ...'
    p_dialog = dialog_progress_bg('NetflixGrab', heading)
    p_dialog.update(0, '')
    t = float(100) / len(tvshows)
    i = 0

    plugintools.log("Total TvShows Items:" + str(len(tvshows)))
    for tv_show in tvshows:

        # Get the name and id of the TV show.
        code = tv_show[0]
        name = parser.unescape(tv_show[1]).encode('utf-8').strip().replace("?","").replace(":","").replace("/","")

        # Update dialog.
        p_dialog.update(int(math.ceil((i + 1) * t)), heading,name + "[Id:" + str(code) + "]")

        plugintools.log("Tv_show_ID:" + str(code) + " Name:" + name)
        source, headers2 = plugintools.read_body_and_headers(
            url="http://unogs.com/cgi-bin/nf.cgi?u=saruciope1a5l7snqcnhnt1085&t=episodes&q=" + code,
            headers=headers)
        seasons = json.loads(source)["RESULTS"]

        if not os.path.exists(dir_path_tv_shows + name + "/"):
            os.mkdir(dir_path_tv_shows + name + "/")
        for season in seasons:
            episodes = season['episodes']
            for episode in episodes:
                num_temp = str(episode['episode'][1])
                num_episode = str(episode['episode'][2])
                episode_code = str(episode['episode'][0])
                with open(dir_path_tv_shows + name + "/" + num_temp + "x" + num_episode + ".strm", "w") as f:
                    f.write("plugin://plugin.video.netflixandroid/?code=" + str(episode_code))
        i = i + 1
    return i


def movies_scraper():
    """
    Scrapes the movies from netflix that are available in the Spain
    :return: Number of scraped movies.
    """

    # Scrapear TvShows
    headers = []
    headers.append(["referer", "http://unogs.com/video/"])
    source, headers2 = plugintools.read_body_and_headers(
        url="http://unogs.com/cgi-bin/nf.cgi?u=saruciope1a5l7snqcnhnt1085&q=-!1900,2016-!0,5-!0,10-!0,10-!Any-!Movie-!Any-!Any-!I%20Don&t=ns&cl=270&st=adv&ob=Relevance&p=1&l=10000&inc=&ao=and",
        headers=headers)
    movies = json.loads(source)["ITEMS"]

    # Dialog
    heading = 'Update library [Movies] ...'
    p_dialog = dialog_progress_bg('NetflixGrab', heading)
    p_dialog.update(0, '')
    t = float(100) / len(movies)
    i = 0

    plugintools.log("Total Movies Items:" + str(len(movies)))
    for movie in movies:
        # Get the name and id of the TVshow
        code = movie[0]
        name = parser.unescape(movie[1]).encode('utf-8').strip().replace("?","").replace(":","").replace("/","")

        #Dialog
        p_dialog.update(int(math.ceil((i + 1) * t)), heading,name + "[Id:" + str(code) + "]")
        with open(dir_path_movies + name + ".strm", "w") as f:
            f.write("plugin://plugin.video.netflixandroid/?code=" + str(code))
        plugintools.log("Movie_show_ID:" + str(code) + " Name:" + name)
        i = i + 1


def play(code):
    """
    Executes the Netflix application and play the media content with the specified code.
    :param code: Netflix media content code
    """
    # Play one image and stop the reproduction to continue the execution without any error
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True,
                              xbmcgui.ListItem(
                                  path=os.path.join(plugintools.get_runtime_path(), "resources", "subtitle.mp4")))

    xbmc.Player().stop()

    # Launch Netflix media from kodi
    cmd = "adb shell am start -c android.intent.category.LEANBACK_LAUNCHER -a android.intent.action.VIEW -d https://www.netflix.com/watch/"+ code +" -f 0x10808000 -e source 1 com.netflix.ninja/.MainActivity"
    os.system(cmd)

run()
