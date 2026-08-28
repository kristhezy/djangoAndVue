//选取当前页
var page = 1;
//每页的条数
var num = 10;
var zys = 0;
var selectElement = document.getElementById('unmae');
var shuju = document.getElementById('shuju');


queryOpName();
function queryOpName(){
    axios.post('/pv/other/queryOpraterName',{},{headers:header})
    .then(res => {
        rlt = res.data.data.otherPartRlt;
        console.log('操作人姓名:', rlt);
        const options = rlt.split(",").filter(item => item.trim() !== ''); // 静态数据
        // 添加新选项
        options.forEach(optionText => {
            const option = document.createElement('option');
            option.text = optionText;
            option.value = optionText;
            selectElement.add(option);
        });
    })
    .catch(err => console.log('other-queryOpName error:',err));
};

//加载数据
window.onload = Load();
let sucrlt = ""
function Load() {
    var vers = document.getElementById('vers').value;
    console.log("000000vers:",vers);
    var env = document.getElementById('env').value;
    var compid = document.getElementById('compid').value;
    var compname = document.getElementById('compname').value;
    var uname = selectElement.value;
    console.log('00001uname:',uname)
    var minfo = document.getElementById('message').value;
    var jsondata = JSON.stringify({
        "page": page,
        "env":env,
        "vers": vers,
        "num": num,
        "compid": compid,
        "compname": compname,
        "uname": uname,
        "minfo": minfo
    });
    console.log('动画加载。。。')
    var tbys = "<tr><td class='fstd' colspan=7 style='width:1500; height:1000;border:0'><img src='../static/img/load.gif' width='1500' height='600'/></td></tr>"
    shuju.innerHTML = tbys; //在后台返回success之前显示loading图标
    axios.post('/pv/other',jsondata,{headers:header})
    .then(response => {
        //加载分页列表
        LoadFenYe();
        var str = "";
        var a = response.data.data.oprationalInfo;
        console.log('aaaaa:',a);
        var d = ['用户不存在! ']
            // for (var i=0; i<a.length; i++){
        if (typeof a === 'string' && a.includes("数据库连接异常")){
            str = str+"<tr><td class='fstd' colspan=7 style='font-size:17px;color:gray'>数据库连接异常!</td></tr>"
        }
        else if (!Array.isArray(a) || a.length === 0){
            str = str+"<tr><td class='fstd' colspan=7 style='font-size:17px;color:gray'>查询无数据</td></tr>"
        }
        else{
            sucrlt = a;
            for (var i in a) {
                // console.log('11111111111111:',a[i])
                var id = a[i].id;
                var env = a[i].env;
                var cn = a[i].companyName;
                var cid = a[i].companyId;
                var m = a[i].message;
                var uname = a[i].uname;
                var ct = a[i].createTime;
                var ss = a[i].serverSide;
                var ver = a[i].version;
                console.log('env000:',env,"version:",ver,typeof(ver))
                if(env == '生产' || env == '测试'){
                    if(ver == "1"){
                        envs = env + "/SAAS"
                    }
                    else if(ver == "3"){
                        envs = env + "/基线版"
                        if (env == '生产' && ss == '3'){
                            envs = "私有化/基线版"
                        }
                    }
                    else if(ver == "4"){
                        envs = env + "/Soon"
                    }
                    else if(ver == "5"){
                        envs = env + "/Meet"
                    }
                    else if(ver == "6"){
                        envs = env + "/通威版"
                    }
                    else{
                        envs = env
                    }
                }
                else if(env != '生产' && env != '测试'){
                    envs = env
                }
                str = str + `
                <tr class='ops-row'>
                    <td class='col-seq td-muted'> ${id} </td>
                    <td class="col-env"> ${envs} </td>
                    <td class="col-cid td-dim truncate"> ${cid} </td>
                    <td class="col-cname">
                        <div class="truncate"> ${escapeHTML(String(cn))} </div>
                    </td>
                    <td>
                        <div class='ops-msg'> ${m} &nbsp;<button data-id=${id} class="ops-del"><i class="fa-solid fa-trash-can"></i> 删除</button></div>
                    </td>
                    <td class="col-user"><div class="truncate"> ${escapeHTML(String(uname))} </div></td>
                    <td class="col-time td-muted"> ${escapeHTML(String(ct))} </td>
                </tr>`;
            }
        }
        // console.log('str:',str)
        shuju.innerHTML = str;
    })
    .catch(err => console.log('other-Load error:',err));
}

