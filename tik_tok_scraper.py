import concurrent.futures
import os
import subprocess
import sys
import time
import tkinter as tk
from datetime import datetime
from random import randint
from tkinter.ttk import Radiobutton
import concurrent.futures

custom_verify = 'verify_kmzg9occ_RHip8NdE_UivQ_4HrX_8Ut3_YHzx2PpD7Rzl'
hashtag_input = None
like_input = None
browser = None
days_input = None
service = None
info = None
videos_downloaded = 0
method_radio_button = None

maximum_videos_to_extract = 5200
step_increment = 1800
max_retries = 2
proxy_index = 0
blocked_user_input = None


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


def upload_video(file):
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


def download_video(url,
                   name=None):
    file_name = f'{name.split("_")[0]}/{name}.mp4'

    if not os.path.exists(f'{name.split("_")[0]}'):
        os.makedirs(f'{name.split("_")[0]}')
    hang_index = -1
    error_index = proxy_index
    error = False
    while True:
        try:
            print(f'Downloading using proxy {proxies[error_index]}')
            subprocess.run([
                'youtube-dl.exe', '--proxy', {proxies[error_index]}, url, '--output', f'{file_name}'],
                check=True, )

            print(f'File {file_name} downloaded successfully')
            break

        except Exception as e:
            if hang_index == -1:
                hang_index = proxy_index
            error_index += 1
            print(f'Retrying with another proxy reason {e}')
            if error_index == len(proxies):
                error_index = 0
            if error_index == hang_index:
                error = True
                break

    if not error:
        upload_video(file_name)


def extract_videos(from_shell=False):
    # Number of retries when error encountered
    retries = 1

    global info
    global days_input
    days_allowed = 10000

    if not from_shell:
        blocked_user = blocked_user_input.get()
        try:
            like_min = float(like_input.get())

        except:
            like_min = 0
        try:
            days_allowed = int(days_input.get())
        except:
            pass
        if method_radio_button.get() == 1:
            print('selected hashtag option')
            for_you = False
            hashtags_list = hashtag_input.get().split(',')
            for _, hashtag in enumerate(hashtags_list):
                if _ > 0:
                    time.sleep(5)
                    subprocess.Popen([
                        'python', 'tik_tok_scraper.py', like_input.get(), str(days_allowed), hashtag, blocked_user,
                        str(_)],
                        shell=True)
            hashtag = hashtags_list[0]
        else:
            print('selected for you option')
            for_you = True
            hashtag = 'forYou'
    else:
        for_you = False
        try:
            like_min = float(sys.argv[1])
        except:
            like_min = 0
        days_allowed = int(sys.argv[2])
        hashtag = sys.argv[3]
        blocked_user = sys.argv[len(sys.argv) - 2]

    # Hashtag_search

    videos_list = []
    hashtag = hashtag.strip()
    all_videos = []
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
                    previous_videos_length = len(all_videos)
                    if for_you:
                        all_videos.extend(api.by_trending(offset=len(all_videos),
                                                          custom_verifyFp=custom_verify))
                    else:
                        all_videos.extend(api.by_hashtag(hashtag=hashtag, offset=len(all_videos),
                                                         custom_verifyFp=custom_verify))

                    # api.clean_up()
                    proxy_index += 1
                    if proxy_index == len(proxies):
                        proxy_index = 0
                    print(
                        f'Loaded  {str(len(all_videos) - previous_videos_length)} videos using proxy {proxies[proxy_index]}, proceeding')
                except Exception as e:
                    print(f'Extracting end as last extraction failed, reason {e}')
                    hashtag_ended = True
                    break

        if hashtag_ended:
            break
        # Loading with step_increment value
        while True:

            try:
                print(
                    f'Launching new request to load {step_increment} videos from position {len(all_videos)} with proxy {proxies[proxy_index]} ')
                api = TikTokApi.get_instance(use_test_endpoints=True,
                                             proxy=proxies[proxy_index])

                if for_you:
                    all_videos.extend(api.trending(offset=len(all_videos), count=step_increment,
                                                   custom_verifyFp=custom_verify))
                else:
                    all_videos.extend(api.byHashtag(hashtag=hashtag, offset=len(all_videos), count=step_increment,
                                                    custom_verifyFp=custom_verify))
                # api.clean_up()
                proxy_index += 1
                if proxy_index == len(proxies):
                    proxy_index = 0
                print(f'Extracted {str(len(all_videos))} videos for hashtag {hashtag}')
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

    time.sleep(2)

    # Continue if no video matching the hashtag was found
    if len(all_videos) == 0:
        print(f'No videos extracted from hashtags {hashtag}')
        return

    # Applying filters and download videos
    with concurrent.futures.ProcessPoolExecutor() as executor:

        counter = 0

        for video in all_videos:
            if video["author"]["uniqueId"] == blocked_user:
                print(f'Blocked user {blocked_user} video detected, proceeding')
                continue
            days_since_creation = (datetime.now() - datetime.fromtimestamp(video['createTime'])).days
            if int(days_since_creation <= days_allowed):
                if float(video['stats']['diggCount']) > like_min:
                    counter += 1
                    name = f'{hashtag}_{video["author"]["uniqueId"]}_{video["video"]["id"]}'

                    url = f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}'

                    time.sleep(randint(1, 5))
                    proxy_index += 1
                    if proxy_index == len(proxies):
                        proxy_index = 0
                    download_video(url, name=name)

                    file_name = f'{hashtag}/{name}.mp4'
                    videos_list.append(file_name)

    if for_you:
        extract_videos()


