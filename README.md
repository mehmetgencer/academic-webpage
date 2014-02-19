Academic-Webpage is a standalone utility to manage website content for academics. It allows you to visually add/edit/organize entities on a man webpage, allowing you to add publications, lecture notes, all with file attachments. It is generic enough to be used for any (non-academic) web site with static content.

To run the program use awmanage.py script:

    $ create mywebsite
    $ cd mywebsite
    $ /path/to/academic-webpage/awmanage.py help
    $ /path/to/academic-webpage/awmanage.py 
    
Last command runs the local webserver, now go to http://localhost:8080 to design your website

Requirements
---------------
Works with Python 3. Requires cherrypy and jinja2 libraries. You can install them on a Linux box (having python3-setuptools) as:

    $ sudo easy_install jinja2
    $ sudo easy_install cherrypy
