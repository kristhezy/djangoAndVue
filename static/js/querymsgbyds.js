// 查询操作信息
function qbdan(dss, num){
    var data = JSON.stringify({ "dss": dss, "num": num });
    const jst = document.getElementById('jst');
    jst.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
    axios.post(`/sv/qmbydsan`, data, {headers: header})
    .then(response => {
        var str = "";
        var res = response.data.data.qmbydsan;
        console.log('查询操作信息:', res);
        if (!Array.isArray(res)) { jst.innerHTML = '<div class="result-empty">暂无数据</div>'; return; }
        for (var i in res) {
            var cn = res[i].companyName;
            var cid = res[i].companyId;
            var env = res[i].env;
            var m = res[i].message;
            var t = res[i].t;
            str = str + `<div class="result-item"><div class="result-item__head"><span class="result-item__title">${env} ┆ ${escapeHTML(String(cn))}（${cid}）</span><span class="result-item__time">${t}</span></div><div class="result-item__msg">${m}</div></div>`;
        }
        jst.innerHTML = str;
    })
    .catch(err => { console.log(`查询操作信息err: ${err}`); });
}

// 查询并异步刷新缓存
function querymsgbyds(dss, num){
    qbdan(dss, num);
    var data = JSON.stringify({ "dss": dss, "num": num });
    axios.post(`/sv/aftergetqmbydsan`, data, {headers: header})
    .then(response => {
        var res = response.data.data;
        console.log('异步调用qmbydsan s:', res);
        if (res == "更新数据成功！"){
            console.log('更新数据成功！ == ', res);
            qbdan(dss, num);
        }
    })
    .catch(err => { console.log(`异步调用qmbydsanerr: ${err}`); });
}
