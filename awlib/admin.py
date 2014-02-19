#!/usr/bin/python3
import cherrypy
from cherrypy._cpcompat import json_encode, json_decode
from jinja2 import Template
import sys,pprint, json, mimetypes, os
pagedata="pagedata.txt"
from esbibtex import ESBibtex
import export
pp=pprint.PrettyPrinter()
def getTemplate():
    return Template(open("templates/admin.html","r").read().replace("{#","{{'{#'}}"))
class Profile(dict):
    def __init__(self,fname):
        self.fname=fname
        d=eval(open(fname,"r").read())
        dict.__init__(self,d)
    def getSection(self,i):
        for s in self["sections"]:
            if s["sectionKey"]==i:
                print("FOUND SECTION:",i)
                return Section(s)
    def saveSec(self,i,s):
        for j in range(len(self["sections"])):
            if self["sections"][j]['sectionKey']==i:
                self["sections"][j]=s
                self.save()
                return
    def deleteSec(self,i):
        for j in range(len(self["sections"])):
            if self["sections"][j]['sectionKey']==i:
                self["sections"].pop(j)
                self.save()
                return
    def getPubKey(self):
        i=-1
        for s in self["sections"]:
            for p in s["publications"]:
                if p["publicationKey"]>i:i=p["publicationKey"]
        return i+1
    def getSecKey(self):
        i=-1
        for s in self["sections"]:
            if s["sectionKey"]>i:i=s["sectionKey"]
        return i+1
    def deleteFile(self,fkey):
        for s in self["sections"]:
            for p in s["publications"]:
                for f in p["pfiles"]:
                    if f["fileKey"]==fkey:
                        p["pfiles"].remove(f)
                        os.remove(os.sep.join(["files",f["fileName"]]))
                        self.save()

    
    def save(self):
        f=open(pagedata,"w")
        pp2=pprint.PrettyPrinter(stream=f)
        pp2.pprint(self)
        f.flush()
        export.export()
class Section(dict):
    def __init__(self, args):
        dict.__init__(self, args)
    def getPub(self,i):
        for p in self["publications"]:
            if p['publicationKey']==i:return p
    def deletePub(self,i):
        for j in range(len(self["publications"])):
            if self["publications"][j]['publicationKey']==i:
                for f in self["publications"][j]["pfiles"]:
                    os.remove(os.sep.join(["files",f["fileName"]]))
                p=self["publications"].pop(j)
                return
    def savePub(self,i,p):
        for j in range(len(self["publications"])):
            if self["publications"][j]['publicationKey']==i:
                self["publications"][j]=p
                return
    
