$( document ).ready(function() {

    loadProfile();
});

function getLocalProfile(callback){
    var profileImgSrc      = localStorage.getItem("PROFILE_IMG_SRC");
    var profileName        = localStorage.getItem("PROFILE_NAME");
    var profileReAuthEmail = localStorage.getItem("PROFILE_REAUTH_EMAIL");

    if(profileName !== null
            && profileReAuthEmail !== null
            && profileImgSrc !== null) {
        callback(profileImgSrc, profileName, profileReAuthEmail);
    }
}
function loadProfile() {
    if(!supportsHTML5Storage()) { return false; }
    getLocalProfile(function(profileImgSrc, profileName, profileReAuthEmail) {
        $("#profile-img").attr("src",profileImgSrc);
        $("#profile-name").html(profileName);
        $("#reauth-email").html(profileReAuthEmail);
        $("#inputEmail").hide();
        $("#remember").hide();
    });
}

function supportsHTML5Storage() {
    try {
        return 'localStorage' in window && window['localStorage'] !== null;
    } catch (e) {
        return false;
    }
}

function testLocalStorageData() {
    if(!supportsHTML5Storage()) { return false; }
    localStorage.setItem("PROFILE_IMG_SRC", "//lh3.googleusercontent.com/-6V8xOA6M7BA/AAAAAAAAAAI/AAAAAAAAAAA/rzlHcD0KYwo/photo.jpg?sz=120" );
    localStorage.setItem("PROFILE_NAME", "César Izquierdo Tello");
    localStorage.setItem("PROFILE_REAUTH_EMAIL", "oneaccount@gmail.com");
}

$(function () {
    $('#loginBtn').click(function (ev) {
        email = $('#inputEmail').val();
        pwd = $('#inputPassword').val();
        csrf = $('meta[name=csrf_token]').attr("value")
        ev.preventDefault();
        $.ajax({
            url:'/cms/login/',
            type:'post',
            data:{
                'email':email,
                'password':pwd,
                'csrf_token':csrf
            },
            success:function (data) {
                if (data.code == 200) {
                    window.location.href = '/cms/index/'
                } else {  // 提示出错误
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })
})