# weavr.py - Access the Weavrs API.
# Copyright (C) 2012  Rob Myers <rob@robmyers.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


################################################################################
# Imports
################################################################################


import datetime
import simplejson as json
import sys
import time
import urllib
from weavrs.client import WeavrsClient
import config

################################################################################
# Date and time utilities
################################################################################

one_day = datetime.timedelta(1)
one_week = datetime.timedelta(7)

def datetime_to_date(dt):
    """Floor the datetime to midnight at the start of the date"""
    return datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0, 0)

def format_datetime(dt):
    """Format the datetime object to a string in Weavrs format"""
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')

def parse_datetime(text):
    """Parse the text as a datetime in Weavrs format"""
    return datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%SZ')


class WeavrApiConnection(object):

    def __init__(self, config):
        self.client = WeavrsClient(config.api_server, config.consumer_key )

    
    def request(self, url, **params):
        return self.client.get(url, cache=False, **params)


################################################################################
# Weavrs API access
################################################################################

def weavr_created_at(weavr):
    """Get the datetime.datetime the weavr was created at, fetching content
       from the WeavrApiConnection weavr if content is None"""
    created_at_string = weavr['created_at']
    # Convert to a datetime
    created_at = datetime.datetime.strptime(created_at_string, "%Y-%m-%dT%H:%M:%SZ" )
    return created_at


def weavr_runs_between(connection, weavr, start, end):
    """Get the weavr's runs (including posts) between the given dates"""
    name = weavr["name"]
    content = connection.request("/weavr/%s/run/" % name, after=format_datetime(start), before=format_datetime(end), posts='true', per_page=config.per_page)
    return list(reversed(content['runs']))

def weavr_runs_all(connection, weavr = None, max_days=100):
    """Get all the runs since the weavr was created"""
    created_at_datetime = weavr_created_at(weavr)
    runs = []
    now = datetime.datetime.now()
    day = datetime_to_date(created_at_datetime)
    day_finish = datetime_to_date(now)
    # Make sure we don't exceed the API limit
    max_days_delta = datetime.timedelta(max_days)
    if day_finish - day > max_days_delta:
        day = day_finish - max_days_delta
    print "Getting runs from %s to %s" % (day, day_finish)
    while day <= day_finish:
        print "Getting runs up to: %s" % day
        next_day = day + one_day
        days_runs = weavr_runs_between(connection, weavr, day, next_day)
        print "(%s runs)" % len(days_runs)
        runs += days_runs
        day = next_day
        time.sleep(config.call_delay_seconds)
    return runs, now

def weavr_runs_by_days(connection, weavr = None, days=0):

    runs = []

    created_at_datetime = weavr_created_at(weavr)
    now = datetime.datetime.now()
    day_finish = datetime_to_date(now)

    if days > config.max_days:
        days = config.max_days

    day = day_finish - datetime.timedelta(days)

    print "Getting runs from %s to %s" % (day, day_finish)
    while day <= day_finish:
        print "Getting runs up to: %s" % day
        next_day = day + one_day
        days_runs = weavr_runs_between(connection, weavr, day, next_day)
        print "(%s runs)" % len(days_runs)
        runs += days_runs
        day = next_day
        time.sleep(config.call_delay_seconds)
    return runs, now
