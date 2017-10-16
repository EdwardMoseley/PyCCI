# PyCCI

Save CCIv3.py to your desktop.

You have to use your terminal to run the program. You can use command+space to open spotlight, and there type in "terminal" and hit enter.

We're greeted by this guy:

![alt text](https://github.com/EdwardMoseley/PyCCI/blob/master/images/img1.png "Terminal Window")

Let's run a few quick checks.

Type "python" into your terminal, and hit enter. Here we'll see what you have for a python version (it should be 2.something). Below is mine:

![alt text](https://github.com/EdwardMoseley/PyCCI/blob/master/images/img2.png "Python")

Once you see that you do indeed have python, you can get out of the python console by typing in:
quit()

We want python to open the patient note annotation program, so now we're going to type:

python ~/Desktop/CCIv3.py

We will have the following result:

![alt text](https://github.com/EdwardMoseley/PyCCI/blob/master/images/img3.png "PyCCI")

Note that your terminal remains open, because any error output from python is going to go to your terminal (this makes everyone's life easier if there's a bug)-- see that below we have a deprecated command (it isn't a problem though), and I purposefully opened a file with no name to show that python will tell us where the error occurred:

![alt text](https://github.com/EdwardMoseley/PyCCI/blob/master/images/img4.png "Terminal Window")

That stuff isn't too important for the user's purposes, though, because hopefully the user won't need to deal with any debugging!

I've also attached sampleDat.csv-- which you can open with CCIv3.py. It's set up in the same way as our data files, but it doesn't have any protected info-- you can use it to make sure everything is working properly.

After annotating the notes, you will notice that you have a SampleDatResultsCCIv3.csv file, also. The results file is where we store our data, and it is the only copy until you email it out. Inside the file will look like this:

![alt text](https://github.com/EdwardMoseley/PyCCI/blob/master/images/img5.png "Terminal Window")

To contact the admin of this repo, please email:
Etmoseley@yahoo.com

Acknowledgements:
Isabel Chien for a complete refactoring and contributions toward an executable/application version of the software.

Kai-ou Tang for front end advice and coding.

William Labadie Moseley for development.

