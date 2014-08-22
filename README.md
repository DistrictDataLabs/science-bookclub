# Science Bookclub #
**Generating the next read for our book club- with Data Science!**

[![The Stockholm Octavo][stockholm_octavo.jpg]][stockholm_octavo.jpg]

## A Recommender Tutorial ##

If you're here, it's probably because you are taking the [District Data Labs](http://districtdatalabs.com) _Building Data Apps with Python_ course. If you're sitting in class, waiting for it to start- go ahead and clone the master branch of this repository:

    $ git clone https://github.com/DistrictDataLabs/science-bookclub.git

Note that you might have to fork the repository into your own username if authentication over SSL is not working correctly. If you're really ahead of the game- go ahead and set up your virtual environment and install the various dependencies.

If you're here after the class- congratulations on making it through! I know the course was probably a whirlwind of full immersion, and you don't know where to begin. This repository is broken up into branches. The `master` branch - or the branch that you're currently in, simply has the python project stubs- but no code has been added as of right now. It is my recommendation that you clone this branch and attempt to fill in the code for yourself.

If you're in trouble and need help- then go ahead and checkout the code from other branches to see the code that we wrote in class (or something close to it). Remember, this is a learning exercise, so try to be creative and come up with your own solutions!

## Quick Start ##

If you're in the Syllabus branch (which is the only branch you should see this text), and you want to run the project from start to finish using the completed `ocatvo-admin.py` command, then this quick start guide will walk you through it! 

### Installation ###

1. **Clone the repository**

        ~$ git clone git@github.com:DistrictDataLabs/science-bookclub.git
        ~$ cd science-bookclub

2. **Create the virtualenv**
    
        ~$ mkvirtualenv -a $(pwd) octavo
        ...
        (octavo)~$ pip install -r requirements.txt

3. **Unpack the fixtures**

        (octavo)~$ unzip fixtures/data.zip
        
4. **Setup your configuration**

        (octavo)~$ cp conf/octavo-sample.yaml conf/octavo.yaml
        (octavo)~$ vim conf/octavo.yaml
       
    Make sure you put in absolute paths to the directories you want to keep the database and the htdocs. Typically I just keep them in the fixtures directory. You also need to add your Goodreads API key and API-Secret. 

### Ingestion ###

To run the ingestion process, see the `reviewers.csv` file that contains a list of Goodreads users and their userids. You can (and should) add your own as well as your friends names and IDs, the caveat here is that their reviews must be public (we're not doing any authentication). 

If you can't find the `reviewers.csv`, simply create a CSV file with a header, that contains `name,id` pairs as follows:

    name,id
    Benjamin,8398291
    Harlan,7962723
    Veronica Belmont,8121761
    Tom Merritt,93524
    Tony,32882668

Create and sync your database:

    (octavo)~$ bin/octavo-admin.py syncdb

This will create the database at the location you specified in your 

To run the ingestor:
    
    (octavo)~$ bin/octavo-admin.py ingest --batch --bulk-ingest fixtures/reviewers.csv

The `--batch` flag specifies a paginated download to get all the fixtures from the user. The --bulk-ingest takes a path to a CSV file where it will load multiple user ids. If you'd like to ingest one id at a time, run the following command:

    (octavo)~$ bin/octavo-admin.py ingest --batch $USER_ID

Where `$USER_ID` is the id of the user you want to fetch. 

Note that all the XML files will be downloaded to the `htdocs` directory that you specified in your configuration file. 

### Wrangling ###

The wrangling process is pretty straight forward, you just have to pass a list of XML files to load into the database. Use the following command:

    (octavo)~$ bin/octavo-admin.py wrangle fixtures/htdocs/*

This may take a few minutes, but it will load all the books, authors, and reviews (as well as users) into the database. 

If you've been using a `reviewers.csv` file to bulk load, then you may want to get those names into the database, there isn't an `ocatavo-admin.py` command for this (yet), but you can load them with a helper function built into the library as follows:

    (octavo)~$ python
    >>> from ocatavo.wrangle import wrangle_users
    >>> wrangle_users('fixtures/reviewers.csv')

This will assure that the names you put in the CSV will now be in the database.

### Model Computation ###

The next part is the model building. This is going to take a long time so book a few hours to let this run in the background. At the time of this writing it took me **12 hours 30 minutes** to build a model with 30k books and 22k reviews!

    (ocatvo)~$ bin/octavo-admin.py build fixtures/reccod-$(date "+%m%d%Y").pickle
    
This will get things going, just ignore your terminal for a while. It may be best to run this overnight. Also note that the `$(date "%m%d%Y")` may be different on your system, this is the command on OS X 10.9 - there is a slightly different format for Linux. However, it is a good idea to label the various models with some means to identify them in the future, rebuilding them is occassionally not an option!

### Reporting ###

At last you can get recommendations out of your system with the model at hand. To generate a recommendation report for a particular user, issue the following command:

    (octavo)~$ bin/ocatvo-admin.py report $USER_ID

Where `$USER_ID` is the Goodreads ID of the user you want to find recommendations for (probably your own). This will write a report out to `$USER_ID.html` in the current working directory; open it in a browser!

## What is an Octavo? ##

The definition of "octavo" is as follows:

    oc·ta·vo
    äkˈtävō/Submit
    noun
    noun: octavo; symbol: 8vo

    1. a size of book page that results from the folding of each printed
       sheet into eight leaves (sixteen pages).

       - a book of octavo size.

    plural noun: octavos

Since we're doing a project with books, this is a farily short namespace and no one else is using this name, I thought it would be a great name for our package and command line program!

The picture refers to the cover of a fictional book by Karen Engelmann: [The Stockholm Octavo](http://www.amazon.com/dp/0061995347/), a literary historical fiction set in Sweeden, where the main characters perform [cartomancy](http://en.wikipedia.org/wiki/Cartomancy) to divine the future. We don't have to perform cartomancy, we have a predictive model in the form our recommender system!

<!-- References -->
[stockholm_octavo.jpg]: http://media.salon.com/2012/10/stockholm_octavo_rect_rev.jpg
