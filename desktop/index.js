const darServer = require('dar-server')
const express = require('express')
const fs = require('fs')
const jwt = require('express-jwt')
const mkdirp = require('mkdirp')
const path = require('path')

const PORT = 4000
const HOST = `http://localhost:${PORT}`
const PATH = '/desktop'
const STATIC = path.join(__dirname, 'static')

const PROJECTS = path.join(__dirname, 'projects')
const DARS = path.join(__dirname, 'dars')

let JWT_SECRET = process.env.JWT_SECRET
if (!JWT_SECRET) throw Error('JWT_SECRET environment variable must be set')

const app = express()

// Index page
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path === PATH || req.path === `${PATH}/`) return res.sendFile(indexFile)
  next()
})

// CSS and JS
app.use(`${PATH}/static`, express.static(STATIC))

// Middleware to check authorization and create a symlink in the `dars` folder.
// This symlink is necessary because `dar-serve` does not yet handle
// DARs in sub-folders so we have to elevate to the top level somewhere.
app.all(`${PATH}/dars/(:token)`, 
  jwt({
    secret: JWT_SECRET,
    credentialsRequired: false,
    getToken: req => req.params.token
  }),
  (req, res, next) => {
    const file = req.user.path
    const token = req.params.token
    try {
      fs.lstatSync(path.join(DARS, token))
    } catch (err) {
      mkdirp.sync(DARS)
      const dir = path.basename(file) === 'manifest.xml' ? path.dirname(file) : file
      fs.symlinkSync(path.join(PROJECTS, dir), path.join(DARS, token))
    }
    next()
  }
)

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
