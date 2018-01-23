# icg_web_test

This tool is based on work found in weihanwang/webdriver-python.  My copy resides in a fork at https://github.com/DigitalGrinnell/icg_web_test and you are certainly welcome to clone or fork this repo and give it a try.  There is much room for improvement in the code and in the Dockerization too.  The process I use to test elements of https://digital.grinnell.edu, as well as Grinnell's ISLE "Alpha" server, and elements of our LIBWEB server. To run the tool on any platform with Docker and git installed…
 
~~~
git clone https://github.com/DigitalGrinnell/icg_web_test.git 
cd icg_web_test
docker build –t “icg:icg_web_test”      <-- build a local image, takes a couple minutes
docker-compose run icg_web_test         <-- run the icg_web_test portion of docker-compose.yml
~~~

You should see some output in your terminal window as the tests run against Digital Grinnell. 
 
If you would like to create tests of your own just make a copy of ./tests/digital_grinnell.yml and give your copy a different name.  The name can be anything you like, but the .yml extension is required and it must reside in the ./tests folder.  Edit your .yml file using my file as a guide.  It should be pretty self-explanatory.  If you leave my digital_grinnell.yml file in place it “should” run both my tests AND yours.  The code should run as many .yml test suites as it finds in ./tests.
 
This early version of the tool uses a Firefox browser and should create screenshot .png files in the ./screenshots folder.  If find these images to be very helpful too.

The README.md contents of weihanwang's origial webdriver-python tool appears below without edits.


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




