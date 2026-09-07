// Load the http module to create an HTTP server.
const http = require('http');

// Configure the HTTP server to respond with "Hello, World!" to all requests.
const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, World!\n');
});

// The server listens on port 3000.
const port = 3000;
server.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});