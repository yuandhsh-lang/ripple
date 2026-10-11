import { configDefaults, defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config.ts'

export default mergeConfig(viteConfig, defineConfig({
  test: {
    // Downloaded upstream sources have their own build/test entry points.
    // Keep Vitest's normal project discovery and all existing default excludes.
    exclude: [...configDefaults.exclude, 'phase1/toolchain/**', 'phase1/sources/**'],
  },
}))
