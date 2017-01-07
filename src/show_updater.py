import sys
import yaml

from dnb_classes import tracklister, dnbradio, site_keys
from time import sleep

'''
Script requires three inputs from the command line. Image file name must
include full path.

Example:
python show_updater.py usr_pswd.yaml
                       my_latest_show.m3u8
                       ~/Users/jdoe/Pictures/my_show_picture.jpg

INPUT
    usr_pswd.yaml - Usernames and passwords for sites listed below, YAML
                        dnbradio
                        dnbforum
                        dogsonacid
    my_latest_show.m3u8 - Track list exported from Rekordbox, M3U8
    ~/Users/jdoe/Pictures/my_show_picture.jpg - Image, JPG

OUTPUT
    None
'''

if __name__ == '__main__':
    '''
    Load credentials
    '''
    dnb_keys = site_keys(sys.argv[1])
    dnb_keys.build()

    '''
    Load tracks from show
    '''
    tracks = tracklister(sys.argv[2])

    '''
    Update DNBRadio
    '''
    dnbr = dnbradio(dnb_keys.dnbradio, tracks.build())
    dnbr.update_show()
