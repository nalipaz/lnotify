lnotify.py
=======

Personal modifications to the WeeChat lnotify.py script.

Supports:
 * Highlighting messages through the use of watch words (weechat.look.highlight), private messages, nick mentions.
 * Sound notifications through the use of aplay (by default) and a custom file.
 * Blacklisting nicks that shouldn't trigger a notification.
 * Configurable icon for libnotify.
 * Disabling of notifications when you are "away".
 * Disabling notifications for the channel in the current buffer.

This runs well for me with WeeChat running remotely on my server, but forks and pull requests are gladly accepted.

There is a client that needs to run locally, you can start it running by executing:
```
(/path/to/lnotify-client.py hostname &) &> /dev/null
```
