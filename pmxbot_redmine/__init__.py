# -*- coding: utf-8 -*-
import pmxbot
from pmxbot.core import regexp, contains, command
from pmxbot.core import ContainsHandler
import httplib2
import json
import re
import logging
import six
import random

log = logging.getLogger(__name__)


class RegexpFindHandler(ContainsHandler):
    class_priority = 4

    def __init__(self, *args, **kwargs):
        super(RegexpFindHandler, self).__init__(*args, **kwargs)
        if isinstance(self.pattern, six.string_types):
            self.pattern = re.compile(self.pattern, re.IGNORECASE)

    def match(self, message, channel):
        return self.pattern.findall(message)

    def process(self, message):
        return self.pattern.findall(message)


def regexpfind(name, regexp, doc=None, **kwargs):
    return RegexpFindHandler(
        name=name,
        doc=doc,
        pattern=regexp,
        **kwargs
    ).decorate


def getticket(ticketnum):
    h = httplib2.Http(".cache")
    try:
        resp, content = h.request("%s/issues/%s.json" %
                                  (pmxbot.config.redmine_url, ticketnum),
                                  "GET",
                                  headers={'X-Redmine-API-Key':
                                           pmxbot.config.redmine_apikey})
    except:
        log.exception("Error retrieving ticket %s", ticketnum)
    if resp['status'] == '404':
        return
    if resp['status'] == '403':
        return
    try:
        tjson = json.loads(content)
    except ValueError:
        return ("Received invalid json from %sissues/%s.json" %
                (pmxbot.config.redmine_url, tnumber))
    if 'assigned_to' not in tjson['issue']:
        tjson['issue']['assigned_to'] = {'name': 'nobody'}
    return tjson


def getprojects():
    h = httplib2.Http(".cache")
    try:
        resp, content = h.request("%sprojects.json" %
                                  (pmxbot.config.redmine_url), "GET",
                                  headers={'X-Redmine-API-Key':
                                           pmxbot.config.redmine_apikey})
    except:
        log.exception("Error retrieving projects")
    if resp['status'] == '404':
        return
    if resp['status'] == '403':
        return
    try:
        pjson = json.loads(content)
    except ValueError:
        return ("Received invalid json from %sprojects.json" %
                (pmxbot.config.redmine_url))
    return pjson


def projectChanWhitelist(ticketNum, channel):
    pjson = getprojects()
    pIds = {p['id']: p['identifier'] for p in pjson['projects']}
    ticket = getticket(ticketNum)
    ticketId = ticket['issue']['project']['id']
    try:
        if pIds[ticketID] in pmxbot.config.redmine_chan_proj_mapping[channel]:
            return ticket
    except:
        pass
    return


@regexpfind("redmine", r"#(\d+)")
def redmine(client, event, channel, nick, tickets):
    if (not pmxbot.config.redmine_apikey or not
            pmxbot.config.redmine_url or not
            pmxbot.config.redmine_chan_proj_mapping):
        return
    ticklist = []
    for ticketnum in tickets:
        ticket = projectChanWhitelist(ticketnum, channel)
        if ticket is not None:
            ticklist.append(ticket)
    for tick in ticklist:
        if tick is not None:
            yield ("%s: %sissues/%s" %
                   (nick, pmxbot.config.redmine_url, tick['issue']['id']))


@command("bug")
def redmine_bug(client, event, channel, nick, rest):
    if (not pmxbot.config.redmine_apikey or not
            pmxbot.config.redmine_url or not
            pmxbot.config.redmine_chan_proj_mapping):
        return
    p = re.compile('(\d+).*')
    ticket = p.match(rest).group(1)
    if not ticket.isdigit():
        return
    ticket = projectChanWhitelist(ticket, channel)
    if ticket is not None:
        yield ("%s: %s is %sissues/%s \"%s - %s: %s\". Its status is %s and ",
               "is assigned to %s" %
               (nick, ticket['issue']['id'], pmxbot.config.redmine_url,
                   ticket['issue']['id'], ticket['issue']['project']['name'],
                   ticket['issue']['tracker']['name'],
                   ticket['issue']['subject'],
                   ticket['issue']['status']['name'],
                   ticket['issue']['assigned_to']['name']))
