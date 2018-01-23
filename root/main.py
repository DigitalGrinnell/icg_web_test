from webdriver_util import init
from selenium.webdriver.support import expected_conditions as EC   # available since 2.26.0
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


def send_notification_via_gmail(t, msg):
  if 'gmail_address' in t:
    message = 'Subject: {}\n\n{}'.format('Failures Encountered in ICG_Web_Test', msg)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls( )
    server.login(t['gmail_address'], t['gmail_password'])
    server.sendmail(t['gmail_address'], t['gmail_address'], message)
    server.quit( )


def clean_file( ):
  with open('/tests/raw.out') as f:
    file = f.read().split('\n')
  for i in range(len(file)):
    file[i] = sub(r'\[\d*m', '', file[i])
  with open('/tests/icg_web_test_output.txt', 'w') as f1:
    f1.writelines(["%s\n" % item  for item in file])
  os.remove('/tests/raw.out')


def run_test(info_dict):
  num_passed = 0
  num_failed = 0

  print(c.OKBLUE + "Loading Firefox driver...", end=' ')
  driver, waiter, selector, datapath = init()
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

      elif 'match' in test:
        for a_match in test['match']:
           if 'id' in a_match:
             print(c.OKBLUE + "  Looking for an element ID of '{0}' in {1}...".format(a_match['id'],full_url) + c.ENDC)
             try:
               found = driver.find_element_by_id(a_match['id']).text
               print(c.OKGREEN + "    Element ID '{}' was found!".format(a_match['id']) + c.ENDC)
               num_passed += 1
               if 'text' in a_match:
                 if a_match['text'] in found:
                   print(c.OKGREEN + "    Element ID '{0}' includes the target text of '{1}'!".format(a_match['id'],a_match['text']) + c.ENDC)
                   num_passed += 1
                 else:
                   print(c.FAIL + "    Element ID '{0}' does NOT contain target '{1}' text.".format(a_match['id'],a_match['text']) + c.ENDC)
                   num_failed += 1
             except:
               print(c.FAIL + "    Element ID '{}' was NOT found.".format(a_match['id']) + c.ENDC)
               num_failed += 1

           elif 'class' in a_match:
             print(c.OKBLUE + "  Looking for an element CLASS of '{0}' in {1}...".format(a_match['class'],full_url) + c.ENDC)
             try:
               found = driver.find_element_by_class_name(a_match['class']).text
               print(c.OKGREEN + "    Element CLASS '{}' was found!".format(a_match['class']) + c.ENDC)
               num_passed += 1
               if 'text' in a_match:
                 if a_match['text'] in found:
                   print(c.OKGREEN + "    Element CLASS '{0}' includes the target text of '{1}'!".format(a_match['class'],a_match['text']) + c.ENDC)
                   num_passed += 1
                 else:
                   print(c.FAIL + "    Element CLASS '{0}' does NOT contain target '{1}' text.".format(a_match['class'],a_match['text']) + c.ENDC)
                   num_failed += 1
             except:
               print(c.FAIL + "    Element CLASS '{}' was NOT found.".format(a_match['class']) + c.ENDC)
               num_failed += 1

           elif 'xpath' in a_match:
             print(c.OKBLUE + "  Looking for an element XPATH of '{0}' in {1}...".format(a_match['xpath'],full_url) + c.ENDC)
             try:
               found = driver.find_element_by_xpath(a_match['xpath']).text
               print(c.OKGREEN + "    Element XPATH '{}' was found!".format(a_match['xpath']) + c.ENDC)
               num_passed += 1
               if 'text' in a_match:
                 if a_match['text'] in found:
                   print(c.OKGREEN + "    Element XPATH '{0}' includes the target text of '{1}'!".format(a_match['xpath'],a_match['text']) + c.ENDC)
                   num_passed += 1
                 else:
                   print(c.FAIL + "    Element XPATH '{0}' does NOT contain target '{1}' text.".format(a_match['xpath'],a_match['text']) + c.ENDC)
                   num_failed += 1
             except:
               print(c.FAIL + "    Element XPATH '{}' was NOT found.".format(a_match['xpath']) + c.ENDC)
               num_failed += 1

    except:
      print(c.FAIL)
      print("Unexpected error:", sys.exc_info()[0])
      print(c.ENDC)
      num_failed += 1
      raise

  msg = "All '{0}' tests are complete with {1} passed and {2} failed.".format(site_description,num_passed,num_failed)
  print(c.OKBLUE + c.HEADER)
  print(msg)
  print(c.ENDC)
  driver.quit( )

  if num_failed > 0:
    send_notification_via_gmail(info_dict['target'], msg)


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
