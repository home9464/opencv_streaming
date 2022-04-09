"""
You need two things to make your linux system to reboot.

1 - Give the user executing your script the privilege for reboot

$ sudo visudo -f /etc/sudoers.d/reboot_privilege

add line :

<user> ALL=(root) NOPASSWD: /sbin/reboot

"""
import logging

logging.basicConfig(filename='default.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

LOG = logging.getLogger('pi_cam_client')

logging.info("info Urban Planning")

logging.debug("debug Urban Planning")



