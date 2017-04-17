// #!/usr/bin/nodejs
// ABOVE LINE FOR TJ SERVER

var express = require('express');
var path = require('path');
var app = express();
// var firebase = require('firebase/app');
// require('firebase/database');

app.use("/css",  express.static(__dirname + '/css'));
app.use("/js", express.static(__dirname + '/js'));
app.use("/media", express.static(__dirname + '/media'));
app.use("/fonts", express.static(__dirname + '/fonts'));

var admin = require("firebase-admin");
var serviceAccount = require(__dirname + '/serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://trendinginmedicine-f41fc.firebaseio.com"
});

//how to firebase:
// var db = admin.database();
// var snowshal = 0;
// var count = db.ref("count");
// count.on("value", function(snapshot)
// {
// 	console.log(snapshot.val()["vistors"]);
// 	snowshal = snapshot.val()["vistors"];
//
// });

app.set('port', process.env.PORT || 8080);

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/index', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/register', function(req, res) {
  console.log("boshal")
  admin.auth().createUser({
    email: req.query['email'],
    emailVerified: false,
    password: req.query['password'],
    displayName: req.query['name'],
    disabled: false
  })
  .then(function(userRecord) {
    // See the UserRecord reference doc for the contents of userRecord.
    console.log("Successfully created new user:", userRecord.uid);
  })
  .catch(function(error) {
    console.log("Error creating new user:", error);
  });
});

var listener = app.listen(app.get('port'), function() {
  console.log( listener.address().port );
});
