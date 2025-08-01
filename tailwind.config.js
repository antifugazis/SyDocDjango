/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./**/templates/**/*.html",
      "./**/static/**/*.js",
      // Add other template paths if needed
    ],
    theme: {
      extend: {
        fontFamily: {
          'sans': ['DM Sans', 'sans-serif'],
          'funnel': ['Funnel Sans', 'sans-serif'],
          'roboto-mono': ['Roboto Mono', 'monospace'],
        },
      },
    },
    plugins: [],
  }