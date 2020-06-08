import resolve from '@rollup/plugin-node-resolve';
import { terser } from 'rollup-plugin-terser';

export default {
  input: 'manager/static/js/index.mjs',
  output: {
    file: 'manager/static/js/index.js',
    sourcemap: true,
    name: 'manager',
    format: 'iife'
  },
  plugins: [ resolve(), terser() ]
};
