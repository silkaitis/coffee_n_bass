import sys
import yaml

from dnb_classes import tracklister, dnbradio, dnbforum, dogsonacid, site_keys, mixcloud
from time import sleep

'''
Script requires three inputs from the command line. Image file name must
include full path.

Example:
python show_updater.py my_latest_show.m3u8
                       ~/Users/jdoe/Pictures/my_show_picture.jpg

INPUT
    my_latest_show.m3u8 - Track list exported from Rekordbox, M3U8
    ~/Users/jdoe/Pictures/my_show_picture.jpg - Image, JPG

OUTPUT
    None
'''

if __name__ == '__main__':
    '''
    Load credentials
    '''
    dnb_keys = site_keys('/Users/danius/Documents/Github/coffee_n_bass/src/usr_pswd.yaml')
    dnb_keys.build()

    '''
    Load tracks from show
    '''
    tracks = tracklister(sys.argv[1])

    '''
    Update DNBRadio
    '''
    dnbr = dnbradio(dnb_keys.dnbradio, tracks.build())
    dnbr.publish()

    '''
    Post to DNBForum
    '''
    dnbf = dnbforum(dnb_keys.dnbforum, dnbr.bbc)
    dnbf.publish()

    '''
    Post to dogsonacid
    '''
    doa = dogsonacid(dnb_keys.doa, dnbr.bbc)
    doa.publish()

    '''
    Post to mixcloud
    '''
    mxcld = mixcloud(dnb_keys.mixcloud, tracks.build(), dnbr.show_filename)
    mxcld.publish()

    print(dnbr.show_filename + 'successfully published.')
