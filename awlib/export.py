#!/usr/bin/python3
import sys,json,pprint
from jinja2 import Template
from esbibtex import *
pagedata="pagedata.txt"

def reparse():
    d=json.load(open("content.json","r"))
    pp=pprint.PrettyPrinter(stream=open("pretty.txt","w"))
    pp.pprint(d)
def renderpub(pub):
    return ESBibtex().render(pub["pubtype"],pub["title"],[x["name"] for x in pub["authors"]],pub["pubinfo"])
template = Template("""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{{profile["name"]}}</title>
<link rel="stylesheet" href="static/stylesheets/defaultstyle.css" />
</head>
<body>
<div id="header">
  <h1>{{data["title"]}}</h1>
</div>

<div id="leftmenu">
 {% if "profilePicture" in data %}
 <img class="profilepic" src="files/{{data["profilePicture"]["fileName"]}}"/>
 {%endif%}
 <ul class="navmenu">
 {% for section in sections %}
 <li><a class="menuitem" href="#{{section["sectionKey"]}}">{{section["title"]}}</a></li>
 {% endfor %}
 </ul>
</div>

<div id="content">
<p>{{data["profiledesc"]}}</p>
{% for section in sections %}
  <h2><a name="{{section["sectionKey"]}}"/>{{section["title"]}}</h2>
  <p>{{section["secdesc"]}}</p>
  {% for pub in section["publications"] %}
    {%if pub["issep"]%}
    <h3>{{pub["title"]}}</h3>
    <p>{{pub["desc"]}}</p>
    {%else%}
      {% if pub["ispub"] %}
        <li>{{renderpub(pub)}}</li>
        {% for f in pub["pfiles"] %}
        <a href="files/{{f["fileName"]}}">{{f["fileName"]}}</a> 
        {%endfor%}
      {%else%}
        <li><strong>{{pub["title"]}}</strong>: {{pub["desc"]}}
        {% for f in pub["pfiles"] %}
        <a href="files/{{f["fileName"]}}">{{f["fileName"]}}</a> 
        {%endfor%}
        </li>
      {%endif%}
    {%endif%}
  {% endfor %}

{% endfor %}
</div>
</body>
</html>
""")
def export():
    if "reparse" in sys.argv:
        reparse()
    data=eval(open(pagedata,"r").read())
    rend=template.render(profile=data,sections=data["sections"],data=data,renderpub=renderpub)
    open("index.html","w").write(rend)
if __name__=="__main__":
    export()
