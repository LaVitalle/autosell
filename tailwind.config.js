// tailwind.config.js
module.exports = {
  darkMode: "class", // Ou 'media' se você preferir que o modo escuro seja baseado nas preferências do usuário
  theme: {
    extend: {
      colors: {
        primary: "#4A90E2",
        secondary: "#50E3C2",
        accent: "#F5A623",
      },
    },
  },
  variants: {
    extend: {
      backgroundColor: ["dark"],
      textColor: ["dark"],
    },
  },
  plugins: [require("@tailwindcss/forms")],
};
