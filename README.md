Darui
-----

#### Introduction

Darui is a simple program written in python. It parses rss feeds and matches
feed entries against supplied keywords. It undertakes to do the tedious work
of filtering your rss entries. Matched entries are sent to your email using
python's smtplib.
It is named after an [anime character](http://naruto.wikia.com/wiki/Darui) who
is constantly referring to things or events as being "dull".

#### Dependencies

* python >= 3
* feedparser >= 5.1

#### Configuration

Darui uses the [JSON](http://json.org/example.html) file format for its configuration
file. It expects a file named `darui.json` in one of the following paths:

* path stored in $XDG_CONFIG_HOME (defaults to ~/.config)
* path from where program runs

Sample configuration file:
```
{
    "email": {
        "from": "",
        "to": ""
    },
    "feeds": [
        { "rss" : "http://www.archlinux.org/feeds/packages/", "rules": [
            "gstreamer",
            "udev",
            "sqlite"
            ]
        },
        { "rss" : "http://rss.feedsportal.com/c/32569/f/491735/index.rss", "rules": [
            "kernel log",
            "new in linux"
            ]
        }
    ]
}

```
The first entry, matches all archlinux packages with "gstreamer", "udev" or "sqlite" in their name.
The second entry matches all articles at [H-Online](http://www.h-online.com/open/)
relevant to new linux kernel releases. Note that searches are *not* case-sensitive.

The "from" and "to" field are used for email sending and are self explanatory.

### License

This program is free software; you can redistribute it and/or modify it under the terms of
the GNU General Public License as published by the Free Software Foundation version 3 of the License.

A copy of theGNU General Public License can be found in [GNU Licence Page](http://www.gnu.org/licenses/gpl.html)

### Credits

2011-2012 Tasos Latsas
