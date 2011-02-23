#!/usr/bin/env python
import vlc

instance = vlc.Instance()
media = 0;
media=instance.media_new('v4l2:///dev/video0')
player = instance.media_player_new()
player.set_media(media)
player.play()

while True:
    pass
