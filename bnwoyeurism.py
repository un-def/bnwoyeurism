#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import sys
import time
import threading
from datetime import datetime
import argparse
import json
import urllib2
import cgi
import webbrowser
import gtk
import gobject
import pynotify
import websocket


web_interfaces = {
    'default': 'https://bnw.im/p/{}',
    'meow': 'https://meow.bnw.im/p/{}',
    '6nw': 'https://6nw.im/p/{}',
}


parser = argparse.ArgumentParser(description="bnwoyeurism — desktop notifications for new BnW posts/comments")
parser.add_argument('-p', '--posts', action='store_true', help="show only posts")
parser.add_argument('-c', '--comments', action='store_true', help="show only comments")
parser.add_argument('-a', '--all', action='store_true', help="show both posts and comments")
parser.add_argument('-w', '--web', choices=web_interfaces.keys(), default='default', help="web interface")
parser.add_argument('users', nargs='*', metavar='user', help="space separated list of users or '@'")
args = parser.parse_args()


class BnWebSocketException(Exception):

    pass


class BnWebSocket(websocket.WebSocketApp):

    def __init__(self, url, ws_type, notifications):
        # ws_type = 'post' | 'comment'
        self.ws_type = ws_type
        self.notifications = notifications
        super(BnWebSocket, self).__init__   (   url,
                                                on_open = self.on_open,
                                                on_close = self.on_close,
                                                on_message = self.on_message,
                                                on_error = self.on_error,
                                            )

    def on_open(self, ws):
        print("*** {0}s ws started on {1:%X %x}".format(self.ws_type, datetime.now()))

    def on_close(self, ws):
        print("*** {0}s ws closed on {1:%X %x}".format(self.ws_type, datetime.now()))

    def on_error(self, ws, error):
        print("*** {0}s ws error on {1:%X %x}: {2}".format(self.ws_type, datetime.now(), error))
        raise BnWebSocketException(error)

    def on_message(self, ws, message):
        message = json.loads(message)
        if users == 'all' or message['user'] in users:
            print("[{0}] [{1:%X}] #{2} {3}: {4}".format(self.ws_type, datetime.now(), message['id'], message['user'], message['text']))
            n_title = "{0} :: {1}".format(message['user'], self.ws_type)
            n_message = cgi.escape(self.truncate_text(message['text']))
            if self.ws_type == 'comment':
                n_message = "<i>{0}</i>\n\n{1}".format(cgi.escape(message['replytotext']), n_message)
            n_icon = self.get_avatar(message['user'])
            n_action = ('show', "#"+message['id'], lambda n, a, m=message['id']: self.show_cb(n, a, m))
            gobject.idle_add(lambda: self.show_notification(n_title, n_message, n_icon, n_action))

    def show_notification(self, title, message, icon, *actions):
        # action = (action, label, callback[, user_data])
        n = pynotify.Notification(title, message, icon)
        if actions:
            for action in actions:
                n.add_action(*action)
        n.connect('closed', self.close_cb)
        n.show()
        self.notifications.append(n)

    def show_cb(self, n, action, message_id):
        n.close()
        webbrowser.open(web_link.format(message_id.replace('/', '#')))

    def close_cb(self, n):
        self.notifications.remove(n)

    def get_avatar(self, user):
        avatar_file = os.path.join(avatars_dir, user)
        if not os.path.exists(avatar_file):
            try:
                avatar_url = 'https://bnw.im/u/{}/avatar/thumb'.format(user)
                u = urllib2.urlopen(avatar_url)
                with open(avatar_file, "wb") as f:
                    f.write(u.read())
            except (urllib2.URLError, urllib2.HTTPError):
                return 'notification-message-im'
        return 'file://' + avatar_file

    def truncate_text(self, text, maxlen=200, tail=30):
        if len(text) > maxlen+tail:
            text = text[:maxlen] + u'[...]'
        return text


def ws_thread(*args):
    while True:
        ws = BnWebSocket(*args)
        try:
            ws.run_forever()
        except BnWebSocketException:
            pass
        time.sleep(1)


if not pynotify.init('bnwoyeurism'):
    sys.exit(1)

app_dir = os.path.join(os.path.expanduser('~'), '.bnwoyeurism')
if not os.path.exists(app_dir):
    os.mkdir(app_dir)
avatars_dir = os.path.join(app_dir, 'avatars')
if not os.path.exists(avatars_dir):
    os.mkdir(avatars_dir)
else:
    for f in os.listdir(avatars_dir):
        os.remove(os.path.join(avatars_dir, f))

if not any((args.posts, args.comments, args.all)):
    args.all = True

web_link = web_interfaces[args.web]

if args.users:
    users = 'all' if '@' in args.users else args.users
else:
    users_file = os.path.join(app_dir, 'users')
    if os.path.isfile(users_file):
        users = []
        with open(users_file) as users_fo:
            for user in users_fo:
                user = user.strip()
                if user:
                    users.append(user)
        if not users:
            users = 'all'
    else:
        users = 'all'

notifications = []
gobject.threads_init()
if args.all or args.posts:
    threading.Thread(target=ws_thread, args=('wss://bnw.im/ws', 'post', notifications)).start()
if args.all or args.comments:
    threading.Thread(target=ws_thread, args=('wss://bnw.im/comments/ws', 'comment', notifications)).start()
gtk.main()
