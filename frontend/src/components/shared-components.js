/**
 * 统一设计系统 — 共享 inline 子组件
 * 所有页面 import 后直接使用
 */

export const EnvRadio = {
  props: ['modelValue', 'name'],
  emits: ['update:modelValue'],
  template: `<div class="env-group"><div class="env-track"><label :class="{active:modelValue==='test'}"><input type="radio" :name="name" value="test" :checked="modelValue==='test'" @change="$emit('update:modelValue','test')"/><i class="fa-solid fa-flask"></i> 测试环境</label><label :class="{active:modelValue==='prod'}"><input type="radio" :name="name" value="prod" :checked="modelValue==='prod'" @change="$emit('update:modelValue','prod')"/><i class="fa-solid fa-server"></i> 生产环境</label></div></div>`,
}

export const BtnGroup = {
  emits: ['reset', 'submit'],
  template: `<div class="btn-group"><el-button class="btn-reset" @click="$emit('reset')">重置</el-button><el-button class="btn-submit" type="primary" @click="$emit('submit')">提交</el-button></div>`,
}

export const ResultBox = {
  props: ['text', 'lines', 'loading'],
  template: `<div class="result"><span v-if="loading" class="result-loading"><i class="fa-solid fa-spinner fa-spin"></i> 处理中...</span><template v-else-if="lines&&lines.length"><div v-for="(l,i) in lines" :key="i" class="result-line" v-html="l"></div></template><span v-else v-html="text||''"></span></div>`,
}

export const TabGroup = {
  props: ['tabs', 'modelValue'],
  emits: ['update:modelValue', 'change'],
  template: `<div class="tab-group"><label v-for="t in tabs" :key="t.v" :class="{active:modelValue===t.v}"><input type="radio" :value="t.v" :checked="modelValue===t.v" @change="$emit('update:modelValue',t.v);$emit('change',t.v)"/><span class="tab-item">{{t.l}}</span></label></div>`,
}
