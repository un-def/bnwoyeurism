bnwoyeurism
===========

Desktop notifications for new BnW posts/comments.



### Requirements

* Python 2
* pynotify (python-notify)
* websocket ([websocket-client](https://pypi.python.org/pypi/websocket-client/))
* gtk, gobject



### Usage

```bnwoyeurism.py [-p|-c|-a] [-w default|meow|6nw] [@|user1 user2 user3 …]```

```-p```, ```--posts``` — show only posts

```-c```, ```--comments``` — show only comments

```-a```, ```--all``` — show both posts and comments (default)

```-w```, ```--web``` — web interface for posts/comments links

```@``` — show notifications from all users

```user1 user2 user3``` — show notifications only from user1, user2, and user3



### ~/.bnwoyeurism/users

Default list of users (if users not specified via command line args). One user per line.



### Examples

```bnwoyeurism.py @``` — show posts and comments from all users

```bnwoyeurism.py -c alice bob``` — show comments from **alice** and **bob**

```bnwoyeurism.py -a```, ```bnwoyeurism.py``` — show comments and posts from users specified in **~/.bnwoyeurism/users** or all users (if **~/.bnwoyeurism/users** doesn't exist)
