// Composable helper: gọi API có kèm token
export function useApi() {
    const { token } = useAuth()

    const apiFetch = <T>(url: string, options: any = {}) => {
        return $fetch<T>(url, {
            ...options,
            headers: {
                ...options.headers,
                ...(token.value ? { Authorization: `Bearer ${token.value}` } : {})
            }
        })
    }

    return { apiFetch }
}
