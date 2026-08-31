import http from './http'

export async function getMenu() {
  const resp = await http.get('/api/menu')
  return resp.data?.data
}
