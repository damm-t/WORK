import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      boxShadow: {
        glow: '0 20px 60px rgba(14, 165, 233, 0.18)',
      },
    },
  },
  plugins: [],
};

export default config;
