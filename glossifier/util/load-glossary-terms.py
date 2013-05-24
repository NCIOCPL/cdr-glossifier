#!/usr/bin/python
# -------------------------------------------------------------------
# $Id$
#
# Script to update the glossifier database with the glossary terms
# from the CDR server
# -------------------------------------------------------------------
import urllib2, sys, cdrutil

#----------------------------------------------------------------------
# Initialize logging.
#----------------------------------------------------------------------
program = "GetGlossifierTerms.py"
logfile = "/weblogs/glossifier/glossifier.log"
cdrutil.log("Starting %s" % program, logfile=logfile)

#----------------------------------------------------------------------
# Connect to the glossifier database.
#----------------------------------------------------------------------
try:
    conn = cdrutil.getConnection("glossifier")
except:
    cdrutil.log("*** Unable to connect to glossifier DB", logfile=logfile)
    raise
cursor = conn.cursor()

#----------------------------------------------------------------------
# Load the terms from the CDR server.
#----------------------------------------------------------------------
env = cdrutil.getEnvironment()
tier = cdrutil.getTier()
hosts = cdrutil.AppHost(env, tier)
ssl = env == "CBIIT" and "Y" or "N"
url = hosts.makeCdrCgiUrl(tier, program, ssl)
reader = urllib2.urlopen(url)
doc = reader.read()

#----------------------------------------------------------------------
# Store the terms in the glossifier database.
#----------------------------------------------------------------------
cursor.execute("""\
    UPDATE terms
       SET loaded = NOW(),
           terms_dict = %s
     WHERE terms_id = 1""", doc)
cursor.execute("DELETE FROM term_regex")
conn.commit()
cdrutil.log("loaded glossifier terms (length %d bytes)" % len(doc),
            logfile=logfile)
