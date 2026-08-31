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
  const token = getCookie('csrftoken')
  if (token) {
    config.headers['X-CSRFToken'] = token
  }
  config.headers['Content-Type'] = 'application/json'
  return config
})

// 拦截「后端重定向」：axios 跟随重定向后拿不到明确的 302 状态，
// 通过返回体无 json 或最终 URL 判断。这里用 401/403 兜底 + 手动检查。
http.interceptors.response.use(
  (resp) => resp,
  (err) => {
    const status = err.response?.status
    if (status === 401 || status === 403) {
      // 未登录/无权限：跳回登录页
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default http
