const express = require('express')
const fs = require('fs')
const darServer = require('dar-server')
const multer = require('multer')
const mkdirp = require('mkdirp')
const path = require('path')
const rimraf = require('rimraf')

const PORT = 4000
const HOST = `http://localhost:${PORT}`
const PATH = '/edit/textilla'
const STATIC = path.join(__dirname, 'static')
const DARS = path.join(__dirname, 'dars')

const app = express()

// HTML served in development
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path === PATH || req.path === `${PATH}/`) return res.sendFile(indexFile)
  next()
})

// In development, serve CSS and JS from local filesystem
// In production, this is served from elsewhere (e.g. a Google Storage bucket)
app.use(`${PATH}/static`, express.static(STATIC))

// Provide endpoints to create (POST) DARs
// Currently, creating DARs is not provided by darServer so
// we implement that here
const upload = multer({
	storage: multer.diskStorage({
    destination: function (req, file, cb) {
      const dest = path.join(DARS, req.params.id)
      if (fs.existsSync()) rimraf.sync(dest)
      mkdirp.sync(dest)
      cb(null, dest)
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname)
    }
  })
})
app.post(`${PATH}/dars/:id`, upload.any(), (req, res) => {
	res.send()
})

// Provide endpoints to read (GET) and write (PUT) DARs
darServer.serve(app, {
  port: PORT,
  serverUrl: HOST,
  apiUrl: `${PATH}/dars`,
  rootDir: DARS
})

app.listen(PORT, () => {
  console.log(`Serving at ${HOST}${PATH}`)
})
