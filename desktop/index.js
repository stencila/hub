const express = require('express')
const fs = require('fs')
const darServer = require('dar-server')
const mkdirp = require('mkdirp')
const path = require('path')

const PORT = 4000
const HOST = `http://localhost:${PORT}`
const PATH = '/desktop'
const STATIC = path.join(__dirname, 'static')

const PROJECTS = path.join(__dirname, 'projects')
const DARS = path.join(__dirname, 'dars')

const app = express()

// Index page
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path === PATH || req.path === `${PATH}/`) return res.sendFile(indexFile)
  next()
})

// CSS and JS
app.use(`${PATH}/static`, express.static(STATIC))

// Initialization endpoint to check JWT and create a symlink in the `dars` folder.
// This is necessary because `dar-serve` does not yet handle
// DARs in sub-folders so we have to elevate to the top level somewhere.
app.get(`${PATH}/init/*`, (req, res) => {
  const pathToDar = req.params[0]
  const linkToDar = pathToDar.replace('/', '-')
  if (!fs.existsSync(linkToDar)) {
    mkdirp.sync(DARS)
    fs.symlinkSync(path.join(PROJECTS, pathToDar), path.join(DARS, linkToDar))
  }
  res.send(linkToDar)
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
