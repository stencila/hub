const express = require('express')
const fs = require('fs')
const darServer = require('dar-server')
const multer = require('multer')
const mkdirp = require('mkdirp')
const path = require('path')
const rimraf = require('rimraf')

const port = 4000
const url = `http://localhost:${port}`
const storage = path.join(__dirname, 'storage')

const app = express()

// HTML served in development
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path === '/edit' || req.path === '/edit/') return res.sendFile(indexFile)
  next()
})

// In development, serve CSS and JS from local filesystem
// In production, this is served from elsewhere (e.g. a Google Storage bucket)
app.use('/edit/static', express.static(path.join(__dirname, 'static')))

// Provide endpoints to create (POST) DARs
// Currently, creating DARs is not provided by darServer so
// we implement that here
const upload = multer({
	storage: multer.diskStorage({
    destination: function (req, file, cb) {
      const dest = path.join(storage, req.params.id)
      if (fs.existsSync()) rimraf.sync(dest)
      mkdirp.sync(dest)
      cb(null, dest)
    },
    filename: function (req, file, cb) {
      cb(null, file.originalname)
    }
  })
})
app.post('/edit/storage/:id', upload.any(), (req, res) => {
	res.send()
})

// Provide endpoints to read (GET) and write (PUT) DARs
darServer.serve(app, {
  port,
  serverUrl: url,
  apiUrl: '/edit/storage',
  rootDir: storage
})

app.listen(port, () => {
  console.log(`Serving at ${url}/edit`)
})
