# icg_web_test

This tool is based on work found in weihanwang/webdriver-python.  My copy resides in a fork at https://github.com/DigitalGrinnell/icg_web_test and you are certainly welcome to clone or fork this repo$

~~~
git clone https://github.com/DigitalGrinnell/icg_web_test.git
cd icg_web_test
docker build -t icg_web_test .     <-- Build a local image. Takes a couple minutes. Don't forget the period at the end!
docker-compose run icg_web_test    <-- Run the icg_web_test portion of docker-compose.yml for all /tests/*.yml files.
~~~

You should see some output in your terminal window as the tests run against Digital Grinnell.

If you would like to create tests of your own just make a copy of ./tests/digital_grinnell_public.yml, or any other .yml file found in /tests or /tests/DISABLED, and give your copy a different name.  You may also find the /tests/DISABLED folder to be useful...you can move .yml files there to effectively "disable" them but also keep them as examples or for use at a later time.

#### Environment Options (Variables)

icg_web_test resoponds to two optional environment varaibles/settings.

**-e TEST** - You may also run a single .yml file or 'glob' of files by specifying a TEST=*path* environment variable with the 'docker-compose run' command, similar to the following:

    docker-compose run -e TEST='/tests/DISABLED/Google.yml' icg_web_test

or

    docker-compose run -e TEST='/tests/DISABLED/Digital*.yml' icg_web_test


Note that when using this option the file(s) specified by TEST must be accessible within the icg_web_test container, as are all files inside the /tests directory and its subordinates.

**-e BASE_URL** - You may override the base URL specified in the selected YAML file(s) using an environment spec similar to the following:

    docker-compose run -e BASE_URL='https://microsoft.com' icg_web_test

or

    docker-compose run -e TEST='/tests/digital_grinnell_public.yml' -e BASE_URL='https://isle-dev.localdomain' icg_web_test


The first example would run all /tests/*.yml test files but with a base URL of 'https://microsoft.com' instead of whatever is specified inside each *.yml file.

The second example would run the tests prescribed for Digital Grinnell - Public, but against an isle-dev.localdomain host instance of ISLE.


#### Firefox and Screenshots

This early version of the tool uses a Firefox browser and should create screenshot .png files in the ./screenshots folder.  I find these images to be very helpful too.

At Grinnell, we run a daily suite of tests using a root cron job on server DGDockerX, a CentOS 7 VM dedicated to running Docker.  The crontab entry in our case reads like this:

~~~
0 6 * * * /bin/bash -c 'source /home/mcfatem/Projects/Docker/icg_web_test/cron.sh'
~~~

The README.md contents of weihanwang's origial webdriver-python tool appears in its original form below.







# webdriver-python

This is a Docker container combined with a few utility functions to simplify writing Selenium tests in Python.
It uses Firefox as the driver. [Dockerfile](https://github.com/weihanwang/webdriver-python/blob/master/Dockerfile).

## Run example code

The example test querys the keyword "test" at google.com and print the first search result to stdout:

    $ docker run weihan/webdriver-python

To export screenshots to the ./shots folder on the host computer:

    $ docker run -v $PWD/shots:/sreenshots aerofs/webdriver-python

## Write tests

Check out [this document](http://selenium-python.readthedocs.org/en/latest/) for Selenium's concepts and operations.

To write new tests, you can either bind mount your python files to the container or create a new Docker image and copy files into the image.
The example code is located at `/main.py` in the container. You may overwrite this file or place your files at different locations. For the latter,
run the container as follows:

    $ docker run weihan/webdriver-python python -u /path/to/your/python/code

At the beginning of your code, call `webdriver_util.init()` to set up the
environment and retrieve a few utility objects. Screenshots will be saved at the container's "/screenshots" folder.
You may use bind mount to export them to the host.

    from webdriver_util import init
    driver, wait, selector = init()

`driver` is the Selenium WebDriver object

`wait` is a convenience wrapper around WebDriverWait. Every call to `wait.until*()` methods produce useful console output and a screenshot at the end of the wait.
You can also use `wait.shoot()` at any time to save a screenshot.

`selector` provides shortcuts to `WebDriver.find_element_by_css_selector()`. It restricts element selection to using CSS selectors only.

See [example code](https://github.com/weihanwang/webdriver-python/tree/master/root/main.py) for the usage of these objects.


## Customize

Use the `RESOLUTION` environmental variable to customize screen size and depth. The default is "1024x768x24".
For example:

    docker run -e RESOLUTION=1920x1600x24 weihan/webdriver-python


## Build from source

Check out [this GitHub repository](https://github.com/weihanwang/webdriver-python) and run this command in the repository's root folder:

    $ docker build -t aerofs/webdriver-python .
