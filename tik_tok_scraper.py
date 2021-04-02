import concurrent.futures
import os
import time
import tkinter as tk
from datetime import datetime
from random import randint
from tkinter.ttk import Radiobutton
import sys
import dropbox as dropbox
from dropbox.files import WriteMode
from TikTokApi import TikTokApi
import subprocess

hashtag_input = None
like_input = None
browser = None
days_input = None
service = None
info = None
videos_downloaded = 0
method_radio_button = None

maximum_videos_to_extract = 18
step_increment = 4
max_retries = 2
proxy_index = 0


def get_my_proxy(proxy_arg):
    """ Static method to get proxy
    """

    http_proxy = proxy_arg
    https_proxy = proxy_arg

    proxyDict = {
        "http": http_proxy,
        "https": https_proxy

    }
    return proxyDict


def upload_video(file, proxy_index, proxies):
    print(f'[Upload] Uploading {file.split("/")[1]} to dropbox using proxy {proxies[proxy_index]} please wait')

    try:
        mysesh = dropbox.create_session(1, get_my_proxy(proxies[proxy_index]))

        d = dropbox.Dropbox(
            'lxvoM1hkhw0AAAAAAAAAAajf03WF1bSYiz9Mm84B88XlhvniePTg3UDkjnuTCfct', session=mysesh)
        with open(file, "rb") as f:
            # upload gives you metadata about the file
            # we want to overwite any previous version of the file
            print(f'Attempting to upload file {file}')
            d.files_upload(f.read(), f'/{file}', mode=dropbox.files.WriteMode.overwrite)
            print(f'File {file.split("/")[1]} uploaded successfully')
            # break
    except Exception as e:
        print(f'Upload failed reason {e}')


def timer(time_count, current_time):
    printed_time = 0
    while True:
        if printed_time != int(time.perf_counter() - current_time):
            printed_time = int(time.perf_counter() - current_time)
            print(printed_time)

        if printed_time >= time_count:
            break


def download_video(download_proxies, download_proxy_index, url, count,
                   name=None, for_you=False):
    if for_you:
        file_name = f'For_you/{name}.mp4'
    else:
        file_name = f'{name.split("_")[0]}/{name}.mp4'

    if not os.path.exists(f'{name.split("_")[0]}'):
        os.makedirs(f'{name.split("_")[0]}')
    error = False
    with open(f'{file_name}', "wb") as f:

        # while True:
        try:
            api = TikTokApi.get_instance(use_test_endpoints=True,
                                         proxy=download_proxies[download_proxy_index])
            print(f'Attempting to download file {file_name} using proxy {download_proxies[download_proxy_index]} ')
            f.write(api.get_video_by_url(url, return_bytes=1,
                                         custom_verifyFp='verify_kmzg9occ_RHip8NdE_UivQ_4HrX_8Ut3_YHzx2PpD7Rzl'))
            print(f'File {file_name} downloaded successfully')
            api.clean_up()
            # break
        except Exception as e:
            error = True
            print(f'Download failed reason:{str(e)}')

    if error:
        try:
            os.remove(file_name)
            print('Failed file removed')
        except Exception as e:
            print(f'Unable to delete file {str(e)}')
    else:

        try:
            file_size = float(os.path.getsize(file_name))

            if float(file_size) <= 1000:
                os.remove(file_name)
                print('Corrupted file removed')
            else:
                upload_video(file_name, download_proxy_index, download_proxies)
        except Exception as e:
            print(f'Failed removing corrupted file {str(e)}')


