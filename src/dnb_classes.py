import yaml, sys, os, random

from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

class bmills_selecta(object):
    '''
    Class to randomly select bmills photo
    '''

    def __init__(self):
        self.art_location = '/Users/danius/Documents/Github/coffee_n_bass/cover_art/'
        self.log = '/Users/danius/Documents/Github/coffee_n_bass/src/art.log'

    def _load(self):
        '''
        Load log of previously used artwork
        '''
        with open(self.log, 'r') as f:
            data = [val.replace(',','').replace('\n','') for val in f.readlines()]
        return(set(data))

    def _read(self):
        '''
        Read files
        '''
        return(set(os.listdir(self.art_location + 'other/')))

    def _reset_log(self):
        '''
        Clear out log after all files are used
        '''
        f = open(self.log, 'w')
        f.close()

    def _add_to_log(self, file):
        '''
        Add to log
        '''
        with open(self.log, 'a') as f:
            f.write(file + ',\n')

    def pick(self):
        '''
        Pick cover for publishing
        '''
        files = self._read()
        used = self._load()

        if files == used:
            self._reset_log()
            return(random.sample(files, 1)[0])
        else:
            return(random.sample(files - used, 1)[0])

    def deliver(self):
        '''
        Return file paths and add file to log
        '''
        art = self.pick()

        print art

        self._add_to_log(art)

        dnbradio = self.art_location + 'dnbradio/' + art
        other = self.art_location + 'other/' + art

        return(dnbradio, other)

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

        self.list = self.read_tracks()

        return

