import yaml

from time import sleep
from selenium import webdriver

class tracklister(object):
    '''
    Class to build track list from M3U8 generated by Rekordbox
    '''

    def __init__(self, fname):
        self.filename = fname

    def read_file(self):
        '''
        Read lines of file and store
        '''
        self.lines = []
        string = ''
        with open(self.filename, 'r') as f:

            for line in f.read():

                string += line

                if line == '\n':
                    self.lines.append(string)
                    string = ''

        return

    def read_tracks(self):
        '''
        Transform file into better format
        '''
        soln = []

        for track in self.lines:
            if track[0:7] == '#EXTINF':
                pos = track.find(',') + 1
                soln.append(track[pos:])

        soln = self.strip_last_return(soln)

        return(soln)

    def strip_last_return(self, tracks):
        '''
        Remove the carriage return from last track
        '''
        tracks[-1] = tracks[-1].strip('\r\n')

        return(tracks)


    def build(self):
        '''
        Build track list and return list
        '''
        self.read_file()

        return(self.read_tracks())

class dnbradio(object):
    """
    Class to login and update latest podcast track list

    Note: Sleep is incorporated into appropriate functions to ensure
            the page is fully loaded before proceeding.
    """
    def __init__(self, login_pass, trk_list):
        '''
        INPUT
            login_pass - username and password, DICT
            raw_playlist - playlist exported from Rekordbox, LIST
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.track_list = trk_list
        self.url = 'https://dnbradio.com/?event=login'

    def launch(self):
        '''
        Launch Chrome webdriver
        '''
        self.driver = webdriver.Chrome('/Users/danius/anaconda2/selenium/webdriver/chromedriver')
        self.driver.get(self.url)

        sleep(5)

        return

    def login(self):
        '''
        Log into dnbradio
        '''
        self.driver \
            .find_element_by_name('username') \
            .send_keys(self.user)

        self.driver \
            .find_element_by_name('password') \
            .send_keys(self.password)

        self.driver \
            .find_element_by_xpath("//input[@type='submit'][@value='login']") \
            .click()

        return

    def goto_archive(self):
        '''
        Go to the archive page
        '''
        self.driver \
            .find_element_by_link_text('archives').click()

        return

    def goto_latest_show(self):
        '''
        Go to most recent show page
        '''
        self.driver \
            .find_element_by_xpath("//a[@class='showLink'][contains(text(),'coffee n bass')]") \
            .click()

        sleep(1)
        return

    def goto_edit_page(self):
        '''
        Enter edit page for a show
        '''
        self.driver \
            .find_element_by_xpath("//a[contains(text(),'edit listing')]") \
            .click()

        sleep(1)
        return

    def enter_track_list(self):
        '''
        Enter track list into text box
        '''
        self.driver \
            .find_element_by_name('frm_tracklist') \
            .send_keys(self.track_list)

        return

    def enter_show_image(self):
        '''
        Enter path for show's image
        '''
        self.driver \
            .find_element_by_name('frm_picture') \
            .send_keys('/Users/danius/Documents/ritchey_cover_05_-_small_4.jpg')

        return

    def save_edits(self):
        '''
        Save edits made to show page
        '''
        self.driver \
            .find_element_by_xpath("//input[@value='Save']") \
            .click()

        sleep(5)
        return

    def bbc_code(self):
        '''
        Save the generated BBC code
        '''
        self.bbc = self.driver \
                        .find_element_by_xpath("//textarea") \
                        .text

        return

    def fetch_filename(self):
        '''
        Store show file name
        '''
        self.show_filename = self.driver \
                                 .find_element_by_xpath('//a[contains(text(),"Download this mix")]') \
                                 .get_attribute('href') \
                                 .split('livesets/')[1]

        return

    def download_show(self):
        '''
        Download the show
        '''
        self.driver \
            .find_element_by_xpath('//a[contains(text(),"Download this mix")]') \
            .click()

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def update_show(self):
        '''
        Update show with track list and image
        '''
        self.launch()

        self.login()

        self.goto_archive()

        self.goto_latest_show()

        self.goto_edit_page()

        self.enter_track_list()

        self.enter_show_image()

        self.save_edits()

        self.goto_archive()

        self.goto_latest_show()

        self.download_show()

        self.fetch_filename()

        self.bbc_code()

        self.shutdown()

        return

class dnbforum(object):

    def __init__(self, login_pass, bbc_code):
        '''
        INPUT
            login_pass - username and password, DICT
            bbc_code - BBC code from DNBRadio, STR
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.bbc = bbc_code
        self.url = 'https://dnbforum.com/threads/ritchey-coffee-bass-live-on-dnbradio.185748/'

    def launch(self):
        '''
        Launch Chrome webdriver
        '''
        self.driver = webdriver.Chrome('/Users/danius/anaconda2/selenium/webdriver/chromedriver')
        self.driver.get(self.url)

        sleep(5)

        return

    def login(self):
        '''
        Log into dnbforum
        '''
        self.driver \
            .find_element_by_xpath("//a[@href='login/']") \
            .click()

        sleep(1)

        self.driver \
            .find_element_by_xpath("//input[@name='login']") \
            .send_keys(self.user)

        self.driver \
            .find_element_by_xpath("//input[@name='password']") \
            .send_keys(self.password)

        self.driver \
            .find_element_by_xpath("//input[@value='Log in']") \
            .click()

        return

    def find_last_page(self):
        '''
        Determine the last page of posts
        '''
        self.last_page = self.driver \
                             .find_element_by_class_name('PageNav') \
                             .get_attribute('data-last')

        return

    def goto_last_page(self):
        '''
        Go to last page of posts
        '''
        self.find_last_page()

        xpath_str = "//nav/a[contains(text()," + self.last_page + ")]"

        self.driver \
            .find_element_by_xpath(xpath_str) \
            .click()

        return

    def enter_bbc_code(self):
        '''
        Select iframe and enter BBC code for show
        '''
        frame = self.driver \
                    .find_element_by_tag_name('iframe')

        self.driver \
            .switch_to_frame(frame)

        self.driver \
            .find_element_by_xpath('//body') \
            .send_keys(self.bbc)

        self.driver \
            .switch_to_default_content()

        return

    def submit_reply(self):
        '''
        Submit post to forum thread
        '''
        self.driver \
            .find_element_by_xpath("//input[@value='Post Reply']") \
            .click()

        sleep(5)

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def post_reply(self):
        '''
        Post show to forum
        '''
        self.launch()

        self.login()

        self.goto_last_page()

        self.enter_bbc_code()

        self.submit_reply()

        self.shutdown()

        return

