#!/usr/bin/python

import glob
import os
import shutil
import sys
import re

from xml.dom.minidom import parseString

last_sync = 0
current_filename = ""

def process_sync_tag(matchobj):
    global last_sync
    current_sync = int( matchobj.group(1) )
    if current_sync < last_sync:
        if last_sync - current_sync >= 10000:
            print "%s: %d (last: %d)"%(current_filename, current_sync, last_sync)
            return ""
    
    if (current_sync / 30000) != (last_sync / 30000):
        last_sync = current_sync
        current_sync = (current_sync / 30000)*30000
        return "[%02d:%02d] "%(current_sync/60000,(current_sync%60000)/1000 )
    else:
        return ""

def strip_smi(filename):
    global current_filename, last_sync
    print "Stripping %s"%filename
    
    shutil.copy2(filename, "%s.bak"%filename)
    current_filename = filename
    
    with open(filename) as f_smi:
        smi_content = f_smi.read()

    smi_body_open_index = smi_content.lower().find("<body>")
    if smi_body_open_index == -1:
        print "ERROR: %s <BODY> tag not exists." % filename
        sys.exit(1)
    smi_content = smi_content[smi_body_open_index + len("<BODY>"):]

    # strip tags
    rec_remove_tag = re.compile(r"""<(?!(SYNC))[^>]+>""")
    smi_content = rec_remove_tag.sub("", smi_content)

    # strip &nbsp; etc
    rec_remove_tag = re.compile(r"""&[^;]+;""")
    smi_content = rec_remove_tag.sub("", smi_content)

    # replace non-ascii characters with ?
    smi_content = "".join((c if ord(c) < 128 else '?' for c in smi_content))

    rec_sync = re.compile(r"""<SYNC[^>]+START=([0-9]+)>""", re.IGNORECASE)
    smi_content = rec_sync.sub(process_sync_tag, smi_content)

    # replace CR/NF
    rec_remove_crlf = re.compile(r"""(?:\n|\r|\r\n?)""")
    smi_content = rec_remove_crlf.sub("\n", smi_content)

    # replace multiple ?? s (non-ascii characters)
    rec_remove_question = re.compile(r"""[?][?].*[?][?]""")
    smi_content = rec_remove_question.sub("", smi_content)


    # strip empty lines
    rec_remove_newline = re.compile(r"""(?:\n|\r|\r\n?){2}( *(?:\n|\r|\r\n?))+""", re.MULTILINE)
    smi_content = rec_remove_newline.sub("\n", smi_content)

    with open("%s.txt"%filename[14:], "w") as f_smi:
        f_smi.write(smi_content)
        
    last_sync = 0
    current_filename = ""
    
filelist = filter(lambda x: x.lower().endswith("smi"), os.listdir("."))
map(strip_smi, filelist)

