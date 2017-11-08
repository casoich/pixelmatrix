var child_process = require('child_process');
// var MongoClient = require('mongodb').MongoClient;
// var ObjectID = require('mongodb').ObjectID;
var config = require('./config.js');

module.exports = (function Services () {
    // need to save the feed process so it can be killed by a second rest call if it doesn't exit by itself
    var feedProcess = null;

    function getParams (req, res, next) {
        console.log('Firing GetParams:',req, res, next);
        server.broadcastParams()
    }

    function wtf (req, res, next) {
        console.log("in wtf",req,res,next);
        return {};

    }

    function getConfig (req, res, next) {
        console.log("in getConfig",req,res,next);
        return res.json(clientParams);
    }

    function updateConfig (req, res, next) {
                console.log("in updateConfig",req,res,next);

                return res.json(clientParams);

    }

    function proxyRequest (req, res, next) {
        var method = req.body.method;
        var ip = req.body.ip;
        var route = req.body.route;
        var params = req.body.params;

        if (!method || !ip || !route || !params) {
            console.error('Missing parameters to proxy');
            return next('Missing parameters to proxy');
        }
    }

    return {
        getParams: getParams,
        wtf: wtf,
        getConfig: getConfig,
        updateConfig: updateConfig,
        proxyRequest: proxyRequest,

    };
})();
