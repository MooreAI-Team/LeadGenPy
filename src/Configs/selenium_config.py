from selenium import webdriver
from Configs import config


def __initialize():
    chrome_options = webdriver.ChromeOptions()

    # block cookies, images, popups, notifs etc to speeds things up
    prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2,
                                                        'plugins': 2, 'popups': 2, 'geolocation': 2,
                                                        'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
                                                        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
                                                        'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2,
                                                        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                                        'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                                                        'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2,
                                                        'durable_storage': 2}}
    chrome_options.add_experimental_option('prefs', prefs)
    chrome_options.add_argument("--disable-extensions")  # no extensions
    chrome_options.add_argument("--disable-gpu")  # needed on some windows setups
    chrome_options.add_argument("--disable-infobars")  # hide "chrome is being controlled" bar

    if config.DEV:
        # dev: open browser so we can see what's happening
        print("[LOG] Dev mode: browser visible")
        chrome_options.add_argument("start-maximized")
    else:
        # prod: no UI needed
        print("[LOG] Prod mode: headless")
        chrome_options.add_argument("--headless=new")

    print("[LOG] Selenium ready")
    d = webdriver.Chrome(options=chrome_options)
    d.set_page_load_timeout(config.page_load_timeout)  # don't hang forever on slow pages
    return d


driver = __initialize()
