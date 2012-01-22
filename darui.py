#!/bin/env python

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
from json import load
from email.mime.text import MIMEText
from datetime import datetime


def read_config():
    """Read JSON formated configuration file

    searches for `darui.json` in path defined in $XDG_CONFIG_HOME environment
    variable (defaults to ~/.config) and in the path from where program runs
    if no configuration file is found or on open/parse error returns None
    """
    config_file = "darui.json"
    config_list = [ ]
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        config_list.append(os.path.join(xdg, config_file))

    config_list.append(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), config_file)
    )

    config_contents = None
    for config in config_list:
        if os.path.isfile(config):
            try:
                fp = open(config, 'r')
                try:
                    config_contents = load(fp)
                except:
                    print("Error reading configuration file", config)
                finally:
                    fp.close()
            except:
                print("Error opening configuration file", config)
                return None
            return config_contents

    return None


class Darui (object):
    def __init__(self, cfg):
        self.cfg = cfg
        self.results = { }
        self.report = ""

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


if __name__ == "__main__":
    cfg = read_config()
    if cfg is None:
        print("Cannot find suitable configuration file, aborting...")
        exit(1)
    darui = Darui(cfg)
    darui.parse()
    #darui.print_results()
    darui.email_results()

