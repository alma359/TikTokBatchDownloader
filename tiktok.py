from TikTokApi import TikTokApi
from selenium import webdriver
import requests, time, sys, os, re, math, random
from random import randrange
from os.path import exists
from selenium.webdriver.firefox.options import Options
options = Options()
options.add_argument("--headless")

if __name__ == '__main__':
    usernames = ['tiktok']
    random.shuffle(usernames)
    api = TikTokApi()
    tiktok_limit = 0
    for username in usernames:
        if(not os.path.exists(username)): 
            os.mkdir(username)
        print("start downloading videos for " + username)
        try:
            a_user_video_downloaded = False
            user_videos = api.byUsername(username, count=2000)
            if len(user_videos) == 0:
                print("No videos found by", username)
            else:
                print(len(user_videos), "videos found.")
                browser = webdriver.Firefox(options=options)
                browser.set_script_timeout(36000)
                for tiktok in user_videos:
                    tiktok_id = tiktok["id"]
                    file_path = username + "/"+ tiktok_id + ".mp4"
                    if (exists(file_path)):
                        print("this file is already downloaded...")
                    else:
                        print("attempting to download id: " + tiktok_id)
                        browser.get('https://godownloader.com/tiktok/' + tiktok_id)
                        seconds_to_sleep = 35 + randrange(10)
                        print("now waiting " + str(seconds_to_sleep) + " secs for the page to load")
                        time.sleep(seconds_to_sleep)
                        result = browser.page_source
                        #print(result)
                        all_urls_found = re.findall(r'(https?://[^\s]+)', result)
                        final_url = ''
                        for url in all_urls_found:
                            if ('https://dl.godownloader.com/' in url):
                                if ('"' in url):
                                    final_url = url.split('"', 1)[0] # the split is used to remove the last " from the url
                                else:
                                    final_url = url
                                break

                        if final_url == '':
                            raise ValueError('url not found!')
                        print("the current url is:")
                        print(final_url)
                        r = requests.get(final_url)
                        with open(file_path, 'wb') as f:
                            f.write(r.content)
                        print("id " + tiktok_id + " was downloaded successfully")
                        a_user_video_downloaded = True
                print("videos for " + username + " are all done!")
                tiktok_limit = tiktok_limit + 1
                if tiktok_limit % 2 == 0:
                    if a_user_video_downloaded:
                        seconds_to_sleep = 10 + randrange(30)
                    else:
                        seconds_to_sleep = 120 + randrange(45)
                    print('now waiting ' + str(seconds_to_sleep) + ' secs, to avoid tiktok from refusing the next connection')
                    time.sleep(seconds_to_sleep)
                browser.quit()
        except Exception as e:
            print(e)
            if 'browser' in locals():
                browser.quit()
            sys.exit("Terminating the script, because an error occured!")
