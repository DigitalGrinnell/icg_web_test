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

from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



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
      f.flush( )
  def flush(self):
    for f in self.files:
      f.flush( )


def send_notification_via_smtp(m_text, num_failed):
  try:
    private.notification_address
    private.mailgun_smtp_login
    private.mailgun_default_password
  except NameError:
    print(c.FAIL + "See /root/private.example.py if you wish to enable failure notifications via email." + c.ENDC)
    return

  ftext = "{txt}".format(txt="One Failure" if num_failed == 1 else "Failures")
  message = 'Subject: {0} {1}\n\n{2}'.format(ftext, 'Encountered in ICG_Web_Test', m_text)
  server = smtplib.SMTP('smtp.mailgun.org', 587)
  server.starttls( )
  server.login(private.mailgun_smtp_login, private.mailgun_default_password)
  server.sendmail(private.mailgun_smtp_login, private.notification_address, message)
  server.quit( )


def clean_file_and_dispatch_notification(total_failed, completed_tests):
  out_file = '/tests/icg_web_test_output.txt'
  ftext = "{txt}".format(txt="Failure" if total_failed == 1 else "Failures")

  with open('/tests/raw.out') as f:
    file = f.read().split('\n')
  for i in range(len(file)):
    file[i] = sub(r'\[\d*m', '', file[i])
  with open(out_file, 'w') as f1:
    f1.writelines(["%s\n" % item  for item in file])

  os.remove('/tests/raw.out')

  # Create the enclosing (outer) message
  outer = MIMEMultipart( )
  outer['Subject'] = "ICG Web Test: {0} {1}".format(total_failed, ftext)
  outer['To'] = private.notification_address
  outer['From'] = private.mailgun_smtp_login
  outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'
  body = "ICG Web Test has checked the following files and finished with {0} {1}.\n{2}".format(total_failed, ftext.lower( ), tests)
  body = MIMEText(body)   # convert the body to a MIME compatible string
  outer.attach(body)      # attach it to your main message

  # List of attachments
  attachments = [out_file]

  # Add the attachments to the message
  for file in attachments:
    try:
        with open(file, 'rb') as fp:
            msg = MIMEBase('application', "octet-stream")
            msg.set_payload(fp.read())
        encoders.encode_base64(msg)
        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))
        outer.attach(msg)
    except:
        print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])
        raise

  composed = outer.as_string( )

  # Send the email
  try:
    with smtplib.SMTP('smtp.mailgun.com', 587) as s:
      s.ehlo( )
      s.starttls( )
      s.ehlo( )
      s.login(private.mailgun_smtp_login, private.mailgun_default_password)
      s.sendmail(private.mailgun_smtp_login, private.notification_address, composed)
      s.close( )
    print(c.OKBLUE + "A summary email has been dispatched!" + c.ENDC)
    print( )
  except:
    print(c.FAIL + "Unable to send the email. Error: " + c.ENDC, sys.exc_info()[0])
    print( )
    raise


def do_authentication(browser, auth, base_url):
#  pp = pprint.PrettyPrinter(indent=2)
#  pp.pprint(auth)

  try:
    username = auth['username']
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but the reqiured 'username' element could not be found." + c.ENDC)
    raise
  try:
    login_url = auth['login-url']
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but the reqiured 'login-url' element could not be found." + c.ENDC)
    raise
  try:
    uname_field = auth['user-input-id']
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but the reqiured 'user-input-id' element could not be found." + c.ENDC)
    raise
  try:
    passw_field = auth['pass-input-id']
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but the reqiured 'pass-input-id' element could not be found." + c.ENDC)
    raise
  try:
    login_form = auth['form-id']
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but the reqiured 'form-id' element could not be found." + c.ENDC)
    raise

  full_url = base_url + login_url
  print(c.OKBLUE + "Authentication as '{0}' at {1}...".format(username, full_url), end=' ')
  browser.get(full_url)
  stripped = base_url.split("://",2)[1]

  ufield = browser.find_element_by_id(uname_field)
  ufield.send_keys(username)
  pfield = browser.find_element_by_id(passw_field)
  try:
    passw = private.passwords[stripped]
  except NameError:
    print(c.FAIL + "Error: Authentication specified, but no password is defined for '{0}'.".format(stripped) + c.ENDC)
    raise
  pfield.send_keys(passw)
  form = browser.find_element_by_id(login_form)
  form.submit( )
  print("...successful." + c.ENDC)
  print( )


