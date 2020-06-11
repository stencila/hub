import babel from "@rollup/plugin-babel";
import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { terser } from "rollup-plugin-terser";

// Plugins to only include during production builds
const prodPlugins = [terser()];

export default {
  input: "manager/static/js/src/index.js",
  output: {
    file: "manager/static/js/index.js",
    sourcemap: true,
    name: "manager",
    format: "iife",
  },
  plugins: [
    resolve(),
    replace({
      "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
    }),
    babel({ babelHelpers: "bundled", presets: ["@babel/preset-env"] }),
    ...(process.env.NODE_ENV === "production" ? prodPlugins : []),
  ],
};
