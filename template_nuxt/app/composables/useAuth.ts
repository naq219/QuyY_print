// Composable quản lý Authentication
interface User {
    id: string
    username: string
    email?: string | null
    phone?: string | null
    ho_ten: string
    role: 'admin' | 'manager' | 'leader'
    org_id: string | null
    ten_to_chuc: string | null
    group_id: string | null
    support_group_ids: string[]
}

interface OrgOption {
    org_id: string
    ten_to_chuc: string
    slug: string
    role: string
}

export function useAuth() {
    const user = useState<User | null>('auth_user', () => null)
    const token = useState<string | null>('auth_token', () => null)
    const isAuthenticated = computed(() => !!token.value)

    // Khôi phục auth từ localStorage
    const initAuth = () => {
        if (!import.meta.client) return
        const savedToken = localStorage.getItem('auth_token')
        const savedUser = localStorage.getItem('auth_user')
        if (savedToken && savedUser) {
            token.value = savedToken
            try {
                user.value = JSON.parse(savedUser)
            } catch {
                logout()
            }
        }
    }

    // Đăng nhập bằng username
    const login = async (username: string, password: string, org_id?: string) => {
        try {
            const data = await $fetch<
                { token: string; user: User } |
                { require_org_select: true; orgs: OrgOption[] }
            >('/api/auth/login', {
                method: 'POST',
                body: { username, password, org_id }
            })

            // Cần chọn org
            if ('require_org_select' in data && data.require_org_select) {
                return { success: false, require_org_select: true, orgs: data.orgs }
            }

            const loginData = data as { token: string; user: User }
            token.value = loginData.token
            user.value = loginData.user
            if (import.meta.client) {
                localStorage.setItem('auth_token', loginData.token)
                localStorage.setItem('auth_user', JSON.stringify(loginData.user))
            }
            return { success: true }
        } catch (error: any) {
            const message = error?.data?.message || error?.message || 'Đăng nhập thất bại'
            return { success: false, error: message }
        }
    }

    // Đăng xuất
    const logout = () => {
        token.value = null
        user.value = null
        if (import.meta.client) {
            localStorage.removeItem('auth_token')
            localStorage.removeItem('auth_user')
        }
        navigateTo('/login')
    }

    // Lấy thông tin user từ server (verify token)
    const fetchUser = async () => {
        if (!token.value) return null
        try {
            const data = await $fetch<{ user: User }>('/api/auth/me', {
                headers: { Authorization: `Bearer ${token.value}` }
            })
            user.value = data.user
            if (import.meta.client) {
                localStorage.setItem('auth_user', JSON.stringify(data.user))
            }
            return data.user
        } catch {
            logout()
            return null
        }
    }

    // Lấy danh sách tất cả DTT mà user thuộc về
    const fetchMyOrgs = async () => {
        if (!token.value) return []
        try {
            const data = await $fetch<{ current_org_id: string; orgs: OrgOption[] }>('/api/auth/my-orgs', {
                headers: { Authorization: `Bearer ${token.value}` }
            })
            return data.orgs
        } catch {
            return []
        }
    }

    // Chuyển sang DTT khác (không cần nhập lại mật khẩu)
    const switchOrg = async (orgId: string) => {
        if (!token.value) return { success: false, error: 'Chưa đăng nhập' }
        try {
            const data = await $fetch<{ token: string; user: User }>('/api/auth/switch-org', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token.value}` },
                body: { org_id: orgId }
            })
            token.value = data.token
            user.value = data.user
            if (import.meta.client) {
                localStorage.setItem('auth_token', data.token)
                localStorage.setItem('auth_user', JSON.stringify(data.user))
            }
            return { success: true }
        } catch (error: any) {
            const message = error?.data?.message || error?.message || 'Chuyển đạo tràng thất bại'
            return { success: false, error: message }
        }
    }

    // Helper: check quyền
    const isAdmin = computed(() => user.value?.role === 'admin')
    const isManager = computed(() => user.value?.role === 'manager' || user.value?.role === 'admin')
    const orgId = computed(() => user.value?.org_id)
    const orgName = computed(() => user.value?.ten_to_chuc)

    // Auto-init on client
    if (import.meta.client) {
        initAuth()
    }

    return {
        user,
        token,
        isAuthenticated,
        isAdmin,
        isManager,
        orgId,
        orgName,
        login,
        logout,
        fetchUser,
        fetchMyOrgs,
        switchOrg,
        initAuth
    }
}
