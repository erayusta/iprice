declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NUXT_PUBLIC_API_BASE?: string
      NUXT_PUBLIC_TRENDYOL_AI_SERVICE?: string
    }
  }
  
  var process: {
    env: NodeJS.ProcessEnv
  }
}

export {}
