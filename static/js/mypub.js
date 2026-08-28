function Trim(str, is_global) { //去除所有空格
    console.log('trim123!!')
    var result;
    result = str.replace(/(^\s+)|(\s+$)/g, "");
    // if (is_global.toLowerCase() == "g") {
    //     result = result.replace(/\s/g, "");
    // }
    return result;
}

function inputSapceTrim(e, this_temp) { //空格输入去除
    this_temp.value = Trim(this_temp.value, "g");
    var keynum;
    if (window.event) // IE
    {
        keynum = e.keyCode
    } else if (e.which) // Netscape/Firefox/Opera
    {
        keynum = e.which
    }
    if (keynum == 32) {
        return false;
    }
    return true;
}

function numberCheck(num){
    if(!/^\d+$/.test(num)){
        return true
    }else{
        return false
    }
}

function banInputSapce(e) { //禁止空格输入
    var keynum;
    if (window.event) // IE
    {
        keynum = e.keyCode
    } else if (e.which) // Netscape/Firefox/Opera
    {
        keynum = e.which
    }
    if (keynum == 32) {
        return false;
    }
    return true;
}

// 转义HTML
function escapeHTML(str,t = "") {
    if(t === "&"){
        return str.replace(/&/g, '&amp;');
    }
    if(t === "<"){
         return str.replace(/</g, '&lt;');
    }
    if(t === ">"){
        return str.replace(/>/g, '&gt;');
    }
    if(t === '"'){
        return str.replace(/"/g, '&quot;');
    }
    if(t === "'"){
        return str.replace(/'/g, '&#039;');
    }
    if(t.length === 0){
        return str
            .replace(/<br\s*\/?>/gi, '\n')  // 将<br>转换为换行符
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;')
            .replace(/\n/g, '<br>');  // 再将换行符转回<br>，但此时是处理后的;   
    }
}

function esBaseData(str){
    return str
        .replace(/\\/g, '')
        .replace(/"/g, '');
}

function getselectvalue(event,opts) { //创建并获取select中的参数
    try {
        var selectElement = event.target;
        // 检查是否是select元素
        if (selectElement.tagName !== 'SELECT') {
            console.error('目标元素不是select');
            return;
        }
        var options = opts;
        // 保存当前选中的值（如果需要保持选择状态）
        var currentValue = selectElement.value;
        // 清空所有选项
        selectElement.innerHTML = '';
        // 添加"请选择"选项
        var pleaseChooseOption = document.createElement('option');
        pleaseChooseOption.value = '';
        pleaseChooseOption.text = '请选择';
        pleaseChooseOption.selected = true;
        selectElement.add(pleaseChooseOption);
        // 添加数据选项
        Object.entries(options).forEach(([key, value]) => {
            const option = document.createElement('option');
            option.text = key;
            option.value = value;
            // 恢复之前的选择状态
            if (value === currentValue) {
                option.selected = true;
            }
            selectElement.add(option);
        });
    } catch (error) {
        console.error('初始化select失败:', error);
    }
}

// 新增：存储淡出定时器的变量（用于清除重复调用）
let toastTimer = null;

/**
 * 显示 Toast 提示
 * @param {string} content - 提示内容
 * @param {number} duration - 自动关闭时长（传 0 则不自动关闭）
 * @param {boolean} isHtml - 是否支持 HTML 内容
 * @returns {Function} 手动关闭 Toast 的方法
 */
function showToast(content, duration = 2000, isHtml = false) {
    const toastText = document.getElementById('m-toast-inner-text');
    const toastPop = document.getElementById('m-toast-pop');
    if (!toastText || !toastPop) return () => {}; // 兜底返回空函数

    // 清除上一次的定时器（避免重复触发）
    if (toastTimer) clearTimeout(toastTimer);

    // 重置 Toast 样式（避免动画错乱）
    toastPop.style.cssText = `
        display: block;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 99;
    `;

    // 设置文本/HTML 内容
    if (isHtml) {
        toastText.innerHTML = content;
    } else {
        toastText.textContent = content;
    }

    // 淡入动画
    setTimeout(() => {
        toastPop.style.opacity = '1';
    }, 10);

    // 定义手动关闭方法（核心：封装淡出逻辑）
    const hideToast = () => {
        toastPop.style.opacity = '0';
        setTimeout(() => {
            toastPop.style.display = 'none';
            toastTimer = null; // 清空定时器标记
        }, 600); // 与过渡时长一致
    };

    // 自动关闭逻辑（duration ≠ 0 时生效）
    if (duration > 0) {
        toastTimer = setTimeout(hideToast, duration);
    }

    // 返回手动关闭方法（供接口回调调用）
    return hideToast;
}

// 获取所有日期输入框
function getDateInput(className){
    const dateInputs = document.querySelectorAll(className);
    dateInputs.forEach(input => {
        // 仅允许一次触发（避免单次点击重复调用报错）
        let isTriggered = false;

        // 核心：仅监听 click 事件（纯用户主动手势）
        input.addEventListener('click', function (e) {
            // 1. 阻止默认行为（避免浏览器自带日历和自定义触发冲突）
            e.preventDefault();
            // 2. 避免单次点击重复触发
            if (isTriggered) return;
            isTriggered = true;

            try {
                // 同步调用：无任何异步延迟，直接执行
                this.showPicker();
            } catch (err) {
                console.warn(`日期选择器调用失败: ${err}`);
                // 降级方案：兼容不支持 showPicker() 的浏览器
                if (err.name === 'NotAllowedError') {
                    // 恢复默认行为（让浏览器触发原生日历）
                    this.type = 'date';
                    isTriggered = false; // 重置标记
                }
            }

            // 3. 重置标记（避免后续点击失效，需在事件结束后重置）
            setTimeout(() => {
                isTriggered = false;
            }, 300); // 短延迟，避免快速点击重复触发
        });

        // 可选：兼容 tab 键聚焦（仅提示用户点击，不强制调用 showPicker）
        input.addEventListener('focus', function () {
            console.log('请点击输入框打开日期选择器');
            // 此处不调用 showPicker()，避免触发安全限制
        });
    });
}

//从 cookie 获取 CSRF 令牌
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 令牌管理器
class CSRFTokenManager {
    constructor(tokenName = 'csrftoken', refreshInterval = 12 * 60 * 60 * 1000) {
        this.tokenName = tokenName;
        this.refreshInterval = refreshInterval;
        this.token = null;
        this.tokenCreationTime = null;
        this.refreshTimer = null;
        this.onTokenRefresh = null;
        this.onTokenExpiryWarning = null;
        
        // 初始化
        this.init();
    }
    
    // 初始化令牌管理器
    init() {
        // 尝试从 cookie 获取现有令牌
        this.token = getCookie(this.tokenName);
        
        // 尝试从本地存储获取令牌创建时间
        const savedCreationTime = localStorage.getItem(`_${this.tokenName}_creationTime`);
        
        if (this.token && savedCreationTime) {
            this.tokenCreationTime = new Date(savedCreationTime);
            
            // 检查令牌是否已过期
            const now = new Date();
            const tokenAge = now - this.tokenCreationTime;
            
            if (tokenAge >= this.refreshInterval) {
                // 令牌已过期，立即刷新
                this.refreshToken();
            } else {
                // 令牌有效，设置下次刷新时间
                this.scheduleNextRefresh(this.refreshInterval - tokenAge);
                
                // 如果令牌即将过期（剩余时间少于10%），触发警告
                if (tokenAge > this.refreshInterval * 0.9) {
                    this.triggerExpiryWarning();
                }
            }
        } else {
            // 没有现有令牌或创建时间，刷新令牌
            this.refreshToken();
        }
    }
    
    // 获取当前令牌
    getToken() {
        return this.token;
    }
    
    // 获取令牌创建时间
    getTokenCreationTime() {
        return this.tokenCreationTime;
    }
    
    // 获取令牌剩余有效时间
    getTokenRemainingTime() {
        if (!this.tokenCreationTime) return 0;
        
        const now = new Date();
        const tokenAge = now - this.tokenCreationTime;
        return Math.max(0, this.refreshInterval - tokenAge);
    }
    
    // 刷新令牌
    refreshToken() {
        // 调用刷新令牌的 API
        this.fetchNewToken()
            .then(() => {
                // 保存新令牌的创建时间
                this.tokenCreationTime = new Date();
                localStorage.setItem(`_${this.tokenName}_creationTime`, this.tokenCreationTime.toISOString());
                
                // 安排下一次刷新
                this.scheduleNextRefresh(this.refreshInterval);
                
                // 触发刷新回调（如果有）
                if (typeof this.onTokenRefresh === 'function') {
                    this.onTokenRefresh(this.token);
                }
                
                console.log(`CSRF 令牌已刷新，下次刷新将在 ${this.formatDuration(this.refreshInterval)} 后进行`);
            })
            .catch(error => {
                console.error('刷新 CSRF 令牌失败:', error);
                
                // 安排一个更短的时间后重试
                this.scheduleNextRefresh(5 * 60 * 1000); // 5分钟后重试
            });
    }
    
    // 从服务器获取新令牌
    fetchNewToken() {
        return new Promise((resolve, reject) => {
            // 这里应该是实际的 API 调用，用于刷新 CSRF 令牌
            // 例如，向服务器发送一个刷新令牌的请求
            
            // 模拟网络请求延迟
            setTimeout(() => {
                // 从 cookie 重新获取令牌
                const newToken = getCookie(this.tokenName);
                
                if (newToken) {
                    this.token = newToken;
                    resolve();
                } else {
                    reject(new Error('无法获取新的 CSRF 令牌'));
                }
            }, 500);
        });
    }
    
    // 安排下次刷新
    scheduleNextRefresh(delay) {
        // 清除现有定时器
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }
        
        // 设置新的定时器
        this.refreshTimer = setTimeout(() => {
            this.refreshToken();
        }, delay);
        
        // 计算并记录下次刷新时间
        const nextRefreshTime = new Date(new Date().getTime() + delay);
        console.log(`下一次 CSRF 令牌刷新计划于 ${nextRefreshTime.toLocaleString()}`);
        
        // 设置过期警告（剩余10%时间时）
        const warningDelay = Math.max(0, delay - this.refreshInterval * 0.1);
        setTimeout(() => {
            this.triggerExpiryWarning();
        }, warningDelay);
    }
    
    // 触发令牌即将过期警告
    triggerExpiryWarning() {
        if (typeof this.onTokenExpiryWarning === 'function') {
            const remainingTime = this.getTokenRemainingTime();
            this.onTokenExpiryWarning(remainingTime);
        }
    }
    
    // 格式化持续时间为易读格式
    formatDuration(ms) {
        const hours = Math.floor(ms / 3600000);
        const minutes = Math.floor((ms % 3600000) / 60000);
        const seconds = Math.floor((ms % 60000) / 1000);
        
        if (hours > 0) {
            return `${hours}小时${minutes}分钟${seconds}秒`;
        } else if (minutes > 0) {
            return `${minutes}分钟${seconds}秒`;
        } else {
            return `${seconds}秒`;
        }
    }
    
    // 清理资源
    destroy() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }
    }
}

// 使用示例
const tokenManager = new CSRFTokenManager();

// 设置令牌刷新回调
tokenManager.onTokenRefresh = (newToken) => {
    console.log('新的 CSRF 令牌已生成:', newToken);
    // 这里可以将新令牌应用到你的应用中
};

// 设置令牌即将过期回调
tokenManager.onTokenExpiryWarning = (remainingTime) => {
    console.warn(`CSRF 令牌即将过期，剩余时间: ${tokenManager.formatDuration(remainingTime)}`);
};