document.addEventListener('DOMContentLoaded',function() {
    const elist = document.getElementById('shuju');
    console.log(`testtest`)
    elist.removeEventListener('click', oprclick); //移除操作事件监听器
    elist.addEventListener('click', oprclick);  //添加操作事件监听器
});
function oprclick(event){ //操作事件函数
    const target = event.target;
    console.log(`target: ${target.id}`)
    //删除note数据
    if (target.closest('button')) {
        const clickedButton = target.closest('button');
        id = clickedButton.getAttribute('data-id');
        console.log(`del选中的ID是: ${id}`);
        const isd = document.getElementById('isdelete');
        isd.style.display = 'flex';
        const dc = document.getElementById("delcont");
        dc.textContent = `序号(${id})的数据`;
        // 获取被点击的列表项的id
        const sacbtn = document.getElementById('sacbtn');
        sacbtn.removeEventListener('click', delsocclick); // 移除删除确认事件监听器
        sacbtn.addEventListener('click', delsocclick); // 添加删除确认事件监听器
    }
}
function delsocclick(event){ //删除事件二次确认函数
    const target = event.target;
    console.log("targetId：",target.id);
    const isd = document.getElementById('isdelete');
    if (target.id === 'suredel'){
        target.disabled = true;
        target.textContent = '删除中...';
        console.log(`delsocclick中获取的ID是: ${id}`);
        var jdata = JSON.stringify({"id":id});
        axios.post('/pv/other/delmsg',jdata,{headers:header})
        .then(response => {
            zts = response.data.data.otherPartRlt;
            console.log('删除结果suc:', zts)
            showToast("删除成功！")
            Load();
        })
        .catch(err => {
            console.log('删除结果err:', err)
            showToast("删除失败！",xhr)
        })
        .finally(() => {
            target.disabled = false;
            target.textContent = '确定';
        });
    }else if (target.id === 'canceldel'){
        console.log("取消删除！")
    }
    isd.style.display = 'none';
}
var isdelete = document.getElementById('isdelete');
isdelete.addEventListener("click",function(){
    console.log('display');
    const isd = document.getElementById('isdelete');
    isd.style.display = 'none';
})

// 封装分页页码生成逻辑（核心优化点）
// 核心：生成动态页码数组
// 核心：生成动态页码数组
// 核心：生成动态页码数组
function generatePageNumbers(currentPage, totalPages) {
    const pageNumbers = [];
    // 总页数≤10：显示所有页码
    if (totalPages <= 10) {
        for (let i = 1; i <= totalPages; i++) {
            pageNumbers.push(i);
        }
    } else {
        // 总页数>10：按「当前页位置」展示核心页码（前后各4页+边界处理）
        let start = Math.max(1, currentPage - 4);
        let end = Math.min(totalPages, currentPage + 4);

        // 左边界：当前页≤5时，从1开始展示10页
        if (currentPage <= 5) {
            start = 1;
            end = 10;
        }
        // 右边界：剩余页数≤4时，展示最后10页
        else if (totalPages - currentPage < 4) {
            start = totalPages - 9;
            end = totalPages;
        }

        // 生成页码数组
        for (let i = start; i <= end; i++) {
            pageNumbers.push(i);
        }
    }
    return pageNumbers;
}

// 全局声明：分页请求锁（初始为false，无请求）
let isFenYeRequesting = false;

