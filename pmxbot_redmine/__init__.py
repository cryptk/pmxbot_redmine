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
        resp, content = h.request("%s/issues/%s.json" % (pmxbot.config.redmine_url, ticketnum), "GET", headers={'X-Redmine-API-Key': pmxbot.config.redmine_apikey})
    except:
        log.exception("Error retrieving ticket %s", ticketnum)
    if resp['status'] == '404':
        return
    if resp['status'] == '403':
        return
    try:
        tjson = json.loads(content)
    except ValueError:
        return ("Received invalid json from %sissues/%s.json" % (pmxbot.config.redmine_url, tnumber))
    if not tjson['issue'].has_key('assigned_to'):
        tjson['issue']['assigned_to'] = {'name':'nobody'}
    return tjson

def getprojects():
    h = httplib2.Http(".cache")
    try:
        resp, content = h.request("%sprojects.json" % (pmxbot.config.redmine_url), "GET", headers={'X-Redmine-API-Key': pmxbot.config.redmine_apikey})
    except:
        log.exception("Error retrieving projects")
    if resp['status'] == '404':
        return
    if resp['status'] == '403':
        return
    try:
        pjson = json.loads(content)
    except ValueError:
        return ("Received invalid json from %sprojects.json" % (pmxbot.config.redmine_url))
    return pjson

def projectChanWhitelist(ticketNum, channel):
    pjson = getprojects()
    projectIdMap = {p['id']: p['identifier'] for p in pjson['projects']}
    ticket = getticket(ticketNum)
    try:
        if projectIdMap[ticket['issue']['project']['id']] in pmxbot.config.redmine_chan_proj_mapping[channel]:
            return ticket
    except:
        pass
    return

@regexpfind("redmine", r"#(\d+)")
def redmine(client, event, channel, nick, tickets):
    if not pmxbot.config.redmine_apikey or not pmxbot.config.redmine_url or not pmxbot.config.redmine_chan_proj_mapping:
        return
    ticklist = []
    for ticketnum in tickets:
        ticket = projectChanWhitelist(ticketnum, channel)
        if ticket is not None:
            ticklist.append(ticket)
    for tick in ticklist:
        if tick is not None:
            #yield ("%s: %s is %sissues/%s \"%s - %s: %s\" It's status is %s and is assigned to %s" % (nick, tick['issue']['id'], pmxbot.config.redmine_url, tick['issue']['id'], tick['issue']['project']['name'], tick['issue']['tracker']['name'], tick['issue']['subject'], tick['issue']['status']['name'], tick['issue']['assigned_to']['name']))
            yield ("%s: %sissues/%s" % (nick, pmxbot.config.redmine_url, tick['issue']['id']))

@command("bug")
def redmine_bug(client, event, channel, nick, rest):
    if not pmxbot.config.redmine_apikey or not pmxbot.config.redmine_url or not pmxbot.config.redmine_chan_proj_mapping:
        return
    if not rest.isdigit():
        return
    ticket = projectChanWhitelist(rest, channel)
    if ticket is not None:
        yield ("%s: %s is %sissues/%s \"%s - %s: %s\" It's status is %s and is assigned to %s" % (nick, ticket['issue']['id'], pmxbot.config.redmine_url, ticket['issue']['id'], ticket['issue']['project']['name'], ticket['issue']['tracker']['name'], ticket['issue']['subject'], ticket['issue']['status']['name'], ticket['issue']['assigned_to']['name']))

#@command('redmine', aliases=('rm'))
#def redminestatus(client, event, channel, nick, rest):
#    if not pmxbot.config.redmine_apikey or not pmxbot.config.redmine_url or not pmxbot.config.redmine_chan_proj_mapping:
#        return
#    h = httplib2.Http(".cache")
#    try:
#        resp, content = h.request("%s/issue_statuses.json" % (pmxbot.config.redmine_url), "GET", headers={'X-Redmine-API-Key': pmxbot.config.redmine_apikey})
#    except:
#        log.exception("Error retrieving ticket statuses")
#    statusdict = json.loads(content)
#    if not rest:
#        statuses = [status['name'].lower().replace(" ","") for status in statusdict['issue_statuses']]
#        yield "Usage: '!redmine STATUS' where STATUS is one of %s" % ", ".join(statuses)
#    if rest:
#        for status in statusdict['issue_statuses']:
#            if rest == status['name'].lower().replace(" ",""):
#                status_id = status['id']
#        try:
#            resp, content = h.request("%s/issues.json?status_id=%s&project_id=%s" % (pmxbot.config.redmine_url, status_id, pmxbot.config.redmine_project), "GET", headers={'X-Redmine-API-Key': pmxbot.config.redmine_apikey})
#        except NameError:
#            log.exception("Error retrieving list of issues")
#            yield "Error retrieving list of issues... did you provide a valid STATUS?"
#            return
#        issuesdict = json.loads(content)
#        if len(issuesdict['issues']) > 5:
#            yield "%sprojects/%s/issues?utf8=%%E2%%9C%%93&set_filter=1&f[]=status_id&op[status_id]=%%3D&v[status_id][]=%s" % (pmxbot.config.redmine_url,  pmxbot.config.redmine_project, status_id)
#        else:
#            for tick in issuesdict['issues']:
#                if not tick.has_key('assigned_to'):
#                    tick['assigned_to'] = {'name':'nobody'}
#                yield ("%s: %s is %sissues/%s \"%s - %s: %s\" It's status is %s and is assigned to %s" % (nick, tick['id'], pmxbot.config.redmine_url, tick['id'], tick['project']['name'], tick['tracker']['name'], tick['subject'], tick['status']['name'], tick['assigned_to']['name']))




@contains('jebbot', channels='unlogged', rate=.05)
def kerbal_quote(client, event, channel, nick, rest):
    quotes = ['Moar Boosters!!!',
              'Scott Manley: But that will have to wait for the next episode',
              'Fell apart on the launch pad, obviously didnt use enough space tape...',
              'Rapid Unplanned Disassembly... more space tape...',
              'Single Stage To Ocean',
              'Something tells me this wouldn\'t work with FAR',
              'Struts make the world go round',
              'Failure is always an option!',
              'Mün or Bust',
              'Rocket Science Can\'t Be That Hard',
              'What Would Jebediah Do?',
              'Takeoff in 3... 2... 1... ... ... revert...',
              '"It\'s the nectar of winners. Nothing like strong, black coffee."',
              '/me applies space tape',
              '/me inserts new batteries',
              '/me turns it off then on again etc',
             ]
    return random.choice(quotes)
