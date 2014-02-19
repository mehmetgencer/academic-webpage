#!/usr/bin/python
"""
Takes an html file and makes it self contained as far as the 
local image and script references are concerned. It replaces image tags such as 
<img src="one.jpg" .../> 
with 
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAA...
and similarly for <script> tags, only if the src is a local file
 .../>
"""
import sys, re, mimetypes,base64, urllib

def debug(*args):
    for a in args:
        sys.stderr.write(str(a))
    sys.stderr.write("\n")

def contain(m):
    pre,fname,post=re.split("""['"]""",m.group(0))
    mtype=mimetypes.guess_type(fname)[0]
    debug("Inserting (%s):"%mtype+fname)
    try:#local
        fcontent=open(fname,"rb").read()
        return pre+"data:%s;base64,"%mtype+base64.b64encode(fcontent)+post
    except:
        #fcontent=urllib.request.urlopen(fname).read()
        return m.group(0)
def containImg(ht):
    #p="!\[.*?\](\(.+?\))"
    p="""<img\s+src=['"](.+?)['"]"""
    return re.sub(p,contain,ht)
def containJs(m):
    debug( m)
    debug( "GROUP 0:",m.group(0))
    debug(re.split("""['"]""",m.group(0)))
    pre,fname=re.split("""['"]""",m.group(0))[:2]
    debug("Inserting script (%s):"%fname)
    try:
        fcontent=open(fname,"rb").read()
        return "<script>%s</script>"%fcontent
    except:
        #fcontent=urllib.urlopen(fname).read()
        return m.group(0)
def containScript(ht):
    p="""<script\s+src=['"](.+?)['"].*?>"""
    return re.sub(p,containJs,ht)
if __name__=="__main__":
    try:
        fname=sys.argv[1]
    except:
        print "Usage: %s <inputfile>" %sys.argv[0]
        sys.exit(1)
    ht=open(fname,"rb").read()
    print containScript(containImg(ht))
