import time
import socket
import os
import sys
import uuid
import json

import snow_ticket as st
import snow_event_base as seb


class SnowEventBaseExt(seb.SnowEventBase):
    """
    """

    # returns true if it was set or false if nothing was done
    def update_event_data(self, tag, default=None):
        val = self.event.get(tag, default)
        if not val is None:
            self.logger.info("Snowflake %s=%s"%(tag, val))
            self.event_data[tag] = val
            return True
        self.logger.info("No Snowflake %s"%(tag))
        return False

    '''
    see https://docs.servicenow.com/bundle/london-it-operations-management/page/product/event-management/task/send-events-via-web-service.html
    for details on props required
    see https://docs.servicenow.com/bundle/jakarta-it-operations-management/page/product/event-management/reference/r_EMAlertBindBestPractice.html
    for details on event to CI binding
    '''
    def _prepare_data(self, event):
        self.logger.info("Snowball In : "+json.dumps(event, indent=2))
        self.event_data = super(SnowEventBaseExt, self)._prepare_data(event)
        self.event = event

        '''
        node, resource, type, severity come from the default UI
        description is optional 
        time_of_event is optional and set if not passed
        source is set to Splunk-[host_name]
        ci_identifier is set from the event
        additional_info gets a 
           url added from either additional_info or SPLUNK_ARG_6
           correlation_id is a uuid generated in the call
        event_class is set to Splunk
        '''
        # these must be passed from the message or this script should fail
        if not (self.update_event_data("node") and self.update_event_data("resource") and
                self.update_event_data("severity") and self.update_event_data("type") ):
            return None

        # if these are passed set them otherwise use the defaults specified here
        self.update_event_data("source", "Splunk-{}".format(socket.gethostname()))
        self.update_event_data("event_class", "Splunk")
        self.update_event_data("time_of_event", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) )

        # only set these guys if they are passed into the method, no default means they get ignored if not provided
        self.update_event_data("message_key")
        self.update_event_data("metric_name")
        self.update_event_data("resolution_state")
        self.update_event_data("description")
        self.update_event_data("correlation_id")

        # this object is a dumping ground for anything we like
    self.logger.info("drilldown: %s\nadditional_info url %s\nSPLUNK_ARG_6:%s"%(
              event.get("drilldown", ""), event.get("additional_info", ""), os.environ.get("SPLUNK_ARG_6")))
        url = event.get("drilldown", event.get("additional_info", os.environ.get("SPLUNK_ARG_6")))
        svcs = event.get("extra.services")
        entities = event.get("extra.entities")
        extra = {
            "url" : url,
            "correlation_id" : event.get("correlation_id", uuid.uuid1(clock_seq=int(time.time())).hex),
            "ci2metric_id" : event.get("ci_id")
        }
        if svcs: extra["services"] = svcs
        if entities: extra["entities"] = entities
        addtl = event.get("additional")
        if addtl:
             try:
                 extra.update(json.loads("{%s}"%addtl))
             except e:
                 self.logger.error("Failed to parse JSON for additional properties: %s, Error: %s"%(addtl, str(e)))

        self.event_data["additional_info"] = json.dumps(extra)

        self.logger.info("Event Snowball away !!!  " +json.dumps(self.event_data, indent=2))
        return self.event_data