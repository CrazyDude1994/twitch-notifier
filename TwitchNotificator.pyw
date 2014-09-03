from urllib2 import urlopen, URLError
from json import loads
from time import sleep
from gntp import notifier

TWITCH_API_URL = "https://api.twitch.tv/kraken"
SLEEP_TIME = 60 * 5
ICON_URL = "http://www.reelnreel.com/wp-content/uploads/2014/05/0f3b7b62-1a8c-4c54-b5a2-836186d376dd.png"

class TwitchStream:

    def __init__(self, stream_name):
        self.stream_name = stream_name
        self.online = False
        self.title = ""
        self.game = ""
        self.avatar = ""

class TwitchNotify:

    def __init__(self, stream_names):
        self.streams = [TwitchStream(stream) for stream in stream_names]
        self.working = True
        self.notifier = None
        self.worker()

    def initNotifier(self):
        try:
            self.notifier = notifier.GrowlNotifier("Twitch.tv Notifier", ["Stream online", "Stream offline", "Info changed"], 
                                                   ["Stream online", "Stream offline", "Info changed"])
            self.notifier.register()
        except:
            return

    def worker(self):
        while self.working:
            if self.notifier:
                self.check_online()
            else:
                self.initNotifier()
            sleep(SLEEP_TIME)

    def check_online(self):
        for stream in self.streams:
            try:
                url = urlopen(TWITCH_API_URL + "/streams/{0}".format(stream.stream_name))
                json_object = loads(url.read())
            except URLError as error:
                print "Failed to retrieve HTTP request. {0}".format(error.message)
                continue
            except ValueError as error:
                print "Failed to parse HTTP request as JSON. {0}".format(error.message)
                continue
            except:
                print "Unexpected error"
                continue
            else:
                if json_object["stream"] == None:
                    if stream.online == True:
                        stream.online = False
                        self.onStreamChangedOnline(False, stream)
                else:
                    if stream.online == False:
                        stream.online = True
                        stream.game = json_object["stream"]["game"]
                        stream.avatar = json_object["stream"]["channel"]["logo"]
                        stream.title = json_object["stream"]["channel"]["status"]
                        self.onStreamChangedOnline(True, stream)
                    else:
                        if (stream.game != json_object["stream"]["channel"]["game"]) or (stream.title != json_object["stream"]["channel"]["status"]):
                            stream.game = json_object["stream"]["channel"]["game"]
                            stream.title = json_object["stream"]["channel"]["status"]
                            self.onStreamChangedInfo(stream.game, stream.title, stream)

    def onStreamChangedOnline(self, newState, stream):
        if newState == True:
            print "Stream just went online!"
            if stream.game:
                self.notifier.notify("Stream online", "{0} is online playing {1}".format(stream.stream_name, stream.game),
                                     "Title: {1}\rLeft click on notification to watch stream!".
                                     format(stream.stream_name, stream.title),
                                     stream.avatar or ICON_URL, True, None, "http://twitch.tv/{0}".format(stream.stream_name))
            else:
                self.notifier.notify("Stream online", "{0} is online".format(stream.stream_name),
                                     "Title: {1}\rLeft click on notification to watch stream!".
                                     format(stream.stream_name, stream.title),
                                     stream.avatar or ICON_URL, True, None, "http://twitch.tv/{0}".format(stream.stream_name))
        else:
            print "Stream just went offline"
            self.notifier.notify("Stream offline", "{0} is offline".format(stream.stream_name), "{0} is not online anymore!".format(stream.stream_name),
                                 stream.avatar or ICON_URL, False)

    def onStreamChangedInfo(self, newGame, newTitle, stream):
        print "Stream changed info"
        if stream.game:
            self.notifier.notify("Info changed", "{0} is now playing {1}".format(stream.stream_name, stream.game),
                            "Title: {1}\rLeft click on notification to watch stream!".
                            format(stream.stream_name, stream.title),
                            stream.avatar or ICON_URL, True, None, "http://twitch.tv/{0}".format(stream.stream_name))
        else:
            self.notifier.notify("Info changed", "{0} is not playing anything".format(stream.stream_name),
                "Title: {1}\rLeft click on notification to watch stream!".
                format(stream.stream_name, stream.title),
                stream.avatar or ICON_URL, True, None, "http://twitch.tv/{0}".format(stream.stream_name))

if __name__ == "__main__":
    TwitchNotify(["starladder1", "etozhemad", "dreadztv", "c_a_k_e", "lirik", "sing_sing", "crazydude1994"])