#!/usr/bin/env python

from sys import exit, version_info
if version_info[0] < 3:
    print("Error, this script needs python version 3 or higher")
    exit(1)

try:
    import feedparser
except:
    print("Error, could not import feedparser library")
    exit(1)

import os
import re
import smtplib
import argparse
from json import load
from email.mime.text import MIMEText
from datetime import datetime
import time
from getpass import getuser

__version__ = "0.6"

def cmd_parse():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Parses rss feeds and emails entries matched against supplied keywords",
        version=__version__)

    parser.add_argument("-p", "--print", action="store_true", default=False,
        help="Print results to stdout [default off]")

    parser.add_argument("-f", "--file", dest="cfg_file", default=None,
        help="Override standard search path and use specified configuration file")

    parser.add_argument("--no-email", action="store_true", default=False,
        help="Do not send email (useful for debug in conjunction with -p)")

    return parser.parse_args()


def read_config(cfg_file = None):
    """Read JSON formated configuration file

    searches for `darui.json` in path defined in $XDG_CONFIG_HOME environment
    variable (defaults to ~/.config) and in the path from where program runs
    if no configuration file is found or on open/parse error returns None
    """
    if cfg_file is None:
        config_filename = "darui.json"
        config_list = [ ]

        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            config_list.append(os.path.join(xdg, config_filename))

        config_list.append(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), config_filename)
        )
    else:
        # do not search standard paths, use specific file
        config_list = [cfg_file]

    config_contents = None
    for config in config_list:
        if os.path.isfile(config):
            try:
                with open(config) as f:
                    config_contents = load(f)
            except:
                print("Error opening configuration file", config)
                return None

            return config_contents

    return None


class Darui (object):

    def __init__(self, cfg, ts_path="/var/tmp"):
        self.cfg = cfg
        self.results = { }
        self.report = ""
        self.ts_file = ""
        self.last_checked = 0

        # file to store last time we parsed a feed
        # default: /var/tmp/[username].darui
        try:
            filename = '.'.join((getuser(), "darui"))
            self.ts_file = os.path.join(ts_path, filename)
            self._read_ts()
        except:
            pass

    def parse(self):
        """Parse rss feeds and try to match feed titles using regex"""
        for feed in self.cfg['feeds']:
            pf = feedparser.parse(feed['rss'])

            rules = ""
            if feed['rules']:
                if len(feed['rules']) > 1:
                    rules = "|".join(feed['rules'])
                else:
                    rules = feed['rules'][0]

            try:
                regex = re.compile(rules, re.I)
            except re.error:
                print("Error compiling regex for rss: ", feed['rss'])
                continue

            for entry in pf.entries:
                if regex.search(entry.title):
                    if pf.feed.title in self.results:
                        self.results[pf.feed.title].append((entry.title, entry.link))
                    else:
                        self.results[pf.feed.title] = [(entry.title, entry.link)]

        # parse done, save timestamp
        self._save_ts()

    def print_results(self):
        self._build_report()
        print(self.report)

    def email_results(self):
        self._build_report()
        if self.report:
            msg = MIMEText(self.report)
            msg['Subject'] = ''.join(
                ('[darui report] ', datetime.now().strftime("%Y-%m-%d %H:%M"))
            )
            msg_from = self.cfg['email']['from']
            msg_to = self.cfg['email']['to']
            msg['From'] = msg_from
            msg['To'] = msg_to

            s = smtplib.SMTP('localhost')
            s.sendmail(msg_from, msg_to, msg.as_string())
            s.quit()

    def _build_report(self):
        """Create a multiline string from results"""
        if self.results:
            # reset report
            self.report = ""
            for rss_title, matched_items in self.results.items():
                self.report = ''.join((self.report, rss_title, "\n"))
                for title, url in matched_items:
                    self.report = ''.join((self.report, ":: ", title, " [", url, "]\n"))
                self.report = ''.join((self.report, "\n"))

    def _read_ts(self):
        """read timestamp - represents the last time we parsed feeds"""
        try:
            with open(self.ts_file) as f:
                self.last_checked = float(f.read().strip('\n'))
        except:
            return

    def _save_ts(self):
        """save timestamp"""
        try:
            with open(self.ts_file, 'w') as f:
                now = datetime.now().timetuple()
                f.write(str(time.mktime(now)))
        except:
            return


if __name__ == "__main__":
    # parse command line arguments
    args = cmd_parse()

    # read config file
    cfg = read_config(args.cfg_file)
    if cfg is None:
        print("Cannot find suitable configuration file, aborting...")
        exit(1)

    # parse our feeds
    darui = Darui(cfg)
    darui.parse()

    if args.print is True:
        darui.print_results()

    if args.no_email is True:
        exit(0)

    darui.email_results()

