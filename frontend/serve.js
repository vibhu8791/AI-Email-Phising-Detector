import { createServer } from 'vite';

async function start() {
  const server = await createServer({
    configFile: './vite.config.js',
    server: {
      port: 5173,
      host: true
    }
  });
  await server.listen();
  server.printUrls();
  // Keep event loop alive
  setInterval(() => {}, 60000);
  if (process.stdin.resume) {
    process.stdin.resume();
  }
}

start().catch(err => {
  console.error('Failed to start Vite dev server:', err);
  process.exit(1);
});
