<script setup>
definePageMeta({ layout: false })

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

// Trường hợp 1 username thuộc nhiều đạo tràng
const orgOptions = ref([])
const showOrgSelect = ref(false)
const selectedOrgId = ref('')

const { login, isAuthenticated } = useAuth()

// Nếu đã đăng nhập, redirect về dashboard
if (isAuthenticated.value) {
  navigateTo('/')
}

const handleLogin = async () => {
  errorMessage.value = ''
  loading.value = true

  const result = await login(username.value, password.value, selectedOrgId.value || undefined)

  if (result.success) {
    navigateTo('/')
  } else if (result.require_org_select) {
    // Cần chọn đạo tràng
    orgOptions.value = result.orgs
    showOrgSelect.value = true
    errorMessage.value = ''
  } else {
    errorMessage.value = result.error || 'Đăng nhập thất bại'
  }

  loading.value = false
}

const handleSelectOrg = async (orgId) => {
  selectedOrgId.value = orgId
  showOrgSelect.value = false
  await handleLogin()
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-surface-50 dark:bg-surface-950">
    <div class="w-full max-w-md px-6">
      <div class="card p-8">
        <!-- Logo & Title -->
        <div class="text-center mb-8">
          <div class="flex items-center justify-center mb-4">
            <i class="pi pi-heart-fill text-primary" style="font-size: 2.5rem"></i>
          </div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
            Chăm Sóc Thành Viên
          </h1>
          <p class="text-muted-color">Đăng nhập để tiếp tục</p>
        </div>

        <!-- Error Message -->
        <Message v-if="errorMessage" severity="error" :closable="false" class="mb-4">
          {{ errorMessage }}
        </Message>

        <!-- Chọn Đạo Tràng (khi 1 username thuộc nhiều tổ chức) -->
        <div v-if="showOrgSelect" class="mb-4">
          <p class="font-medium mb-3">Chọn đạo tràng để đăng nhập:</p>
          <div class="flex flex-col gap-2">
            <Button
              v-for="org in orgOptions"
              :key="org.org_id"
              :label="org.ten_to_chuc || org.slug"
              icon="pi pi-building"
              severity="secondary"
              outlined
              class="w-full justify-start"
              @click="handleSelectOrg(org.org_id)"
            />
          </div>
          <Button
            label="Quay lại"
            icon="pi pi-arrow-left"
            text
            class="w-full mt-2"
            @click="showOrgSelect = false; selectedOrgId = ''"
          />
        </div>

        <!-- Login Form -->
        <form v-else @submit.prevent="handleLogin" class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <label for="username" class="font-medium">Tài khoản</label>
            <InputText
              id="username"
              v-model="username"
              type="text"
              placeholder="Nhập tài khoản"
              :disabled="loading"
              class="w-full"
              autocomplete="username"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="password" class="font-medium">Mật khẩu</label>
            <Password
              id="password"
              v-model="password"
              placeholder="Nhập mật khẩu"
              :disabled="loading"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full"
            />
          </div>

          <Button
            type="submit"
            label="Đăng nhập"
            icon="pi pi-sign-in"
            :loading="loading"
            class="w-full mt-2"
          />

          <!-- Link đăng ký -->
          <div class="text-center mt-2">
            <span class="text-muted-color text-sm">Chưa có tài khoản? </span>
            <NuxtLink to="/register" class="text-primary text-sm font-medium hover:underline">
              Đăng ký đạo tràng mới →
            </NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
