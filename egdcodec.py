# -*- coding: utf-8 -*-
import codecs

def egd_replace(e):
    if e.object[e.start:e.end] == u'ö':
        return (u'oe', e.end)
    elif e.object[e.start:e.end] == u'Ö':
        return (u'Oe', e.end)
    elif e.object[e.start:e.end] == u'Ä':
        return (u'Ae', e.end)
    elif e.object[e.start:e.end] == u'ä':
        return (u'ae', e.end)
    elif e.object[e.start:e.end] == u'Å':
        return (u'Aa', e.end)
    elif e.object[e.start:e.end] == u'å':
        return (u'aa', e.end)
    elif e.object[e.start:e.end] == u'é':
        return (u'e', e.end)
    return codecs.ignore_errors(e)

