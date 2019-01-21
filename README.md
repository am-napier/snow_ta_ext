# snow_ta_ext
An extension for Splunk Snow TA (https://splunkbase.splunk.com/app/1928/) that makes additional fields passed to events or incidents a little easier to manage.
This version is only extending the events code but the same approach can be made for incidents as well (just haven't done it yet)

The idea is the Snow TA is extended and a new alert action has been added (Extended Snow Event).
The files are seperate from the splunk supported TA so upgrades can be done to the Snow TA without impacting this integration, so long as the snow TA doesn't change fundamentally.

User needs to test this works in their environment.

One change might be required, depending on how the TA is deployed.  Line 5 in the file bin/snow_event_ext.py references the actual TA by path and if the original Snow TA is not installed at etc/apps/Splunk_TA_snow then you must update as required (or fix the diodgy code so this doesn't need to happen)

Please contribute any changes back here
