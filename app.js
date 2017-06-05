// #!/usr/bin/nodejs
// ABOVE LINE FOR TJ SERVER
var express = require('express');
const socketIO = require('socket.io');
var path = require('path');
var hb = require('handlebars');
var exphbs = require('express-handlebars');

const PORT = process.env.PORT || 8080;
var app = express()
.use("/css",  express.static(path.join(__dirname, '/css')))
.use("/js", express.static(path.join(__dirname, '/js')))
.use("/media", express.static(path.join(__dirname, '/media')))
.use("/fonts", express.static(path.join(__dirname, '/fonts')))
.use("/views", express.static(path.join(__dirname, 'views')))
.engine('.hbs', exphbs({extname: '.hbs' }))
.set('view engine', '.hbs')
.get('/trends', function(req, res) {
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
})
.get('/register', function(req, res) {
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
})
.get('/', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
})
.get('/index', function(req, res) {
  res.sendFile(path.join(__dirname + '/index.html'));
})
.listen(PORT, () => console.log(`Listening on ${ PORT }`))

var admin = require("firebase-admin");
var serviceAccount = require(__dirname + '/serviceAccountKey.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  databaseURL: "https://trendinginmedicine-f41fc.firebaseio.com"
});


const io = socketIO(app);
var articles = [];
io.on("connection", function(socket){
  socket.on("topic", function(data){
    articles = [];
    fillArticles(data.topic, articles, function(){
      console.log(articles.length);
      socket.emit("articles", {articles:articles})
    });
  });
});
function fillArticles(topic, articles, callback){
  var db = admin.database();
  var ref = db.ref(topic);
  console.log("Got topic: " + topic);
  ref.on("value", function(snapshot) {
    snapshot.forEach(function(childSnapshot){
      for(var i = 0; i < childSnapshot.val().length; i++){
        articles.push(childSnapshot.val()[i]);
      }
    });
    callback();

  })
}
