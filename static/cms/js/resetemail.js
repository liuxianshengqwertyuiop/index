$(function () {
    $('#sendEmailCode').click(function (ev) {
        self = $(this);
        email = $('#email').val()
        csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        $.ajax({
            url: '/cms/send_email_code/',
            type: 'post',
            data: {
                'email': email,
                'csrf_token': csrf,
            },
            success: function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("邮箱验证码发送成功，请查收")
                    self.attr('disabled', true);
                    var time = 5;
                    self.html(time + "s") // 就是5秒
                    var timer = setInterval(function () {
                        self.html(--time + 's');
                        if (time <= 0) {
                            clearInterval(timer);
                            self.html("再次发送");
                            self.attr('disabled', false);
                        }
                    }, 1000);
                } else {  // 提示出错误
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })

    $('#resetpwdbtn').click(function (ev) {
        ev.preventDefault();
        email = $('#email').val();
        csrf = $('meta[name=csrf_token]').attr("value");
        emailCode = $('#emailcode').val();
        "".match()
        $.ajax({
            url: '/cms/resetemail/',
            type: 'post',
            data: {
                'email': email,
                'csrf_token': csrf,
                'emailCode': emailCode
            },
            success: function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("修改邮箱成功")
                } else {
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })

    })
})