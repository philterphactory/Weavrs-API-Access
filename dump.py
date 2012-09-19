# dump.py - Dump a weavr's posts' keywords to file.
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

import codecs
import weavrs_wrapper
import config
import gexf
import urllib
import logging


################################################################################
# Tag graph
################################################################################

def dump_emotion_edges(runs, now):
    nodes, edges = gexf.emotion_edge_graph(runs)
    stream = codecs.open("%s-emotion-edges-%s.gexf" %
                         (urllib.quote(runs[0]['weavr']),
                          now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.emotion_edge_graph_to_xml(stream, nodes, edges)

def dump_emotion_nodes(runs, now):
    nodes, edges = gexf.emotion_node_graph(runs)
    stream = codecs.open("%s-emotion-nodes-%s.gexf" %
                         (urllib.quote(runs[0]['weavr']),
                          now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.emotion_node_graph_to_xml(stream, nodes, edges)

def dump_keywords(runs, now):
    nodes, edges = gexf.keyword_graph(runs)
    stream = codecs.open("%s-keywords-%s.gexf" %
                  (urllib.quote(runs[0]['weavr']),
                   now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.keyword_graph_to_xml(stream, nodes, edges)

def dump_keywords_dynamic_edges(runs, now):
    nodes = gexf.runs_keywords(runs)
    edges = gexf.keyword_edge_durations(runs)
    stream = codecs.open("%s-keywords-dynamic-edges-%s.gexf" %
                  (urllib.quote(runs[0]['weavr']),
                   now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.keyword_durations_to_xml(stream, nodes, edges)

def dump_keywords_dynamic_nodes_and_edges(runs, now):
    nodes = gexf.runs_keywords(runs)
    edges = gexf.keyword_edge_durations(runs)
    node_start_times = gexf.keywords_first_run_times(runs, nodes)
    stream = codecs.open("%s-keywords-dynamic-nodes-and-edges-%s.gexf" %
                  (urllib.quote(runs[0]['weavr']),
                   now.strftime('%Y-%m-%d-%H-%M-%S')),
                         encoding='utf-8', mode='w')
    gexf.keyword_durations_to_xml(stream, nodes, edges, node_start_times)

if __name__ == '__main__':

    logging.getLogger().setLevel(config.logging_level)

    connection = weavrs_wrapper.WeavrApiConnection(config)

    page = 0
    per_page = 100

    active = 0
    inactive = 0
    problems = 0

    while True:

        weavrs = connection.request("/weavr/", page="can_test_stuff", per_page=per_page, format='json')


        if len(weavrs['weavrs']) == 0:
            logging.info('Finished')
            break

        for weavr in weavrs['weavrs']:

            name = weavr['name']

            # double try so we always get (in)active
            try:

                if bool(weavr['active']):

                    active += 1

                    try:
                        runs, now = weavrs_wrapper.weavr_runs_by_days(connection, weavr)

                        dump_emotion_edges(runs, now)
                        dump_emotion_nodes(runs, now)
                        dump_keywords(runs, now)
                        dump_keywords_dynamic_edges(runs, now)
                        dump_keywords_dynamic_nodes_and_edges(runs, now)
                    except:
                        logging.info("Exception [%s]" % name)
                        problems += 1

                else:
                    logging.info("Inactive [%s]" % name)
                    inactive += 1

            except:
                logging.info("Exception [%s]" % name)
                problems += 1

        page += 1

        break

    logging.info("Summary:")
    logging.info("\tActive : %s" % active)
    logging.info("\tInactive : %s" % inactive)
    logging.info("\tProblems : %s" % problems)
    logging.info("\tTotal : %s" % (active + inactive + problems))

