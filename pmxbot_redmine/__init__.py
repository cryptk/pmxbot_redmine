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
        tjson = json.loads(content.decode('utf-8'))
    except ValueError:
        return ("Received invalid json from %s/issues/%s.json" %
                (pmxbot.config.redmine_url, tnumber))
    if 'assigned_to' not in tjson['issue']:
        tjson['issue']['assigned_to'] = {'name': 'nobody'}
    return tjson


def getprojects():
    h = httplib2.Http(".cache")
    try:
        resp, content = h.request("%s/projects.json" %
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
        pjson = json.loads(content.decode('utf-8'))
    except ValueError:
        return ("Received invalid json from %s/projects.json" %
                (pmxbot.config.redmine_url))
    return pjson


@command("build")
def getlatestbuild(client, event, channel, nick, rest):
    if (not pmxbot.config.redmine_apikey or not
            pmxbot.config.redmine_url or not
            pmxbot.config.redmine_chan_proj_mapping or not
            pmxbot.config.redmine_default_project):
        return

    h = httplib2.Http(".cache")
    try:
        resp, content = h.request("%s/projects/%s/versions.json" %
                                  (pmxbot.config.redmine_url,
                                   pmxbot.config.redmine_default_project),
                                  "GET",
                                  headers={'X-Redmine-API-Key':
                                           pmxbot.config.redmine_apikey})
    except:
        log.exception("Error retrieving builds")
    if resp['status'] == '404':
        return
    if resp['status'] == '403':
        return
    try:
        latest_build = json.loads(content.decode('utf-8'))['versions'][-2]['name']
    except ValueError:
        yield ("Received invalid json from %s/projects/%s/versions.json" %
                (pmxbot.config.redmine_url, pmxbot.config.redmine_default_project))
    yield ("The latest version is: %s" % (latest_build))


def projectChanWhitelist(ticketNum, channel):
    pjson = getprojects()
    pIds = {p['id']: p['identifier'] for p in pjson['projects']}
    ticket = getticket(ticketNum)
    try:
        ticketId = ticket['issue']['project']['id']
    except TypeError:
        return
    try:
        if pIds[ticketId] in pmxbot.config.redmine_chan_proj_mapping[channel]:
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
    tick = projectChanWhitelist(ticket, channel)
    if tick is not None:
        yield ("%s: %s is %sissues/%s \"%s - %s: %s\". Its status is %s and "
               "is assigned to %s" %
               (nick, tick['issue']['id'], pmxbot.config.redmine_url,
               tick['issue']['id'], tick['issue']['project']['name'],
               tick['issue']['tracker']['name'], tick['issue']['subject'],
               tick['issue']['status']['name'],
               tick['issue']['assigned_to']['name']))
