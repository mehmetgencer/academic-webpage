#!/usr/bin/python3
VERSION="0.1"
import sys, os, os.path, shutil
mydir=os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(os.sep.join([mydir,"awlib"]))
import esbibtex,admin,export
cmdname=os.path.basename(sys.argv[0])
usage="""Usage:
    %s help : print this help message
    %s [pagename] design: design a website. If pagename is not given and
                         not in the web directory, "www.example.com" is taken as default
                         and a directory with that name is created
    %s [pagename] export: export the index.html page. If pagename is given
                        directory is change to one with that name
Examples:
    %s www.mehmet.com design
    cd www.mehmet.com && %s design
    cd www.mehmet.com && %s export #creates index.html www.mehmet.com is now ready to publish
"""%(cmdname,cmdname,cmdname,cmdname,cmdname,cmdname)

def main():
    args=sys.argv[1:]
    if len(args)==2:
        pagename=args.pop(0)
        workdir=os.sep.join([os.getcwd(),pagename])
    else:
        if os.path.exists("pagedata.txt"):
            workdir="."
        else:
            pagename="www.example.com"
            workdir=os.sep.join([os.getcwd(),pagename])
    try:
        mode=args.pop()
    except:
        mode="design"
    if not mode in ["design","export","help"]:
        print("invalid command:",mode)
        return
    print("Working directory:",workdir)
    if not os.path.exists(workdir):
        print("Populating directory with skeleton files")
        shutil.copytree(os.sep.join([mydir,"skeleton"]),workdir)
        shutil.copy(os.sep.join([mydir,"template.txt"]),os.sep.join([workdir,"pagedata.txt"]))
    else:
        for x in ["static","templates"]:
            shutil.rmtree(os.sep.join([workdir,x]))
            shutil.copytree(os.sep.join([mydir,"skeleton",x]),os.sep.join([workdir,x]))
        shutil.copy(os.sep.join([mydir,"skeleton","designs","default.html"]),os.sep.join([workdir,"designs","default.html"]))
    os.chdir(workdir)
    if mode=="design":
        admin.srv()
    elif mode=="help":
        print(usage)
    else:#export
        export.export()
if __name__=="__main__":
    main()
