$(function () {
    $('#saveBanner').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        var bannerName = $("#bannerName").val();
        var imglink=$('#imglink').val();
        var link=$('#link').val();
        var priority = $('#priority').val();
        var id = $('#id').val();
        ev.preventDefault();
        self = $(this);
        var saveoradd = self.attr('from');
        url = '/cms/addbanner/';
        if (saveoradd == '1') {
              url = '/cms/updatebanner/';
        }
        $.ajax({
            url:url,
            type:'post',
            data:{
                'csrf_token':csrf,
                'bannerName':bannerName,
                'imglink':imglink,
                'link':link,
                'priority':priority,
                'id':id
            },
            success:function (data) {
                if (data.code == 200) {
                    xtalert.alertSuccessToast("添加成功");
                    $('#myModal').modal('hide');
                    window.location.reload(); //  重新加载这个页面
                } else {  // 提示出错误
                    xtalert.alertErrorToast(data.msg)
                }
            },
            error:function (err) {
                xtalert.alertErrorToast('请检查网络');
            }
        })
    })

    $('.delete-btn').click(function (ev) {
        var csrf = $('meta[name=csrf_token]').attr("value");
        ev.preventDefault();
        self = $(this);
        id = self.attr('data-id');
         $.ajax({
            url:'/cms/deletebanner/',
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
    })

    // 当模态视图隐藏的时候
    $('#myModal').on('hidden.bs.modal', function (e) {
         e.preventDefault();
         $('#saveBanner').attr("from",'0');
         // 把表单中的值设置成空
         $("#bannerName").val("");
         $('#imglink').val("");
         $('#link').val("");
         $('#priority').val("");
    })

    $('.update-btn').click(function () {
        self = $(this);
        $('#myModal').modal('show');// 让模态框出来
        $('meta[name=csrf_token]').attr("value");
        $("#bannerName").val(self.attr('data-bannerName'));
        $('#imglink').val(self.attr('data-imglink'));
        $('#link').val(self.attr('data-link'));
        $('#priority').val(self.attr("data-priority"));
        $('#saveBanner').attr("from",'1')
        $('#id').val(self.attr('data-id'))
    })

    // 上传图片到七牛云
uploader = Qiniu.uploader({
            runtimes: 'html5,html4,flash',
            browse_button: 'select_img_btn',//上传按钮的ID,
            max_file_size: '4mb',//最大文件限制
            dragdrop: false, //是否开启拖拽上传
            uptoken_url: '/cms/qiniu_token/',//设置请求qiniu-token的url
            domain: 'pfpjd7i5o.bkt.clouddn.com',//自己的七牛云存储空间域名
            get_new_uptoken: false, //是否每次上传文件都要从业务服务器获取token
            auto_start: true, //如果设置了true,只要选择了图片,就会自动上传
            unique_names: true,
            multi_selection: false,//是否允许同时选择多文件
            //文件类型过滤，这里限制为图片类型
            filters: {
              mime_types : [
                {title : "Image files", extensions: "jpg,jpeg,png"}
              ]
            },
            init: {
                'FileUploaded': function (up, file, info) {
                    var res = eval('(' + info + ')');
                    res.key;//获取上传文件的链接地址
                    // $('#imglink').attr('value',sourceLink)
                    sourceLink = 'http://pfpjd7i5o.bkt.clouddn.com/' + res.key;
                    console.log(sourceLink)  // 访问图片的网址
                    // 放到我们的input标签中
                    $("#imglink").val(sourceLink);
                },

                'Error': function(up, err, errTip) {
                    console.log(err);
                    xtalert.alertErrorToast("上传失败")
                }
            }
        })

})