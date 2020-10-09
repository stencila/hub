import babel from "@rollup/plugin-babel";
import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import { terser } from "rollup-plugin-terser";

// Plugins to only include during production builds
const prodPlugins = [terser()];

const plugins = [
  resolve(),
  replace({
    "process.env.NODE_ENV": JSON.stringify(process.env.NODE_ENV),
  }),
  babel({ babelHelpers: "bundled", presets: ["@babel/preset-env"] }),
  ...(process.env.NODE_ENV === "production" ? prodPlugins : []),
];

export default [
  {
    input: "manager/static/js/src/index.js",
    output: {
      file: "manager/static/js/index.js",
      sourcemap: true,
      name: "manager",
      format: "iife",
    },
    plugins,
  },
  {
    input: "manager/static/js/src/libs.js",
    output: {
      file: "manager/static/js/libs.js",
      sourcemap: true,
      name: "managerLibs",
      format: "iife",
    },
    plugins,
  },
  {
    input: "manager/static/js/src/errorHandler.js",
    output: {
      file: "manager/static/js/errorHandler.js",
      sourcemap: true,
      name: "ERAerrorHandler",
      format: "iife",
    },
    plugins,
  },
];
