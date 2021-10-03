function doLogin(e) {
    if (e != null && e.keyCode != 13) {
        return false;
    }

    var loginname = $.trim($("#login-name").val());
    var loginpass = $.trim($("#login-password").val());
    var logincode = $.trim($("#login-code").val());

    if (loginname.length < 5 || loginpass.length < 5) {
        bootbox.alert({title:"错误提示", message:"用户名和密码少于5位."});
        return false;
    }
    else {
        // 构建POST请求的正文数据
        var param = "username=" + loginname;
        param += "&password=" + loginpass;
        param += "&vcode=" + logincode;
        // 利用jQuery框架发送POST请求，并获取到后台登录接口的响应内容
        $.post('/login', param, function (data) {
            if (data == "vcode-error") {
                bootbox.alert({title:"错误提示", message:"验证码无效."});
                $("#logincode").val('');  // 清除验证码框的值
                $("#logincode").focus();   // 让验证码框获取到焦点供用户输入
            }
            else if (data == "login-pass") {
                bootbox.alert({title:"信息提示", message:"恭喜你，登录成功."});
                // 注册成功后，延迟1秒钟重新刷新当前页面即可
                setTimeout('location.reload();', 1000);
            }
            else if (data == "login-fail") {
                bootbox.alert({title:"错误提示", message:"登录失败，请联系管理员."});
            }
        });
    }
}