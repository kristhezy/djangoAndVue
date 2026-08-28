    var color1 = "green"
    var color2 = "white"
    // 设置 AJAX 请求头

    function getEmailSuffix() {
        return document.getElementById('emailSuffix').value || '@jt.com';
    }

    // 解析用户名中的数字后缀，返回 { base, num, len }
    function parseUnameBase(rawUname) {
        var match = rawUname.match(/^(.*?)(\d+)$/);
        if (match) {
            return { base: match[1], num: parseInt(match[2]), len: match[2].length };
        }
        return { base: rawUname, num: 0, len: 0 };
    }

    // 卡片折叠/展开功能
    document.addEventListener('DOMContentLoaded', function() {
        const cardHeaders = document.querySelectorAll('.card-header');
        cardHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const card = this.parentElement;
                card.classList.toggle('collapsed');
            });
        });

        // 设置卡片5的默认时间（按月固定周期：1-7号第1周，8-14号第2周，15-21号第3周，22号-月底第4周）
        function setDefaultTimes() {
            const now = new Date();
            const year = now.getFullYear();
            const month = now.getMonth();
            const day = now.getDate();

            // 判断当前日期在哪个周期
            let startDay, endDay;
            if (day <= 7) {
                startDay = 1;
                endDay = 7;
            } else if (day <= 14) {
                startDay = 8;
                endDay = 14;
            } else if (day <= 21) {
                startDay = 15;
                endDay = 21;
            } else {
                startDay = 22;
                // 月底 = 当月最后一天
                endDay = new Date(year, month + 1, 0).getDate();
            }

            const startDate = new Date(year, month, startDay);
            const endDate = new Date(year, month, endDay);

            const formatDate = (date) => {
                const y = date.getFullYear();
                const m = String(date.getMonth() + 1).padStart(2, '0');
                const d = String(date.getDate()).padStart(2, '0');
                return `${y}-${m}-${d}`;
            };

            document.getElementById('startTime').value = formatDate(startDate);
            document.getElementById('endTime').value = formatDate(endDate);
        }

        setDefaultTimes();

        // 日期范围选择器初始化
        initDateRangePicker();

        // 处理算力值选择变化
        const computingType = document.getElementById('computingType');
        const customGroup = document.getElementById('customPowerGroup');

        computingType.addEventListener('change', function() {
            if (this.value === '0') {
                customGroup.style.display = '';
            } else {
                customGroup.style.display = 'none';
            }
        });

        // 初始状态：隐藏自定义输入框
        customGroup.style.display = 'none';

        // 算力充值/扣减模式切换
        const powerOpRadios = document.querySelectorAll('input[name="powerOp"]');
        const powerRechargeGroup = document.getElementById('powerRechargeGroup');
        const powerDeductGroup = document.getElementById('powerDeductGroup');
        powerOpRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'recharge') {
                    powerRechargeGroup.style.display = '';
                    powerDeductGroup.style.display = 'none';
                    document.getElementById('pctl').classList.add('active');
                    document.getElementById('pdtl').classList.remove('active');
                } else {
                    powerRechargeGroup.style.display = 'none';
                    powerDeductGroup.style.display = '';
                    document.getElementById('pdtl').classList.add('active');
                    document.getElementById('pctl').classList.remove('active');
                }
            });
        });

        // 奖励类型43切换时显示/隐藏重跑模式
        const rerunModeGroup = document.getElementById('rerunModeGroup');
        const rewardType43Cb = document.getElementById('rewardType43');
        rewardType43Cb.addEventListener('change', function() {
            if (this.checked) {
                rerunModeGroup.style.display = '';
            } else {
                rerunModeGroup.style.display = 'none';
            }
        });

        // 奖励类型全选/取消全选
        const rewardTypeAllCb = document.getElementById('rewardTypeAll');
        rewardTypeAllCb.addEventListener('change', function() {
            document.querySelectorAll('input[name="rewardType"]').forEach(function(cb) {
                cb.checked = rewardTypeAllCb.checked;
            });
            if (rewardTypeAllCb.checked) {
                rerunModeGroup.style.display = '';
            } else {
                rerunModeGroup.style.display = 'none';
            }
        });
        // 单个checkbox变化时同步全选状态
        document.querySelectorAll('input[name="rewardType"]').forEach(function(cb) {
            cb.addEventListener('change', function() {
                var all = document.querySelectorAll('input[name="rewardType"]');
                var allChecked = Array.from(all).every(function(c) { return c.checked; });
                document.getElementById('rewardTypeAll').checked = allChecked;
            });
        });

        // 初始执行一次（设置默认状态）
        handleRadioChange();
        // 给内容区单选框绑定change事件
        const radioList = document.querySelectorAll('.right.part input[type="radio"]');
        radioList.forEach(radio => {
            radio.addEventListener('change', handleRadioChange);
        });
        // 给 env/env3/env4 单选框绑定切换监听，切换时重新获取国家列表
        ['env', 'env3', 'env4'].forEach(envName => {
            const radios = document.querySelectorAll(`input[type="radio"][name="${envName}"]`);
            radios.forEach(radio => {
                radio.addEventListener('change', () => {
                    if (envName === 'env') {
                        getCountryList('env', 'country', '3630979328926013');
                    } else if (envName === 'env3') {
                        getCountryList('env3', 'country3', '3630979328926013');
                    } else if (envName === 'env4') {
                        getCountryList('env4', 'country4', null, true);
                    }
                });
            });
        });
        // 给 env6 单选框绑定切换监听，切换时重新获取算力列表
        const env6Radios = document.querySelectorAll('input[type="radio"][name="env6"]');
        env6Radios.forEach(radio => {
            radio.addEventListener('change', () => {
                getComputingList();
            });
        });

        // 懒加载：用户首次点击下拉框时才获取数据
        function lazyLoadOnce(selectId, loadFn) {
            var loaded = false;
            var el = document.getElementById(selectId);
            if (!el) return;
            el.addEventListener('focus', function handler() {
                if (!loaded) {
                    loaded = true;
                    el.removeEventListener('focus', handler);
                    loadFn();
                }
            });
        }
        lazyLoadOnce('computingType', function() { getComputingList(); });

        // 国家列表首次加载：任意下拉框首次聚焦时，共用一次API请求填充3个下拉框
        var _countryPromise = null;  // 暴露到外层供 queryUser 使用
        (function() {
            var sharedLoaded = false;
            var ids = ['country', 'country3', 'country4'];
            function loadOnce() {
                if (sharedLoaded) return;
                sharedLoaded = true;
                ids.forEach(function(id) {
                    var el = document.getElementById(id);
                    if (el) el.removeEventListener('focus', loadOnce);
                });
                var env = document.querySelector("input[name='env']:checked").value;
                var data = JSON.stringify({
                    uname: "", env: env, version: 7,
                    emailSuffix: getEmailSuffix(), type: "queryCountryInfo"
                });
                _countryPromise = axios.post('/ov/pmmeett/queryCountryInfo', data, {headers: header})
                .then(function(response) {
                    var res = response.data.data;
                    var resStr = JSON.stringify(res);
                    ['env', 'env3', 'env4'].forEach(function(envName) {
                        if (initialCountryData[envName] === undefined) {
                            initialCountryData[envName] = resStr;
                        }
                    });
                    fillCountrySelect('country', res, '3630979328926013', false);
                    fillCountrySelect('country3', res, '3630979328926013', false);
                    fillCountrySelect('country4', res, null, true);
                    console.log('sharedCountryLoad succ: ' + resStr);
                    return res;
                })
                .catch(function(err) {
                    console.log('sharedCountryLoad err: ' + err);
                    _countryPromise = null;
                    throw err;
                });
            }
            ids.forEach(function(id) {
                var el = document.getElementById(id);
                if (el) el.addEventListener('focus', loadOnce);
            });
            // 暴露手动触发方法，供 queryUser 等场景提前加载
            window._loadCountries = function() {
                if (_countryPromise) return _countryPromise;
                loadOnce();
                return _countryPromise;
            };
        })();
    })

    // 存储首次加载的数据，用于后续切换时对比
    let initialCountryData = {};  // key: envName, value: JSON string of data
    let initialComputingData = null;

    // 获取国家列表并填充到指定 select
    function getCountryList(envName, selectId, defaultValue, hasEmptyOption = false) {
        const uname = "";
        const env = document.querySelector(`input[name='${envName}']:checked`).value;
        const version = 7;
        const data = JSON.stringify({uname,env, version, "emailSuffix":getEmailSuffix(),"type": "queryCountryInfo"});
        axios.post(`/ov/pmmeett/queryCountryInfo`, data, {headers: header})
        .then(response => {
            const res = response.data.data;
            const resStr = JSON.stringify(res);
            // 首次加载，保存初始数据
            if (initialCountryData[envName] === undefined) {
                initialCountryData[envName] = resStr;
                fillCountrySelect(selectId, res, defaultValue, hasEmptyOption);
            } else if (initialCountryData[envName] !== resStr) {
                // 与首次数据不同，才更新
                fillCountrySelect(selectId, res, defaultValue, hasEmptyOption);
            } else {
                console.log(`getCountryList(${envName}) 数据与首次一致，跳过更新`);
            }
            console.log(`getCountryList(${envName}) succ: ${JSON.stringify(res)}`);
        })
        .catch(err => {
            console.log(`getCountryList(${envName}) err: ${err}`);
        });
    }

    // 填充国家下拉框
    function fillCountrySelect(selectId, countries, defaultValue, hasEmptyOption = false) {
        const select = document.getElementById(selectId);
        select.innerHTML = '';
        if (hasEmptyOption) {
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = ' --请选择-- ';
            select.appendChild(emptyOption);
        }
        countries.forEach(item => {
            const option = document.createElement('option');
            option.value = item.value;
            option.textContent = ` ${item.name} `;
            if (defaultValue && item.value == defaultValue) {
                option.selected = true;
            }
            select.appendChild(option);
        });
    }

    // 获取算力选项
    let ccntlist = "";
    let computingNames = "";
    function getComputingList() {
        const uname = "";
        const env = document.querySelector("input[name='env6']:checked").value;
        const version = 7;
        const data = JSON.stringify({
            uname,env,version,"emailSuffix":getEmailSuffix(),"type": "queryComputingList"})
        axios.post(`/ov/pmmeett/queryComputingList`,data,{headers: header})
        .then(response => {
            const res = response.data.data;
            ccntlist = res.clist;
            computingNames = res.computingNames;
            const resStr = JSON.stringify(res);
            // 首次加载，保存初始数据
            if (initialComputingData === null) {
                initialComputingData = resStr;
                if (ccntlist && Array.isArray(ccntlist)) {
                    fillPowerOptions(ccntlist);
                }
            } else if (initialComputingData !== resStr) {
                // 与首次数据不同，才更新
                if (ccntlist && Array.isArray(ccntlist)) {
                    fillPowerOptions(ccntlist);
                }
            } else {
                console.log(`getComputingList 数据与首次一致，跳过更新`);
            }
            console.log(`getComputingList succ: ${JSON.stringify(ccntlist)}`);
        })
        .catch(err => {
            console.log(`getComputingList err: ${err}`);
        });
    }

    // 填充算力下拉框
    function fillPowerOptions(options) {
        const select = document.getElementById('computingType');
        select.innerHTML = '<option value="">--请选择--</option>';

        options.forEach(item => {
            const option = document.createElement('option');
            option.value = item.value || item.id;
            option.textContent = item.name || item.label;
            select.appendChild(option);
        });
    }

    function handleRadioChange(){
        const iptradio = document.querySelectorAll('input[type="radio"][name="mset"]:checked');
        iptradio.forEach(radio => {
            const radioId = radio.id;
            console.log("radioId:",radioId)
            switch(radioId){
                case 'ms1':
                    document.getElementById("rcodetr").style.display = "";
                    // document.getElementById("unumtr").style.display = "";
                    document.getElementById("countr").style.display = "";
                    break;
                case 'ms2':
                    document.getElementById("rcodetr").style.display = "none";
                    // document.getElementById("unumtr").style.display = "none";
                    document.getElementById("countr").style.display = "none";
                    break;
            }
        })
        const envradio = document.querySelectorAll('input[type="radio"][name="env"]:checked');
        envradio.forEach(radio => {
            const radioId = radio.id;
            console.log("radioId:",radioId)
            switch(radioId){
                case 'p1':
                    document.getElementById("bemtr").style.display = "none";
                    document.getElementById("spptr").style.display = "none";
                    document.getElementById("ms1").checked = true;
                    document.getElementById("beapp").style.display = "none";
                    document.getElementById("rcodetr").style.display = "";
                    document.getElementById("unumtr").style.display = "";
                    document.getElementById("countr").style.display = "";
                    break;
                case 't1':
                    document.getElementById("bemtr").style.display = "";
                    document.getElementById("spptr").style.display = "";
                    document.getElementById("beapp").style.display = "";
                    break;
            }
        })
    }

    //mmeett注册用户
    var wxaiSubmit = document.getElementById('wxaiSubmit');
    wxaiSubmit.addEventListener('click', async function(){
        var wxain = "mmeett注册用户";
        const mset = document.querySelector("input[name='mset']:checked").value;
        var uname = document.getElementById('uname').value;
        var rcode = document.getElementById('rcode').value;
        var pwd = document.getElementById("pwd").value || "qq123456";
        var repwd = pwd;
        var country = document.getElementById("country").value;
        var bemail = document.getElementById("bindemail").value;
        var paypwd = document.getElementById("paypwd").value;
        const unum = parseInt(document.getElementById('unum').value);
        var env = document.querySelector("input[name='env']:checked").value;
        var version = 7;

        if (mset == 'regist' && (uname.length == 0 || rcode.length == 0)){
            alert('必填项不能为空！');
            return;
        }
        if (mset == 'regist' && unum < 1){
            alert("'账号数量'必须是正整数! ");
            return;
        }

        var wxaiResult = document.getElementById('wxaiResult');
        wxaiResult.innerHTML = '';
        this.disabled = true;
        this.textContent = '提交中...';

        var baseInfo = parseUnameBase(uname);

        for (var i = 1; i <= unum; i++) {
            var currentUname = baseInfo.len > 0
                ? baseInfo.base + String(baseInfo.num + i - 1).padStart(baseInfo.len, '0')
                : uname;

            wxaiResult.insertAdjacentHTML('afterbegin', `<div id="reg-${i}" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> 第${i}条 [${escapeHTML(String(currentUname))}] 请求中...</div>`);

            var data = JSON.stringify({
                mset,uname:currentUname,rcode,pwd,repwd,country,bemail,paypwd,unum:1,env,version,"emailSuffix":getEmailSuffix(),"type": "mmeettRegist"
            });
            try {
                response = await axios.post(`/ov/pmmeett/mmeettRegist`, data, {headers: header});
                var rescode = response.data.code;
                if (rescode >= 500) {
                    document.getElementById(`reg-${i}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${i}条 [${escapeHTML(String(currentUname))}] 服务端异常 (code=${rescode}), 已停止后续请求</div>`;
                    console.log(`${wxain} 第${i}条 [${escapeHTML(String(currentUname))}] 服务端异常: ${rescode}`);
                    break;
                }
                var res = response.data.data;
                document.getElementById(`reg-${i}`).innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;"> ${res}</div>`;
                console.log(`${wxain} 第${i}条 [${escapeHTML(String(currentUname))}] succ: ${res}`);
            } catch(err) {
                document.getElementById(`reg-${i}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${i}条 [${escapeHTML(String(currentUname))}] 失败: ${err.message || err}</div>`;
                console.log(`${wxain} 第${i}条 [${escapeHTML(String(currentUname))}] err: ${err}`);
                break;
            }
        }

        this.disabled = false;
        this.textContent = '提交';
    })

    let rcinfo = "";
    function getRechargeConfig(){
        let grcn = "获取会员配置信息";
        let version = 7;
        document.getElementById("level2").value='';
        let env = document.querySelector("input[name='env2']:checked").value;
        let uname = document.getElementById("uname2").value;
        const unum = document.getElementById('unum2').value;
        let data = JSON.stringify({
            uname,env,version,"emailSuffix":getEmailSuffix(),"type": "getRechargeConfig"
        });
        if (!uname) {
            document.getElementById('level2').innerHTML = '<option value="">-- 请选择 --</option>';
            return;
        }
        axios.post(`/ov/pmmeett/getRechargeConfig`,data,{headers: header})
        .then(response => {
            let res = response.data;
            console.log(`getRechargeConfig: ${res.data}`)
            rcinfo = res.data;
            if (res.code == 0 && rcinfo.length !== 0){
                let rcid = [30,1,3,35,39,43,47,5,45,41,33,7,9,37];
                let matchedData = rcid
                    .map(id => rcinfo.find(item => item.id === id))
                    .filter(item => item !== undefined);
                const selectElement = document.getElementById('level2');
                const prevValue = selectElement.value;
                selectElement.innerHTML = '';
                matchedData.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.id;
                    option.textContent = item.name;
                    selectElement.appendChild(option);
                });
                if (prevValue && selectElement.querySelector(`option[value="${prevValue}"]`)) {
                    selectElement.value = prevValue;
                }
                console.log("已加载的选项数量:", matchedData.length);
                console.log("数据详情:", matchedData);
                console.log(`${grcn} succ: ${res.data}`);
            }
            else if(res.code != 0){
                rlt = res.msg
                if (res.code == -15){
                    rlt += "【本系统仅支持默认密码为 'qq123456' 的用户操作!】"
                }
                alert(rlt);
                return;
            }
            else{
                alert('用户已是钻石会员，请先降级再购买！');
                if (env == "test"){
                    // 自动带入到会员降级模块
                    document.getElementById('unameSV').value = uname;
                    document.querySelector(`input[name="envSV"][value="${env}"]`).checked = true;
                    const demotionCard = document.getElementById('demotionCard');
                    demotionCard.classList.remove('collapsed');
                    document.getElementById('svResult').innerHTML = "";
                }
                return;
            }
        })
        .catch(err => {
            console.log(`${grcn} err: ${err}`)
        })
    }
    const svClear = document.getElementById("svClear");
    svClear.addEventListener('click',function(){
        document.getElementById('unameSV').value = '';
        document.getElementById('svResult').innerHTML = '';
    })
    const sureSV = document.getElementById("sureSV");
    sureSV.addEventListener('click',function(){
        const svn = "会员降级"
        const uname = document.getElementById('unameSV').value;
        const level = document.getElementById('level2t').value;
        const env = document.querySelector("input[name='envSV']:checked").value;
        const version = 7;
        const data = JSON.stringify({
            uname,level,env,version,"emailSuffix":getEmailSuffix(),"type": "demotionVip"
        })
        if (!uname || !level){
            alert("用户账号和等级不能为空！");
            return;
        }
        const svResult = document.getElementById('svResult');
        svResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
        axios.post(`/ov/pmmeett/demotionVip`,data,{headers: header})
        .then(response => {
            var res = response.data.data;
            console.log(`${svn} succ: ${res}`);
            svResult.innerHTML = res;
            setTimeout(function(){
                document.getElementById('svResult').innerHTML = "";
            },3000)
        })
        .catch(err => {
            console.log(`${svn} err: ${err}`)
        })
        .finally(() => {
            this.disabled = false;
            this.textContent = '确定';
        })
    })
    const abvSubmit = document.getElementById("abvSubmit");
    abvSubmit.addEventListener('click', async function(){
        const abvn = "mmeett购买会员";
        var uname = document.getElementById('uname2').value;
        const level = document.getElementById('level2').value;
        const unum = parseInt(document.getElementById('unum2').value);
        const env = document.querySelector("input[name='env2']:checked").value;
        const version = 7;

        if (uname.length == 0){
            alert('用户账号不能为空！');
            return;
        }
        if (!level){
            alert('请选择会员类型！');
            return;
        }
        if (unum < 1){
            alert("'账号数量'必须是正整数! ");
            return;
        }

        var abvResult = document.getElementById('abvResult');
        abvResult.innerHTML = '';
        this.disabled = true;
        this.textContent = '提交中...';

        var baseInfo = parseUnameBase(uname);

        for (var i = 1; i <= unum; i++) {
            var currentUname = baseInfo.len > 0
                ? baseInfo.base + String(baseInfo.num + i - 1).padStart(baseInfo.len, '0')
                : uname;

            abvResult.insertAdjacentHTML('afterbegin', `<div id="abv-${i}" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> 第${i}条 [${escapeHTML(String(currentUname))}] 请求中...</div>`);

            var data = JSON.stringify({
                rcinfo,uname:currentUname,level,unum:1,env,version,"emailSuffix":getEmailSuffix(),"type": "buyVip"});
            try {
                var response = await axios.post(`/ov/pmmeett/buyVip`, data, {headers: header});
                var res = response.data.data;
                document.getElementById(`abv-${i}`).innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res}</div>`;
                console.log(`${abvn} 第${i}条 [${escapeHTML(String(currentUname))}] succ: ${res}`);
            } catch(err) {
                document.getElementById(`abv-${i}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${i}条 [${escapeHTML(String(currentUname))}] 失败: ${err.message || err}</div>`;
                console.log(`${abvn} 第${i}条 [${escapeHTML(String(currentUname))}] err: ${err}`);
            }
        }

        this.disabled = false;
        this.textContent = '提交';
    })

    function queryRCode(param,un,env,btn){
        const qrcn = "mmeett查询邀请码";
        const uname = document.getElementById(un).value;
        var envVal = document.querySelector(`input[name=${env}]:checked`).value;
        var version = 7;
        const data = JSON.stringify({uname,env:envVal,version,"emailSuffix":getEmailSuffix(),"type":"queryRCode"})
        if(btn){
            btn.disabled = true;
            btn.style.opacity = '0.6';
            btn.dataset.originalText = btn.textContent;
            btn.textContent = '查询中...';
        }
        axios.post(`/ov/pmmeett/queryRCode`,data,{headers: header})
        .then(response => {
            var res = response.data.data;
            if (param === "rcode"){
                let rcode = document.getElementById('referralCode3');
                rcode.value = res.rcode;
            // }
            // if (param === "country"){
                let ctid = "";
                let country = document.getElementById('country3');
                if (res.country === "TW"){
                    ctid = "3630979328926013"}
                if (res.country === "JP"){
                    ctid = "3630979328926009"}
                if (res.country === "ID"){
                    ctid = "3630979328925988"}
                if (res.country === "TH"){
                    ctid = "3630979328926003"}
                if (res.country === "SG"){
                    ctid = "3630979328925990"}
                if (res.country === "MY"){
                    ctid = "3630979328925992"}

                country.value = ctid;
            }
            console.log(`${qrcn} succ: ${JSON.stringify(res)}`);
        })
        .catch(err => {
            console.log(`${qrcn} err: ${err}`)
        })
        .finally(() => {
            if(btn){
                btn.disabled = false;
                btn.style.opacity = '1';
                btn.textContent = btn.dataset.originalText || '查询中...';
            }
        })
    }

    // 统一查询方法，通过type区分
    function queryUser(unameId, type) {
        var uname = document.getElementById(unameId).value;
        if (!uname) { alert('请输入用户账号！'); return; }
        var env = document.querySelector("input[name='env4']:checked").value;
        var version = 7;

        var resultEl = document.getElementById(unameId + 'Result');
        if (!resultEl) return;
        resultEl.style.display = 'block';
        resultEl.innerHTML = '<span style="color:#999;">查询中...</span>';

        var actionType = '';
        if (type === 'userName') actionType = 'queryUserName';
        else if (type === 'userEmail') actionType = 'queryUserEmail';
        else if (type === 'country') actionType = 'queryRCode';

        axios.post('/ov/pmmeett/' + actionType, JSON.stringify({
            uname, env, version, emailSuffix: getEmailSuffix()
        }), {headers: header})
        .then(function(response) {
            var res = response.data.data;
            if (type === 'userName' && res && res.userName) {
                document.getElementById('userName4').value = res.userName;
                resultEl.innerHTML = '<span style="color:green;">用户名：' + escapeHTML(res.userName) + '</span>';
            } else if (type === 'userEmail' && res && res.email) {
                document.getElementById('userEmail4').value = res.email;
                resultEl.innerHTML = '<span style="color:green;">邮箱：' + escapeHTML(res.email) + '</span>';
            } else if (type === 'country' && res && res.country) {
                var countryMap = {'TW':'3630979328926013','JP':'3630979328926009','ID':'3630979328925988','TH':'3630979328926003','SG':'3630979328925990','MY':'3630979328925992'};
                var targetValue = countryMap[res.country] || '';
                // 确保国家下拉框已加载选项（否则直接赋值无效）
                var ensureLoad = window._loadCountries ? window._loadCountries() : Promise.resolve();
                ensureLoad.then(function() {
                    document.getElementById('country4').value = targetValue;
                }).catch(function() {
                    document.getElementById('country4').value = targetValue;
                });
                resultEl.innerHTML = '<span style="color:green;">注册国家/地区：' + res.country + '</span>';
            } else {
                resultEl.innerHTML = '<span style="color:red;">查询失败：' + (response.data.msg || '未知错误') + '</span>';
            }
        })
        .catch(function(err) {
            resultEl.innerHTML = '<span style="color:red;">请求失败：' + (err.message || err) + '</span>';
        });
    }

    const refSubmit = document.getElementById("refSubmit");
    refSubmit.addEventListener('click', async function(){
        const refn = "mmeett生成邀请链路";
        const rcode = document.getElementById('referralCode3').value;
        var uname = document.getElementById('uname3').value;
        const country = document.getElementById('country3').value;
        const level = document.getElementById('level3').value;
        const unum = parseInt(document.getElementById('unum3').value);
        var env = document.querySelector("input[name='env3']:checked").value;
        var version = 7;

        if (uname.length == 0){
            alert('用户账号不能为空！');
            return;
        }
        if (!level){
            alert('请选择会员类型！');
            return;
        }
        if (unum < 1){
            alert("'账号数量'必须是正整数! ");
            return;
        }

        var refResult = document.getElementById('refResult');
        refResult.innerHTML = '';
        this.disabled = true;
        this.textContent = '提交中...';

        var baseInfo = parseUnameBase(uname);

        for (var i = 1; i <= unum; i++) {
            var currentUname = baseInfo.len > 0
                ? baseInfo.base + String(baseInfo.num + i - 1).padStart(baseInfo.len, '0')
                : uname;

            refResult.insertAdjacentHTML('afterbegin', `<div id="ref-${i}" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> 第${i}条 [${escapeHTML(String(currentUname))}] 请求中...</div>`);

            var data = JSON.stringify({
                uname:currentUname,rcode,country,level,unum:1,env,version,"emailSuffix":getEmailSuffix(),"type": "mmeettAddReferralLinks"});
            try {
                var response = await axios.post(`/ov/pmmeett/mmeettAddReferralLinks`, data, {headers: header});
                var res = response.data.data;
                document.getElementById(`ref-${i}`).innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res}</div>`;
                console.log(`${refn} 第${i}条 [${escapeHTML(String(currentUname))}] succ: ${res}`);
            } catch(err) {
                document.getElementById(`ref-${i}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${i}条 [${escapeHTML(String(currentUname))}] 失败: ${err.message || err}</div>`;
                console.log(`${refn} 第${i}条 [${escapeHTML(String(currentUname))}] err: ${err}`);
            }
        }

        this.disabled = false;
        this.textContent = '提交';
    })

    const cfgSubmit = document.getElementById("cfgSubmit");
    cfgSubmit.addEventListener('click',function(){
        const cfgn = "mmeett修改用户信息";
        const uname = document.getElementById('uname4').value;
        const userName = document.getElementById('userName4').value;
        const userEmail = document.getElementById('userEmail4').value;
        const country = document.getElementById('country4').value;
        const env = document.querySelector("input[name='env4']:checked").value;
        const version = 7;
        const data = JSON.stringify({
            uname,userName,userEmail,country,env,version,"emailSuffix":getEmailSuffix(),"type": "updateUserInfo"
        })
        if (uname.length == 0){
            alert('用户账号不能为空！');
            return;
        }
        let cfgResult = document.getElementById('cfgResult');
        cfgResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
        this.disabled = true;
        this.textContent = '提交中...';
        axios.post(`/ov/pmmeett/updateUserInfo`,data,{headers: header})
        .then(response => {
            const res = response.data.data;
            cfgResult.innerHTML = res;
            console.log(`${cfgn} succ: ${res}`);
        })
        .catch(err => {
            console.log(`${cfgn} err: ${err}`)
        })
        .finally(() => {
            this.disabled = false;
            this.textContent = '提交';
        })
    })

    // 分成奖励重跑
    const rewardSubmit = document.getElementById("rewardSubmit");
    rewardSubmit.addEventListener('click', async function(){
        const rewardn = "分成奖励重跑";
        const startTime = document.getElementById('startTime').value;
        const endTime = document.getElementById('endTime').value;
        const env = document.querySelector("input[name='env5']:checked").value;

        // 获取选中奖励类型
        const rewardTypeCheckboxes = document.querySelectorAll('input[name="rewardType"]:checked');
        const selectedRewardTypes = Array.from(rewardTypeCheckboxes).map(cb => cb.value);

        // 获取rerun复选框值
        const checkboxes = document.querySelectorAll('.checkbox-group input[name="rerun"]:checked');
        const types = Array.from(checkboxes).map(cb => cb.value);

        // 重跑模式（仅奖励类型43时）
        var rerunMode = [];
        var has43 = selectedRewardTypes.indexOf('43') !== -1;
        if (has43) {
            const modeCheckboxes = document.querySelectorAll('input[name="rerunMode"]:checked');
            rerunMode = Array.from(modeCheckboxes).map(cb => cb.value);
        }
        var rewardTypeNames = {
            '27':'感恩分红奖','28':'推荐奖','29':'分享奖','30':'安置奖',
            '31':'层碰奖','32':'级差奖','33':'级差对等奖','35':'全球分红','43':'集团奖励分红'
        };

        if (selectedRewardTypes.length === 0){
            alert('请选择奖励类型！');
            return;
        }
        if (!startTime || !endTime){
            alert('请选择开始和结束时间！');
            return;
        }

        const version = 7;
        const uname = "";
        const rewardResult = document.getElementById('rewardResult');
        rewardResult.innerHTML = '';
        this.disabled = true;
        this.textContent = '提交中...';

        for (var i = 0; i < selectedRewardTypes.length; i++) {
            var rt = selectedRewardTypes[i];
            var rtName = rewardTypeNames[rt] || rt;
            var idx = i + 1;
            rewardResult.insertAdjacentHTML('afterbegin', `<div id="reward-${idx}" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> 第${idx}条 [${rtName}] 请求中...</div>`);

            var sendTypes = rt === '43' ? ['summary'] : types;
            var data = JSON.stringify({
                uname,rewardType:rt,startTime,endTime,env,types:sendTypes,rerunMode:has43?rerunMode:[],version,"emailSuffix":getEmailSuffix(),"type": "runReward"});
            try {
                var response = await axios.post(`/ov/pmmeett/runReward`, data, {headers: header});
                var res = response.data.data;
                document.getElementById(`reward-${idx}`).innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res}</div>`;
                console.log(`${rewardn} 第${idx}条 [${rtName}] succ: ${res}`);
            } catch(err) {
                document.getElementById(`reward-${idx}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${idx}条 [${rtName}] 失败: ${err.message || err}</div>`;
                console.log(`${rewardn} 第${idx}条 [${rtName}] err: ${err}`);
            }
        }

        this.disabled = false;
        this.textContent = '提交';
    })

    // 算力充值/扣减 提交
    const powerSubmit = document.getElementById("powerSubmit");
    powerSubmit.addEventListener('click',function(){
        const powerOp = document.querySelector("input[name='powerOp']:checked").value;
        const version = 7;
        const powerResult = document.getElementById('powerResult');

        if (powerOp === 'recharge') {
            // ===== 充值模式（原有逻辑不变） =====
            const powerName = "算力充值";
            const uname = document.getElementById('uname6').value;
            const computingType = document.getElementById('computingType').value;
            const computingNum = document.getElementById('computingNum').value;
            const sendAward = document.getElementById('sendAward').value;
            const env = document.querySelector("input[name='env6']:checked").value;

            if (!uname) { alert('请输入用户账号！'); return; }
            if (!computingType) { alert('请选择充值类型！'); return; }
            if (computingType === '0' && !computingNum) { alert('请输入算力数值！'); return; }

            const data = JSON.stringify({
                computingNames,ccntlist,uname,computingType,computingNum,sendAward,env,version,"emailSuffix":getEmailSuffix(),"type": "sendComputing"
            });
            powerResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
        this.disabled = true;
        this.textContent = '提交中...';
        axios.post(`/ov/pmmeett/sendComputing`,data,{headers: header})
            .then(response => {
                const res = response.data.data;
                powerResult.innerHTML = res;
                console.log(`${powerName} succ: ${res}`);
            })
            .catch(err => {
                console.log(`${powerName} err: ${err}`)
            })
            .finally(() => {
                this.disabled = false;
                this.textContent = '提交';
            });
        } else {
            // ===== 扣减模式 =====
            const powerName = "算力扣减";
            const uname = document.getElementById('uname6d').value;
            const amount = document.getElementById('computingDeductNum').value;
            const env = document.querySelector("input[name='env6d']:checked").value;

            if (!uname) { alert('请输入用户账号！'); return; }
            if (!amount) { alert('请输入算力数值！'); return; }

            const data = JSON.stringify({
                uname,amount,env,version,"emailSuffix":getEmailSuffix(),"type": "computingConsumption"
            });
            powerResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
        this.disabled = true;
        this.textContent = '提交中...';
        axios.post(`/ov/pmmeett/computingConsumption`,data,{headers: header})
            .then(response => {
                const res = response.data.data;
                powerResult.innerHTML = res;
                console.log(`${powerName} succ: ${res}`);
            })
            .catch(err => {
                console.log(`${powerName} err: ${err}`)
            })
            .finally(() => {
                this.disabled = false;
                this.textContent = '提交';
            });
        }
    })

    // 用户安置提交
    const settleSubmit = document.getElementById("settleSubmit");
    settleSubmit.addEventListener('click', async function(){
        const settleName = "用户安置";
        const uname = document.getElementById('uname7').value;
        const settleType = document.querySelector("input[name='settleType']:checked").value;
        const cancelDirs = document.querySelector("input[name='cancelDir']:checked").value;
        const env = document.querySelector("input[name='env7']:checked").value;
        const version = 7;

        if (uname.length == 0){
            alert('用户账号不能为空！');
            return;
        }
        if (settleType === 'cancel' && cancelDirs.length === 0){
            alert('请至少选择一个取消方向！');
            return;
        }

        const settleResult = document.getElementById('settleResult');
        settleResult.innerHTML = '';
        this.disabled = true;
        this.textContent = '提交中...';

        if (settleType === 'cancel') {
            settleResult.innerHTML = `<div id="settle-item" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> [${uname}] 请求中...</div>`;

            var data = JSON.stringify({
                uname,env,version,settleType,cancelDirs,"emailSuffix":getEmailSuffix(),"type": "userCancelSettle"
            });
            try {
                var response = await axios.post(`/ov/pmmeett/userCancelSettle`, data, {headers: header});
                var res = response.data.data;
                document.getElementById('settle-item').innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res}</div>`;
                console.log(`${settleName} 取消安置 succ: ${res}`);
            } catch(err) {
                document.getElementById('settle-item').innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">失败: ${err.message || err}</div>`;
                console.log(`${settleName} 取消安置 err: ${err}`);
            }
        } else {
            var isBatch = document.querySelector("input[name='isBatch7']:checked").value;
            if (isBatch === '1') {
            var baseInfo = parseUnameBase(uname);
            var idx = 0;
            var maxLoop = 1000;
            var notFoundCount = 0;
            while (idx < maxLoop) {
                idx++;
                var currentUname = baseInfo.len > 0
                    ? baseInfo.base + String(baseInfo.num + idx - 1).padStart(baseInfo.len, '0')
                    : uname;

                settleResult.insertAdjacentHTML('afterbegin', `<div id="settle-${idx}" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> 第${idx}条 [${escapeHTML(String(currentUname))}] 请求中...</div>`);

                var data = JSON.stringify({
                    uname:currentUname,isBatch,idx,env,version,"emailSuffix":getEmailSuffix(),"type": "userSettle"
                });
                try {
                    var response = await axios.post(`/ov/pmmeett/userSettle`, data, {headers: header});
                    var res = response.data.data;
                    document.getElementById(`settle-${idx}`).innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res.usrlt}</div>`;
                    console.log(`${settleName} 第${idx}条 [${escapeHTML(String(currentUname))}] succ: ${res.usrlt}`);
                    if (res.usrlt.indexOf('不存在') !== -1) {
                        notFoundCount++;
                        if (notFoundCount >= 3) {
                            settleResult.insertAdjacentHTML('afterbegin', `<div style="color:#999;margin:4px 0;">连续3次用户不存在，已停止</div>`);
                            break;
                        }
                    } else {
                        notFoundCount = 0;
                    }
                    if (res.stop == 1) {
                        settleResult.insertAdjacentHTML('afterbegin', `<div style="color:#999;margin:4px 0;">已停止</div>`);
                        break;
                    }
                } catch(err) {
                    document.getElementById(`settle-${idx}`).innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">第${idx}条 [${escapeHTML(String(currentUname))}] 失败: ${err.message || err}</div>`;
                    console.log(`${settleName} 第${idx}条 [${escapeHTML(String(currentUname))}] err: ${err}`);
                }
            }
        } else {
            settleResult.innerHTML = `<div id="settle-item" style="margin:4px 0;"><img src="../static/img/loading.gif" height="10"/> [${uname}] 请求中...</div>`;

            var data = JSON.stringify({
                uname,isBatch,env,version,"emailSuffix":getEmailSuffix(),"type": "userSettle"
            });
            try {
                var response = await axios.post(`/ov/pmmeett/userSettle`, data, {headers: header});
                var res = response.data.data;
                document.getElementById('settle-item').innerHTML = `<div style="border-bottom:1px solid #e0e0e0;padding:6px 0;">${res.usrlt}</div>`;
                console.log(`${settleName} succ: ${res.usrlt}`);
            } catch(err) {
                document.getElementById('settle-item').innerHTML = `<div style="color:red;border-bottom:1px solid #e0e0e0;padding:6px 0;">失败: ${err.message || err}</div>`;
                console.log(`${settleName} err: ${err}`);
            }
        }
        }

        this.disabled = false;
        this.textContent = '提交';
    })

    // 查看树形结构 - 打开新tab页面
    function getTree(gtype) {
        const uname = document.getElementById('uname7').value;
        if (!uname) {
            alert('请先输入用户账号！');
            return;
        }
        const env = document.querySelector("input[name='env7']:checked").value;
        const emailSuffix = getEmailSuffix();
        const version = 7;
        if (gtype == "issettle"){
            var data = JSON.stringify({
                uname,"emailSuffix":getEmailSuffix(),env,version,"type": gtype
            });
            axios.post(`/ov/pmmeett/issettle`, data, {headers: header})
            .then(function(response){
                var res = response.data.data;
                console.log(`getTree succ: ${res}`);
                document.getElementById('ckrlt').innerHTML = `<div style="color:blue;">${res}</div>`;
            })
            .catch(function(err) {
                console.log('getTree err: ' + err);
            });
        }
        if(gtype == "gettree"){
            treeUrl = '/ov/mmeettTreeView?uname=' + encodeURIComponent(uname) + '&env=' + env + '&version=' + version + '&emailSuffix=' + encodeURIComponent(emailSuffix) + '&_plain=1';
window.open(treeUrl, '_blank');
        }
    }

    // 安置/取消安置 Tab切换
    const settleTypeRadios = document.querySelectorAll('input[name="settleType"]');
    settleTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const cancelDirGroup = document.getElementById('cancelDirectionGroup');
            const isBatchGroup = document.getElementById('isBatchGroup');
            if (this.value === 'cancel') {
                cancelDirGroup.style.display = '';
                isBatchGroup.style.display = 'none';
                document.getElementById('sptl').classList.remove('active');
                document.getElementById('sctl').classList.add('active');
            } else {
                cancelDirGroup.style.display = 'none';
                isBatchGroup.style.display = '';
                document.getElementById('sctl').classList.remove('active');
                document.getElementById('sptl').classList.add('active');
            }
        });
    })

    // ====== 各模块重置功能 ======
    // 模块1: Mmeett注册用户 重置
    document.getElementById('wxaiReset').addEventListener('click', function(){
        document.getElementById('uname').value = '';
        document.getElementById('rcode').value = '';
        document.getElementById('country').value = '3630979328926013';
        document.getElementById('bindemail').value = 'yes';
        document.getElementById('paypwd').value = '123123';
        document.getElementById('unum').value = '1';
        document.querySelector('input[name="mset"][value="regist"]').checked = true;
        handleRadioChange();
    })

    // 模块2: Mmeett修改国家/地区 重置
    document.getElementById('cfgReset').addEventListener('click', function(){
        document.getElementById('uname4').value = '';
        document.getElementById('userName4').value = '';
        document.getElementById('userEmail4').value = '';
        document.getElementById('country4').value = '';
        document.getElementById('uname4Result').style.display = 'none';
        document.getElementById('userName4Result').style.display = 'none';
        document.getElementById('userEmail4Result').style.display = 'none';
    })

    // 模块3: 用户安置 重置
    document.getElementById('settleReset').addEventListener('click', function(){
        document.getElementById('uname7').value = '';
        document.querySelector('input[name="isBatch7"][value="1"]').checked = true;
        document.querySelector('input[name="settleType"][value="place"]').checked = true;
        document.getElementById('cancelDirectionGroup').style.display = 'none';
        document.getElementById('isBatchGroup').style.display = '';
        document.querySelectorAll('input[name="cancelDir"]').forEach(r => r.checked = false);
        document.getElementById('sctl').classList.remove('active');
        document.getElementById('sptl').classList.add('active');
        document.getElementById('ckrlt').innerHTML = '';
    })

    // 模块4: Mmeett余额购买会员 重置
    document.getElementById('abvReset').addEventListener('click', function(){
        document.getElementById('uname2').value = '';
        document.getElementById('unum2').value = '1';
        document.getElementById('level2').innerHTML = '<option value="">-- 请选择 --</option>';
    })

    // 模块5: 会员降级 重置
    document.getElementById('svClear').addEventListener('click', function(){
        document.getElementById('unameSV').value = '';
        document.getElementById('level2t').value = '0';
        document.getElementById('svResult').innerHTML = '';
    })

    // 模块6: 分成奖励重跑 重置
    document.getElementById('rewardReset').addEventListener('click', function(){
        document.querySelectorAll('input[name="rewardType"]').forEach(function(cb){ cb.checked = false; });
        document.getElementById('rewardTypeAll').checked = false;
        var rerunPre = document.querySelector('input[name="rerun"][value="pre"]');
        var rerunDetail = document.querySelector('input[name="rerun"][value="detail"]');
        var rerunSummary = document.querySelector('input[name="rerun"][value="summary"]');
        rerunPre.checked = false; rerunPre.disabled = false;
        rerunDetail.checked = true; rerunDetail.disabled = false;
        rerunSummary.checked = true; rerunSummary.disabled = false;
        document.querySelector('input[name="rerunMode"][value="1"]').checked = true;
        document.querySelector('input[name="rerunMode"][value="2"]').checked = false;
        document.getElementById('rerunModeGroup').style.display = 'none';
        setDefaultTimes();
        if (datePickerState) updateDateRangeDisplay();
    })

    // 模块7: Mmeett生成邀请链路 重置
    document.getElementById('refReset').addEventListener('click', function(){
        document.getElementById('uname3').value = '';
        document.getElementById('referralCode3').value = '';
        document.getElementById('country3').value = '';
        document.getElementById('level3').value = '3';
        document.getElementById('unum3').value = '1';
    })

    // 模块7: 算力充值/扣减 重置
    document.getElementById('powerReset').addEventListener('click', function(){
        // 充值字段
        document.getElementById('uname6').value = '';
        document.getElementById('computingType').value = '';
        document.getElementById('computingNum').value = '';
        document.getElementById('sendAward').value = '0';
        document.getElementById('customPowerGroup').style.display = 'none';
        // 扣减字段
        document.getElementById('uname6d').value = '';
        document.getElementById('computingDeductNum').value = '';
        // 切回充值模式
        document.querySelector("input[name='powerOp'][value='recharge']").checked = true;
        document.getElementById('powerRechargeGroup').style.display = '';
        document.getElementById('powerDeductGroup').style.display = 'none';
        // tab-item active 样式
        document.getElementById('pctl').classList.add('active');
        document.getElementById('pdtl').classList.remove('active');
    })

    // 模块10: 账户充值/扣减 提交
    const accountSubmit = document.getElementById("accountSubmit");
    accountSubmit.addEventListener('click',function(){
        const uname = document.getElementById('uname10').value;
        const state = document.querySelector("input[name='rechargeType']:checked").value;
        const camount = document.getElementById('amount10').value;
        const env = document.querySelector("input[name='env10']:checked").value;
        const version = 7;
        const accountResult = document.getElementById('accountResult');

        if (!uname) {
            alert('请输入用户账号！');
            return;
        }
        if (!camount) {
            alert('请输入金额！');
            return;
        }
        const typeLabel = state === '1' ? '充值' : '扣减';
        const confirmMsg = `确认对用户「${uname}」进行「${typeLabel}」操作，金额：${camount}？`;
        if (!confirm(confirmMsg)) return;

        const data = JSON.stringify({
            "uname": uname,
            "state": state,
            "camount": camount,
            "env": env,
            "version": version,
            "emailSuffix":getEmailSuffix(),"type": "assetChange"
        });
        const powerResult = document.getElementById('powerResult');
        powerResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";
        this.disabled = true;
        this.textContent = '提交中...';
        axios.post(`/ov/pmmeett/assetChange`, data, {headers: header})
        .then(response => {
            const res = response.data.data;
            accountResult.innerHTML = res;
            console.log(`账户充值/扣减 succ: ${res}`);
        })
        .catch(err => {
            console.log(`账户充值/扣减 err: ${err}`);
            accountResult.innerHTML = '请求异常，请稍后重试。';
        })
        .finally(() => {
            this.disabled = false;
            this.textContent = '提交';
        })
    });

    // 模块10: 账户充值/扣减 重置
    document.getElementById('accountReset').addEventListener('click', function(){
        document.getElementById('uname10').value = '';
        document.querySelector("input[name='rechargeType'][value='1']").checked = true;
        document.getElementById('amount10').value = '';
    })

    // 模块9: 赠送点位 提交
    document.getElementById('giftSubmit').addEventListener('click', function(){
        const giftName = "赠送点位";
        const uname = document.getElementById('giftUname').value;
        const level = document.getElementById('giftLevel').value;
        const amount = document.getElementById('giftAmount').value;
        const expire = document.getElementById('giftExpire').value;
        const env = document.querySelector("input[name='envGift']:checked").value;
        const version = 7;

        if (!uname) { alert('用户账号不能为空！'); return; }
        if (!level) { alert('等级不能为空！'); return; }
        if (!amount) { alert('数量不能为空！'); return; }

        const giftResult = document.getElementById('giftResult');
        giftResult.innerHTML = "<img src='../static/img/loading.gif' height='10'/>";

        axios.post('/ov/pmmeett/assetChange', JSON.stringify({
            uname, level, amount, expire, env, version, emailSuffix: getEmailSuffix(), type: "giftPoints"
        }), {headers: header})
        .then(function(response) {
            giftResult.innerHTML = response.data.data;
            console.log(giftName + ' succ: ' + response.data.data);
        })
        .catch(function(err) {
            console.log(giftName + ' err: ' + err);
        });
    });

    // 模块9: 赠送点位 重置
    document.getElementById('giftReset').addEventListener('click', function(){
        document.getElementById('giftUname').value = '';
        document.getElementById('giftLevel').value = '';
        document.getElementById('giftAmount').value = '1';
        document.getElementById('giftExpire').value = '';
        document.getElementById('giftResult').innerHTML = '';
    })

    // ====== 日期范围选择器 ======
    var datePickerState = {
        year: new Date().getFullYear(),
        month: new Date().getMonth(),
        startDate: null,
        endDate: null,
        selectingEnd: false
    };

    function initDateRangePicker() {
        // 如果有默认值，更新显示
        var start = document.getElementById('startTime').value;
        var end = document.getElementById('endTime').value;
        if (start && end) {
            datePickerState.startDate = start;
            datePickerState.endDate = end;
            updateDateRangeDisplay();
        }
    }

    function openDateRangePicker() {
        var start = document.getElementById('startTime').value;
        var end = document.getElementById('endTime').value;
        datePickerState.startDate = start || null;
        datePickerState.endDate = end || null;
        datePickerState.selectingEnd = false;
        datePickerState.year = new Date().getFullYear();
        datePickerState.month = new Date().getMonth();
        renderDatePicker();
        document.getElementById('dateRangePicker').classList.add('show');
    }

    function closeDateRangePicker() {
        document.getElementById('dateRangePicker').classList.remove('show');
    }

    function confirmDateRange() {
        if (datePickerState.startDate && datePickerState.endDate) {
            document.getElementById('startTime').value = datePickerState.startDate;
            document.getElementById('endTime').value = datePickerState.endDate;
            updateDateRangeDisplay();
        }
        closeDateRangePicker();
    }

    function updateDateRangeDisplay() {
        var start = datePickerState.startDate || '开始日期';
        var end = datePickerState.endDate || '结束日期';
        document.getElementById('dateRangeDisplay').textContent = start + ' 至 ' + end;
    }

    function renderDatePicker() {
        var year = datePickerState.year;
        var month = datePickerState.month;
        var monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
        document.getElementById('pickerTitle').textContent = year + '年' + monthNames[month];

        var firstDay = new Date(year, month, 1).getDay();
        var daysInMonth = new Date(year, month + 1, 0).getDate();
        var today = new Date();

        var html = '';
        for (var i = 0; i < firstDay; i++) {
            html += '<div class="day empty"></div>';
        }
        for (var d = 1; d <= daysInMonth; d++) {
            var dateStr = year + '-' + String(month + 1).padStart(2, '0') + '-' + String(d).padStart(2, '0');
            var classes = 'day';
            if (dateStr === today.toISOString().split('T')[0]) classes += ' today';
            if (datePickerState.startDate === dateStr) classes += ' selected start-date';
            else if (datePickerState.endDate === dateStr) classes += ' selected end-date';
            else if (datePickerState.startDate && datePickerState.endDate) {
                if (dateStr > datePickerState.startDate && dateStr < datePickerState.endDate) {
                    classes += ' in-range';
                }
            }
            html += '<div class="' + classes + '" onclick="selectDate(\'' + dateStr + '\')">' + d + '</div>';
        }
        document.getElementById('pickerDays').innerHTML = html;
    }

    function selectDate(dateStr) {
        if (!datePickerState.selectingEnd) {
            datePickerState.startDate = dateStr;
            datePickerState.endDate = null;
            datePickerState.selectingEnd = true;
        } else {
            if (dateStr >= datePickerState.startDate) {
                datePickerState.endDate = dateStr;
                datePickerState.selectingEnd = false;
            } else {
                datePickerState.startDate = dateStr;
                datePickerState.endDate = null;
                datePickerState.selectingEnd = true;
            }
        }
        renderDatePicker();
        if (datePickerState.startDate && !datePickerState.endDate) {
            document.getElementById('dateRangeDisplay').textContent = dateStr + ' 至 结束日期';
        }
    }

    function datePickerPrevMonth() {
        datePickerState.month--;
        if (datePickerState.month < 0) {
            datePickerState.month = 11;
            datePickerState.year--;
        }
        renderDatePicker();
    }

    function datePickerNextMonth() {
        datePickerState.month++;
        if (datePickerState.month > 11) {
            datePickerState.month = 0;
            datePickerState.year++;
        }
        renderDatePicker();
    }

    // 点击遮罩关闭
    document.getElementById('dateRangePicker').addEventListener('click', function(e) {
        if (e.target === this) closeDateRangePicker();
    });

    // ── 用户注销 ──
    const delSubmit = document.getElementById('delSubmit');
    const delReset = document.getElementById('delReset');

    delSubmit.addEventListener('click', async function() {
        const account = document.getElementById('delAccount').value.trim();
        const pwd = document.getElementById('delPwd').value.trim();
        const num = parseInt(document.getElementById('delNum').value) || 1;
        const env = document.querySelector("input[name='envDel']:checked").value;
        const resultEl = document.getElementById('delResult');
        const version = 7;

        if (!account) { resultEl.innerHTML = '<span class="error">请输入账号</span>'; return; }
        if (!pwd) { resultEl.innerHTML = '<span class="error">请输入密码</span>'; return; }

        // 生成要注销的账号列表
        const accounts = [];
        if (num <= 1) {
            accounts.push(account);
        } else {
            const match = account.match(/^(.*?)(\d+)$/);
            const base = match ? match[1] : account;
            const start = match ? parseInt(match[2]) : 0;
            const width = match ? match[2].length : 0;
            for (let i = 0; i < num; i++) {
                const n = start + i;
                accounts.push(base + String(n).padStart(width, '0'));
            }
        }

        const label = accounts.length === 1 ? `"${accounts[0]}"` : `"${accounts[0]}" ~ "${accounts[accounts.length-1]}"`;
        if (!confirm(`确定要注销 ${accounts.length} 个账号: ${label} 吗？（${env === 'prod' ? '生产' : '测试'}环境）此操作不可逆！`)) return;

        resultEl.innerHTML = `<img src="../static/img/loading.gif" height="10"/> 正在注销 ${accounts.length} 个账号…`;

        const data = JSON.stringify({account: accounts[0], accounts, pwd, env, version, type: 'delAccount'});
        axios.post('/ov/pmmeett/delAccount', data, {headers: header})
        .then(response => {
            const res = response.data;
            if (res.code == '0') {
                resultEl.innerHTML = `<span class="success">✅ ${res.data || '注销成功'}</span>`;
            } else {
                resultEl.innerHTML = `<span class="error">❌ 注销失败: ${res.msg || '未知错误'}</span>`;
            }
        })
        .catch(err => {
            resultEl.innerHTML = `<span class="error">❌ 请求异常: ${err.message}</span>`;
        });
    });

    delReset.addEventListener('click', function() {
        document.getElementById('delAccount').value = '';
        document.getElementById('delPwd').value = '';
        document.getElementById('delNum').value = '1';
        document.getElementById('delResult').innerHTML = '';
    });
