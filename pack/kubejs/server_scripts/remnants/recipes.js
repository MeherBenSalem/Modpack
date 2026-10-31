// Recipe clashes between the pack's mods. Two shaped recipes with the same grid make the crafting table hand out
// only one of the results, so the duplicate goes or gets a grid of its own.
//
// Sprout & Soil 1.0.0:
// - its beetroot, carrot and potato crates use Farmer's Delight's exact grids; Farmer's Delight's crates stay
//   (they are in older worlds already), and Sprout & Soil's crates still unpack into their crops.
// - its sprinkler uses Better Farming++'s exact grid (copper around a bucket). Better Farming++ keeps that one
//   (the Hearth and Harvest quests use it); Sprout & Soil's sprinkler is copper around its watering can.

ServerEvents.recipes(function (event) {
  ['beetroot_crate', 'carrot_crate', 'potato_crate'].forEach(function (crate) {
    event.remove({ id: 'sprout_and_soil:' + crate })
  })
  event.remove({ id: 'sprout_and_soil:sprinkler' })
  event.shaped('sprout_and_soil:sprinkler', [' C ', 'CWC', ' C '], {
    C: 'minecraft:copper_ingot',
    W: 'sprout_and_soil:watering_can'
  }).id('remnants:sprout_and_soil/sprinkler')
})
