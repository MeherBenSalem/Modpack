// priority: -1000
// DEV ONLY. Never shipped: tools/dump_live.py copies this into the test server's kubejs/server_scripts/ for one boot.
// When the server has finished loading it writes what the game REALLY registered, after every mod, datapack and
// KubeJS script has had its say, to kubejs/exported/live/*.json: ids of items, blocks, entities, advancements,
// structures, biomes, dimensions and loot tables, every tag's members, the command roots, and every recipe, loot
// table and worldgen feature as JSON (through the game's own codecs, so KubeJS's added, removed and rebuilt recipes
// and every datapack override are exactly what a player gets).

ServerEvents.loaded(function (event) {
  var server = event.server
  var BuiltInRegistries = Java.loadClass('net.minecraft.core.registries.BuiltInRegistries')
  var Registries = Java.loadClass('net.minecraft.core.registries.Registries')
  var JsonOps = Java.loadClass('com.mojang.serialization.JsonOps')
  var Recipe = Java.loadClass('net.minecraft.world.item.crafting.Recipe')
  var access = server.registryAccess()
  var out = 'kubejs/exported/live/'

  function keys(registry) {
    var ids = []
    registry.keySet().forEach(function (k) { ids.push(String(k)) })
    ids.sort()
    return ids
  }
  function tags(registry) {
    var result = {}
    registry.getTags().forEach(function (pair) {
      var members = []
      pair.getSecond().forEach(function (holder) {
        var key = holder.unwrapKey()
        if (key.isPresent()) members.push(String(key.get().location()))
      })
      members.sort()
      result[String(pair.getFirst().location())] = members
    })
    return result
  }

  var ids = {
    item: keys(BuiltInRegistries.ITEM),
    block: keys(BuiltInRegistries.BLOCK),
    entity_type: keys(BuiltInRegistries.ENTITY_TYPE),
    structure: keys(access.registryOrThrow(Registries.STRUCTURE)),
    biome: keys(access.registryOrThrow(Registries.BIOME)),
    dimension: [],
    advancement: [],
    loot_table: [],
    command: []
  }
  server.levelKeys().forEach(function (k) { ids.dimension.push(String(k.location())) })
  server.getAdvancements().getAllAdvancements().forEach(function (holder) { ids.advancement.push(String(holder.id())) })
  server.reloadableRegistries().getKeys(Registries.LOOT_TABLE).forEach(function (k) { ids.loot_table.push(String(k)) })
  server.getCommands().getDispatcher().getRoot().getChildren().forEach(function (node) { ids.command.push(String(node.getName())) })
  Object.keys(ids).forEach(function (k) { ids[k].sort() })
  JsonIO.write(out + 'ids.json', ids)

  JsonIO.write(out + 'tags.json', {
    item: tags(BuiltInRegistries.ITEM),
    block: tags(BuiltInRegistries.BLOCK),
    entity_type: tags(BuiltInRegistries.ENTITY_TYPE),
    structure: tags(access.registryOrThrow(Registries.STRUCTURE)),
    biome: tags(access.registryOrThrow(Registries.BIOME))
  })

  // Recipes, one JSON text per id. Written as strings: Rhino would otherwise have to rebuild 6,000 objects.
  var ops = access.createSerializationContext(JsonOps.INSTANCE)
  var recipes = {}
  var failed = []
  server.getRecipeManager().getRecipes().forEach(function (holder) {
    var id = String(holder.id())
    try {
      recipes[id] = String(Recipe.CODEC.encodeStart(ops, holder.value()).getOrThrow())
    } catch (e) {
      failed.push(id)
    }
  })
  JsonIO.write(out + 'recipes.json', recipes)

  // Loot tables and configured features (which blocks the world generates), the same way.
  function encodeAll(registry, codec, into) {
    registry.entrySet().forEach(function (entry) {
      var id = String(entry.getKey().location())
      try {
        into[id] = String(codec.encodeStart(ops, entry.getValue()).getOrThrow())
      } catch (e) {
        failed.push(id)
      }
    })
  }
  var LootTable = Java.loadClass('net.minecraft.world.level.storage.loot.LootTable')
  var ConfiguredFeature = Java.loadClass('net.minecraft.world.level.levelgen.feature.ConfiguredFeature')
  var loot = {}
  encodeAll(server.reloadableRegistries().get().registryOrThrow(Registries.LOOT_TABLE), LootTable.DIRECT_CODEC, loot)
  JsonIO.write(out + 'loot.json', loot)
  var features = {}
  encodeAll(access.registryOrThrow(Registries.CONFIGURED_FEATURE), ConfiguredFeature.DIRECT_CODEC, features)
  JsonIO.write(out + 'features.json', features)

  JsonIO.write(out + 'done.json', { recipes: Object.keys(recipes).length, loot: Object.keys(loot).length, features: Object.keys(features).length, failed: failed })
  console.info('[dump_live] wrote ' + Object.keys(recipes).length + ' recipes, ' + Object.keys(loot).length + ' loot tables, ' + ids.item.length + ' items; ' + failed.length + ' entries could not be encoded')
})
