"""
You need two things to make your linux system to reboot.

1 - Give the user executing your script the privilege for reboot

$ sudo visudo -f /etc/sudoers.d/reboot_privilege

add line :

<user> ALL=(root) NOPASSWD: /sbin/reboot

"""

import os
import time

start_time = time.time()
while True:
    if int(time.time() - start_time) % 10 == 0:  # every minute check out if internet connection OK
        print('reboot')
        os.system('sudo reboot')
    print('alive')
    time.sleep(1)

