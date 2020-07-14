const atImport = require("postcss-import");
const autoprefixer = require("autoprefixer");
const cssnano = require("cssnano");
const importUrl = require("postcss-import-url");
const mqPacker = require("css-mqpacker");
const purgecss = require("@fullhuman/postcss-purgecss");
const sass = require("postcss-node-sass");

const prodPlugins = [
  purgecss({
    content: ["./**/templates/**/*.html", "./manager/static/js/src/**/*.js"],
  }),
  cssnano({
    preset: ["default", { discardUnused: true, mergeIdents: true }],
  }),
];

module.exports = {
  syntax: "postcss-scss",
  plugins: [
    sass,
    importUrl({
      modernBrowser: true,
      resolveUrls: true,
    }),
    atImport(),
    autoprefixer,
    mqPacker(),
    ...(process.env.NODE_ENV === "production" ? prodPlugins : []),
  ],
};