def tkinter_create_window():
    global days_input
    global hashtag_input
    global like_input
    global info
    global method_radio_button
    global blocked_user_input
    window = tk.Tk()
    # window initialisation
    window.geometry("350x250")
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
    # Blocked user label
    blocked_user_label = tk.Label(text="Blocked user")
    # Blocked user input
    blocked_user_input = tk.Entry()
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

    by_hashtags = Radiobutton(window, text="By Hashtags", variable=method_radio_button, value=1,
                              )
    blocked_user_label.pack()
    blocked_user_input.pack()
    by_hashtags.pack()
    for_you.pack()
    button.pack(pady=10, side=tk.TOP)

    window.resizable(False, False)
    window.attributes("-topmost", True)
    method_radio_button.set(1)
    window.mainloop()


def print_progress():
    dots = 0
    while not installation_finished:
        if dots == 0:
            printed_dot = ''
        elif dots == 1:
            printed_dot = '.'
        elif dots == 2:
            printed_dot = '..'
        else:
            printed_dot = '...'

        print(f'\rinstalling/upgrading dependencies, this can take minutes on the first run {printed_dot}', end='',
              flush=True)
        dots += 1
        if dots == 4:
            dots = 0
        time.sleep(0.5)
    print('\r', end='', flush=True)


if __name__ == '__main__':
    installation_finished = False
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(print_progress)
        subprocess.run(['pip', 'install', '--upgrade', 'dropbox'], capture_output=True)
        subprocess.run(['pip', 'install', '--upgrade', 'TikTokApi'], capture_output=True)
        subprocess.run(['python ', '-m', 'playwright', 'install'], capture_output=True)
        installation_finished = True
    import dropbox as dropbox
    from TikTokApi import TikTokApi
    from dropbox.files import WriteMode

    proxies = [

        'http://umhnxdxl:db70460384@23.94.177.150:36505', 'http://umhnxdxl:db70460384@107.174.143.220:36505',
        'http://umhnxdxl:db70460384@172.245.103.125:36505', 'http://umhnxdxl:db70460384@107.174.139.141:36505',
        'http://umhnxdxl:db70460384@192.3.126.142:36505', 'http://umhnxdxl:db70460384@107.174.143.231:36505',
        'http://umhnxdxl:db70460384@192.3.126.146:36505', 'http://umhnxdxl:db70460384@198.23.169.86:36505',
        'http://umhnxdxl:db70460384@23.94.177.130:36505', 'http://umhnxdxl:db70460384@23.94.177.151:36505',

        'http://ghulrcuk:bad3428050@192.227.241.105:36505', 'http://rcrvtkug:21d0ec259e@23.94.75.149:36505',
        'http://rcrvtkug:21d0ec259e@198.46.174.110:36505', 'http://rcrvtkug:21d0ec259e@107.172.65.205:36505',
        'http://ghulrcuk:bad3428050@107.172.227.249:36505', 'http://ghulrcuk:bad3428050@171.22.121.42:36505',
        'http://ghulrcuk:bad3428050@23.94.32.57:36505', 'http://ghulrcuk:bad3428050@23.94.32.28:36505',
        'http://ghulrcuk:bad3428050@198.46.201.164:36505',

        'http://ghulrcuk:bad3428050@198.12.66.196:36505', 'http://rcrvtkug:21d0ec259e@198.46.203.46:36505',
        'http://rcrvtkug:21d0ec259e@192.227.253.235:36505', 'http://ghulrcuk:bad3428050@171.22.121.131:36505',
        'http://rcrvtkug:21d0ec259e@107.172.71.71:36505',

        'http://rcrvtkug:21d0ec259e@192.3.147.213:36505',
        'http://ghulrcuk:bad3428050@172.245.103.97:36505',
        'http://rcrvtkug:21d0ec259e@198.46.176.68:36505',
        'http://rcrvtkug:21d0ec259e@172.245.242.237:36505'

    ]

    # executing from shell
    if len(sys.argv) > 3:
        proxy_index = int(sys.argv[len(sys.argv) - 1])
        if proxy_index == len(proxies) - 1:
            proxy_index = 0
        extract_videos(True)
    # executing from GUI
    else:
        proxy_index = 0
        tkinter_create_window()
