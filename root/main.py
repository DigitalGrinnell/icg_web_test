from webdriver_util import init
from selenium.webdriver.support import expected_conditions as EC   # available since 2.26.0
import private

from re import sub
import glob
import yaml
import pprint
import sys
import os
import smtplib


class c:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


class Tee(object):
  def __init__(self, *files):
    self.files = files
  def write(self, obj):
    for f in self.files:
      f.write(obj)
      f.flush( )        # If you want the output to be visible immediately
  def flush(self):
    for f in self.files:
      f.flush( )


def send_notification_via_smtp(m_text):
  try:
    private.notification_address
    private.mailgun_smtp_login
    private.mailgun_default_password
  except NameError:
    print(c.FAIL + "See /root/private.example.py if you wish to enable failure notifications via email." + c.ENDC)
    return

  message = 'Subject: {}\n\n{}'.format('Failures Encountered in ICG_Web_Test', m_text)
  server = smtplib.SMTP('smtp.mailgun.org', 587)
  server.starttls( )
  server.login(private.mailgun_smtp_login, private.mailgun_default_password)
  server.sendmail(private.mailgun_smtp_login, private.notification_address, message)
  server.quit( )


def clean_file( ):
  with open('/tests/raw.out') as f:
    file = f.read().split('\n')
  for i in range(len(file)):
    file[i] = sub(r'\[\d*m', '', file[i])
  with open('/tests/icg_web_test_output.txt', 'w') as f1:
    f1.writelines(["%s\n" % item  for item in file])
  os.remove('/tests/raw.out')


def do_match(driver, a_match, url):
#  pp = pprint.PrettyPrinter(indent=2)
#  pp.pprint(a_match)

  found = mtext = mtype = mattr = False
  passed = failed = 0

  for typ, attr in a_match.items( ):
    if (typ == 'text'):
      mtext = attr
    else:
      mtype = typ
      mattr = attr

    if mtype:
      print(c.OKBLUE + "  Looking for {2} of '{0}' in {1}...".format(attr, url, mtype.upper( )) + c.ENDC)
      try:
        if (mtype == 'xpath'):
          found = driver.find_element_by_xpath(mattr).text
        elif (mtype == 'class'):
          found = driver.find_element_by_class_name(mattr).text
        elif (mtype == 'id'):
          found = driver.find_element_by_id(mattr).text
        elif (mtype == 'link'):
          found = driver.find_element_by_partial_link_text(mattr).text
        else:
          print(c.FAIL + "Check your .yml file.  Match type '{}' is not supported.".format(mtype) + c.ENDC)
          return 0,0
      except:
        print(c.FAIL + "    Element with {1} = '{0}' was NOT found.".format(mattr, mtype.upper( )) + c.ENDC)
        failed += 1

    if found:
      print(c.OKGREEN + "    Element with {1} = '{0}' was found!".format(mattr, mtype.upper( )) + c.ENDC)
      passed += 1

    if found and mtext:
      if mtext in found:
        print(c.OKGREEN + "    Element with {2} = '{0}' contains the target text of '{1}'!".format(mattr, mtext, mtype.upper( )) + c.ENDC)
        passed += 1
      else:
        print(c.FAIL + "    Element with {2} = '{0}' does NOT contain the target text of '{1}'.".format(mattr, mtext, mtype.upper( )) + c.ENDC)
        failed += 1

  return passed, failed


def run_test(info_dict):
  num_passed = passed = 0
  num_failed = failed = 0

  print(c.OKBLUE + "Loading Firefox driver...", end=' ')
  driver, waiter, selector, datapath = init( )
  print("...done." + c.ENDC)

  target = info_dict['target']
  base_url = target['base-url']
  site_description = target['site-description']
  tests = target['tests']

  print(c.OKBLUE + "Begin processing tests for '{}' with a base URL of '{}'.".format(site_description, base_url) + c.ENDC)

  for test in tests:
    description = test['description']
    full_url = base_url + test['url']
    print(" ")
    print(c.OKBLUE + "{} ---------- ".format(description))
    print("Fetching '{}'...".format(full_url), end=' ')

    try:
      driver.get(full_url)
      print("...done." + c.OKBLUE)
      waiter.shoot(site_description + " - " + description)
      print(c.ENDC),

      if 'fail' in test:
        print(c.FAIL + "Forced Failure!!!  {} ".format(test['fail']) + c.ENDC)
        num_failed += 1

      elif 'match' in test:
        for a_match in test['match']:
          (passed, failed) = do_match(driver, a_match, full_url)
          num_passed += passed
          num_failed += failed

    except:
      print(c.FAIL)
      print("Unexpected error:", sys.exc_info()[0])
      print(c.ENDC)
      num_failed += 1
      raise

  msg = "All '{0}' tests are complete with {1} passed and {2} failed.".format(site_description, num_passed, num_failed)
  print(c.OKBLUE + c.HEADER)
  print(msg)
  print(c.ENDC)
  driver.quit( )

  if num_failed > 0:
    send_notification_via_smtp(msg)


def parse_and_run_tests( ):
  files = glob.glob('/tests/*.yml')
  f = open('/tests/raw.out', 'w')
  original = sys.stdout
  sys.stdout = Tee(sys.stdout, f)   # print to both console and output file

  for yml in files:
    print("----------------")
    print("Found '{}' in /tests.  Processing it now.".format(yml))
    with open(yml) as info:
      info_dict = yaml.load(info)
#      pp = pprint.PrettyPrinter(indent=2)
#      pp.pprint(info_dict)
      run_test(info_dict)


if __name__ == '__main__':
  parse_and_run_tests( )
  clean_file( )
