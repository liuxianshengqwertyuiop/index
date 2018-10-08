$(function () {
    $("#saveBoard").click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        var name = $("#boardName").val();
        var id = $("#id").val()
        ev.preventDefault();
        var saveoradd = $(this).attr('from');
        if  (saveoradd == 1){
             url = "/cms/updateboard/";
        }else {
            url = "/cms/addboard/";
        }
        $.ajax({
            url:url,
            type:"post",
            data :{
                "csrf_token":csrf,
                "boardname":name,
                "id":id
            },
            success:function (data) {
                if (data.code == 200){
                    xtalert.alertSuccessToast(data.msg);
                    window.location = "/cms/board/"
                }else {
                    xtalert.alertErrorToast(data.msg)
                }
            }
        })
    });
    $('.update-btn').click(function () {
        self = $(this);
        $('#myModal').modal('show');// 让模态框出来
        $('meta[name=csrf_token]').attr("value");
        $("#data-boardname").val();
        $('#saveBoard').attr("from",'1');
        $('#id').val(self.attr('data-id'));
        console.log($('#id').val())
    });
     $('#myModal').on('hidden.bs.modal', function (e) {
         e.preventDefault();
         $('#saveBoard').attr("from",'0')
    });
     $('.delete-btn').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        self = $(this);
        id = self.attr('data-id');
         $.ajax({
            url:'/cms/deleteboard/',
            type:'post',
            data:{
                'csrf_token':csrf,
                'id':id
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
    });
});