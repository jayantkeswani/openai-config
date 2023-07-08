const { loadSKUConfig } = require('../../../lib/helper')

const list = loadSKUConfig(__dirname, 'pnp-za.list.sku.json')
const detail = loadSKUConfig(__dirname, 'pnp-za.detail.sku.json')
const parsed = require('./pnp-za.parsed.json')

const homeCarousel = require('./banners/pnp-za.home-carousel.banner.json')

list.parsed = parsed
detail.parsed = parsed

module.exports = {
  category: { sku: list },
  search: { sku: list },
  detail: { sku: detail },
  home: {
    banners: [
      homeCarousel,
    ]
  },
  store: { sku: list }
}