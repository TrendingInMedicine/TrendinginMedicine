function openLoginModal(){
showLoginForm();
setTimeout(function(){
    $('#loginModal').modal('show');
}, 230);

}
function openRegisterModal(){
showRegisterForm();
setTimeout(function(){
    $('#loginModal').modal('show');
}, 230);

}
function showRegisterForm(){
$('.loginBox').fadeOut('fast',function(){
    $('.registerBox').fadeIn('fast');
    $('.login-footer').fadeOut('fast',function(){
        $('.register-footer').fadeIn('fast');
    });
    $('.modal-title').html('Register');
});
$('.error').removeClass('alert alert-danger').html('');

}
function showLoginForm(){
$('#loginModal .registerBox').fadeOut('fast',function(){
    $('.loginBox').fadeIn('fast');
    $('.register-footer').fadeOut('fast',function(){
        $('.login-footer').fadeIn('fast');
    });

    $('.modal-title').html('Login');
});
 $('.error').removeClass('alert alert-danger').html('');
}


//email validation
function validateForm() {
    var x = document.forms["myForm"]["email"].value;
    var atpos = x.indexOf("@");
    var dotpos = x.lastIndexOf(".");
    if (atpos<1 || dotpos<atpos+2 || dotpos+2>=x.length) {
        alert("Not a valid e-mail address!");
        return false;
    }
    var y = document.forms["myForm"]["password"].value;
    var z = document.forms["myForm"]["password_confirmation"].value;
    if(y.length < 6 || y.length>20)
    {
      alert("Password needs to be 6-20 characters!");
      return false;
    }
    if(y!=z)
    {
      alert("Passwords need to match!");
      return false;
    }
}
