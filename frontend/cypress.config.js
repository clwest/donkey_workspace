import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    specPattern: 'cypress/integration/**/*.spec.js',
    baseUrl: 'http://localhost:5173',
    supportFile: false
  }
})