class dogsonacid(object):

    def __init__(self, login_pass, bbc_code):
        '''
        INPUT
            login_pass - username and password, DICT
            bbc_code - BBC code from DNBRadio, STR
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.bbc = bbc_code
        self.url = 'https://www.dogsonacid.com/threads/ritchey-coffee-bass-live-on-dnbradio.771638/'

    def launch(self):
        '''
        Launch Chrome webdriver
        '''
        self.driver = webdriver.Chrome('/Users/danius/anaconda2/selenium/webdriver/chromedriver')
        self.driver.get(self.url)

        sleep(5)

        return

    def login(self):
        '''
        Log into dnbforum
        '''
        self.driver \
            .find_element_by_xpath("//a[@href='login/']") \
            .click()

        sleep(1)

        self.driver \
            .find_element_by_xpath("//input[@name='login']") \
            .send_keys(self.user)

        self.driver \
            .find_element_by_xpath("//input[@name='password']") \
            .send_keys(self.password)

        self.driver \
            .find_element_by_xpath("//input[@value='Log in']") \
            .click()

        return

    def find_last_page(self):
        '''
        Determine the last page of posts
        '''
        self.last_page = self.driver \
                             .find_element_by_class_name('PageNav') \
                             .get_attribute('data-last')

        return

    def goto_last_page(self):
        '''
        Go to last page of posts
        '''
        self.find_last_page()

        xpath_str = "//nav/a[contains(text()," + self.last_page + ")]"

        self.driver \
            .find_element_by_xpath(xpath_str) \
            .click()

        return

    def enter_bbc_code(self):
        '''
        Select iframe and enter BBC code for show
        '''
        frame = self.driver \
                    .find_element_by_tag_name('iframe')

        self.driver \
            .switch_to_frame(frame)

        self.driver \
            .find_element_by_xpath('//body') \
            .send_keys(self.bbc)

        self.driver \
            .switch_to_default_content()

        sleep(1)

        return

    def submit_reply(self):
        '''
        Submit post to forum thread
        '''
        self.driver \
            .find_element_by_xpath("//input[@value='Post Reply']") \
            .click()

        sleep(5)

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def post_reply(self):
        '''
        Post show to forum
        '''
        self.launch()

        self.login()

        self.goto_last_page()

        self.enter_bbc_code()

        self.submit_reply()

        self.shutdown()

        return

class site_keys(object):
    '''
    Login and password class to store credentials for sites
    '''

    def __init__(self, fname):
        self.filename = fname

    def load_keys(self):
        '''
        Load data from YAML file
        '''
        with open(self.filename, 'r') as f:
            self.raw_keys = yaml.load(f)

        return

    def redefine(self):
        '''
        Transform YAML file into dictionary
        '''
        self.dnbradio = {self.raw_keys['dnbradio_usr'] : self.raw_keys['dnbradio_pswd']}

        self.dnbforum = {self.raw_keys['dnbforum_usr'] : self.raw_keys['dnbforum_pswd']}

        self.doa = {self.raw_keys['doa_usr'] : self.raw_keys['doa_pswd']}

        return

    def build(self):
        '''
        Build credential class
        '''
        self.load_keys()

        self.redefine()

        return
