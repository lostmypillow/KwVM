<script setup>
const demo = {
  id: 1,
    hostname : 'mis-kw',
    proxmox: 1,
    user_name : 'lostmypillow',
    token_name: 'lostmypillow',
    token_value:  'lostmypillow',
    vm_id: 301,
    proxy_from NVARCHAR(255) NULL,
    proxy_to NVARCHAR(255) NOT NULL,
    password NVARCHAR(255) NULL,
    created_at DATETIME2 DEFAULT SYSDATETIME() NOT NULL,
    updated_at DATETIME2 DEFAULT SYSDATETIME() NOT NULL,
}
</script>

<template>
  <div class="navbar bg-base-100 shadow-sm">
    <div class="flex-1">
      <a class="btn btn-ghost text-xl">daisyUI</a>
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
      <dialog id="my_modal_1" class="modal">
        <div class="modal-box">
          <h3 class="text-lg font-bold">Hello!</h3>
          <p class="py-4">Press ESC key or click the button below to close</p>
          <div class="modal-action">
            <form method="dialog">
              <!-- if there is a button in form, it will close the modal -->
              <button class="btn">Close</button>
              <button class="btn">Submit</button>
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
          <th>
            <label>
              <input type="checkbox" class="checkbox" />
            </label>
          </th>
          <th>hostname</th>
          <th>
            <div class="tooltip" data-tip="(1 for proxmox, 0)">
              Proxmox? (Hover for details)
            </div>
          </th>
          <th>Username (e.g. lostmypillow)</th>
          <th>token Name (e.g. lostmypillow)</th>
          <th>Token Value</th>
          <th>VM ID</th>
          <th>Proxy From URL (Proxmox SPICE Proxy)</th>
          <th>Proxy To URL (SPICE URL)</th>
          <th>Password</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <!-- row 1 -->
        <tr>
          <th>1</th>
          <td>Cy Ganderton</td>
          <td>Quality Control Specialist</td>
          <td>Blue</td>
          <td>meow</td>
          <td>meow</td>
          <td>meow</td>
          <td>meow</td>
          <td>meow</td>
          <td>meow</td>
          <td>
            <button class="btn btn-secondary" onclick="my_modal_1.showModal()">
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
                ></path></svg
              >Edit
            </button>
            <dialog id="my_modal_1" class="modal">
              <div class="modal-box">
                <h3 class="text-lg font-bold">Hello!</h3>
                <p class="py-4">
                  Press ESC key or click the button below to close
                </p>
                <div class="modal-action">
                  <form method="dialog">
                    <!-- if there is a button in form, it will close the modal -->
                    <button class="btn">Close</button>
                    <button class="btn">Submit</button>
                  </form>
                </div>
              </div>
            </dialog>
          </td>
        </tr>
        <!-- row 2 -->

        <!-- row 3 -->
      </tbody>
    </table>
  </div>
</template>
