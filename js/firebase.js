// Set the configuration for your app
// TODO: Replace with your project's config object
var config = {
  apiKey: "apiKey",
  authDomain: "projectId.firebaseapp.com",
  databaseURL: "https://databaseName.firebaseio.com",
  storageBucket: "bucket.appspot.com"
};
firebase.initializeApp(config);

var urlParams = new URLSearchParams(window.location.search);
// console.log(urlParams.get('topic'));
var s = urlParams.get('topic');
if (s == null) {
  s = "Medicine";
}
else {
  var s = s[0].toUpperCase() + s.slice(1);
  var myDiv = document.getElementById('boshal');
  var h1 = document.createElement("h1");
  var t = document.createTextNode(s);
  h1.appendChild(t);
  myDiv.appendChild(h1);
  console.log(s.toLowerCase());
}

// Get a reference to the database service
var db = firebase.database();
var ref = db.ref(s.lowerCase())
ref.once("value")
.then(function(snapshot) {
  snapshot.forEach(function(childSnapshot)
  {
    for(var i = 0; i < childSnapshot.val().length; i++)
    {
      articles.push(childSnapshot.val()[i]);
    }
  });
  console.log(articles);
});

function displayArticles(){
  console.log("xd");
  var myDiv = document.getElementById("topPhrases");
  console.log(data.articles);
  for (var i = 0; i < data.articles.length; i++) {
    var temp = data.articles[i].split(" ");
    if (temp.length <= 4 ){
      var term = document.createElement("h3");
      console.log(term);
      var t = document.createTextNode(data.articles[i]);
      term.appendChild(t);
      myDiv.appendChild(term);
      var j = 0;
    }
    else{
      var article = document.createElement("a");
      var ref  = data.articles[i].substring(data.articles[i].indexOf("https:"), data.articles[i].length);
      // console.log(ref);
      article.setAttribute('href', ref);
      var t = document.createTextNode(data.articles[i]);
      article.appendChild(t);
      if (j <= 4){
        myDiv.appendChild(article);
        myDiv.appendChild(document.createElement("br"));
        myDiv.appendChild(document.createElement("br"));
      }
      if (j == 4){
        var read = document.createElement("a");
        var rt = document.createTextNode("View more");
        read.style.align = "center"
        read.appendChild(rt);
        read.setAttribute('class', "read_more");
        myDiv.appendChild(read);

      }
      j++;
    }
  }
});
}
