<script setup>
definePageMeta({ layout: false })

const { isAuthenticated } = useAuth()
if (isAuthenticated.value) {
  navigateTo('/')
}

const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const form = ref({
  ten_to_chuc: '',
  slug: '',
  email: '',
  password: '',
  confirmPassword: '',
  ho_ten: '',
  dia_chi: ''
})

// Tự sinh slug từ tên đạo tràng
watch(() => form.value.ten_to_chuc, (val) => {
  form.value.slug = val
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/đ/g, 'd')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .slice(0, 50)
})

const handleRegister = async () => {
  errorMessage.value = ''

  if (!form.value.ten_to_chuc || !form.value.slug || !form.value.email || !form.value.password || !form.value.ho_ten) {
    errorMessage.value = 'Vui lòng điền đầy đủ các trường bắt buộc'
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    errorMessage.value = 'Mật khẩu xác nhận không khớp'
    return
  }

  if (form.value.password.length < 6) {
    errorMessage.value = 'Mật khẩu phải có ít nhất 6 ký tự'
    return
  }

  loading.value = true
  try {
    const data = await $fetch('/api/auth/register', {
      method: 'POST',
      body: {
        ten_to_chuc: form.value.ten_to_chuc,
        slug: form.value.slug,
        email: form.value.email,
        password: form.value.password,
        ho_ten: form.value.ho_ten,
        dia_chi: form.value.dia_chi
      }
    })

    // Lưu token và đăng nhập ngay
    if (import.meta.client) {
      localStorage.setItem('auth_token', data.token)
      localStorage.setItem('auth_user', JSON.stringify(data.user))
    }

    navigateTo('/')
  } catch (error) {
    errorMessage.value = error?.data?.message || error?.message || 'Đăng ký thất bại'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex items-center justify-center min-h-screen bg-surface-50 dark:bg-surface-950 py-8">
    <div class="w-full max-w-lg px-6">
      <div class="card p-8">
        <!-- Logo & Title -->
        <div class="text-center mb-8">
          <div class="flex items-center justify-center mb-4">
            <i class="pi pi-building text-primary" style="font-size: 2.5rem"></i>
          </div>
          <h1 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
            Đăng Ký Đạo Tràng
          </h1>
          <p class="text-muted-color">Tạo tổ chức mới và tài khoản quản trị</p>
        </div>

        <!-- Messages -->
        <Message v-if="errorMessage" severity="error" :closable="false" class="mb-4">
          {{ errorMessage }}
        </Message>

        <!-- Form -->
        <form @submit.prevent="handleRegister" class="flex flex-col gap-4">

          <!-- Thông tin đạo tràng -->
          <div class="text-sm font-semibold text-muted-color uppercase tracking-wide mb-1">
            Thông tin đạo tràng
          </div>

          <div class="flex flex-col gap-2">
            <label for="ten_to_chuc" class="font-medium">
              Tên đạo tràng <span class="text-red-500">*</span>
            </label>
            <InputText
              id="ten_to_chuc"
              v-model="form.ten_to_chuc"
              placeholder="VD: Đạo Tràng Quận 1"
              :disabled="loading"
              class="w-full"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="slug" class="font-medium">
              Slug (định danh URL) <span class="text-red-500">*</span>
            </label>
            <InputText
              id="slug"
              v-model="form.slug"
              placeholder="VD: dao-trang-quan-1"
              :disabled="loading"
              class="w-full font-mono"
            />
            <small class="text-muted-color">Chỉ chữ thường, số, dấu gạch ngang. Tự sinh từ tên.</small>
          </div>

          <div class="flex flex-col gap-2">
            <label for="dia_chi" class="font-medium">Địa chỉ</label>
            <InputText
              id="dia_chi"
              v-model="form.dia_chi"
              placeholder="Địa chỉ đạo tràng"
              :disabled="loading"
              class="w-full"
            />
          </div>

          <Divider />

          <!-- Thông tin quản trị viên -->
          <div class="text-sm font-semibold text-muted-color uppercase tracking-wide mb-1">
            Tài khoản quản trị viên
          </div>

          <div class="flex flex-col gap-2">
            <label for="ho_ten" class="font-medium">
              Họ và tên <span class="text-red-500">*</span>
            </label>
            <InputText
              id="ho_ten"
              v-model="form.ho_ten"
              placeholder="Họ tên admin"
              :disabled="loading"
              class="w-full"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="email" class="font-medium">
              Email <span class="text-red-500">*</span>
            </label>
            <InputText
              id="email"
              v-model="form.email"
              type="email"
              placeholder="admin@example.com"
              :disabled="loading"
              class="w-full"
              autocomplete="email"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="password" class="font-medium">
              Mật khẩu <span class="text-red-500">*</span>
            </label>
            <Password
              id="password"
              v-model="form.password"
              placeholder="Ít nhất 6 ký tự"
              :disabled="loading"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full"
            />
          </div>

          <div class="flex flex-col gap-2">
            <label for="confirmPassword" class="font-medium">
              Xác nhận mật khẩu <span class="text-red-500">*</span>
            </label>
            <Password
              id="confirmPassword"
              v-model="form.confirmPassword"
              placeholder="Nhập lại mật khẩu"
              :disabled="loading"
              :feedback="false"
              toggleMask
              class="w-full"
              inputClass="w-full"
            />
          </div>

          <Button
            type="submit"
            label="Đăng ký Đạo Tràng"
            icon="pi pi-check"
            :loading="loading"
            class="w-full mt-2"
          />

          <div class="text-center mt-2">
            <span class="text-muted-color text-sm">Đã có tài khoản? </span>
            <NuxtLink to="/login" class="text-primary text-sm font-medium hover:underline">
              Đăng nhập →
            </NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
