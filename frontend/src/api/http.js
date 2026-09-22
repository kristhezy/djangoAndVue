import axios from 'axios'

function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'))
  return m ? decodeURIComponent(m[1]) : ''
}

const http = axios.create({
  baseURL: '',
  withCredentials: true,
})

http.interceptors.request.use((config) => {
  const token = getCookie('djv_csrftoken')
  if (token) {
    config.headers.set('X-CSRFToken', token)
  }
  // FormData 不设置 Content-Type，让浏览器自动设置 multipart/form-data 及 boundary
  if (config.data instanceof FormData) {
    config.headers.delete('Content-Type')
  } else if (!config.headers.has('Content-Type')) {
    config.headers.set('Content-Type', 'application/json')
  }
  return config
})

// 拦截「后端重定向」：Django 的 login_required 默认返回 302 到登录页，
// axios 跟随重向后拿到的是 HTML（200），无法解析为 JSON。
// 通过检查响应类型和最终 URL 来判断是否需要跳登录页。
http.interceptors.response.use(
  (resp) => {
    // 后端 302 跟随后拿到 HTML：Content-Type 为 text/html 说明被重定向到了登录页
    const ct = resp.headers['content-type'] || ''
    if (ct.includes('text/html')) {
      // 如果最终 URL 包含 /login 说明被重定向到了登录页
      if (resp.request?.responseURL?.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return resp
  },
  (err) => {
    const status = err.response?.status
    if (status === 401 || status === 403) {
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// 供 fetch 等非 axios 场景获取 CSRF token（如 SSE 流式请求）
http.getCSRF = () => getCookie('djv_csrftoken')

export default http
