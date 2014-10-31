#  Project: lnotify
#  Description: A libnotify script that sends notifications
#  to a client through a socket.  The client does all the
#  actual work and nofification in the remote system.
#  Author: Nicholas Alipaz <nicholas@alipaz.net>
#
import weechat as weechat, string, os, urllib, urllib2, shlex, zmq, json

lnotify_name = "lnotify"
lnotify_version = "0.2.0"
lnotify_license = "GPL3"

# Setup zmq
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5000")

# convenient table checking for bools
true = { "on": True, "off": False }

# declare this here, will be global config() object
# but is initialized in __main__
cfg = None

class config(object):
    def __init__(self):
        # default options for lnotify
        self.opts = {
            "highlight": "on",
            "highlight_sound": "",
            "query": "on",
            "query_sound": "",
            "sounds": "off",
            "sound_cmd": "/usr/bin/aplay",
            "notify_away": "off",
            "notify_current_channel": "on",
            "icon": "weechat",
            "nick_blacklist": "--,-->",
            "irssi_notifications": "off",
            "irssi_api_token": "",
            "irssi_encryption_password": ""
        }

        self.init_config()
        self.check_config()

    def init_config(self):
        for opt, value in self.opts.items():
            temp = weechat.config_get_plugin(opt)
            if not len(temp):
                weechat.config_set_plugin(opt, value)

    def check_config(self):
        for opt in self.opts:
            self.opts[opt] = weechat.config_get_plugin(opt)

    def __getitem__(self, key):
        return self.opts[key]

def printc(msg):
    weechat.prnt("", msg)

def handle_msg(data, pbuffer, date, tags, displayed, highlight, prefix, message):
    highlight = bool(highlight == "1") and true[cfg["highlight"]]
    query = true[cfg["query"]]
    notify_away = true[cfg["notify_away"]]
    notify_current_channel = true[cfg["notify_current_channel"]]
    buffer_type = weechat.buffer_get_string(pbuffer, "localvar_type")
    away = weechat.buffer_get_string(pbuffer, "localvar_away")

    if prefix == weechat.buffer_get_string(pbuffer,"localvar_nick"):
        return weechat.WEECHAT_RC_OK

    if pbuffer == weechat.current_buffer() and not notify_current_channel:
        return weechat.WEECHAT_RC_OK

    if away and not notify_away:
        return weechat.WEECHAT_RC_OK

    if prefix == "":
        return weechat.WEECHAT_RC_OK

    nick_blacklist = cfg["nick_blacklist"].split(",")
    for nick in nick_blacklist:
        if prefix == nick:
            return weechat.WEECHAT_RC_OK
            break

    buffer_name = weechat.buffer_get_string(pbuffer, "short_name")
    if pbuffer == weechat.current_buffer() and buffer_type == "private" and query:
        notify_user("WeeChat: Private Message from {}".format(prefix), message, prefix, buffer_name, "query")

    elif buffer_type == "private" and query:
        notify_user("WeeChat: Private Message from {}".format(prefix), message, prefix, buffer_name, "highlight")

    elif buffer_type == "channel" and highlight:
        notify_user("WeeChat: Message from {} ({})".format(prefix, buffer_name), message, prefix, buffer_name, "highlight")

    return weechat.WEECHAT_RC_OK

def process_cb(data, command, return_code, out, err):
    if return_code == weechat.WEECHAT_HOOK_PROCESS_ERROR:
        weechat.prnt("", "Error with command '%s'" % command)
    elif return_code != 0:
        weechat.prnt("", "return_code = %d" % return_code)
        weechat.prnt("", "notify-send has an error")

    return weechat.WEECHAT_RC_OK

def notify_user(origin, message, nick, channel, query_type):
    info = {
        "origin": origin,
        "message": message,
        "nick": nick,
        "channel": channel,
        "query_type": query_type,
        "highlight_sound": cfg["highlight_sound"],
        "query_sound": cfg["query_sound"],
        "sounds": true[cfg["sounds"]],
        "sound_cmd": cfg["sound_cmd"],
        "icon": cfg["icon"]
    }
    info = json.dumps(info)
    socket.send("message " + info)

    return weechat.WEECHAT_RC_OK

# execute initializations in order
if __name__ == "__main__":
    weechat.register(lnotify_name, "kevr", lnotify_version, lnotify_license,
        "{} - A libnotify script for weechat".format(lnotify_name), "", "")

    cfg = config()
    print_hook = weechat.hook_print("", "", "", 1, "handle_msg", "")
