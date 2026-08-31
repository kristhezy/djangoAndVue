import { defineStore } from 'pinia'
import { getMenu } from '../api/menu'

export const useMenuStore = defineStore('menu', {
  state: () => ({
    user: {},
    groups: [],
    standalone: [],
    loaded: false,
  }),
  actions: {
    async fetchMenu() {
      const data = await getMenu()
      this.user = data.user || {}
      this.groups = data.groups || []
      this.standalone = data.standalone || []
      this.loaded = true
    },
  },
})
