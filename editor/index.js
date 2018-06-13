const express = require('express')
const darServer = require('dar-server')
const path = require('path')

const port = 4000
const url = `http://localhost:${port}`

const app = express()

// In development, serve the editor application HTML, CSS and JS
// In production, this is served from elsewhere (e.g. a Google Storage bucket)
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path == '/') return res.sendFile(indexFile)
  next()
})

const staticDir = path.join(__dirname, 'node_modules/stencila/dist')
app.use('/static', express.static(staticDir))

// Provide read (GET) and write (PUT) of DARs in the `storage` directory 
const storageDir = path.join(__dirname, 'storage')
darServer.serve(app, {
  port,
  serverUrl: url,
  apiUrl: '/storage',
  rootDir: storageDir
})

app.listen(port, () => {
  console.log(`Serving at ${url}`)
})
