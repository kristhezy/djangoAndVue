import { ref } from 'vue'

const darkMq = window.matchMedia('(prefers-color-scheme: dark)')

// 迁移旧版 localStorage
function readSkin() {
  const skin = localStorage.getItem('skin')
  if (skin && ['classic', 'night', 'stone', 'ocean', 'abyss', 'warm'].includes(skin)) return skin
  const old = localStorage.getItem('theme')
  if (old === 'dark') return 'night'
  if (old === 'auto') return darkMq.matches ? 'night' : 'classic'
  if (old === 'light') return 'classic'
  return 'classic'
}

const skin = ref(readSkin())
const themeColor = ref(document.documentElement.getAttribute('data-theme') || 'indigo')

// auto 模式迁移：如果旧值是 auto，监听系统偏好
const _oldTheme = localStorage.getItem('theme')
if (_oldTheme === 'auto') {
  darkMq.addEventListener('change', (e) => {
    if (localStorage.getItem('theme') === 'auto') {
      const s = e.matches ? 'night' : 'classic'
      skin.value = s
      document.documentElement.setAttribute('data-skin', s)
    }
  })
}

export const SKINS = [
  { key: 'classic', label: '经典亮色' },
  { key: 'stone',   label: '石灰' },
  { key: 'night',   label: '暗夜' },
  { key: 'abyss',   label: '纯黑' },
]

export function useTheme() {
  function setSkin(s) {
    skin.value = s
    const isDarkSkin = s === 'night' || s === 'abyss'
    document.documentElement.classList.toggle('dark', isDarkSkin)
    document.documentElement.setAttribute('data-skin', s)
    localStorage.setItem('skin', s)
    localStorage.removeItem('theme')
  }
  function setColor(color) {
    themeColor.value = color
    document.documentElement.setAttribute('data-theme', color)
    localStorage.setItem('themeColor', color)
  }
  return { skin, setSkin, themeColor, setColor }
}