def do_match(driver, a_match, url):
#  pp = pprint.PrettyPrinter(indent=2)
#  pp.pprint(a_match)

  passed = failed = 0

  for mtyp, mattr in a_match.items( ):
    typ = mtyp
    if isinstance(mattr, dict):
      attr = mattr['attr']
      txt = mattr['text']
    else:
      attr = mattr
      txt = False

    print(c.OKBLUE + "  Looking for {2} of '{0}' in {1}...".format(attr, url, typ.upper( )) + c.ENDC)
    found = False

    try:
      if (typ == 'xpath'):
        found = driver.find_element_by_xpath(attr)
      elif (typ == 'class'):
        found = driver.find_element_by_class_name(attr)
      elif (typ == 'id'):
        found = driver.find_element_by_id(attr)
      elif (typ == 'link'):
        found = driver.find_element_by_partial_link_text(attr)
      elif (typ == 'selector'):
        found = driver.find_element_by_css_selector(attr)
      else:
        print(c.FAIL + "Check your .yml file.  Match type '{}' is not supported.".format(typ) + c.ENDC)
        return 0,0
    except:
      print(c.FAIL + "    Element with {1} = '{0}' was NOT found.".format(attr, typ.upper( )) + c.ENDC)
      failed += 1

    if found:
      print(c.OKGREEN + "    Element with {1} = '{0}' was found!".format(attr, typ.upper( )) + c.ENDC)
      passed += 1
      if txt:
        if txt in found.text:
          print(c.OKGREEN + "    Element with {2} = '{0}' contains the target text of '{1}'!".format(attr, txt, typ.upper( )) + c.ENDC)
          passed += 1
        else:
          print(c.FAIL + "    Element with {2} = '{0}' does NOT contain the target text of '{1}'.".format(attr, txt, typ.upper( )) + c.ENDC)
          failed += 1

  return passed, failed


def run_test(info_dict):
  num_passed = passed = 0
  num_failed = failed = 0

  print(c.OKBLUE + "Loading Firefox driver...", end=' ')
  driver, waiter, selector, datapath = init( )
  print("...done." + c.ENDC)

  try:
    target = info_dict['target']
  except NameError or KeyError:
    print(c.FAIL + "Error: The reqiured 'target' element could not be found." + c.ENDC)
    return 1

  try:
    base_url = target['base-url']
  except NameError or KeyError:
    print(c.FAIL + "Error: The reqiured 'base-url' element could not be found." + c.ENDC)
    return 1

  try:
    site_description = target['site-description']
  except NameError or KeyError:
    print(c.FAIL + "Error: The reqiured 'site-description' element could not be found." + c.ENDC)
    return 1

  # If authentication is reqiured...do it here.
  try:
    auth = target['authentication']
  except:
    print(c.OKBLUE + "Authentication is not specified.  Tests will run without login." + c.ENDC)
  else:
    do_authentication(driver, auth, base_url)

  try:
    tests = target['tests']
  except NameError or KeyError:
    print(c.FAIL + "Error: The reqiured 'tests' element could not be found." + c.ENDC)
    return 1

  print(c.OKBLUE + "Begin processing tests for '{0}' with a base URL of '{1}'.".format(site_description, base_url) + c.ENDC)

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
      print(c.ENDC)

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
    send_notification_via_smtp(msg, num_failed)

  return num_failed


def parse_and_run_tests( ):
  total_failed = 0
  tests = ''

  files = glob.glob('/tests/*.yml')
  f = open('/tests/raw.out', 'w')
  original = sys.stdout
  sys.stdout = Tee(sys.stdout, f)   # print to both console and output file

  for yml in files:
    print("----------------")
    print("Found '{}' in /tests.  Processing it now.".format(yml))
    tests += '\n\t{}'.format(yml)

    with open(yml) as info:
      info_dict = yaml.load(info)
#      pp = pprint.PrettyPrinter(indent=2)
#      pp.pprint(info_dict)
      total_failed += run_test(info_dict)

  return total_failed, tests.strip(', ')


# ------------------------------------------------------

if __name__ == '__main__':
  (total_failed, tests) = parse_and_run_tests( )
  clean_file_and_dispatch_notification(total_failed, tests)
