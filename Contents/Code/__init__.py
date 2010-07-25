from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

CACHE_INTERVAL = 3600*1
AREENA_PREFIX = "/video/areena"
AREENA_NS     = { 'm':'http://search.yahoo.com/mrss/' }
CATEGORIES = {"uutiset" : 115, "urheilu": 114, "ajankohtaisohjelmat": 108, "asiaohjelmat": 102, "viihde": 116, "draama": 109}

def Start():
  Plugin.AddPrefixHandler(AREENA_PREFIX, MainMenu, 'YLE Areena', None, None)
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'Areena'
  MediaContainer.content = 'Items'
  HTTP.SetCacheTime(CACHE_INTERVAL)

def MainMenu():
  dir = MediaContainer(filelabel='%T', viewGroup='Details')
  dir.Append(Function(DirectoryItem(GetMostPopular,       title="Popular")))

  for category in sorted(CATEGORIES.keys(), key= lambda cat : L(cat).lower):
    dir.Append(Function(DirectoryItem(GetCategory,       title=L(category)), category = category))

  dir.Append(
    Function(InputDirectoryItem(GetSearch, L("search"), L("search")))
  )
  return dir

def parsePage(url, title = None):
  dir = MediaContainer(filelabel='%T', viewGroup='Details', title1 = "Areena", title2 = title)
  xml = HTTP.Request(url)

  for post in XML.ElementFromString(xml).xpath('//item', namespaces=AREENA_NS):
    try:
      clip_id = post.find('link').text.split("/")[-1]
      title = post.find('title').text.strip()
      summary = post.find('description').text
      subtitle = Datetime.ParseDate(post.find('pubDate').text).strftime('%a %b %d, %Y')
      duration = int(post.xpath('m:content', namespaces=AREENA_NS)[0].get('duration')) * 1000
      thumbnail = post.xpath('m:thumbnail', namespaces=AREENA_NS)[0].get('url')
      dir.Append(WebVideoItem(post.find('link').text, title=title, summary=summary, subtitle=subtitle, duration=duration, thumb=thumbnail))
    except:
      pass

  return dir

def GetMostPopular(sender):
  return parsePage("http://areena.yle.fi/katsotuimmat/feed/rss", L("Popular"))

def GetCategory(sender, **kwargs):
  page = kwargs.get("page", 1)
  category = kwargs["category"]
  dir = parsePage("http://areena.yle.fi/lista/%d/uusimmat/media/video/sivu/%d/feed/rss" % (CATEGORIES[category], page), L(category))
  dir.Append(Function(DirectoryItem(GetCategory,       title=L("more")), page = (page + 1), category = category))
  if (page > 1):
    dir.Insert(0, Function(DirectoryItem(GetCategory,       title=L("back")), page = (page - 1), category = category))
  return dir

def GetSearch(sender, **kwargs):
  term = kwargs["query"]
  page = kwargs.get("page", 1)
  dir = parsePage("http://areena.yle.fi/haku//uusimmat/hakusana/%s/media/video/sivu/%d/feed/rss" % (term, page), "%s: %s" % (L("search") , term))
  dir.Append(Function(DirectoryItem(GetSearch,       title=L("more")), page = (page + 1), query = term))
  if (page > 1):
    dir.Insert(0, Function(DirectoryItem(GetSearch,       title=L("back")), page = (page - 1), query = term))
  return dir
