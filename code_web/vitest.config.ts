import { defineConfig } from 'vitest/config'

export default defineConfig({
    test: {
        // Test timeout dài hơn vì gọi DB remote (Turso)
        testTimeout: 30000,
        hookTimeout: 30000,

        // Thư mục test
        include: ['tests/**/*.test.ts'],

        // Chạy tuần tự (tránh race condition với DB)
        sequence: {
            concurrent: false
        },

        // Env
        env: {
            NODE_ENV: 'test'
        }
    }
})
