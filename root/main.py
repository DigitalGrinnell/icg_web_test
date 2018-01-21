from webdriver_util import init
from selenium.webdriver.support import expected_conditions as EC   # available since 2.26.0
import glob
import yaml
import pprint
import sys

#def query_google(keywords):
#    print("Loading Firefox driver...")
#    driver, waiter, selector, datapath = init()
#
#    print("Fetching google front page...")
#    driver.get("http://google.com")
#
#    print("Taking a screenshot...")
#    waiter.shoot("frontpage")
#
#    print("Typing query string...")
#    selector.get_and_clear("input[type=text]").send_keys(keywords)
#
#    print("Hitting Enter...")
#    selector.get("input[type=submit]").click()
#
#    print("Waiting for results to come back...")
#    waiter.until_display("#ires")
#
#    print
#    print("The top search result is:")
#    print
#    print('    "{}"'.format(selector.get("#ires a").text))
#    print

class c:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'

def run_test(info_dict):
  print(c.OKBLUE + "Loading Firefox driver..."),
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
    print("Fetching '{}'...".format(full_url)),
    try:
      driver.get(full_url)
      print("...done." + c.OKBLUE)
      waiter.shoot(description)
      print(c.ENDC),
      if 'fail' in test:
        print(c.FAIL + "!!! Test Failed !!!  {} ".format(test['fail']) + c.ENDC)
      if 'match' in test:
        for one_match in test['match']:
           print(c.OKBLUE + "  Looking for '{}' in {}...".format(one_match,full_url) + c.ENDC)

    except:
      print(c.FAIL)
      print("Unexpected error:", sys.exc_info()[0])
      print(c.ENDC)
      raise

  print(c.OKBLUE + c.HEADER)
  print("All '{}' tests are complete.".format(site_description))
  print(c.ENDC)
  driver.quit()

#    print("Taking a screenshot...")
#    waiter.shoot("dg_home_page")
#
#    print('Initial page title is: "{}"'.format(driver.title))
#
#    try:
#        #waiter.shoot("inside_try")
#        waiter.until(EC.title_contains("Grinnell"))
#        print('Inside "try" the page title is: "{}"'.format(driver.title))
#
#    finally:
#        driver.quit( )


def parse_and_run_tests( ):
  files = glob.glob('/tests/*.yml')
  for yml in files:
    print("----------------")
    print("Found '{}' in /tests.  Processing it now.".format(yml))
    with open(yml) as info:
      info_dict = yaml.load(info)
      pp = pprint.PrettyPrinter(indent=2)
      pp.pprint(info_dict)
      run_test(info_dict)

if __name__ == '__main__':
#    query_google('test')
    parse_and_run_tests( )