// 分页渲染主函数（核心修复：不替换父容器，仅更新xinxi/tongji内容）
function LoadFenYe() {
    // 只拦“并发请求”：如果上一次请求还在跑，就等它结束后再处理
    if (isFenYeRequesting) {
        setTimeout(() => LoadFenYe(), 100);
        return;
    }
    // 标记为“请求中”，避免并发
    isFenYeRequesting = true;

    // 1. 初始化变量（统一声明+类型校验）
    let pageHtml = "<ul class='page-nav-ul'><li id='fpage' class='page-nav-item fpage'>首页</li><li id='prev' class='page-nav-item prev'>«</li>";
    let totalCount = 0; // 总条数
    let totalPages = 0; // 总页数
    const num = window.num || 10; // 每页条数（容错：默认10）
    let currentPage = parseInt(window.page) || 1; // 当前页（容错：默认1）

    // 2. 获取查询参数（封装+容错）
    const getQueryParams = () => {
        const env = document.getElementById('env')?.value || '';
        const vers = document.getElementById('vers')?.value || '';
        const compid = document.getElementById('compid')?.value || '';
        const compname = document.getElementById('compname')?.value || '';
        const uname = window.selectElement?.value || '';
        const minfo = document.getElementById('message')?.value || '';
        return { env, vers, compid, compname, uname, minfo };
    };

    // 3. 发送请求获取分页总数
    const queryParams = getQueryParams();
    console.log('查询参数:', queryParams);
    
    axios.post('/pv/pagecount', JSON.stringify(queryParams), { headers: header })
        .then(response => {
            // 数据校验
            if (!response.data || !response.data.data) {
                console.warn('分页接口返回数据格式异常:', response);
                return;
            }

            totalCount = parseInt(response.data.data.total) || 0;
            totalPages = Math.ceil(totalCount / num);
            // 修正当前页：防止超出总页数/小于1
            currentPage = Math.max(1, Math.min(currentPage, totalPages));
            window.page = currentPage; // 同步全局page值

            console.log('分页信息:', { totalCount, totalPages, currentPage });

            // 4. 生成页码列表（核心：调用封装的页码生成函数）
            const pageNumbers = generatePageNumbers(currentPage, totalPages);
            pageNumbers.forEach(pageNum => {
                const isActive = pageNum === currentPage;
                pageHtml += `<li ys='${pageNum}' class='page-nav-item ${isActive ? 'page-active' : 'page-list'}'>${pageNum}</li>`;
            });

            // 5. 拼接分页尾部
            pageHtml += `
                <li id='next' class='page-nav-item next'>»</li>
                <li id='epage' class='page-nav-item epage'>末页</li>
                &nbsp;<input type='text' id='spn' class='page-nav-input' placeholder='页码数'/>
            </ul>`;

            // 6. 核心修复：仅更新xinxi/tongji的内容，不修改父容器（保留列表DOM）
            const xinxiEl = document.getElementById('xinxi');
            const tongjiEl = document.getElementById('tongji');
            
            // 给xinxi/tongji添加一行展示的样式类，不改变DOM结构
            if (xinxiEl) {
                xinxiEl.className = 'page-nav-container'; // 分页容器类
                xinxiEl.innerHTML = pageHtml;
            }
            if (tongjiEl) {
                tongjiEl.className = 'page-nav-stat'; // 统计容器类
                tongjiEl.innerHTML = `总共 ${totalCount} 条记录，共 ${totalPages} 页。`;
            }

            // 7. 绑定分页事件（封装+防抖）
            bindPaginationEvents(totalPages, currentPage);
        })
        .catch(err => {
            console.error('分页加载失败:', err);
            // 错误兜底：仅更新xinxi内容，不影响列表
            const xinxiEl = document.getElementById('xinxi');
            if (xinxiEl) {
                xinxiEl.className = 'page-nav-container';
                xinxiEl.innerHTML = "<ul class='page-nav-ul'><li class='page-nav-item'>数据加载失败，请重试</li></ul>";
            }
        })
        .finally(() => {
            isFenYeRequesting = false;
        });
}

