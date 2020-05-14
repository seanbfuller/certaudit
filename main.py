# main.py
# See README for usage
# See note in README about errors when tryign to parse "CNAME 1" records

# Libraries for argument handling
import sys, getopt
# Libraries for DNS zonefile parsing
import dns.zone
from dns.exception import DNSException
from dns.rdataclass import *
from dns.rdatatype import *
from collections import defaultdict
# Libraries for connecting to the remote host and getting the cert
import ssl, socket
# Libraries for date parsing and formatting
from datetime import datetime
import dateparser
# Library to output the results
import os
import csv
# Library for progress bar
import progressbar

##
# Function to get the cert information from a url
##
def get_cert_info(hostname):
  # Build our empty dictionary object
  ssl_info = {'common_name':'', 'issued_name':'', 'serial_number':'', 'expiration_date':'', 'status':''}
  # convert wildcards into simple urls so we can request them
  wildcards = ('@.','*.')
  if hostname.startswith(wildcards):
    hostname = hostname[2:]
  # Turn off errors for invalid hostnames
  ctx.check_hostname = False
  with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
    try:
      s.settimeout(3)
      s.connect((hostname, 443))
      cert = s.getpeercert()
      # step into the subject so we can get the common_name
      subject = dict(x[0] for x in cert['subject'])
      ssl_info['common_name'] = subject['commonName']
      # step into the issuer to get the oganirationName
      issuer = dict(x[0] for x in cert['issuer'])
      ssl_info['issued_name'] = issuer['organizationName']
      # Get the serial number so we can compare
      ssl_info['serial_number'] = cert['serialNumber']
      # Get the expiration
      exp_date_object = dateparser.parse(cert['notAfter'])
      ssl_info['expiration_date'] = exp_date_object.strftime('%Y-%m-%d')
      ssl_info['status'] = 200
    except socket.error as err:
      error_string = repr(err)
      err_string_full = ("ERROR: Connection error for "+ hostname +": "+ error_string +".")
      ssl_info['status'] = err_string_full
  # Return our info
  return ssl_info

##
# Main applicaiton.
##
print('Starting script...')

# Get args
inputfile = ''
domain = ''
arg_err_string = "Error: invalid arguments."
help_string = "main.py -i <inputfile> -d <domain>"
try:
  opts, args = getopt.getopt(sys.argv[1:],"hi:d:",["inputfile=","domain="])
except getopt.GetoptError:
  sys.exit(2)
for opt, arg in opts:
  if opt == '-h':
    print(help_string)
    sys.exit()
  elif opt in ("-i", "--inputfile"):
    inputfile = arg
  elif opt in ("-d", "--domain"):
     domain = arg
if not inputfile:
  print("Error: input file missing")
  print(help_string)
  sys.exit()
if not domain:
  print("Error: Domain missing")
  print(help_string)
  sys.exit()

# Give feedback about what we are parsing
print(f'Parsing {inputfile} for domain {domain}')

# Setup our dictionary
domain_urls = defaultdict(dict)

# Parse the zone file
try:
  zone = dns.zone.from_file(inputfile, domain)
  # Loop down to each entry and add it to our dictionary
  for name, node in zone.nodes.items():
    rdatasets = node.rdatasets
    full_name = f"{name}.{domain}"
    for rdataset in rdatasets:
      for rdata in rdataset:
        if rdataset.rdtype == NS:
          domain_urls[full_name]['type'] = "NS"
        if rdataset.rdtype == CNAME:
          domain_urls[full_name]['type'] = "CNAME"
        if rdataset.rdtype == A:
          domain_urls[full_name]['type'] = "A"
except DNSException as e:
  print(e.__class__, e)

# Determine how many we have to create our progress bar
number_of_urls = len(domain_urls)
print(f'Getting certificates for {number_of_urls} domains...')
bar = progressbar.ProgressBar(maxval=number_of_urls, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
current_progress = 0
bar.start()

# Loop through each
if not os.path.exists('output'):
    os.makedirs('output')
f = csv.writer(open('output/domains.csv', 'w'))
for url in domain_urls:
  current_progress = current_progress+1
  bar.update(current_progress)
  url_type = domain_urls[url]['type']
  ssl_info = get_cert_info(url)
  common_name = ssl_info['common_name']
  issued_name = ssl_info['issued_name']
  serial_number = ssl_info['serial_number']
  expiration_date = ssl_info['expiration_date']
  status = ssl_info['status']
  f.writerow([url, url_type, common_name, issued_name, expiration_date, serial_number, status])
bar.finish()

# Give feedback that we are done!
print('Script finished.')



