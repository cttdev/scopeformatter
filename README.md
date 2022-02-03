### Welcome to Scope Formatter, a program that allows you to graph a oscilliscope curve and zoom in to the curve. It requires data logged in the form of a txt file. 
#Installation:
##Artifact Method:
At the navigation bar, go to actions, then to click the topmost workflow flow, scroll down, then download the artifact for the specified os.
##Base Method:
Clone the repository and enter
`
py -3.9 -m pip install -r ./requirements.txt
`
then run
`
py scope_formatter.py
`
##Usage:
* To start, click the load txt file button and choose the specified file, then hit plot.
* Hit zero offset.
* The graph on the left is the overall curve which will always stay the same.
* To zoom in, click and drag to create a magnifier which will show up on the right.
* Hovering over any point will give the "coordinate" or the details of the point.