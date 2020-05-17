#!/usr/bin/env python3
import time
import logging
import subprocess
import json
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from pyvirtualdisplay import Display
import requests
import click

ROUTER_URL = 'http://192.168.0.1'
ROUTER_LOGIN_USERNAME = 'Admin'
ROUTER_LOGIN_PASSWORD = ''
PING_SERVER = '1.1.1.1'

# TODO: Add notify-send support on flip action
# TODO: Add validation checks
# Setup logging
LOGGER = logging.getLogger()


def accept_javascript_prompt_blindly(driver):
    try:
        obj = driver.switch_to.alert
        obj.accept()
    except NoAlertPresentException:
        pass


def switch_wantype(driver, wantype):
    time.sleep(5)
    id_wantype_dropdown = driver.find_element_by_name('wantype')
    id_savebtn = driver.find_element_by_name('save')
    id_wantype_dropdown.send_keys(wantype)
    id_savebtn.click()
    # Accept whatever Javascript prompts there may be.
    accept_javascript_prompt_blindly(driver)


def validate_with_ipinfo_io():
    req = requests.get('https://ipinfo.io', headers={'Accept': 'application/json'})
    logging.info(json.dumps(req.json(), indent=2))


@click.command()
@click.option('--sequence', '-s', help='The order in which to sequentially '
              'change the WAN connection type. E.g. "PPPoE:Static IP:PPPoE"',
              required=True)
@click.option('--no-headless', help="Don't be headless ! Show me the Chrome "
              "window.", is_flag=True, default=False)
@click.option('--on-ping-fail', help="Run the flip sequence only "
              "when ping fails", is_flag=True, default=False)
@click.option('--run-every', help="Run the flip sequence every these "
              "many seconds.", type=int)
@click.option('--no-ipinfo', help="Don't query ipinfo.io.",
              default=False)
@click.option('--debug', help="Don't log debug messages.", is_flag=True,
              default=False)
def main(sequence, no_headless, run_every, no_ipinfo, on_ping_fail, debug):
    '''
    The script flips through different WAN options (PPPoE, Ethernet) on your router.
    This could serve following purposes:

    *  Your PPPoE connection just dies periodically and you want your router to
       dial it again but what you have is a cheap, $10 router that doesn't
       automatically re-dial and doesn't provide any ssh/telnet interface to
       make automate re-dialing easier either. So you use selenium to interact
       with the router over the web interface.

    *  If you are in a situation like mine, where you can alternatively switch
       between operators over the same physical link. You can use this script
       to flip between operators.

    Tips:
    * You can use a combination of --no-headless, --run-every and
      --on-ping-fail options to automatically detect connection failures
      and re-dial. Cloudflare's DNS service at 1.1.1.1 is pinged to check
      network availability.
    * The script calls up ipinfo.io and logs the details


    Requirements:
    selenium, chrome(browser), pyvirtualdisplay, click, requests

    '''
    # Set the loglevel
    global LOGGER

    consolehandler = logging.StreamHandler()
    logformat = logging.Formatter('%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    consolehandler.setFormatter(logformat)
    LOGGER.addHandler(consolehandler)
    LOGGER.setLevel(logging.DEBUG) if debug else LOGGER.setLevel(logging.INFO)

    def runner():
        if on_ping_fail:
            ping_test = not subprocess.run(['ping', PING_SERVER, '-c', '3', '-W', '10'],
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL).returncode
            if ping_test:
                logging.info(f'{PING_SERVER} is pingable. Skipping this run.')
                return
            logging.error(f'{PING_SERVER} is not pingable. ',
                          f'Running your WANTYPE flip sequence now.')
        chrome_options = webdriver.ChromeOptions()
        if not no_headless:
            display = Display(visible=0, size=(1024, 768))
            display.start()
        driver = webdriver.Chrome(chrome_options=chrome_options, service_args=['--verbose'])
        driver.get(ROUTER_URL)

        # Get the username, password, login button ids
        id_username = driver.find_element_by_id('username')
        id_password = driver.find_element_by_id('password')
        id_loginbtn = driver.find_element_by_id('loginBtn')

        id_username.clear()
        id_username.send_keys(ROUTER_LOGIN_USERNAME)
        id_password.send_keys(ROUTER_LOGIN_PASSWORD)
        id_loginbtn.click()

        # Blind accept any previously logged in prompts
        accept_javascript_prompt_blindly(driver)

        # Go to the WAN settings page
        driver.get('http://192.168.0.1/wan.htm')

        # Flip WANTYPEs are asked for.
        for wantype in sequence.split(':'):
            logging.info(f'Switching WANTYPE to {wantype}')
            switch_wantype(driver, wantype)

        # Wait for 5 second and then close the chrome webdriver and the virtual Xvfb display
        time.sleep(5)
        driver.close()
        display.popen.kill()

        # Wait 10s for WAN to come up
        time.sleep(30)
        logging.info("Results from ipinfo.io are dummped below: ")
        validate_with_ipinfo_io()

    runner()
    if run_every:
        while True:
            logging.info(f'Sleeping {run_every} seconds before the next run.')
            time.sleep(run_every)
            runner()

if __name__ == '__main__':
    main()
