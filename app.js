// #!/usr/bin/nodejs
// ABOVE LINE FOR TJ SERVER

var express = require('express');
var path = require('path');
var app = express();
var hb = require('handlebars');
var exphbs = require('express-handlebars');
// var firebase = require('firebase/app');
// require('firebase/database');

app.use("/css",  express.static(path.join(__dirname, '/css')));
app.use("/js", express.static(path.join(__dirname, '/js')));
app.use("/media", express.static(path.join(__dirname, '/media')));
app.use("/fonts", express.static(path.join(__dirname, '/fonts')));
app.use("/views", express.static(path.join(__dirname, 'views')))  ;
app.engine('.hbs', exphbs({extname: '.hbs' }));
app.set('view engine', '.hbs');
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

app.get('/trends', function(req, res) {
  var articles = [];
  // res.sendFile(path.join(__dirname + '/trends.html'));
  var db = admin.database();
  var ref = db.ref("surgery")
  ref.once("value")
  .then(function(snapshot) {
    snapshot.forEach(function(childSnapshot)
    {
      for(var i = 0; i < childSnapshot.val().length; i++)
      {
        articles.push(childSnapshot.val()[i]);
      }
  });
  console.log(articles)
  });

  res.render('trends2', {});
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
