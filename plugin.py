###
# Copyright (c) 2013, Gabriel Morell-Pacheco
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.world as world
import supybot.ircmsgs as ircmsgs

import urllib2,base64,simplejson
def sec_to_h_m_s(seconds):
    hrs = seconds / 3600
    r_h = seconds % 3600
    
    mins = r_h / 60
    r_m = r_h % 60
    
    secs = r_m
    
    return hrs,mins,secs

class XBMCctl(callbacks.Plugin):
    """Add the help for "@plugin help XBMCctl" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def __init__(self,irc,host="localhost",port="8080"):
        self.__parent = super(XBMCctl,self)
        self.__parent.__init__(irc)
        self.host = host
        self.port = port
        self.uname = "xbmc"
        self.pw = "dicks"
        
        self.b64auth =  base64.encodestring("%s:%s" % (self.uname,self.pw))
        self.authheadera = "Authorization"
        self.authheaderb = "Basic %s" % self.b64auth.replace('\n','')
        self.url = 'http://%s:%s/jsonrpc' % (self.host,self.port)
    def query(self,data):
        req = urllib2.Request(self.url,data,{'Content-Type': 'application/json'})
        req.add_header(self.authheadera,self.authheaderb)
        resp = urllib2.urlopen(req).read()
        return resp
    def np(self,irc,msg,args):
        data = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        resp = self.query(data)
        o = simplejson.loads(resp)
        if o['result']:
            if o['result'][0]['type'] == "audio":
                data = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "duration", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 0 }, "id": "AudioGetItem"}'
                a = simplejson.loads(self.query(data))
                
                artist = " ".join(x for x in a['result']['item']['artist'])
                title = a['result']['item']['title']
                album = a['result']['item']['album']
                irc.reply("NP: %s by %s on %s" % (title,artist,album))
            else:
                data = '{"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "artist", "season", "episode", "duration", "showtitle", "tvshowid", "thumbnail", "file", "fanart", "streamdetails"], "playerid": 1 }, "id": "VideoGetItem"}'
                v = simplejson.loads(self.query(data))
                i = v['result']['item']
                if i['type'] == "episode":
                    title = i['showtitle']
                    eptitle = i['title']
                    season = i['season']
                    ep = i['episode']
                    irc.reply('NP: "%s" from %s [S%sE%s]' % (eptitle,title,season,ep))
                elif i['type'] == "movie":
                    title = i['title']
                    irc.reply('NP: %s' % title)
                else:
                    label = i['label']
                    irc.reply('NP: %s' % label)
        else:
            irc.reply("XBMC isn't playing anything atm")
    np = wrap(np)
    def pause(self,irc,msg,args):
        data = '{"jsonrpc": "2.0", "method": "Player.PlayPause", "params": { "playerid": 1 }, "id": 1}'
        resp = self.query(data)
        reply = simplejson.loads(resp)
        if reply['result']['speed']:
            irc.reply('XBMC is now Playing')
        else:
            irc.reply('XBMC has been Paused')
    pause = wrap(pause)
    
    def seek(self,irc,msg,args,text):
        time = int(text)
        data = '{"jsonrpc": "2.0", "method": "Player.Seek", "params": { "playerid": 1, "value": {"hours" : %s, "minutes" : %s, "seconds": %s, "milliseconds": 0 }}}' % (sec_to_h_m_s(time))
        resp = self.query(data)
        
        irc.reply("seeked to %s seconds" % text) 
    
    seek = wrap(seek,['text'])
    
    def recenttv(self,irc,msg,args):
        data = '{ "jsonrpc": "2.0", "method": "VideoLibrary.GetRecentlyAddedEpisodes", "params": { "properties": [ "title", "showtitle", "tvshowid", "uniqueid" ,"file" ] }, "id": 1 }'
        resp = self.query(data)
        reply = simplejson.loads(resp)
        irc.reply(reply)
    recenttv = wrap(recenttv)

    def playtv(self,irc,msg,args,text):
        data = '{ "jsonrpc": "2.0", "method": "Player.Open", "params": { "item": { "file": "%s" } }, "id": 1 }' % text
        irc.reply(data) 
        resp = self.query(data)
        reply = simplejson.loads(resp)
        irc.reply(resp) 
    
    playtv = wrap(playtv,['text'])
    
Class = XBMCctl


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
