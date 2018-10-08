$(function () {
    $(".update-btn").click(function (ev) {
        ev.preventDefault();
        self = $(this);
        var csrf = $("meta[name=csrf_token]").attr("value")
        var data_tag = self.attr('data-tag');
        var url = "/cms/addtag/";
        if  (data_tag == 'canceltag'){
            url = "/cms/deletetag/";
        }
        var post_id = self.attr('data-id');
        $.ajax({
            url:url,
            type:"post",
            data :{
                "csrf_token":csrf,
                "post_id":post_id
            },
            success:function (data) {
                if (data.code == 200){
                    xtalert.alertSuccessToast(data.msg);
                    window.location.reload()
                }else {
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    });
    $('.delete-btn').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        self = $(this);
        var post_id = self.attr('data-id');
        var baord_name = self.attr('delete-boardname');
         $.ajax({
            url:'/cms/deletepost/',
            type:'post',
            data:{
                'csrf_token':csrf,
                "post_id":post_id,
                "board_name":baord_name
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