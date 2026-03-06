// Middleware: Redirect về /login nếu chưa đăng nhập
const PUBLIC_ROUTES = ['/login', '/register']

export default defineNuxtRouteMiddleware((to) => {
    // Bỏ qua các trang public (không cần đăng nhập)
    if (PUBLIC_ROUTES.includes(to.path)) return

    const { isAuthenticated } = useAuth()

    if (!isAuthenticated.value) {
        return navigateTo('/login')
    }
})