class AWAdmin(object):
    def __init__(self,profile):
        self.profile=profile
    def api(self,a,kw):
        status=0
        errmsg=""
        if a[0]=="getProfile":
            jresp=self.profile
        elif a[0]=="createSection":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Creating section")
            sec={"title":"New Section", "publications":[],"sectionKey":self.profile.getSecKey(),"displayOrder":self.profile.getSecKey(),"puborder":[],"secdesc":"No description"}
            self.profile["sections"].append(sec)
            self.profile.save()
            jresp={}
        elif a[0]=="updateSec":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Updating section:",req["sectionKey"])
            sec=self.profile.getSection(req["sectionKey"])
            sec["title"]=req["title"]
            sec["secdesc"]=req["secdesc"]
            #self.profile.save()#setsec.save()
            neworder=req["puborder"]
            o=1
            newpubs=[]
            for pkey in neworder:
                pub=sec.getPub(pkey)
                newpubs.append(pub)
                #if pub["displayOrder"]!=o:
                #    pub["displayOrder"]=o
                o+=1
            sec["publications"]=newpubs
            self.profile.saveSec(req["sectionKey"],sec)
            jresp={}
        elif a[0]=="deleteSec":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Deleting section:",req["sectionKey"])
            self.profile.deleteSec(req["sectionKey"])
            jresp={}
        elif a[0]=="createPub":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Creating pub in section:",req["sectionKey"])
            sec=self.profile.getSection(req["sectionKey"])
            publication={"publicationKey":self.profile.getPubKey(),"parent":sec["sectionKey"],"title":"Başlıksız yayın","displayOrder":len(sec["publications"])+1,"authors":[{"name":self.profile["name"]}], "ispub":False,"issep":False,"pubtype":"article","desc":"Açıklama yok","pfiles":[],"pubinfo":ESBibtex().defaultValues(),"fileorder":[]}
            if req["ptype"]=="academic":
                publication["ispub"]=True
            elif req["ptype"]=="non-academic":
                pass
            else:#sep
                publication["issep"]=True
            sec["publications"].insert(0,publication)
            self.profile.saveSec(req["sectionKey"],sec)
            jresp={}
        elif a[0]=="updatePub":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Updating pub in section:",req["publicationKey"])
            sec=self.profile.getSection(req["sectionKey"])
            pub=sec.getPub(req["publicationKey"])
            pub["pubinfo"]=req["pubinfo"]
            pub["title"]=req["title"]
            pub["desc"]=req["desc"]
            pub["pubtype"]=req["pubtype"]
            #pub["ispub"]=req["ispub"]
            pub["authors"]=[{"name":x} for x in req["authors"]]
            forder=[x for x in filter(lambda x:x is not None,req["fileorder"])]
            def getPfile(pfiles,k):
                for pf in pfiles:
                    if pf["fileKey"]==k:return pf
            pub["pfiles"]=[getPfile(pub["pfiles"],k) for k in forder]
            sec.savePub(req["publicationKey"],pub)
            self.profile.saveSec(req["sectionKey"],sec)
            jresp={}
        elif a[0]=="deletePub":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Deleting pub in section:",req["publicationKey"])
            sec=self.profile.getSection(req["sectionKey"])
            sec.deletePub(req["publicationKey"])
            self.profile.saveSec(req["sectionKey"],sec)
            jresp={}
        elif a[0]=="addPublicationFiles":
            #rbody=cherrypy.request.body.fp.read()
            cl = int(cherrypy.request.headers['Content-Length'])
            #raw=cherrypy.request.body.read(cl)
            #print("REQUEST",raw)
            #req=json_decode(raw)
            print("Adding pub files:",kw["publicationKey"])
            sec=self.profile.getSection(int(kw["sectionKey"]))
            pub=sec.getPub(int(kw["publicationKey"]))
            print("To pub:",pub)
            for fname in kw[".fnames"].split("###"):
                if os.path.exists(os.sep.join(["files",fname])):
                    status=1
                    errmsg="File already exists"
                    jresp={}
                    retval={"status":status,"message":errmsg,"result":jresp}
                    return json.dumps(retval)
            for fname in kw[".fnames"].split("###"):
                pfile={'description': '',
                       'displayOrder': len(pub["pfiles"])+1,
                       'downloadCount': 0,
                       'fileCleanUrl': '/files/'+fname,
                       'fileKey': fname,
                       'fileName': fname,
                       'fileUrl': '/files/'+fname}
                pub["pfiles"].append(pfile)
                f=kw[fname].file.read()
                print("FILE CONTENT",f)
                open("files/"+fname,"wb").write(f)
            #raise Exception("not implemented")
            sec.savePub(int(kw["publicationKey"]),pub)
            self.profile.saveSec(int(kw["sectionKey"]),sec)
            jresp={}
        elif a[0]=="deletePubFile":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Deleting file in section:",req["fkey"])
            self.profile.deleteFile(req["fkey"])
            jresp={}
        elif a[0]=="updateProfile":
            rbody=cherrypy.request.body.fp.read()
            print("REQUEST",rbody)
            req=json_decode(rbody.decode("utf-8"))
            print("Updating profile:")
            #self.profile
            self.profile["title"]=req["profileName"]
            self.profile["name"]=req["username"]
            self.profile["desc"]=req["profileDesc"]
            self.profile["profiledesc"]=req["profileDesc"]
            self.profile["associations"]=req["associations"]
            neworder=req["sectionOrder"]
            o=1
            newsecs=[]
            for skey in neworder:
                newsecs.append(self.profile.getSection(skey))
                o+=1      
            self.profile["sections"]=newsecs      
            self.profile.save()
            jresp={}
        elif a[0]=="setProfilePicture":
            print("Update profile pic")
            for fname in kw[".fnames"].split(" "):
                f=kw[fname].file.read()
                print("FILE CONTENT",f)
                open("files/"+fname,"wb").write(f)
            self.profile["profilePicture"]={'fileCleanUrl': '/files/'+fname,
                       'fileKey': fname,
                       'fileName': fname,
                       'fileUrl': '/files/'+fname}
            self.profile.save()
            jresp={}
        elif a[0]=="deleteProfilePicture":
            print("Delete profile pic")
            del self.profile["profilePicture"]
            self.profile.save()
            jresp={}
        else:
            status=1
            errmsg="Unknown command"
            jresp={}
        retval={"status":status,"message":errmsg,"result":jresp}
        return json.dumps(retval)
    def default(self,*a,**kw):
        print("params:",a,kw)
        if a[0] in ["static","files","preview"]:
            if a[0]=="files":
                fname="files/"+"/".join([x.split("?")[0] for x in a[1:]])
            elif a[0]=="static":
                fname="static/"+"/".join(a[1:])
            else:
                fname="index.html"
                #export.export()
            mtype=mimetypes.guess_type(fname)[0]
            if mtype is None and a[-1].split(".")[-1]=="less":mtype="text/css"
            print(fname,mtype)
            cherrypy.response.headers['Content-Type']= mtype
            return open(fname,"rb")
        elif a[0]=="api":
            return self.api(a[1:],kw)
    default.exposed=True
    def index(self):
        #return "<pre>"+pp.pformat(self.profile)+"</pre>"
        template_values = {
            "user":"MehmetGencer",
            "profile":self.profile,
            "sections":self.profile["sections"],
            #"pubs":profile.getPublications(),
            "esbibtex":ESBibtex(),
            "logoutUrl":"/",
            "profileJson":json.dumps(self.profile),
            "cwd":os.getcwd()
        }
        return getTemplate().render(template_values)
    index.exposed = True
    #def preview(self):
    #    return open("index.html","r").read()
    #preview.exposed=True
def srv():
    root=AWAdmin(Profile(pagedata))
    cherrypy.quickstart(root)

if __name__=="__main__":
    srv()
