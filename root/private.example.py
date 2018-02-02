# You must make a copy this file and create private.py in order for these settings to take effect.
# Do NOT share or publish your private.py file!  Make sure it is included in your .gitignore file.
#
# To take advantage of failure notifications via email you must have a working Mailgun.com SMTP server.
# You can obtain a free "sandbox" server at https://mailgun.com.  This is required
# only if you want the system to dispatch notification of failed tests to private.notification_address.
#
mailgun_smtp_login = "Enter your 'Default SMTP Login' From Mailgun Dashboard here"
mailgun_default_password = "Enter the 'Default Password' from your Mailgun Dashboard here"
notification_address = 'digital@grinnell.edu'
#
# Passwords for sites/tests which require authentication.
# @TODO: As of 2-Feb-2018 only the digital_grinnell_admin.yml tests require authentication.
#
passwords = {
  'digital.grinnell.edu': 'putPasswordHere',         # be sure to edit in username's password here!
  'libweb.grinnell.edu': 'putPasswordHere',
  }
