## Banishing Tedium

### A smattering of tools I use to reduce the drudgery of being a computer user (one that likes the command line).

Highlights:

- utils.py in lib has some things that can make your life easier in general
- ytp will search youtube and play videos for you without the need for a browser (mpv needed)
- ytd will do the same but download the videos
- imdb will allow you to query the imdb for movie / tv show info, again without the need for a browser
- dsubs downloads subtitles for all media in the cwd and below
- pbkp.py does a backup of my environment making it so I don't need to worry about starting over at a new computer
- pp checks if you're online, I cannot stress how much this has helped me over the years
- synctime - on BSDs my experience with ntp daemons is they jack up start up times and have me waiting longer than
  I'm ready to accept, so I usually disable ntp and use this to sync time using an ntp server
- mpip is pip install with some nicer options
- st for sailing the high seas
- and miscellanea to do all sorts of things from starting vms using qemu to searching and playing media quickly


You may need to change bin/priv_init.py to fit your env

Most of the stuff in lib bootstraps itself

Warning: There is minimal strict adherance to best practices and I
instead just try to get the annoyances I experience in my daily
computering addressed, for example you won't find the use of virtual
envrinments here.
