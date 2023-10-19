try:
    ##for Type Hinting
    from typing import Union, Optional
    
    ##selenium libraries
    import seleniumwire.undetected_chromedriver.v2 as seleniumWireWebdriver
    import undetected_chromedriver as webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver import Keys
    from selenium.webdriver.support.ui import Select
    
    ##cv2
    import cv2

    ##indispensable
    import httpx
    import string
    import random
    import os
    import time
    import json
    from sys import platform
    from functools import reduce
    import base64
    import subprocess

except:
    print('Modules not found! Please run `install.bat` and restart the tool.')
    input()
    exit()

class ChromeWithPrefs(webdriver.Chrome):
    def __init__(self, *args, options=None,data_dir=False,**kwargs):
        if options:
            self.handle_prefs(options,data_dir)
        super().__init__(*args, options=options, **kwargs)
        if data_dir != False:
            self.keep_user_data_dir = True
        else:
            self.keep_user_data_dir = False
    
    @staticmethod
    def handle_prefs(options,data_dir):
        if prefs := options.experimental_options.get("prefs"):
            def undot_key(key, value):
                if "." in key:
                    key, rest = key.split(".", 1)
                    value = undot_key(rest, value)
                return {key: value}
            undot_prefs = reduce(lambda d1, d2: {**d1, **d2},
                (undot_key(key, value) for key, value in prefs.items()), )

            if type(data_dir) == str:
                options.add_argument(f"--user-data-dir={data_dir}")
                default_dir = os.path.join(data_dir, "Default")

                #prefs_file = os.path.join(default_dir, "Preferences")
                #with open(prefs_file, encoding="latin1", mode="w") as f:
                #    json.dump(undot_prefs, f)

                del options._experimental_options["prefs"]


class wireChromeWithPrefs(seleniumWireWebdriver.Chrome):
    def __init__(self, *args, options=None,data_dir=False,**kwargs):
        if options:
            ChromeWithPrefs.handle_prefs(options,data_dir)
        super().__init__(*args, options=options,data_dir=data_dir, **kwargs)

        if data_dir == False:
            self.keep_user_data_dir = False
        else:
            self.keep_user_data_dir = True

def callUcDriver(**kwargs):
    proxy =  kwargs.get("proxy",None)
    two_captcha = kwargs.get("two_captcha",False)
    headless = kwargs.get("headless",True)
    data_directory = kwargs.get("data_directory",False)
    page_load_str = kwargs.get("page_load_str","eager")
    prefs = {'intl.accept_languages': 'en,en_US'}

    caps = DesiredCapabilities().CHROME
    if proxy != None:
        if type(proxy) != list:
            proxy = proxy.split(':')

        if len(proxy) > 2:
            IP = proxy[0]
            port = proxy[1]
            username = proxy[2]
            password = proxy[3]
            useAuth = True
        else:
            IP = proxy[0]
            port = proxy[1]
            useAuth = False

        if useAuth:
            wireOptions = {'proxy': {'http': 'http://' + username + ':' + password + '@' + IP + ':' + port,'https': 'https://' + username + ':' + password + '@' + IP + ':' + port,'no_proxy': 'localhost,127.0.0.1'}}
        else:
            wireOptions = {'proxy': {'http': 'http://@' + IP + ':' + port,'https': 'https://@' + IP + ':' + port,'no_proxy': 'localhost,127.0.0.1'}}

    caps["pageLoadStrategy"] = page_load_str
    op = webdriver.ChromeOptions()
    if headless:
        op.add_argument("--headless=new")

    # Sertifika hatasi alinmasi dahilinde,
    # python -m seleniumwire extractcert ile indirdiginiz
    # sertifikayi chrome'a ekleyiniz.

    op.add_argument('--ignore-certificate-errors')
    op.add_experimental_option("prefs", prefs)
    op.add_argument("--no-sandbox")
    #op.add_argument("--dns-prefetch-disable")
    #op.add_argument("--disable-gpu")
    #op.add_argument("--disable-user-media-security=true")
    #op.add_argument("--disable-popup-blocking")

    if two_captcha:
        op.add_argument('--load-extension={}HTML-Elements-Screenshot,{}2Captcha'.format("src/extensions" + os.path.sep, "src/extensions" + os.path.sep))

    if proxy != None:
        driver = wireChromeWithPrefs(options=op, driver_executable_path="src/chromedriver", desired_capabilities=caps, seleniumwire_options=wireOptions, data_dir=data_directory)
    else:
        driver = ChromeWithPrefs(options=op, driver_executable_path="src/chromedriver", desired_capabilities=caps, data_dir=data_directory)
    return driver

