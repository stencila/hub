import resolve from "@rollup/plugin-node-resolve";
import { terser } from "rollup-plugin-terser";
import replace from "@rollup/plugin-replace";

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
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV)
    }),
    terser(),
  ],
};
