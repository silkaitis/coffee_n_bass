import sys
import yaml

from time import sleep
from dnb_classes import site_keys,tracklister, dnbradio, dnbforum, dogsonacid, mixcloud, soundcloud, bmills_selecta

'''
Script requires one input from the command line.

Example:
python show_updater.py my_latest_show.m3u8

INPUT
    my_latest_show.m3u8 - Track list exported from Rekordbox, M3U8

OUTPUT
    None
'''

if __name__ == '__main__':
    '''
    Pick artwork
    '''
    art = bmills_selecta()
    dnbr_art, cld_art = art.deliver()

    '''
    Load credentials
    '''
    dnb_keys = site_keys('/Users/danius/Documents/Github/coffee_n_bass/src/usr_pswd.yaml')
    dnb_keys.build()

    '''
    Load tracks from show
    '''
    track = tracklister(sys.argv[1])
    track.build()

    '''
    Update DNBRadio
    '''
    dnbr = dnbradio(dnb_keys.dnbradio, track.list, dnbr_art)
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
    mxcld = mixcloud(dnb_keys.mixcloud, track.list, dnbr.show_filename, cld_art)
    mxcld.publish()

    # '''
    # Post to soundcloud
    # '''
    sdcld = soundcloud(dnb_keys.soundcloud, track.list, dnbr.show_filename, cld_art)
    sdcld.publish()

    print(mxcld.title + ' successfully published.')
