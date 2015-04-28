#! /usr/bin/env python

# Many thanks to:
# 
# Nathan Henrie for this post on decrypting Chrome cookies: http://n8henrie.com/2014/05/decrypt-chrome-cookies-with-python/
# meska for mywt2myfp: https://github.com/meska
# The Chrome development team for developer console->network->right-click->copy as curl
#     and for using a sqlite cookie file for persistance
# Microsoft for developing IMO the best wrist-based tracker as of 2015-04-27
# MyFitnessPal for providing a great service, even though it is not cool to restrict access to their API

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import json
#import lxml.html
from mechanize import Browser
import os
from os.path import expanduser
import pickle
#import requests
import sqlite3
import time
import urllib

# Function to get rid of padding
def clean(x): 
    return x[:-ord(x[-1])]

def decrypt(encrypted_value):
    # Trim off the 'v10' that Chrome/ium prepends
    encrypted_value = encrypted_value[3:]

    # Default values used by both Chrome and Chromium in OSX and Linux
    salt = b'saltysalt'
    iv = b' ' * 16
    length = 16

    # On Mac, replace MY_PASS with your password from Keychain
    # On Linux, replace MY_PASS with 'peanuts'
    my_pass = ""
    my_pass = my_pass.encode('utf8')

    # 1003 on Mac, 1 on Linux
    iterations = 1003

    key = PBKDF2(my_pass, salt, length, iterations)
    cipher = AES.new(key, AES.MODE_CBC, IV=iv)

    decrypted = cipher.decrypt(encrypted_value)
    return clean(decrypted)

# TODO: currently this only works with chrome cookies on Mac
def get_cookies(host):
    cookie_str = ''
    # using Mac directory structure
    cookie_db = expanduser('~') + '/Library/Application Support/Google/Chrome/Default/Cookies'
    conn = sqlite3.connect(cookie_db)
    c = conn.cursor()
    for row in c.execute("select name,value,encrypted_value from cookies where host_key like '%"+host+"%' and (length(value) > 0 or length(encrypted_value) > 0)"):
        if row[1] == "":
            cookie_str = cookie_str + row[0] + "=" + decrypt(row[2]) + ";"
        else:
            cookie_str = cookie_str + row[0] + "=" + row[1] + ";"
    conn.close()
    return cookie_str

def get_calories_from_mshealth(today):
    host = 'https://dashboard.microsofthealth.com/card/getuseractivitybyhour?date='+today+'&utcOffsetMinutes=-240'
    cookie = get_cookies('microsofthealth')
    curl_str = "curl --silent '" + host + "' -H 'Cookie: " + cookie + "' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36' -H 'Accept: application/json, text/plain, */*' -H 'Cache-Control: max-age=0' -H 'X-Requested-With: XMLHttpRequest' -H 'Connection: keep-alive' -H 'If-Modified-Since: 0' -H 'Referer: https://dashboard.microsofthealth.com/' --compressed"

    json_response = os.popen(curl_str).read()
    data = json.loads(json_response)
    calories = data.get("TotalCaloriesBurned")

    return calories

# Leaving this here for now - should switch to independent login rather than relying on Chrome cookies
#def login_to_mfp(browser):
#    global username, password
#
#    browser.open("http://www.myfitnesspal.com/account/login")
#    browser.select_form(nr=0)
#    browser["username"] = username
#    browser["password"] = password
#    try:
#        response = browser.submit()
#        return True
#    except:
#        pass
#
#    return False


def update_mfp(today,calories):
#    browser = Browser()
#    if login_to_mfp(browser) is False:
#        print "Problem logging into MyFitnessPal"
#        sys.exit(1)
    search_url = 'http://www.myfitnesspal.com/exercise/search'
    add_url = 'http://www.myfitnesspal.com/exercise/add'
    cookie = get_cookies('www.myfitnesspal')
    auth_curl_str = "curl --silent '" + search_url + "' -H 'Cookie: " + cookie + "' -H 'Origin: http://www.myfitnesspal.com' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36' -H 'Cache-Control: max-age=0' -H 'Referer: http://www.myfitnesspal.com/exercise/search' -H 'Connection: keep-alive' | grep AUTH_TOKEN | cut -d '\"' -f 2"

    auth_token = os.popen(auth_curl_str).read().rstrip()

    data = "utf8=%E2%9C%93&authenticity_token="+auth_token+"&calorie_multiplier=1.0&search=general&exercise_entry%5Bexercise_id%5D=1&exercise_entry%5Bdate%5D="+today+"&exercise_entry%5Bexercise_type%5D=0&authenticity_token="+auth_token+"&exercise_entry%5Bquantity%5D=1&exercise_entry%5Bstart_time%281i%29%5D=2015&exercise_entry%5Bstart_time%282i%29%5D=4&exercise_entry%5Bstart_time%283i%29%5D=27&exercise_entry%5Bstart_time%284i%29%5D=5&exercise_entry%5Bstart_time%285i%29%5D=45&exercise_entry%5Bcalories%5D="+calories

    add_curl_str = "curl --silent '" + add_url + "' -H 'Cookie: " + cookie + "' -H 'Origin: http://www.myfitnesspal.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36' -H 'Content-Type: application/x-www-form-urlencoded' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8' -H 'Cache-Control: max-age=0' -H 'Referer: http://www.myfitnesspal.com/exercise/search' -H 'Connection: keep-alive' --data '" + data + "' --compressed"
    response = os.popen(add_curl_str).read()

# MFP won't let you set a goal of 0 calories but have a macronutrient goal, 
# so if we want to have a protein goal we have to also have a calorie goal.
# This happens to be 800 based on the protein goal.
# So we have to subtract 800 in order to get calorie delta
def cache_calories(today,calories):
    last_calories = 800
    cache = ['1967-01-01',last_calories]
    cache_file = expanduser('~') + '/.band_to_mfp'

    try:
        f = open(cache_file)
        unpickler = pickle.Unpickler(f)
        cache = unpickler.load()
    except:
        pass

    if cache[0] == today:
        last_calories = cache[1]

    if calories < last_calories:
        calories = last_calories

    cache[0] = today
    cache[1] = calories

    f = open(cache_file, 'w')
    pickle.dump(cache, f)

    return last_calories

def main():
    today = time.strftime('%Y-%m-%d')
    calories = get_calories_from_mshealth(today)
    last_calories = cache_calories(today,calories)
    if last_calories < calories:
        calories = str(calories - last_calories)
        print "updating"
        print "last_calories is " + str(last_calories)
        print "calories is " + calories
        update_mfp(today,calories)
    else:
        print "not updating"
        print "last_calories is " + str(last_calories)
        print "calories is " + str(calories)

if __name__ == '__main__':
    main()
