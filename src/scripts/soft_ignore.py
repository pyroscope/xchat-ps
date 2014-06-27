# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) 2009 Steven Pigeon,
#
# based on earlier version by
#
# Copyright (C) 2004 Marduk Enterprises <marduk@python.net>
#
# minor fixes (in addition to changing message type from
# msg highlight to local console print)
#

# Source: http://hbfs.wordpress.com/2009/03/24/soft-ignore-filter-buggers-in-xchat/

import xchat
import gdbm
import os

from itertools import dropwhile
import string
import re


__module_name__ = 'soft-ignore'
__module_version__ = '0.95'
__module_description__ = """With this plug-in, you can prevent some people
from getting your attention."""

DBFILE = os.environ['HOME'] + '/.xchat2/soft-ignore.conf'
SEPARATOR=''

xchat.prnt('%(name)s, version %(version)s' % {'name': __module_name__,
    'version': __module_version__})

# loads the database
db = gdbm.open(DBFILE,'c')
try:
    nicks = db['soft-ignore'].split(SEPARATOR)
except KeyError:
    db['soft-ignore'] = ''
    nicks = []

# this function strops the colors
# from the nicknames in a safe(r) fashion
def remove_color( nick ):
    # 0 is x3
    # then follows 1 or 2 numbers
    return "".join(list(dropwhile( lambda x : x.isdigit(), nick[1:] )))

# commit changes to database
#
def save_nicks():
    nicks.sort()
    db['soft-ignore'] = SEPARATOR.join(nicks)

# adds a pattern/nick to the list, and
# prints the list if no pattern/nick is
# supplied.
#
def add_soft_ignore(word, word_eol, userdata):
    if len(word) == 1:
        return soft_ignore_list(word, word_eol, userdata)
    for nick in word[1:]:
        if nick not in nicks:
            try:
                re.compile(nick)
            except:
                xchat.prnt('\x032* \x034 %s \x032 is not a valid PCRE' % nick)
            else:
                nicks.append(nick)
                xchat.prnt('\x032* %s will be soft-ignored' % nick)
        else:
            xchat.prnt('\x032* %s is already being soft-ignored' % nick)
        save_nicks()
    return xchat.EAT_XCHAT

# shows soft-ignore-list
#
def soft_ignore_list(word, word_eol, userdata):
    xchat.prnt('\x032Current soft-ignore-list: %d soft-ignored.' % len(nicks) )
    for nick in nicks:
        xchat.prnt('\x032 --- %s' % nick)
    xchat.prnt('\x032* End of soft-ignore list')
    return xchat.EAT_XCHAT

# removes a pattern/nick from the list
# or prints a colorful error if pattern/nick
# is not in the list
#
def delete_soft_ignore(word, word_eol, userdata):
    for nick in word[1:]:
        if nick in nicks:
            nicks.remove(nick)
            xchat.prnt('\x032* %s is removed from soft-ignore list' % nick)
        else:
            xchat.prnt('\x032* \x034 %s \x032 is not in soft-ignore list' % nick)
    save_nicks()
    return xchat.EAT_XCHAT

# filter message according to pattern/nicks
#
def ignore_message(word, word_eol, userdata):
    nick = remove_color(word[0]).lower() # skips the initial coloring
    if ([p for p in nicks if re.match('^'+p+'$',nick,re.IGNORECASE)] or
        word[1][0]=='~'):
        #should be more or less like the normal 'Channel Message' display
        xchat.prnt('\x0314 <%s>\t%s' % (nick,word[1]))
        return xchat.EAT_XCHAT
    else:
        return xchat.EAT_NONE


xchat.hook_command('soft-ignore', add_soft_ignore)
xchat.hook_command('soft-ignore-list', soft_ignore_list)
xchat.hook_command('soft-unignore', delete_soft_ignore)

# here we wanna hook in to the channel message event
xchat.hook_print("Channel Message", ignore_message)
