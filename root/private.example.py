# You must make a copy this file and create private.py in order for these settings to take effect.
# Do NOT share or publish your private.py file!  Make sure it is indluced in your .gitignore file.
#
# To take advantage of failure notifications via email you must have a working Mailgun.com SMTP server.
# You can obtain a free "sandbox" server at https://mailgun.com.  This is required
# only if you want the system to dispatch notification of failed tests to private.notification_address.
#
mailgun_smtp_login = "Enter your 'Default SMTP Login' From Mailgun Dashboard here"
mailgun_default_password = "Enter the 'Default Password' from your Mailgun Dashboard here"
notification_address = 'digital@grinnell.edu'
#
# Usernames and passwords for sites/tests which require authentication.
# @TODO: As of 24-Jan-2018 no tests require authentication.
#
authuser['digital.grinnell.edu'] =
  { 'name': 'System Admin',           # username for any auth required tests
    'pass': 'putYourPasswordHere' }   # be sure to edit in username's password here!
#
authuser['libweb.grinnell.edu'] =
  { 'name': 'System Admin',           # username for any auth required tests
    'pass': 'putYourPasswordHere' }   # be sure to edit in username's password here!
