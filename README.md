# PPE-Data-Visualization

A WebGL app for visualising HepMC files. Designed as part of a summer project for University of Glasgow's Experimental Particle Physics group by Darius Darulis building on Dr Andy Buckley's work.

# Requirements:

All Python dependencies are part of the included Python virtual environment (for now, to be replaced by a requirements.txt), but are listed below for posterity:

* Flask
* PyMongo-Flask
* PyPDT
* NumPy

Additionally, some sort of MongoDB instance must be installed.

# How to use:

The app is currently fairly simple. Upload HepMC files using the upload page; access them for visualization in the Visualiser tab by using a Visualiser/<filename> URL pattern. 

Press 1 to switch to momentum view and 2 to switch to spacetime view. B and N change to previous and next event in the file respectively.
