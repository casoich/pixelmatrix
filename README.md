# pixelmatrix
A web application for the pixelmatrix light project.

Contains an Angular 1.5 front end, a node-js api to run on the master PI, and a node-js api .

Packages to install:
- node.js & npm (sudo apt-get install nodejs npm)
- may need to symlink node (because debian called it nodejs for whatever reason) (cd /usr/bin \n sudo ln -s ./nodejs ./node)
- forever (sudo npm install -g forever)
- bower (sudo npm install -g bower)

In project root, run
- npm install

In /app folder, run
- bower install

To run on master PI, start (as sudo, to run on port 80) master-server.js. 
- sudo forever start master-server.js

The angular app will be served from the PI via port 80.
