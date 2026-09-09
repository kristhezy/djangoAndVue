import http from './http'

/** POST /login — 登录 */
export function doLogin(ln, pw, next) {
  return http.post('/login', { ln, pw, next })
}