class dnbradio(object):
    """
    Class to login and update latest podcast track list

    Note: Sleep is incorporated into appropriate functions to ensure
            the page is fully loaded before proceeding.
    """
    def __init__(self, login_pass, trk_list, art_file):
        '''
        INPUT
            login_pass - username and password, DICT
            trk_list - playlist exported from Rekordbox, LIST
            art_file - file path to cover art, STR

        EXAMPLE
            dnbradio({'usr':'pswd'}, ['artist1 - track1', 'artist2 - track2', ...])
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.track_list = trk_list
        self.url = 'https://dnbradio.com/?event=login'
        self.art = art_file

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

    def scroll_to_element(self, element):
        '''
        Scroll till element is within view
        '''
        loc = element.location_once_scrolled_into_view

        self.driver \
            .execute_script("window.scrollTo(0, " + str(loc['y']) + ");")

    def goto_archive(self):
        '''
        Go to the archive page
        '''
        self.driver \
            .get('https://dnbradio.com/podcast/ritchey')
            # .find_element_by_link_text('archives').click()

        return

    def goto_latest_show(self):
        '''
        Go to most recent show page
        '''
        self.driver \
            .execute_script("window.scrollTo(0, document.body.scrollHeight);")

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
            .execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(2)

        self.driver \
            .find_element_by_xpath("//a[contains(text(),'edit listing1')]") \
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

        sleep(5)

        return

    def enter_show_image(self):
        '''
        Enter path for show's image
        '''
        self.driver \
            .find_element_by_name('frm_picture') \
            .send_keys(self.art)

        sleep(1)

        return

    def save_edits(self):
        '''
        Save edits made to show page
        '''
        self.driver \
            .execute_script("window.scrollTo(0, document.body.scrollHeight);")

        sleep(2)

        self.driver \
            .find_element_by_xpath("//input[@value='Save']") \
            .click()

        sleep(2)
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

        self._sleep_progress(180)

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def publish(self):
        '''
        Execute entire workflow to publish show
        '''
        print('Launch dnbradio driver')
        self.launch()

        self.login()

        print('Begin publishing')
        self.goto_archive()

        self.goto_latest_show()

        self.goto_edit_page()

        self.enter_track_list()

        self.enter_show_image()

        self.save_edits()

        print('Publishing complete')
        self.goto_archive()

        self.goto_latest_show()

        print('Download show')
        self.download_show()

        self.fetch_filename()

        self.bbc_code()

        print('Shutdown dnbradio driver\n')
        self.shutdown()

        return

    def refetch_filename(self):
        self.launch()

        self.goto_archive()

        self.goto_latest_show()

        self.fetch_filename()

        self.shutdown()

        return


    def _sleep_progress(self, length):
        '''
        Input:
            - length: time in seconds to wait till next API call (INT)
        Output:
            - None
        '''
        toolbar_width = 40

        # setup toolbar
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        increment = length / float(toolbar_width)
        for i in xrange(toolbar_width):
            sleep(increment)
            # update the bar
            sys.stdout.write("-")
            sys.stdout.flush()

        sys.stdout.write("\n")

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

    def save_edits(self):
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

    def publish(self):
        '''
        Execute entire workflow to publish show
        '''
        print('Launch dnbforum driver')
        self.launch()

        self.login()

        print('Begin publishing')
        self.goto_last_page()

        self.enter_bbc_code()

        print('Publishing complete')
        self.save_edits()

        print('Shutdown dnbforum driver\n')
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

    def save_edits(self):
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

    def publish(self):
        '''
        Execute entire workflow to publish show
        '''
        print('Launch dogsonacid driver')
        self.launch()

        self.login()

        print('Begin publishing')
        self.goto_last_page()

        self.enter_bbc_code()

        print('Publishing complete')
        self.save_edits()

        print('Shutdown dogsonacid driver\n')
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

        self.mixcloud = {self.raw_keys['mcloud_usr'] : self.raw_keys['mcloud_pswd']}

        self.soundcloud = {self.raw_keys['scloud_usr'] : self.raw_keys['scloud_pswd']}
        return

    def build(self):
        '''
        Build credential class
        '''
        self.load_keys()

        self.redefine()

        return

class soundcloud(object):
    """
    Class to login and publish show to soundcloud

    Note: Sleep is incorporated into appropriate functions to ensure
            the page is fully loaded before proceeding.
    """
    def __init__(self, login_pass, trk_list, filename, art_file):
        '''
        INPUT
            login_pass - username and password, DICT
            trk_list - playlist exported from Rekordbox, LIST
            filename - show filename downloaded from dnbradio, STR
            art_file - file path to cover art, STR

        EXAMPLE
            mixcloud({'usr' : 'pswd'},
                     ['artist1 - track1', 'artist2 - track2', ...],
                     'myshow.mp3')
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.track_list = trk_list
        self.show_filename = filename
        self.url = 'https://soundcloud.com/'
        self.trk_url = 'https://soundcloud.com/ritchey/tracks'
        self.art = art_file

    def _rand_sleep(self):
        '''
        Sleep for random amount of time
        '''
        sleep(random.randint(5,15))
        return

    def launch(self):
        '''
        Launch Chrome webdriver
        '''
        self.driver = webdriver.Chrome('/Users/danius/anaconda2/selenium/webdriver/chromedriver')
        self.driver.get(self.url)

        self._rand_sleep()

        return

    def login(self):
        '''
        Log into soundcloud
        '''
        self.driver \
            .find_elements_by_xpath("//button[@title='Sign in']")[1] \
            .click()

        self._rand_sleep()

        self.type_at_cursor(self.user)

        self.driver \
            .find_element_by_xpath("//button[@title='Continue']") \
            .click()

        self._rand_sleep()

        self.type_at_cursor(self.password)

        self.driver \
            .find_elements_by_xpath("//button[@title='Sign In']")[3] \
            .click()

        # "//button[@title='Sign in']"

        self._rand_sleep()

        return

    def del_previous(self):
        '''
        Delete previous show on soundcloud
        '''
        self.driver.get(self.trk_url)

        self._rand_sleep()

        self.driver \
            .find_element_by_xpath("//button[@title='More']") \
            .click()

        self._rand_sleep()

        self.driver \
            .find_element_by_xpath("//button[@title='Delete track']") \
            .click()

        self._rand_sleep()

        self.driver \
            .find_elements_by_xpath("//button[@type='submit']")[1] \
            .click()

        self._rand_sleep()

        return

    def goto_upload_page(self):
        '''
        Go to upload page
        '''
        self.driver \
            .find_element_by_xpath("//span[@class='uploadButton__title']") \
            .click()

        self._rand_sleep()

        return

    def select_file(self):
        '''
        Select file to upload
        '''
        loc = '/Users/danius/Downloads/' + self.show_filename

        self.driver \
            .find_element_by_xpath("//input[@class='chooseFiles__input sc-visuallyhidden']") \
            .send_keys(loc)

        self._sleep_progress(240)

        return

    def enter_show_name(self):
        '''
        Soundcloud is able to extract show name from the MP3
        '''
        print('Method not required, use select_file()')
        return

    def upload(self):
        '''
        Soundcloud begins uploading a file once it's selected
        '''
        print('Method not required, use select_file()')
        return

    def _prep_track_list(self):
        '''
        Reconfigure tracklist for input
        '''
        trk_list = ''

        for trk in self.track_list:
            trk_list += trk.replace('\r','')

        return(trk_list)

    def enter_track_list(self):
        '''
        Enter track list for show
        '''
        self.driver \
            .find_element_by_xpath("//textarea") \
            .send_keys(self._prep_track_list())

        self._rand_sleep()

        return

    def enter_show_image(self):
        '''
        Select image for show
        '''
        self.driver \
            .find_element_by_xpath("//input[@class='imageChooser__fileInput sc-visuallyhidden']") \
            .send_keys(self.art)

        self._rand_sleep()

        return

    def add_tags(self):
        '''
        Add tags and genre
        '''
        self.driver \
            .find_element_by_xpath("//div[@class='select__wrapper']") \
            .click()

        self._rand_sleep()

        self.driver \
            .find_element_by_xpath("//a[contains(text(),'Drum & Bass')]") \
            .click()

        self._rand_sleep()

        for tag in ['Liquid\t', 'Seattle\t']:

            self.driver \
                .find_element_by_xpath("//input[@id='tokenInput__tags']") \
                .send_keys(tag)

            self._rand_sleep()

        return

    def change_permissions(self):
        '''
        Make the show downloadable
        '''
        self.driver \
            .find_element_by_xpath("//a[contains(text(), 'Permissions')]") \
            .click()

        self._rand_sleep()

        self.driver \
            .find_element_by_xpath("//label[contains(text(),'Enable downloads')]") \
            .click()

        self._rand_sleep()

        return

    def save_edits(self):
        '''
        Save show changes
        '''
        self.driver \
            .find_element_by_xpath("//button[@title='Save']") \
            .click()

        self._rand_sleep()

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def publish(self):
        '''
        Execute entire workflow to publish show
        '''
        print('Launch soundcloud driver')
        self.launch()

        self.login()

        print('Remove previous show')
        self.del_previous()

        self._rand_sleep()

        print('Beign publishing')
        self.goto_upload_page()

        self.select_file()
        print('Upload show')

        self.enter_show_image()

        self.add_tags()

        self.enter_track_list()

        self.change_permissions()

        print('Publishing complete')
        self.save_edits()

        print('Shutdown soundcloud driver\n')
        self.shutdown()

        return

    def type_at_cursor(self, text):
        '''
        Enter text at the cursor location
        '''
        act = ActionChains(self.driver)

        act.send_keys(text)

        self._rand_sleep()

        act.perform()

        del act

        return


    def _sleep_progress(self, length):
        '''
        Input:
            - length: time in seconds to wait till next API call (INT)
        Output:
            - None
        '''
        toolbar_width = 40

        # setup toolbar
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        increment = length / float(toolbar_width)
        for i in xrange(toolbar_width):
            sleep(increment)
            # update the bar
            sys.stdout.write("-")
            sys.stdout.flush()

        sys.stdout.write("\n")
        return

