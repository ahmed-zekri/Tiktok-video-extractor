import requests as requests
from TikTokApi import TikTokApi
import tkinter as tk
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

hashtag_input = None
like_input = None
browser = None
info = None


def download_video(url, count, last_index=False):
    browser.get('https://snaptik.app/')
    text_url = browser.find_element_by_id('url')
    info.config(text=f"Downloading video number {str(count)} please wait ...")
    time.sleep(5)
    text_url.send_keys(url)
    time.sleep(1)
    text_submit = browser.find_element_by_id('send')
    text_submit.click()
    time.sleep(5)

    browser.find_element_by_xpath('//*[@title="Download Server 02"]').click()
    time.sleep(5)

    try:

        browser.find_element_by_id('dismiss-button').click()

    except NoSuchElementException:
        pass
    try:

        browser.switch_to_frame(browser.find_element_by_id('ad_iframe'))
        browser.find_element_by_id('dismiss-button').click()
        browser.switch_to_default_content()

    except NoSuchElementException:
        pass

    time.sleep(2)

    if last_index:
        info.config(text=f"Downloading Finished {str(count)}")


def extract_videos():
    global info
    info.config(text=f"Exporting videos info to a txt file, this will take a moment")
    videos_list = []
    hashtags_list = hashtag_input.get().split(',')
    # Hashtag_search
    for hashtag in hashtags_list:

        videos = api.byHashtag(hashtag, count=100)
        if len(videos) == 0:
            return
            # loop through the videos
        with open('ticktock.txt', 'w', encoding="utf-8") as opened_file:
            for video in videos:
                if video['stats']['diggCount'] > int(like_input.get()):
                    opened_file.write(
                        f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}  ; Author: {video["author"]["nickname"]} \n')
                    videos_list.append(
                        f'https://www.tiktok.com/@{video["author"]["uniqueId"]}/video/{video["video"]["id"]}')
    info.config(text=f"Videos infos exported to ticktock.txt downloading videos now ")
    for count, video_item in enumerate(videos_list):
        download_video(video_item, count, last_index=(count == len(videos_list) - 1))


def tkinter_create_window():
    global hashtag_input
    global like_input
    global info
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
    # Extract data button
    button = tk.Button(text="Extract videos", command=extract_videos)
    info = tk.Label(text="", fg='#0000CD')
    # error = tk.Label(text="", fg='#f00')
    # info2 = tk.Label(text="", fg='#008000')
    # include widgets in ui
    hashtags_label.pack()
    hashtag_input.pack()
    likes_label.pack()
    like_input.pack()
    button.pack(pady=10, side=tk.TOP)
    # error.pack(pady=5, side=tk.TOP)
    # info2.pack(pady=7, side=tk.TOP)
    info.pack(pady=5, side=tk.TOP)

    window.resizable(False, False)
    window.attributes("-topmost", True)
    window.mainloop()


def initialize_selinuim():
    global browser
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)  # custom location
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', '/tmp')
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                           'video/mp4,text/plain,text/csv,application/csv,application/download,application/octet-stream')
    browser = webdriver.Firefox(firefox_profile=profile, executable_path=r'geckodriver.exe')


if __name__ == '__main__':
    # Initialize selenium
    initialize_selinuim()

    # initialize tiktok api
    api = TikTokApi.get_instance()

    # Create Ui
    tkinter_create_window()