// 封装分页事件绑定逻辑（解耦+复用）
function bindPaginationEvents(totalPages) {
    // 防抖函数：避免快速点击重复触发
    const debounce = (fn, delay = 200) => {
        let timer = null;
        return function(...args) {
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    };

    // 页码切换核心逻辑
    const switchPage = (newPage) => {
        newPage = parseInt(newPage);
        const currentPage = parseInt(window.page) || 1;
        if (isNaN(newPage) || newPage < 1 || newPage > totalPages || newPage === currentPage) return;
        window.page = newPage;
        Load(); // 加载数据
        LoadFenYe(); // 重新渲染分页
    };

    // 8.1 首页
    const fpageEl = document.getElementById('fpage');
    if (fpageEl) {
        fpageEl.removeEventListener('click', fpageEl.onclick);
        fpageEl.addEventListener('click', debounce(() => switchPage(1)));
    }

    // 8.2 末页
    const epageEl = document.getElementById('epage');
    if (epageEl) {
        epageEl.removeEventListener('click', epageEl.onclick);
        epageEl.addEventListener('click', debounce(() => switchPage(totalPages)));
    }

    // 8.3 上一页
    const prevEl = document.getElementById('prev');
    if (prevEl) {
        prevEl.removeEventListener('click', prevEl.onclick);
        const currentPage = parseInt(window.page) || 1;
        prevEl.addEventListener('click', debounce(() => switchPage(currentPage - 1)));
    }

    // 8.4 下一页
    const nextEl = document.getElementById('next');
    if (nextEl) {
        nextEl.removeEventListener('click', nextEl.onclick);
        const currentPage = parseInt(window.page) || 1;
        nextEl.addEventListener('click', debounce(() => switchPage(currentPage + 1)));
    }

    // 8.5 数字页码
    const listItems = document.getElementsByClassName('page-list');
    Array.from(listItems).forEach(item => {
        item.removeEventListener('click', item.onclick);
        item.addEventListener('click', debounce(function() {
            const targetPage = parseInt(this.getAttribute('ys')) || 1;
            switchPage(targetPage);
        }));
    });

    // 8.6 输入页码跳转
    const spnEl = document.getElementById('spn');
    if (spnEl) {
        spnEl.removeEventListener('keydown', spnEl.onkeydown);
        spnEl.addEventListener('keydown', debounce(function(e) {
            if (e.key === 'Enter') {
                const inputPage = parseInt(this.value.trim()) || 1;
                switchPage(inputPage);
                this.value = '';
            }
        }));
    }
}

// 分页样式：一行展示 + 固定宽度页码 + 右对齐 + 不影响列表
if (!document.querySelector('#page-nav-style')) {
    const style = document.createElement('style');
    style.id = 'page-nav-style';
    style.textContent = `
        /* ========== 核心：xinxi和tongji一行展示（不改变DOM结构） ========== */
        /* 父容器样式（需确保xinxi/tongji的父容器是这个类，或直接用父容器ID） */
        /* 如果你的xinxi/tongji父容器有ID（如page-box），替换为 #page-box */
        .page-nav-parent { 
            font-size: 14px;
            color: #333;
            line-height: 32px;
            font-family: "Microsoft Yahei", sans-serif;
            display: flex;
            justify-content: flex-end; /* 整体右对齐 */
            align-items: center; /* 垂直居中 */
            gap: 20px; /* 统计区和分页区间距 */
        }
        /* 兼容无父容器的情况：直接让xinxi/tongji行内展示 */
        .page-nav-stat, .page-nav-container {
            display: inline-block; /* 行内块级，实现一行展示 */
            vertical-align: middle; /* 垂直居中 */
            margin: 0 5px; /* 间距 */
        }
        /* ========== 分页核心样式（固定宽度页码） ========== */
        .page-nav-container .page-nav-ul { 
            list-style: none; 
            padding: 0; 
            margin: 0; 
            display: inline-flex; 
            align-items: center; 
            gap: 4px; 
        }
        /* 所有页码LI固定宽度（核心） */
        .page-nav-container .page-nav-ul .page-nav-item { 
            width: 39px; /* 固定宽度（可调整） */
            height: 32px; /* 固定高度 */
            line-height: 32px; /* 文字垂直居中 */
            padding: 0 !important; /* 清空padding，避免宽度变化 */
            border: 1px solid #ddd; 
            cursor: pointer; 
            border-radius: 4px; 
            user-select: none; 
            font-size: 14px;
            margin: 0;
            text-align: center; /* 文字水平居中 */
            overflow: hidden; /* 防止多位数溢出 */
            text-overflow: ellipsis; /* 溢出省略 */
        }
        /* 选中页码样式 */
        .page-nav-container .page-nav-ul .page-active { 
            background: #6366f1; 
            color: #fff; 
            border-color: #6366f1; 
        }
        /* 普通页码hover */
        .page-nav-container .page-nav-ul .page-list:hover { 
            background: #f5f5f5; 
        }
        /* 首页/末页（固定宽度兼容） */
        .page-nav-container .page-nav-ul .page-nav-item.fpage, 
        .page-nav-container .page-nav-ul .page-nav-item.epage { 
            background: #f8f8f8;
        }
        /* 页码输入框样式 */
        .page-nav-container .page-nav-input { 
            width: 50px;
            height: 32px;
            line-height: 32px;
            border: 1px solid #ddd; 
            border-radius: 4px; 
            outline: none;
            text-align: center;
            font-size: 14px;
            padding: 0;
            box-sizing: border-box;
            margin: 0 4px;
        }
        /* 输入框聚焦样式 */
        .page-nav-container .page-nav-input:focus {
            border-color: #6366f1;
            box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
        }
    `;
    document.head.appendChild(style);
}

// ========== 关键：给xinxi/tongji的父容器添加样式类（必做） ==========
// 页面加载后，给xinxi和tongji的共同父容器添加.page-nav-parent类
document.addEventListener('DOMContentLoaded', function() {
    // 找到xinxi和tongji的共同父容器（替换为你实际的父容器选择器，如#page-footer）
    const xinxiEl = document.getElementById('xinxi');
    const tongjiEl = document.getElementById('tongji');
    if (xinxiEl && tongjiEl) {
        const parentEl = xinxiEl.parentNode === tongjiEl.parentNode 
            ? xinxiEl.parentNode 
            : null;
        if (parentEl) {
            parentEl.classList.add('page-nav-parent'); // 添加一行展示的样式类
        }
    }

});

// 查询按钮事件
var chaxun = document.getElementById('chaxun');
if (chaxun) {
    chaxun.addEventListener('click',function() {
        this.disabled = true;
        this.querySelector('span').textContent = '查询中...';
        page = 1;
        num = 10;
        Load(); // 加载列表数据
        LoadFenYe(); // 刷新分页
        setTimeout(() => {
            this.disabled = false;
            this.querySelector('span').textContent = '查询';
        }, 1500);
    });
}
//点击回车键查询
// 监听全局键盘按下事件（等价于 $(document).keypress()）
document.addEventListener('keypress', function(e) {
    // 获取按键编码（兼容不同浏览器）
    var eCode = e.keyCode ? e.keyCode : (e.which ? e.which : e.charCode);
    console.log(eCode);

    if (eCode === 13) { // 回车按键
        // 原生 JS 获取输入框/选择框值（替换 jQuery 的 $('#xxx').val()）
        var env = document.getElementById('env').value;
        var vers = document.getElementById('vers').value;
        var compid = document.getElementById('compid').value;
        var compname = document.getElementById('compname').value;
        var uname = document.getElementById('unmae').value; // 需确保 selectElement 已定义
        console.log("uname:", uname);
        var minfo = document.getElementById('message').value;
        var spage = document.getElementById('spn').value;
        console.log('页码数: ',spage)

        if (env || vers || compid || compname || uname || minfo) {
            console.log(`env: ${env}, vers: ${vers}, compid: ${compid}, compname: ${compname}, uname: ${uname}, minfo: ${minfo} `)
            page = 1;
            num = 10;
            Load(); // 假设 Load() 已定义
        } else if (spage) {
            console.log('页码数不为空，',spage)
            if (spage > zys) { // 需确保 zys 已定义
                spage = zys;
            } else if (spage < 1) {
                spage = 1;
            }
            page = spage;
            num = 10;
            Load();
        }
    }
});
//重置查询条件
var reset = document.getElementById('reset');
reset.addEventListener('click',function() {
    this.disabled = true;
    this.querySelector('span').textContent = '重置中...';
    document.getElementById('env').value = '';
    document.getElementById('vers').value = '';
    document.getElementById('compid').value = '';
    document.getElementById('compname').value = '';
    selectElement.value = "";
    document.getElementById('message').value = '';
    page = 1;
    num = 10;
    //重新加载数据
    Load();
    //重新加载分页信息
    // LoadFenYe();
    setTimeout(() => {
        this.disabled = false;
        this.querySelector('span').textContent = '重置';
    }, 800);
})
