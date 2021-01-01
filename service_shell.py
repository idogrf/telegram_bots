import grp
import os
import pwd
from signal import signal, SIGINT, SIGTERM
from sys import exit

from telegram_first_bot import run as run_telegram_bot

def drop_privileges(uid_name='nobody', gid_name='nogroup'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Reset group access list
    os.initgroups(uid_name, running_gid)

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(0o77)


def get_shutdown_handler(message=None):
    """
    Build a shutdown handler, called from the signal methods
    :param message:
        The message to show on the second line of the LCD, if any. Defaults to None
    """

    def handler(signum, frame):
        # If we want to do anything on shutdown, such as stop motors on a robot,
        # you can add it here.
        print(message)
        exit(0)

    return handler


signal(SIGINT, get_shutdown_handler('SIGINT received'))
signal(SIGTERM, get_shutdown_handler('SIGTERM received'))

# Do anything you need to do before changing to the 'pi' user (our service
# script will run as root initially so we can do things like bind to low
# number network ports or memory map GPIO pins)

# Become 'pi' to avoid running as root
drop_privileges(uid_name='pi', gid_name='pi')

# Do the rest of your service after this point, you'll be running as 'pi'
while True:
    run_telegram_bot()
