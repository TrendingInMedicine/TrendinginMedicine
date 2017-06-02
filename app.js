// #!/usr/bin/nodejs
// ABOVE LINE FOR TJ SERVER
var express = require('express');
const socketIO = require('socket.io');
var path = require('path');
var hb = require('handlebars');
var exphbs = require('express-handlebars');

const PORT = process.env.PORT || 8080;
// #!/usr/bin/nodejs
// ABOVE LINE FOR TJ SERVER

var express = require('express');
var path = require('path');
var app = express();
var hb = require('handlebars');
var exphbs = require('express-handlebars');
var http = require("http").Server(app);
var io = require("socket.io")(http);

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
var articles = [];

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

// app.set('port', process.env.PORT || 8080);
http.listen(PORT, function(){
  console.log('hosted on: http://localhost:8080');
})
app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
});

app.get('/index', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
});

io.on("connection", function(socket){
  // socket.emit("connection", {articles:articles});
  socket.on("topic", function(data){
    var db = admin.database();
    console.log(data.topic);
    var ref = db.ref(data.topic);
    ref.once("value")
    .then(function(snapshot) {
      snapshot.forEach(function(childSnapshot)
      {
        for(var i = 0; i < childSnapshot.val().length; i++)
        {
          articles.push(childSnapshot.val()[i]);
        }
    });

    socket.emit("topPhrases", {articles : articles});
    console.log("xd");
    });
  });
});

app.get('/trends', function(req, res) {
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

  // console.log(articles)
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
