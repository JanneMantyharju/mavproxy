MavProxy (c) Janne MŠntyharju

File					Location			Description
--------------------------------------------------------------------
elisa					/etc/ppp/peers		Example operator settings
elisa-connect-chat		/etc/ppp			Example connect script (make executable)
elisa-disconnect-chat	/etc/ppp			Example disconnect script (make executable)
90-linkit.rules			/etc/udev/rules.d	Example udev rule to start connection when modem is connected
nettitikku				/lib/udev			Script to start 3G connection (make executable)
mavproxy.py									MavLink proxy
mavlink.py									MavLink python wrapper. See notes below.
mavlink.conf			Selected server		Example configuration file.

3G modem settings are for finnish operator "Elisa", you may use these as examples for other operators.

Supplied mavlink.py file is already outdated. This file is created from mavlink message definition XML-file
which is included with Ardupilot Mega sources. See mavlink page (http://qgroundcontrol.org/mavlink/pymavlink)
for information about generating up to date file.

See the sources of mavproxy.py. Change the interface to your 3G modems interface (usually ppp0). Also change
the serial port, if you are going to use second serial port.

Remember to disable console on selected serial port by renaming the appropriate init file (to disable console
on onboard serial port, rename /etc/init/ttyO2.conf to ttyO2.conf.off). Only do this after making sure
you can connect to board via Internet. If you installed os to sd-card, you can revert this by mounting 
the card on desktop and naming the console file back.

You can use /etc/rc.local file to run the mavproxy at boot.

Finally, place mavlink.conf to some server that mavproxy can contact, update it with ground stations ip-
address and give the file URI as a parameter to mavlink.