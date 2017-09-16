import sys
import yaml

from time import sleep
from dnb_classes import site_keys, tracklister, dnbradio, dnbforum, dogsonacid, mixcloud, soundcloud

'''
Script requires three inputs from the command line. Image file name must
include full path.

Example:
python show_updater.py my_latest_show.m3u8

INPUT
    my_latest_show.m3u8 - Track list exported from Rekordbox, M3U8

OUTPUT
    None
'''



def fix_mcloud(name, art):
    '''
    Load credentials
    '''
    dnb_keys = site_keys('/Users/slice/Documents/Github/coffee_n_bass/src/usr_pswd.yaml')
    dnb_keys.build()

    '''
    Load tracks from show
    '''
    track = tracklister(name)
    track.build()

    '''
    Update DNBRadio
    '''
    dnbr = dnbradio(dnb_keys.dnbradio, track.list, 'a')
    dnbr.reload()

    '''
    Artwork
    '''
    cld_art = '/Users/slice/Documents/Github/coffee_n_bass/cover_art/other/{}'.format(art)

    '''
    Post to mixcloud
    '''
    mxcld = mixcloud(dnb_keys.mixcloud, track.list, dnbr.show_filename, cld_art)
    dnbf = dnbforum(dnb_keys.dnbforum, dnbr.bbc)
    doa = dogsonacid(dnb_keys.doa, dnbr.bbc)
    sdcld = soundcloud(dnb_keys.soundcloud, track.list, dnbr.show_filename, cld_art)

    return(mxcld, dnbf, doa, sdcld)
#
# if __name__ == '__main__':

#
#     mxcld, dnbf, doa, sdcld = fix_mcloud(sys.argv[1])
#
#     import pdb; pdb.set_trace()
