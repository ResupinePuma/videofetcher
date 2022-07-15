# Videofetcher - Simple telegram bot to fetch videos from social networks

Bot uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) library to fetch videos from [supported sites](https://ytdl-org.github.io/youtube-dl/supportedsites.html) and custom parsers for tiktok, pikabu etc.
For avoiding captcha bot emutales human behavior via [splash](https://splash.readthedocs.io/en/stable/index.html).

### Deployment

For deployment needed docker and docker-compose.
Run ```docker-compose up```, edit config.ini file (check videofetcher folder after first run), ```docker-compose restart``` and continue to use bot.

In addition add cleaner.sh to auto remove weekly downlaoded videos from temp folder.


### Analytics

Bot can write messages into console, ndjson file or elsticsearch. You must select what do you want in `config.ini`

### To-Do

- proxy support
- admin commands
