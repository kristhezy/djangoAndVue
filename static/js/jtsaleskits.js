window.onload = querymsgbyds([3],10);
//点击复制到剪切板
var skInit = document.getElementById('skInit');
skInit.addEventListener('click',function() {
    var cids = document.getElementById('companyIds').value;
    var sseats = document.getElementById('sseats').value;
    var pseats = document.getElementById('pseats').value;
    var env = document.querySelector("input[name='env']:checked").value;
    var type = document.querySelector("input[name='type']:checked").value;
    var jzc = document.querySelector("input[name='jz']:checked").value;
    const mk = Array.from(document.querySelectorAll("input[type='checkbox'][name='mk']:checked"))
        .map(cb => cb.value)
        .join(","); 
    if (cids.length == 0 || sseats.length == 0 || pseats.length == 0) {
        alert('必填项不能为空！');
        return;
    }
    //企业类型
    console.log('type:',type)
    if(type == 'zs'){
        var t = 0
    }else if(type == 'jz'){
        t=1
        if(!jzc){
            alert('家装类型不能为空! ');
            return
        }
    }
    var data = JSON.stringify({
        "companyIds": cids,
        "sseats": sseats,
        "pseats": pseats,
        "mk":mk,
        "env": env,
        "jzc": jzc,
        "type":t
    })
    //输入为空校验
    console.log('mkkkk:',mk,'\ndata:',data)
    document.getElementById('skInit').setAttribute('disabled','');
    var result1 = document.getElementById('result1');
    result1.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
    axios.post(`/sv/jtSaleskits`,data,{headers: header})
    .then(response => {
        var res = response.data;
        console.log('加推Saleskits企业初始化s:', res.code,res.data);
        result1.innerHTML = res.data.skCompanyConfig;
        document.getElementById('skInit').removeAttribute('disabled');
        querymsgbyds([3],6);
    })
    .catch(err => {
        console.log(`加推Saleskits企业初始化err: ${err}`)
    })
});
//控制版本和环境的选择
document.addEventListener('DOMContentLoaded', function() {
    // 初始执行一次（设置默认状态）
    handleRadioChange();
    // 给所有单选框绑定change事件（按name分组，也可全局监听）
    const radioList = document.querySelectorAll('input[type="radio"]');
    radioList.forEach(radio => {
        radio.addEventListener('change', handleRadioChange);
    });
});

function handleRadioChange(e) {
    const radio = document.querySelectorAll('input[type="radio"]:checked');
    radio.forEach(radio => {
        const radioId = radio.id;
        const bb = document.getElementById('jz'); //家装版本
        var mks = document.querySelectorAll('input[name="mk"]');
        // console.log($(this).attr('id'))
        if (radioId == 'zs') {
            tenv.removeAttribute('disabled');
            document.getElementById("cmk").style.display='';
            document.getElementById("jzc").style.display='none';
        }
        if (radioId == 'jz') {
            //家装版时，宁夏联通环境不可选择
            tenv.setAttribute('disabled', '');
            document.getElementById("cmk").style.display='none';
            document.getElementById("jzc").style.display='';
            for (var i = 0; i < mks.length; i++) {
                mks[i].checked = false; //清除模块勾选状态
            }
        }
    })
}
