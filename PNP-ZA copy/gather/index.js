const { loadGatherConfig } = require('../../../lib/helper')

const category = loadGatherConfig(__dirname, 'pnp-za.category.gather.json')
const search = loadGatherConfig(__dirname, 'pnp-za.search.gather.json')
const detail = loadGatherConfig(__dirname, 'pnp-za.detail.gather.json')
const home = loadGatherConfig(__dirname, 'pnp-za.home.gather.json')
const store = loadGatherConfig(__dirname, 'pnp-za.store.gather.json')

module.exports = {
  category,
  search,
  detail,
  home,
  store
}