<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import axios from "axios";

const formData = reactive({
  vm_name: "",
  human_owner: null,
  pc_owner: null,
  pve: 0,
  pve_host: "192.168.2.13:8006",
  pve_token_username: null,
  pve_token_name: null,
  pve_token_value: null,
  pve_vm_id: null,
  pve_proxy: null,
  spice_proxy: "",
  vm_password: null,
  usb: 0,
});
// window.location.host
// const formData.pve == 1 = computed(() => formData.pve === true);
const isEdit = ref(false);
const clear = () => {
  isEdit.value = false;
  Object.keys(formData).forEach((key) => {
    formData[key] = key === "pve" || "usb" ? 0 : null;
  });
};
// ${window.location.host}
const submit = async () => {
  let response;
  try {
    if (isEdit.value == false) {
      response = await axios.post(
        `http://${window.location.host}/vm`,
        formData
      );
    } else {
      response = await axios.put(
        `http://${window.location.host}/vm/${formData.id}`,
        formData
      );
      isEdit.value = false;
    }
    console.log("Success:", response.data);
  } catch (error) {
    console.error("Error:", error);
  } finally {
    await getAll();
  }
};

const vmList = ref([]);
const getAll = async () => {
  try {
    const response = await axios.get(`http://${window.location.host}/vm/all`);
    vmList.value = response.data;
    console.log(vmList.value)
  } catch (error) {
    console.error("Error:", error);
  }
};
const showEdit = (x) => {
  isEdit.value = true;
  Object.assign(formData, x);
  my_modal_1.showModal();
  console.log(formData);
};
const test = ref();

const toggleEnabled = ref(false);
const input1 = ref("");
const input2 = ref("");
const alwaysEnabledInput = ref("");
onMounted(() => getAll());
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
        >Add VM Configuration
      </button>
      <dialog id="my_modal_1" class="modal ">
        <div class="modal-box max-w-1/2">
          <div class="join">
            <h3 class="text-lg font-bold">
              {{ isEdit ? "Edit" : "Add" }} VM Configuration
            </h3>
            
          </div>
          <div class="p-6 max-w-full mx-auto space-y-4">
            <div class="join">
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
              <!-- PVE Toggle -->
              <div class="form-control"></div>

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
            </div>

            <!-- PVE hOST -->
            <label class="label cursor-pointer">
              <span class="label-text">Enable if it's a Proxmox VM</span>
              <input
                type="checkbox"
                v-model="formData.pve"
                class="toggle"
                :true-value="1"
                :false-value="0"
              />
            </label>
            <div class="form-control">
              
              <label class="label">PVE HOST</label>
              <input
                type="text"
                v-model="formData.pve_host"
                class="input input-bordered w-full"
                :disabled="formData.pve == 0"
                :required="formData.pve == 1"
                placeholder="e.g. 192.168.x.x:0000"
              />
            </div>
            <div class="join">
              <!-- PVE Token Username -->
              <div class="form-control">
                <label class="label">PVE Token Username</label>
                <input
                  type="text"
                  v-model="formData.pve_token_username"
                  class="input input-bordered w-full"
                  :disabled="formData.pve == 0"
                  :required="formData.pve == 1"
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
                  :disabled="formData.pve == 0"
                  :required="formData.pve == 1"
                  placeholder="e.g. lostmypillow"
                />
              </div>
            </div>
            <!-- PVE Token Value -->
            <div class="form-control">
              <label class="label">PVE Token Value</label>
              <input
                type="text"
                v-model="formData.pve_token_value"
                class="input input-bordered w-full"
                :disabled="formData.pve == 0"
                :required="formData.pve == 1"
                placeholder="e.g. c1f03f8b-5e1d-4c4a-a51e-1f32f1a9d7b2"
              />
            </div>

            <div class="join">
              <!-- PVE VM ID -->
              <div class="form-control">
                <label class="label">PVE VM ID</label>
                <input
                  type="number"
                  v-model.number="formData.pve_vm_id"
                  class="input input-bordered w-full"
                  :disabled="formData.pve == 0"
                  :required="formData.pve == 1"
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
                  :disabled="formData.pve == 0"
                  placeholder="e.g. pve1.kaowei.tw:3128 or pve2.kaowei.tw:3128"
                />
              </div>
              <div class="join">
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
              </div>
            </div>

            <!-- VM Password -->
            <div class="form-control">
              <label class="label">VM Password</label>
              <input
                type="text"
                v-model="formData.vm_password"
                class="input input-bordered w-full"
                :disabled="formData.pve == 1"
              />
            </div>
            
          </div>

          <div class="form-control">
          <label class="label cursor-pointer pl-4">
              <span class="label-text">Enable for USB Passthru</span>
              <input
                type="checkbox"
                v-model="formData.usb"
                class="toggle"
                :true-value="1"
                :false-value="0"
              />
            </label>
            </div>

          <div class="modal-action">
            <form method="dialog">
              <!-- if there is a button in form, it will close the modal -->
              <!-- Submit & Clear Buttons -->
              <div class="flex gap-4 mt-4">
                <button @click="submit" class="btn btn-success">
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
                    class="feather feather-check"
                  >
                    <polyline points="20 6 9 17 4 12"></polyline></svg
                  >Submit
                </button>
                <button @click="clear" class="btn btn-secondary">
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
                    class="feather feather-x"
                  >
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line></svg
                  >Cancel
                </button>
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
          <th>human<br />owner</th>
          <th>pc<br />owner</th>
          <th>pve?</th>
          <th>pve<br />host</th>
          <th>pve<br />token<br />username</th>
          <th>
            pve <br />
            token <br />

            name
          </th>
          <th>pve<br />token<br />value</th>
          <th>pve<br />vm_id</th>
          <th>pve_proxy</th>
          <th>spice_proxy</th>
          <th>vm<br />password</th>
          <th>usb</th>
        </tr>
      </thead>
      <tbody>
        <!-- row 1 -->
        <tr v-for="x in vmList">
          <th>
            <button @click="showEdit(x)" class="btn btn-circle">
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
                class="feather feather-edit"
              >
                <path
                  d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"
                ></path>
                <path
                  d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"
                ></path>
              </svg>
            </button>
          </th>
          <td>{{ x.vm_name }}</td>
          <td>{{ x.human_owner }}</td>
          <td>{{ x.pc_owner }}</td>
          <td>{{ x.pve == 1 ? 'yes': 'no' }}</td>
          <td>{{ x.pve_host }}</td>
          <td>{{ x.pve_token_username }}</td>
          <td>{{ x.pve_token_name }}</td>
          <td>{{ x.pve_token_value }}</td>
          <td>{{ x.pve_vm_id }}</td>
          <td>{{ x.pve_proxy }}</td>
          <td>{{ x.spice_proxy }}</td>
          <td>{{ x.vm_password }}</td>
          <td>{{ x.usb == 1 ? 'yes' : 'no' }}</td>
        </tr>
        <!-- row 2 -->

        <!-- row 3 -->
      </tbody>
    </table>
  </div>
</template>
