const gulp = require("gulp");
const sass = require("gulp-sass");
const autoprefixer = require("gulp-autoprefixer");
const moduleImporter = require("sass-module-importer");

const sassOptions = {
  errLogToConsole: true,
  outputStyle: "expanded",
  sourceMap: true,
  importer: moduleImporter(),
};

sass.compiler = require("node-sass");

const dest = "./director/assets/css";

const sassBuild = function (overrides = {}) {
  return gulp
    .src([
      "./director/assets/style/**/*.sass",
      "./director/assets/sass/**/*.sass",
    ])
    .pipe(sass({ ...sassOptions, ...overrides }).on("error", sass.logError))
    .pipe(autoprefixer())
    .pipe(gulp.dest(dest));
};

const watch = function (done) {
  gulp.watch(
    "./director/assets/style/**/*.sass",
    { ignoreInitial: false },
    gulp.series(sassBuild)
  );
  gulp.watch(
    "./director/assets/sass/**/*.sass",
    { ignoreInitial: false },
    gulp.series(sassBuild)
  );
  done();
};

exports.build = () => sassBuild({ outputStyle: "compressed" });
exports.default = watch;
exports.watch = watch;
