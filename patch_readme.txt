The patch "patch" fixes incompatible sasl behaviour of python's xmppp package and the openFire XAMPP server: 
http://community.igniterealtime.org/thread/20551

Instructions:
Open a shell.
Navigate to the package jabberbot (needs root priviledges if it should be changed for all users)
and type:
patch jabberbot.py patch

This should disable the use of SASL.
