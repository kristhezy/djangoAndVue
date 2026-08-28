window.onload = querymsgbyds([1],10);
//点击复制到剪切板
function copy(){
    const input = document.createElement('input') // 创建input对象
    const testDiv = document.querySelector('.rsql') // 获取需要复制文字的容器
    input.value = testDiv.innerText; // 设置复制内容
    document.body.appendChild(input); // 添加临时实例
    input.select(); // 选择实例内容
    document.execCommand('Copy'); // 执行复制
    document.body.removeChild(input); // 删除临时实例
    alert('复制成功！')
}
//升级转介绍3.0版本
let sysUpgrade = document.getElementById('sysUpgrade');
sysUpgrade.addEventListener('click',function(){
    var companyIds = document.getElementById('companyIds').value;
    var seats = document.getElementById('seats').value;
    var env = document.querySelector("input[name='env']:checked").value;
    var data = JSON.stringify({
        companyIds,seats,env
    })
        //输入为空校验
    if (companyIds.length == 0 || seats.length == 0) {
        if (companyIds.length == 0) {
            alert('企业id不能为空！');
            return;
        }
        if (seats.length == 0) {
            alert('席位数不能为空！');
            return;
        }
    }
    const rsql = document.getElementById('rsql');
    const copybtn = document.getElementById('copybtn');
    const result1 = document.getElementById('result1');
    rsql.innerHTML = '';
    copybtn.innerHTML = ' ';
    result1.innerHTML = "<img src='../static/img/loading.gif' height='10'/>"; //在后台返回success之前显示loading图标
    axios.post(`/sv/upgradeR3`,data,{headers: header})
    .then(response => {
        var res = response.data;
        console.log('升级转介绍3.0/配置招商版企业s:', res);
        result1.innerHTML = res.data.upgradeR3;
        document.getElementById("tips").innerHTML = "菜单sql,若企业菜单异常,需执行此处sql";
        rsql.innerHTML = res.data.ur3sql;
        copybtn.innerHTML = "<a href='https://sqlprod.jiatuiyun.net/submitsql/' target='_blank'><button class='btnstyle' onclick='copy()'>复制并跳转提交sql</button></a>";
        querymsgbyds([1],4);
    })
    .catch(err => {console.log(`升级转介绍3.0/配置招商版企业 err: ${err}`)})
});
