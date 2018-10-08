$(function () {
    $('.delete-btn').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        self = $(this);
        var common_id = self.attr('data-id');
         $.ajax({
            url:'/cms/deletecommon/',
            type:'post',
            data:{
                'csrf_token':csrf,
                "common_id":common_id
            },
            success:function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("删除成功");
                    window.location.reload(); //  重新加载这个页面
                } else {  // 提示出错误
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    })
});