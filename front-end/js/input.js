$(document).ready(function () {

    $('.form-login')
        .bootstrapValidator({
            feedbackIcons: {
                valid: 'glyphicon glyphicon-ok',
                invalid: 'glyphicon glyphicon-remove',
                validating: 'glyphicon glyphicon-refresh'
            },
            fields: {
                name: {
                    validators: {
                        notEmpty: {
                            message: '请输入姓名'
                        },
                    }
                },
                mac: {
                    validators: {
                        notEmpty: {
                            message: '请输入mac地址'
                        },
                    }
                }
            }
        })//下面必须重写表单，因为bootstrapValidator靠这个来识别提交事件
        .on('success.form.bv', function (e) {

            e.preventDefault();
            var form = $(e.target);

            $.post(form.prop('action'), form.serialize(), function (data) {

                if (data[0] === "true") {
                    $('input[type="text"]').val('');
                    $('input[name="name"]').focus();
                    $('.form-group').removeClass('has-success');
                    $('.form-group i').css('display','none');

                } else {

                    var errmsg = data[1];
                    function make_danger(msg) {
                        return $('<div class="alert alert-danger fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a>' + msg + '</div>');
                    }

                    if (errmsg === 'mac_not_correct') {
                        tip = make_danger('mac地址格式错误,格式形如1A:2B:3C:4D:5E:6F')
                    }else if (errmsg === 'db_connect_error'){
                        tip = make_danger('数据库连接错误,请联系管理员')
                    }else if (errmsg === 'need_mac'){
                        tip = make_danger('未输入mac地址')
                    }else if (errmsg === 'need_name'){
                        tip = make_danger('未输入姓名')
                    }else if (errmsg === 'unknown'){
                        tip = make_danger('未知错误')
                    } else {
                        tip = make_danger('登录失败,错误信息读取失败')
                    }

                    form.children('.tip').html(tip);
                    $('input[name="password"]').val('');

                }

            }, 'json');

        });

    $('input[name="name"]').keypress(function(event){
        var keycode = (event.keyCode ? event.keyCode : event.which);
        if(keycode == '13'){
            $('input[name="mac"]').focus();
            return false;
        }
    });

});