class mixcloud(object):
    """
    Class to login and publish show to mixcloud

    Note: Sleep is incorporated into appropriate functions to ensure
            the page is fully loaded before proceeding.
    """
    def __init__(self, login_pass, trk_list, filename, art_file):
        '''
        INPUT
            login_pass - username and password, DICT
            trk_list - playlist exported from Rekordbox, LIST
            filename - show filename downloaded from dnbradio, STR
            art_file - file path to cover art, STR

        EXAMPLE
            mixcloud({'usr' : 'pswd'},
                     ['artist1 - track1', 'artist2 - track2', ...],
                     'myshow.mp3')
        '''
        self.user = login_pass.keys()[0]
        self.password = login_pass.values()[0]
        self.track_list = trk_list
        self.show_filename = filename
        self.url = 'http://www.mixcloud.com/'
        self.art = art_file

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
        self.driver.get('http://www.mixcloud.com/settings/')

        self.driver \
            .find_element_by_xpath("//a[contains(text(), 'Login')]") \
            .click()
        #
        # self.driver \
        #     .find_element_by_xpath('''//div[@class='user-actions']
        #                                 /a[contains(text(),'Log in')]''') \
        #     .click()
        #
        # sleep(0.5)

        self.driver \
            .find_element_by_xpath('''//input[@ng-model='formData.email']''') \
            .send_keys(self.user)

        self.driver \
            .find_element_by_xpath('''//input[@type='password']''') \
            .send_keys(self.password)

        self.driver \
            .find_element_by_xpath('''//button[@class='btn btn-big btn-secondary']''') \
            .click()

        sleep(1)

        return

    def goto_upload_page(self):
        '''
        Go to upload page
        '''
        self.driver \
            .find_element_by_xpath('''//a[@href='/upload/']''') \
            .click()

        sleep(1)
        return

    def select_file(self):
        '''
        Select file to upload
        '''
        loc = '/Users/danius/Downloads/' + self.show_filename

        self.driver \
            .find_element_by_xpath('''//input[@type='file']''') \
            .send_keys(loc)

        sleep(1)

        return

    def enter_show_name(self):
        '''
        Enter show name
        '''
        self.title = self.show_filename.split('_-_')[-1].replace('.mp3', '')

        self.driver \
            .find_element_by_xpath('''//input[@id='cloudcast-name']''') \
            .send_keys('coffee n bass : ' + self.title)

        sleep(1)

        return

    def upload(self):
        '''
        Upload file
        '''
        self.driver \
            .find_element_by_xpath('''//div[@m-click='upload.submit()']''') \
            .click()

        #Waiting long enough to ensure the file uploaded
        self._sleep_progress(360)

        return

    def _initialize_track_list(self):
        '''
        Go to tracklist window and prep it for data entry
        '''
        tlist_window = self.driver \
                           .find_element_by_xpath('''//textarea[@class='tracklist-textarea ng-pristine ng-valid']''')

        self.scroll_to_element(tlist_window)

        #Rough work around because sending command+v doesn't work
        tlist_window.click()
        tlist_window.send_keys('t')

        return

    def _prep_track_list(self):
        '''
        Clear out the initialization of the tracklist
        '''
        self.driver \
            .find_element_by_xpath('''//textarea[@m-field-type='artist']''') \
            .clear()

        return

    def enter_track_list(self):
        '''
        Enter track list for the show
        '''
        self._initialize_track_list()

        self._prep_track_list()

        for i, trk in enumerate(self.track_list):
            trk = trk.replace('\r\n', '').split(' - ')

            if len(trk) > 2:
                del trk[2:]

            if i < len(self.track_list) - 1:
                trk[1] = trk[1] + '\n'

            act2 = ActionChains(self.driver)

            act2.send_keys(trk[0] + '\t')

            sleep(1)

            act2.send_keys(trk[1])
            act2.perform()

            del act2

            sleep(1)

        return

    def enter_show_image(self):
        '''
        Enter path for show's image
        '''
        self.driver \
            .find_element_by_xpath('''//input[@m-file-input-model='cloudcastEdit.picture']''') \
            .send_keys(self.art)

        sleep(1)

        return

    def add_tags(self):
        '''
        Enter tags for the show
        '''
        tags = ['Liquid Drum and Bass,',
                'Drum & Bass,',
                'Drum and Bass,',
                'Seattle,']

        tag_elem = self.driver \
                       .find_element_by_xpath('''//input[@ng-model='newToken']''')
        print('Adding Tags:')
        for t in tags:
            print t
            tag_elem.send_keys(t)

            sleep(0.5)

        sleep(1)

        return

    def scroll_to_element(self, element):
        '''
        Scroll till element is within view
        '''
        loc = element.location_once_scrolled_into_view

        self.driver \
            .execute_script("window.scrollTo(0, " + str(loc['y']) + ");")

        return

    def save_edits(self):
        '''
        Save edits made to show page
        '''
        sleep(1)

        self.driver \
            .execute_script("window.scrollTo(0, document.body.scrollHeight);")

        self.driver \
            .find_element_by_xpath('''//div[@m-click='save()']''') \
            .click()

        sleep(20)

        return

    def shutdown(self):
        '''
        Close Chrome webdriver
        '''
        self.driver.close()

        return

    def publish(self):
        '''
        Execute entire workflow to publish show
        '''
        print('Launch mixcloud driver')
        self.launch()

        self.login()

        print('Beign publishing')
        self.goto_upload_page()

        self.select_file()

        self.enter_show_name()

        print('Upload show')
        self.upload()

        self.enter_show_image()

        self.add_tags()

        self.enter_track_list()

        print('Publishing complete')
        self.save_edits()

        print('Shutdown mixcloud driver\n')
        self.shutdown()

        return

    def _sleep_progress(self, length):
        '''
        Input:
            - length: time in seconds to wait till next API call (INT)
        Output:
            - None
        '''
        toolbar_width = 40

        # setup toolbar
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write("\b" * (toolbar_width+1)) # return to start of line, after '['

        increment = length / float(toolbar_width)
        for i in xrange(toolbar_width):
            sleep(increment)
            # update the bar
            sys.stdout.write("-")
            sys.stdout.flush()

        sys.stdout.write("\n")
        return
