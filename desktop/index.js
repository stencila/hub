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

// Initialization endpoint to check JWT and create a symlink in the `dars` folder.
// This is necessary because `dar-serve` does not yet handle
// DARs in sub-folders so we have to elevate to the top level somewhere.
app.get(`${PATH}/init`,
  jwt({
    secret: JWT_SECRET,
    credentialsRequired: false,
    getToken: function fromHeaderOrQuerystring (req) {
      if (req.headers.authorization && req.headers.authorization.split(' ')[0] === 'Bearer') {
          return req.headers.authorization.split(' ')[1];
      } else if (req.query && req.query.token) {
        return req.query.token;
      }
      return null;
    }
  }),
  (req, res) => {
    // Check the token is correct for the DAR path requested
    const path_ = req.query.path
    const token = req.query.token
    if (req.user.path !== path_) {
      return res.sendStatus(401)
    }
    // OK, so create a link to the DAR that the editor can use
    // to talk to the dar-serve. Currently the link is the token.
    if (!fs.existsSync(path.join(DARS, token))) {
      mkdirp.sync(DARS)
      fs.symlinkSync(path.join(PROJECTS, path_), path.join(DARS, token))
    }
    res.send(token)
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