def extract_videos(from_shell=False):
    # Number of retries when error encountered
    retries = 1
    if not from_shell:
        if method_radio_button.get() == 1:
            print('selected hashtag option')
            for_you = False
        else:
            print('selected for you option')
            for_you = True
    else:
        for_you = False

    global info
    global days_input
    days_allowed = 10000
    try:
        if not from_shell:
            days_allowed = int(days_input.get())
        else:
            days_allowed = int(sys.argv[2])
    except:
        pass
    # info.config(text=f"Exporting videos info to a txt file, this will take a moment")
    if not from_shell:
        if method_radio_button.get() == 1:
            hashtags_list = hashtag_input.get().split(',')
            for _, hashtag in enumerate(hashtags_list):
                if _ > 0:
                    subprocess.Popen([
                        'python', 'tik_tok_scraper.py', like_input.get(), str(days_allowed), hashtag],
                        shell=True)
        else:
            hashtags_list = ['forYou']
    else:
        hashtags_list = [sys.argv[3]]

    # Hashtag_search
    for _, hashtag in enumerate(hashtags_list):
        videos_list = []
        hashtag = hashtag.strip()
        one_hashtag_videos = []
        time.sleep(3)
        if from_shell:
            print(
                f'extracting videos with hashtag \"{hashtag}\" this will take a couple of minutes')
        else:
            if not for_you:
                print(
                    f'extracting videos with hashtag \"{hashtag}\" this will take a couple of minutes')
            else:
                print(f'Extracting videos for you please wait ')

        tiktok_hang = False
        global proxy_index

        # Hashtag section

        if not for_you:

            for _ in range(int(maximum_videos_to_extract / step_increment) + 1):
                hashtag_ended = False
                # loading Step increment value failed section
                if tiktok_hang:

                    print(
                        f'Can\'t extract {step_increment} videos attempting to load less')

                    while True:
                        try:

                            api = TikTokApi.get_instance(use_test_endpoints=True,
                                                         proxy=proxies[proxy_index])
                            previous_videos_length = len(one_hashtag_videos)
                            one_hashtag_videos.extend(api.byHashtag(hashtag=hashtag, offset=len(one_hashtag_videos)))

                            proxy_index += 1
                            if proxy_index == len(proxies):
                                proxy_index = 0
                            print(
                                f'Loaded  {str(len(one_hashtag_videos) - previous_videos_length)} videos using proxy {proxies[proxy_index]}, proceeding')
                        except:

                            if _ == len(hashtags_list) - 1:
                                print('Last try failed, finished extracting videos')
                            else:
                                print('Last try failed, proceeding to next hashtag')
                            hashtag_ended = True
                            break

                if hashtag_ended:
                    break
                # Loading with step_increment value
                while True:

                    try:
                        print(
                            f'Launching new request to load {step_increment} videos from position {len(one_hashtag_videos)} with proxy {proxies[proxy_index]} ')
                        api = TikTokApi.get_instance(use_test_endpoints=True,
                                                     proxy=proxies[proxy_index])
                        one_hashtag_videos.extend(
                            api.byHashtag(hashtag=hashtag, offset=len(one_hashtag_videos), count=step_increment))

                        proxy_index += 1
                        if proxy_index == len(proxies):
                            proxy_index = 0
                        print(f'Extracted {str(len(one_hashtag_videos))} videos for hashtag {hashtag}')
                        break
                    except Exception as e:

                        # Load failed trying for max reties time then forward to tiktok hang section
                        print(f'Error retrying {str(retries)} of {str(max_retries)} reason {str(e)}')
                        proxy_index += 1
                        if proxy_index == len(proxies):
                            proxy_index = 0

                        if retries == max_retries:
                            print(f'Tried {retries} times, exiting now')
                            tiktok_hang = True
                            break
                        retries += 1

                        time.sleep(5)


        # For you section
        else:

            while True:
                try:
                    print(f'Trying with proxy {proxies[proxy_index]}')
                    api = TikTokApi.get_instance(use_test_endpoints=True,
                                                 proxy=proxies[proxy_index])
                    one_hashtag_videos = api.trending()
                    break
                except Exception as e:
                    print(f'Failed reason {e} retrying...')
                    proxy_index += 1
                    if proxy_index == len(proxies):
                        proxy_index = 0

        # print(f'_____Extracted a total of {len(one_hashtag_videos)} for hashtag {hashtag} applying your filters now')
        time.sleep(2)

        # Continue if no video matching the hashtag was found
        if len(one_hashtag_videos) == 0:
            print(f'No videos extracted from hashtags {hashtag}')
            continue

        # Applying filters and download videos
        with concurrent.futures.ProcessPoolExecutor() as executor:

            counter = 0
            if from_shell:
                like_min = sys.argv[1]
            else:
                like_min = like_input.get()
            urls = []
            for video in one_hashtag_videos:
                days_since_creation = (datetime.now() - datetime.fromtimestamp(video['createTime'])).days
                if int(days_since_creation <= days_allowed):
                    if float(video['stats']['diggCount']) > float(like_min):
                        counter += 1
                        name = f'{hashtag}_{video["author"]["uniqueId"]}_{video["video"]["id"]}'

                        url = f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}'
                        if urls.__contains__(url):
                            continue
                        urls.append(url)
                        time.sleep(randint(1, 5))
                        proxy_index += 1
                        if proxy_index == len(proxies):
                            proxy_index = 0
                        download_video(proxies, proxy_index,
                                       url, counter,
                                       name=name,
                                       for_you=for_you)

                        if for_you:
                            file_name = f'For_you/{name}.mp4'
                        else:
                            file_name = f'{name.split("_")[0]}/{name}.mp4'
                        videos_list.append(file_name)

        # Uploading downloaded videos
        # for video in videos_list:
        #     time.sleep(randint(1, 5))
        #     upload_video(video, proxy_index)
        #     proxy_index += 1
        #     if proxy_index == len(proxies):
        #         proxy_index = 0

        break


