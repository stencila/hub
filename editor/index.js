const express = require('express')
const darServer = require('dar-server')
const path = require('path')

const port = 4000
const url = `http://localhost:${port}`

const app = express()

// HTML served in development
const indexFile = path.join(__dirname, 'index.html')
app.use('/', function (req, res, next) {
  if(req.path == '/') return res.sendFile(indexFile)
  next()
})

// In development, serve CSS and JS from local filesystem
// In production, this is served from elsewhere (e.g. a Google Storage bucket)
app.use('/static', express.static(path.join(__dirname, 'static')))

// Provide read (GET) and write (PUT) of DARs in the `storage` directory 
darServer.serve(app, {
  port,
  serverUrl: url,
  apiUrl: '/storage',
  rootDir: path.join(__dirname, 'storage')
})

app.listen(port, () => {
  console.log(`Serving at ${url}`)
})
