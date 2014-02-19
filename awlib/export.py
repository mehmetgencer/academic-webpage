#!/usr/bin/python3
import sys,json,pprint,os
from jinja2 import Template
from esbibtex import *
pagedata="pagedata.txt"

def reparse():
    d=json.load(open("content.json","r"))
    pp=pprint.PrettyPrinter(stream=open("pretty.txt","w"))
    pp.pprint(d)
def renderpub(pub):
    return ESBibtex().render(pub["pubtype"],pub["title"],[x["name"] for x in pub["authors"]],pub["pubinfo"])
def gettemplate():
    return Template(open(os.sep.join(["designs","default.html"]),"r").read())
def export():
    if "reparse" in sys.argv:
        reparse()
    data=eval(open(pagedata,"r").read())
    rend=gettemplate().render(profile=data,sections=data["sections"],data=data,renderpub=renderpub)
    open("index.html","w").write(rend)
if __name__=="__main__":
    export()
