// AV1技术夹具：临时本地静态宿主与模拟私人响应，不接业务服务。
const fs = require('node:fs/promises')
const http = require('node:http')
const path = require('node:path')
const assert = require('node:assert/strict')
const { chromium } = require('playwright')

async function main() {
  const publicRoot = path.resolve(process.argv[2])
  const resultFile = process.argv[3]
  const privateMarker = 'AV1_RUNTIME_ONLY_PRIVATE_7C03'
  const files = []
  async function scan(folder) {
    for (const entry of await fs.readdir(folder, { withFileTypes: true })) {
      const target = path.join(folder, entry.name)
      if (entry.isDirectory()) await scan(target)
      else {
        const data = await fs.readFile(target)
        assert(!data.includes(Buffer.from(privateMarker)), `private marker leaked: ${target}`)
        files.push({ path: path.relative(publicRoot, target), bytes: data.length })
      }
    }
  }
  await scan(publicRoot)
  assert((await fs.readFile(path.join(publicRoot, 'index.html'), 'utf8')).includes('AV1_PUBLIC_HOME'))
  assert((await fs.readFile(path.join(publicRoot, 'games/fixture/index.html'), 'utf8')).includes('AV1_PUBLIC_GAME'))
  const accountHtml = await fs.readFile(path.join(publicRoot, 'account/index.html'), 'utf8')
  assert(!accountHtml.includes('AV1_PRIVATE_SHELL'), 'private page body unexpectedly prerendered')
  const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json',
    '.html': 'text/html; charset=utf-8', '.css': 'text/css' }
  const server = http.createServer(async (request, response) => {
    try {
      const urlPath = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
      if (urlPath === '/__av1_private') {
        response.writeHead(401, { 'content-type': 'application/json', 'cache-control': 'no-store' })
        response.end('{"error":"fixture unauthenticated"}')
        return
      }
      const full = path.resolve(publicRoot, '.' + urlPath)
      if (!full.startsWith(publicRoot + path.sep) && full !== publicRoot) {
        response.writeHead(403); response.end(); return
      }
      let candidate = full
      const stat = await fs.stat(candidate).catch(() => null)
      if (stat?.isDirectory()) candidate = path.join(candidate, 'index.html')
      const bytes = await fs.readFile(candidate).catch(() => null)
      if (bytes) {
        response.writeHead(200, { 'content-type': types[path.extname(candidate)] || 'application/octet-stream' })
        response.end(bytes)
      } else {
        response.writeHead(404, { 'content-type': 'text/html; charset=utf-8' })
        response.end(await fs.readFile(path.join(publicRoot, '404.html')))
      }
    } catch { response.writeHead(500); response.end() }
  })
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  const base = 'http://127.0.0.1:' + server.address().port
  let browser
  const result = { status: 'running', host: 'temporary strict static host on 127.0.0.1',
    limits: 'fixture only; HTTP status is a host rule, not automatic Nuxt deployment behavior',
    files, routes: [], pageErrors: [], consoleWarningsAndErrors: [] }
  try {
    for (const route of ['/', '/games/fixture/', '/account/', '/not-present/', '/games/not-present/']) {
      const response = await fetch(base + route)
      const expected = route.includes('not-present') ? 404 : 200
      assert.equal(response.status, expected, route)
      result.routes.push({ path: route, status: response.status })
    }
    browser = await chromium.launch({ headless: true,
      ...(process.env.AV1_BROWSER_EXECUTABLE ? { executablePath: process.env.AV1_BROWSER_EXECUTABLE } : {}) })
    const page = await browser.newPage()
    page.on('pageerror', error => result.pageErrors.push(error.message))
    page.on('console', message => {
      if (message.type() === 'warning' || message.type() === 'error') {
        result.consoleWarningsAndErrors.push({ type: message.type(), text: message.text() })
      }
    })
    await page.goto(base)
    await page.getByRole('heading', { name: 'AV1_PUBLIC_HOME' }).waitFor()
    await page.waitForFunction(() => !!document.querySelector('#__nuxt')?.__vue_app__)
    const documentMarker = 'av1-document-' + Date.now()
    await page.evaluate(value => { window.__av1DocumentMarker = value }, documentMarker)
    await page.getByRole('link', { name: 'Public fixture' }).click()
    await page.getByRole('heading', { name: 'AV1_PUBLIC_GAME' }).waitFor()
    assert.equal(await page.evaluate(() => window.__av1DocumentMarker), documentMarker,
      'public navigation reloaded the document')
    await page.goto(base + '/account/')
    await page.getByText('AV1_PRIVATE_SHELL', { exact: true }).waitFor()
    await page.route('**/__av1_private', route => route.fulfill({
      status: 200, contentType: 'application/json', body: JSON.stringify({ message: privateMarker })
    }))
    await page.reload()
    await page.getByText(privateMarker, { exact: true }).waitFor()
    await page.unroute('**/__av1_private')
    await page.reload()
    await page.getByText('AV1_PRIVATE_SHELL', { exact: true }).waitFor()
    assert(!(await page.locator('body').innerText()).includes(privateMarker))
    const response = await page.goto(base + '/not-present/')
    assert.equal(response.status(), 404)
    await page.getByText('Page not found', { exact: false }).first().waitFor()
    assert.deepEqual(result.pageErrors, [])
    assert(!result.consoleWarningsAndErrors.some(message => /hydration|mismatch/i.test(message.text)),
      'hydration diagnostic observed')
    result.status = 'passed'
    result.checks = ['public prerender', 'private HTML shell', 'runtime response simulated',
      'fresh navigation clears simulated private state', 'static output excludes private marker',
      'HTTP 404 for missing routes', 'Nuxt mount observed and public navigation retains document',
      'no hydration mismatch diagnostic observed']
  } catch (error) {
    result.status = 'failed'
    result.error = error.stack
    process.exitCode = 1
  } finally {
    if (browser) await browser.close()
    await new Promise(resolve => server.close(resolve))
    result.serverClosed = true
    await fs.writeFile(resultFile, JSON.stringify(result, null, 2) + '\n')
    console.log(JSON.stringify({ status: result.status, routes: result.routes,
      pageErrors: result.pageErrors, serverClosed: result.serverClosed, error: result.error }))
  }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
