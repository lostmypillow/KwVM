<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import axios from "axios";

const formData = reactive({
  vm_name: "",
  human_owner: null,
  pc_owner: null,
  pve: 0,
  pve_host: '192.168.2.13:8006',
  pve_token_username: null,
  pve_token_name: null,
  pve_token_value: null,
  pve_vm_id: null,
  pve_proxy: null,
  spice_proxy: "",
  vm_password: null,
});

const isProxmoxEnabled = computed(() => formData.pve === 1);
const isEdit = ref(false)
const clear = () => {
  Object.keys(formData).forEach((key) => {
    formData[key] = key === "pve" ? 0 : null;
  });
};

const submit = async () => {
  let response
  try {
    if( isEdit.value == false){
    response = await axios.post(`http://${window.location.host}/vm`, formData);
    } else {
      response = await axios.put(`http://${window.location.host}/vm/${formData.id}`, formData);
      isEdit.value = false
    }
      console.log("Success:", response.data);
  } catch (error) {
    console.error("Error:", error);
  } finally {
    await getAll()
  }
};

const vmList = ref([])
const getAll = async () => {
  try {
    const response = await axios.get(`http://192.168.2.32:8005/vm/all`);
    vmList.value = response.data
  } catch (error) {
    console.error("Error:", error);
  }
};
const showEdit = (x) => {
  isEdit.value = true
  Object.assign(formData, x)
  my_modal_1.showModal()
  
}
const test = ref();

const toggleEnabled = ref(false);
const input1 = ref("");
const input2 = ref("");
const alwaysEnabledInput = ref("");
onMounted(()=> getAll())
</script>

<template>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">KwVM{{ test }}</a>
      <!-- <button @click="getAll" class="btn btn-primary">Hi</button> -->
    </div>
    <div class="flex-none">
      <!-- Open the modal using ID.showModal() method -->
      <button class="btn btn-primary" onclick="my_modal_1.showModal()">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="feather feather-plus"
        >
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line></svg
        >{{ isEdit? 'Edit' : 'Add'}} VM Configuration
      </button>
      <dialog id="my_modal_1" class="modal">
        <div class="modal-box">
          <h3 class="text-lg font-bold">Add VM Configuration</h3>
          <div class="p-6 max-w-lg mx-auto space-y-4">
            <!-- PVE Toggle -->
            <div class="form-control">
              <label class="label cursor-pointer">
                <span class="label-text">Enable if this is a Proxmox VM</span>
                <input
                  type="checkbox"
                  v-model="formData.pve"
                  class="toggle"
                  :true-value="1"
                  :false-value="0"
                />
              </label>
            </div>
            <!-- VM Name -->
            <div class="form-control">
              <label class="label">VM Name</label>
              <input
                type="text"
                v-model="formData.vm_name"
                class="input input-bordered w-full"
                required
              />
            </div>

            <!-- Human Owner -->
            <div class="form-control">
              <label class="label">Human Owner</label>
              <input
                type="text"
                v-model="formData.human_owner"
                class="input input-bordered w-full"
                placeholder="e.g. 201350"
              />
            </div>

            <!-- PC Owner -->
            <div class="form-control">
              <label class="label">PC Owner</label>
              <input
                type="text"
                v-model="formData.pc_owner"
                class="input input-bordered w-full"
                placeholder="e.g. DESKTOP-KWMIS"
              />
            </div>

            <!-- PVE hOST -->
            <div class="form-control">
              <label class="label">PVE  HOST</label>
              <input
                type="text"
                v-model="formData.pve_host"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                :required="isProxmoxEnabled"
                placeholder="e.g. lostmypillow"
              />
            </div>

            <!-- PVE Token Username -->
            <div class="form-control">
              <label class="label">PVE Token Username</label>
              <input
                type="text"
                v-model="formData.pve_token_username"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                :required="isProxmoxEnabled"
                placeholder="e.g. lostmypillow"
              />
            </div>

            <!-- PVE Token Name -->
            <div class="form-control">
              <label class="label">PVE Token Name</label>
              <input
                type="text"
                v-model="formData.pve_token_name"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                :required="isProxmoxEnabled"
                placeholder="e.g. lostmypillow"
              />
            </div>

            <!-- PVE Token Value -->
            <div class="form-control">
              <label class="label">PVE Token Value</label>
              <input
                type="text"
                v-model="formData.pve_token_value"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                :required="isProxmoxEnabled"
                placeholder="e.g. c1f03f8b-5e1d-4c4a-a51e-1f32f1a9d7b2"
              />
            </div>

            <!-- PVE VM ID -->
            <div class="form-control">
              <label class="label">PVE VM ID</label>
              <input
                type="number"
                v-model.number="formData.pve_vm_id"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                :required="isProxmoxEnabled"
                placeholder="e.g. 301"
              />
            </div>

            <!-- PVE Proxy -->
            <div class="form-control">
              <label class="label">PVE Proxy</label>
              <input
                type="text"
                v-model="formData.pve_proxy"
                class="input input-bordered w-full"
                :disabled="!isProxmoxEnabled"
                placeholder="e.g. pve1.kaowei.tw:3128 or pve2.kaowei.tw:3128"
              />
            </div>

            <!-- Spice Proxy -->
            <div class="form-control">
              <label class="label">Spice Proxy</label>
              <input
                type="text"
                v-model="formData.spice_proxy"
                class="input input-bordered w-full"
                required
                placeholder="e.g. 192.168.2.13:3128"
              />
            </div>

            <!-- VM Password -->
            <div class="form-control">
              <label class="label">VM Password</label>
              <input
                type="password"
                v-model="formData.vm_password"
                class="input input-bordered w-full"
                :disabled="isProxmoxEnabled"
              />
            </div>
          </div>
          <div class="modal-action">
            <form method="dialog">
              <!-- if there is a button in form, it will close the modal -->
              <!-- Submit & Clear Buttons -->
              <div class="flex gap-4 mt-4">
                <button @click="submit" class="btn btn-primary">Submit</button>
                <button @click="clear" class="btn btn-secondary">Clear</button>
              </div>
            </form>
          </div>
        </div>
      </dialog>
    </div>
  </div>

  <div
    class="overflow-x-auto rounded-box border border-base-content/5 bg-base-100"
  >
    <table class="table">
      <!-- head -->
      <thead>
        <tr>
          <th></th>
          <th>vm_name</th>
          <th>human_owner</th>
          <th>pc_owner</th>
          <th>pve?</th>
          <th>pve_host</th>
          <th>pve_token_username</th>
          <th>pve_token_name</th>
          <th>pve_token_value</th>
          <th>pve_vm_id</th>
          <th>pve_proxy</th>
          <th>spice_proxy</th>
          <th>vm_password</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <!-- row 1 -->
        <tr v-for="x in vmList">
          <th>
            {{x.id}}
          </th>
          <td>{{x.vm_name}}</td>
          <td>{{x.human_owner}}</td>
          <td>{{x.pc_owner}}</td>
          <td>{{x.pve}}</td>
          <td>{{x.pve_host}}</td>
          <td>{{x.pve_token_username}}</td>
          <td>{{x.pve_token_name}}</td>
          <td>{{x.pve_token_value}}</td>
          <td>{{x.pve_vm_id}}</td>
          <td>{{x.pve_proxy}}</td>
          <td>{{x.spice_proxy}}</td>
          <td>{{x.vm_password}}</td>
          <td><button @click="showEdit(x)" class="btn btn-circle">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>

          </button></td>
        </tr>
        <!-- row 2 -->

        <!-- row 3 -->
      </tbody>
    </table>
  </div>
</template>
