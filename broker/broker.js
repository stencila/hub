var http = require('http');
var httpServer = http.createServer();

var express = require('express');
var expressApp = express();
var bodyParser = require('body-parser');
expressApp.use(bodyParser.json())
httpServer.on('request', expressApp);

var collab = require('stencila/web/collab');
collab.bind(httpServer, expressApp);

httpServer.listen(7315, '0.0.0.0', function() {
  console.log("Listening at http://" + httpServer.address().address + ":" + httpServer.address().port + "/");
});
