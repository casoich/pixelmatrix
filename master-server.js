var express = require('express');
var bodyParser = require('body-parser');
var Auth = require('./auth.js');
var auth = Auth.auth;
var services = require('./services.js');
var proxy_request = require('./proxy-request.js');
var zerorpc = require("zerorpc");
var util = require('util');

// Create server
var app = express();

// var client = new zerorpc.Client();
// client.connect("tcp://127.0.0.1:4242");
// app.use(function sendParams (params){
//  client.invoke("getparams", params, function(error, res, more) {
//      console.log("node says:", res);
//  });

// })
var clientParams={
        argument:"scurry",
        brightness:"255",
        saturation:"100",
        hue:"26",
        hue2:"128",
        count:"67",
        speed:"100",
        offset:"50"
    };
var server = new zerorpc.Server({
    hello: function(name, reply) {
        reply(null, "services Hello, " + name);
    },
    broadcastParams: function(params,reply) {
    	//console.log("broadcast request:",clientParams)
        //this talks from the node server to the Python script whenever python requests it
        reply(null, clientParams);
    }
    // getParams: function(name, reply) {
    //     reply(null, )
    // }
});

server.bind("tcp://0.0.0.0:4242");


// Configure middleware
app.use(bodyParser.json()); // for parsing appplication/json
app.use(function logRequest (req, res, next) {
    //console.log('Received request: ' + req.url);
    if (req.url=="/param")
    {
        clientParams=req.body.params;
    }
    if (req.url=="/brightness")
    {
        clientParams['brightness']=req.body.params['brightness'];
    }
    return next();
});

// Configure static files
app.use(express.static('app'));

// Login route
app.post('/login', Auth.login);

// Ping route to check auth
app.head('/ping', auth, function (req, res, next) {
    return res.sendStatus(200);
});

// config route,s (unique to master pi)
app.get('/config', auth, services.getConfig);
app.put('/config', auth, services.updateConfig);

app.get('/brightness', auth, services.getConfig);
app.put('/brightness', auth, services.updateConfig);
app.get('/wtf',auth, services.wtf);

app.get('/param',auth, services.getParams);

// error handler
app.use(function errorHandler(err, req, res, next) {
    //console.log(util.inspect(req));
    //res.status(500).json({'error': 'master-server.js: An error occurred on:'+req+':' + err});
});

app.listen(80, function listen () {
   console.log("Master Server listening at port 80.");
});
