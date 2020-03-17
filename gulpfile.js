const gulp = require('gulp')
const sass = require('gulp-sass')
const autoprefixer = require('gulp-autoprefixer')
const moduleImporter = require('sass-module-importer')

const sassOptions = {
    errLogToConsole: true,
    outputStyle: 'expanded',
    sourceMap: true,
    importer: moduleImporter()
}

sass.compiler = require('node-sass')

const sassDev = function() {
  return gulp.src([
    './node_modules/@stencila/style/sass/**/*.sass',
    './director/assets/sass/**/*.sass'
  ])
  .pipe(sass(sassOptions).on('error', sass.logError))
  .pipe(autoprefixer())
  .pipe(gulp.dest('./director/assets/css'))
}

const sassBuild = function() {
  let options = sassOptions
  options['outputStyle'] = 'collapsed'
  
  return gulp.src([
    './node_modules/@stencila/style/sass/**/*.sass',
    './director/assets/sass/**/*.sass'
  ])
  .pipe(sass(sassOptions).on('error', sass.logError))
  .pipe(autoprefixer())
  .pipe(gulp.dest('./director/assets/css'))
}

const watch = function(done) {
    gulp.watch('./node_modules/@stencila/style/sass/**/*.sass', { ignoreInitial: false }, gulp.series(sassDev))
    gulp.watch('./director/assets/sass/**/*.sass', { ignoreInitial: false }, gulp.series(sassDev))
    done()
};

exports.build = sassBuild
exports.default = watch
exports.watch = watch
