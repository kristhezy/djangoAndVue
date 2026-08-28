// 添加样式的函数
function addStyle(elementId, styleName, value) {
    var element = document.getElementById(elementId);
    
    if (element !== null && typeof element === 'object') {
        // 判断元素存在并且类型正确
        
        element.style[styleName] = value;
        // 设置指定样式名称对应的值
    } else {
        console.error('无效的元素ID');
    }
}
 
// 移除样式的函数
function removeStyle(elementId, styleName) {
    var element = document.getElementById(elementId);
    
    if (element !== null && typeof element === 'object') {
        // 判断元素存在并且类型正确
        
        element.style[styleName] = '';
        // 清空指定样式名称对应的值
    } else {
        console.error('无效的元素ID');
    }
}