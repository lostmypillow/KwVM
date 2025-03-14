import { reactive, computed } from 'vue'
import axios from 'axios'

const formData = reactive({
  vm_name: '',
  human_owner: null,
  pc_owner: null,
  pve: 0,
  pve_token_username: null,
  pve_token_name: null,
  pve_token_value: null,
  pve_vm_id: null,
  pve_proxy: null,
  spice_proxy: '',
  vm_password: null,
})

const isProxmoxEnabled = computed(() => formData.pve === 1)

const clear = () => {
  Object.keys(formData).forEach(key => {
    formData[key] = key === 'pve' ? 0 : null
  })
}

const submit = async () => {
  try {
    const response = await axios.post('https://example.com/api/vm', formData)
    console.log('Success:', response.data)
  } catch (error) {
    console.error('Error:', error)
  }
}
