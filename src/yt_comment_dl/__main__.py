#!/usr/bin/env python

import yt_comment_dl

if __package__ is None:
    import sys, os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


if __name__ == "__main__":
    yt_comment_dl.main()
