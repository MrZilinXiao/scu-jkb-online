function my_ajax(url,callback,params=null,method='get',isasy=true){
    var xmlhttp;
    /*获取XMLRequest的对象，可以发送异步请求*/
    if (window.XMLHttpRequest){
        xmlhttp = new XMLHttpRequest();
    }else{
        xmlhttp - new ActiveXOBject('Microsoft.XMLHTTP');
    }
    /*绑定事件*/
    xmlhttp.onreadystatechange = function(){
        if (xmlhttp.readyState==4 && xmlhttp.status==200){
            callback(xmlhttp.responseText)
        }
    }
    /*准备并发送*/
    xmlhttp.open(method, url, isasy)
    xmlhttp.send(params)
}