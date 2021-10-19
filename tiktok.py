from TikTokApi import TikTokApi
from selenium import webdriver
import requests, time, sys, os, re, math, random
from random import randrange
from os.path import exists
from shutil import move
from os import remove

usernames = ['tiktok'] # ADD USERNAMES HERE
max_error_count = 10
completed_file_path = "completed_users.txt"
error_file_path = "error_count.txt"
max_age_videos = 86400 # 86400 seconds = 24 hours

def resetCurrentErrorCount():
    with open(error_file_path, 'w') as f:
        f.write('0' + " " + str(time.time()))
        f.close()

def readCurrentErrorCount():
    try:
        fp = open(error_file_path)
    except IOError: # If not exists, create the file
        fp = open(error_file_path, 'w+')
    with open(error_file_path, 'r') as f:
        for line in f:
            words = line.split()
            if (time.time() - float(words[1]) > 1800): # 1800 secs = 30 mins
                resetCurrentErrorCount()
                return 0
            else:
                return int(words[0])
    return 0

def incrementCurrentErrorCount():
    current_error_count = readCurrentErrorCount()
    with open(error_file_path, 'w') as f:
        f.write(str(current_error_count + 1) + " " + str(time.time()))
        f.close()

def readtime(name):
    try:
        fp = open(completed_file_path)
    except IOError: # If not exists, create the file
        fp = open(completed_file_path, 'w+')
    with open(completed_file_path, 'r') as f:
        for line in f:
            words = line.split()
            if (words[0] == name):
                return words[1]
    return ''

def savetime(name):
    if (readtime(name) == ''):
        with open(completed_file_path, 'a') as f:
            string_to_write = name + " " + str(time.time()) + "\n"
            f.seek(0,0)
            f.write(string_to_write)
            f.close()
    else:
        fin = open(completed_file_path)
        fout = open("temp.txt", "wt")
        for line in fin:
            fout.write(line.replace(readtime(name), str(time.time())))
        fin.close()
        fout.close()
        remove(completed_file_path)
        move('temp.txt', completed_file_path)

def timediff(name):
    ctime = readtime(name)
    if (ctime == ''):
        return float('inf')
    else:
        return time.time() - float(ctime)

def main():
    random.shuffle(usernames)
    api = TikTokApi()
    tiktok_limit = 0
    for username in usernames:
        if(not os.path.exists(username)): 
            os.mkdir(username)
        print("start downloading videos for " + username)
        if (timediff(username) > max_age_videos):
            try:
                user_videos_downloaded_count = 0
                user_videos = api.by_username(username, count=2000)
                if len(user_videos) == 0:
                    print("No videos found by", username)
                else:
                    print(len(user_videos), "videos found.")
                    options = webdriver.ChromeOptions()
                    options.add_argument('headless')
                    chromedriver_path = os.path.abspath(os.getcwd()) + '/chromedriver'
                    browser = webdriver.Chrome(chromedriver_path, options=options)
                    browser.set_script_timeout(36000)
                    for tiktok in user_videos:
                        tiktok_id = tiktok["id"]
                        file_path = username + "/"+ tiktok_id + ".mp4"
                        if (exists(file_path)):
                            print(tiktok_id + ".mp4 is already downloaded...")
                        else:
                            print("attempting to download id: " + tiktok_id)
                            browser.get('https://godownloader.com/tiktok/' + tiktok_id)
                            seconds_to_sleep = 25 + randrange(10)
                            print("now waiting " + str(seconds_to_sleep) + " secs for the page to load")
                            time.sleep(seconds_to_sleep)
                            result = browser.page_source
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
                                raise Exception('url not found!')
                            else:
                                final_url += '&hd=1' # make sure hd version is downloaded

                            print("the current url for downloading is:")
                            print(final_url)
                            r = requests.get(final_url)
                            with open(file_path, 'wb') as f:
                                f.write(r.content)
                            print("id " + tiktok_id + " was downloaded successfully")
                            user_videos_downloaded_count = user_videos_downloaded_count + 1
                            seconds_to_sleep = 2 + randrange(4)
                            print('now waiting ' + str(seconds_to_sleep) + ' secs, to avoid godownloader from refusing the next connection')
                            time.sleep(seconds_to_sleep)
                    print("videos for " + username + " are all done!")
                    savetime(username) # saves information about completed profiles (with date)
                    tiktok_limit = tiktok_limit + 1
                    if (tiktok_limit < len(usernames)):
                        if tiktok_limit % 2 == 0:
                            seconds_to_sleep = 100 + randrange(45) - (user_videos_downloaded_count * 10)
                            if (seconds_to_sleep > 0):
                                print('now waiting ' + str(seconds_to_sleep) + ' secs, to avoid tiktok from refusing the next connection')
                                time.sleep(seconds_to_sleep)
                    else:
                        print('Everything is downloaded. Goodbye!')
                    browser.quit()
            except Exception as e:
                print(e)
                if 'browser' in locals():
                    browser.quit()
                global max_error_count
                if (max_error_count == readCurrentErrorCount()):
                    sys.exit("Terminating the script, because too many errors occured!")
                else:
                    incrementCurrentErrorCount()
                    seconds_to_sleep = 5 + randrange(30)
                    print("Restarting the script in " + str(seconds_to_sleep) + " secs, because an error occured!")
                    time.sleep(seconds_to_sleep)
                    os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            print('skipping this username, because it was downloaded not too long ago!')
    print('All done!')

main()
