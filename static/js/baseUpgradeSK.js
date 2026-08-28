
// 设置 AJAX 请求头
let busk = document.getElementById('busk');
busk.addEventListener('click',function() {
    let cids = document.getElementById('companyIds').value;
    let sseats = document.getElementById('sseats').value;
    let pseats = document.getElementById('pseats').value;
    let env = document.querySelector("input[name='env']:checked").value;
    const mk = Array.from(document.querySelectorAll("input[type='checkbox'][name='mk']:checked"))
        .map(cb => cb.value)
        .join(",");
    let data = JSON.stringify({
        "companyIds": cids,
        "sseats": sseats,
        "pseats": pseats,
        "mk": mk,
        "env": env
    })
        //输入为空校验
    if (cids.length == 0 || sseats.length == 0 || pseats.length == 0) {
        alert('必填项不能为空！');
        return;
    }
    document.getElementById('busk').setAttribute('disabled','');
    const rlt = document.getElementById('rlt'); 
    rlt.innerHTML = "<img src='../static/img/loading.gif' height='10'/>"; //在后台返回success之前显示loading图标
    axios.post(`/sv/baseUpgradeSK`,data,{headers: header})
    .then(response => {
        var res = response.data;
        console.log('销售工具版升级Saleskits版s:', res);
        rlt.innerHTML = res.data;
        document.getElementById('busk').removeAttribute('disabled');
    })
});