import { definePreset } from "@primeuix/themes";
import Aura from "@primeuix/themes/aura";

const CustomPreset = definePreset(Aura, {
  components: {
    menubar: {
      colorScheme: {
        light: {
          item: {
            activeBackground: "black",
            activeColor: "white",
            focusBackground: "black",
            focusColor: "white",
            icon: {
              focusColor: "white",
              activeColor: "white",
            },
          },
        },
        dark: {
          item: {
            activeBackground: "white",
            activeColor: "black",
            focusBackground: "white",
            focusColor: "black",
            icon: {
              focusColor: "black",
              activeColor: "black",
            },
          },
        },
      },
    },
  },
});

export default CustomPreset;