def tkinter_create_window():
    global days_input
    global hashtag_input
    global like_input
    global info
    global method_radio_button
    window = tk.Tk()
    # window initialisation
    window.geometry("350x200")
    window.winfo_toplevel().title("Tiktok scraper")

    # Hashtags label
    hashtags_label = tk.Label(text="Enter hashtags separated by commas like this ,")
    # Hashtag input
    hashtag_input = tk.Entry()
    # Minimum likes label
    likes_label = tk.Label(text="Minimum likes")
    # Minimum likes Input
    like_input = tk.Entry()
    # Minimum days label
    days_label = tk.Label(text="Specify the number of days allowed since video uploaded")
    # Minimum days Input
    days_input = tk.Entry()
    method_radio_button = tk.IntVar()
    for_you = Radiobutton(window, text="For you", variable=method_radio_button, value=2,
                          )

    # Extract data button
    button = tk.Button(text="Extract videos", command=extract_videos)
    info = tk.Label(text="", fg='#0000CD')

    hashtags_label.pack()
    hashtag_input.pack()
    likes_label.pack()
    like_input.pack()
    days_label.pack()
    days_input.pack()

    recent_days = Radiobutton(window, text="By Hashtags", variable=method_radio_button, value=1,
                              )

    recent_days.pack()
    for_you.pack()
    button.pack(pady=10, side=tk.TOP)

    window.resizable(False, False)
    window.attributes("-topmost", True)
    method_radio_button.set(1)
    window.mainloop()


if __name__ == '__main__':

    proxies = ['http://ghulrcuk:bad3428050@104.140.83.219:36505', 'http://ghulrcuk:bad3428050@154.16.61.23:36505',
               'http://ghulrcuk:bad3428050@23.108.47.207', 'http://ghulrcuk:bad3428050@198.46.174.117:36505',
               'http://ghulrcuk:bad3428050@107.172.246.184', 'http://ghulrcuk:bad3428050@198.46.176.105',
               'http://ghulrcuk:bad3428050@154.16.61.56:36505', 'http://ghulrcuk:bad3428050@107.172.225.52',
               'http://ghulrcuk:bad3428050@192.210.194.137:36505', 'http://ghulrcuk:bad3428050@154.16.61.79',

               'http://rcrvtkug:21d0ec259e@192.3.240.187:36505', 'http://rcrvtkug:21d0ec259e@107.174.231.174:36505',
               'http://rcrvtkug:21d0ec259e@107.174.249.78:36505', 'http://rcrvtkug:21d0ec259e@107.174.151.237:36505',
               'http://rcrvtkug:21d0ec259e@107.174.5.101:36505',
               'http://rcrvtkug:21d0ec259e@107.175.90.3:36505',
               'http://rcrvtkug:21d0ec259e@107.174.151.232:36505',
               'http://rcrvtkug:21d0ec259e@107.175.129.23:36505',
               'http://rcrvtkug:21d0ec259e@107.174.5.114:36505',
               'http://rcrvtkug:21d0ec259e@107.175.90.101:36505',

               ]

    proxy_index = randint(0, len(proxies) - 1)
    if len(sys.argv) > 3:

        extract_videos(True)
    else:
        tkinter_create_window()
