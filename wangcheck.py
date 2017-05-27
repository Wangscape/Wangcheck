from jsonschema import validate, Draft4Validator, ValidationError
from json import load, JSONDecodeError
from os import path
import sys

class Wangcheck(object):
  def __init__(self, config_dir, options_fn, schema_dir):
    self.config_dir = config_dir
    self.options_fn = options_fn
    self.schema_dir = schema_dir
  def config_file_path(self, filename):
    return path.join(self.config_dir, filename)
  def schema_file_path(self, filename):
    return path.join(self.schema_dir, filename)
  def output_file_path(self, filename):
    return path.join(self.config_file_path(self.options['OutputDirectory']), filename)
  def loadf(self, fn):
    with open(fn) as f:
      return load(f)
  def load_schemas(self):
    self.schema_options = self.loadf(self.schema_file_path('options_schema.json'))
    self.schema_module_group = self.loadf(self.schema_file_path('module_group_schema.json'))
    self.schema_tiles = self.loadf(self.schema_file_path('tiles_schema.json'))
    self.schema_tilesets = self.loadf(self.schema_file_path('tilesets_schema.json'))
    self.schema_tile_groups = self.loadf(self.schema_file_path('tile_groups_schema.json'))
    self.schema_terrain_hypergraph = self.loadf(self.schema_file_path('terrain_hypergraph_schema.json'))
  def load_options(self):
    self.options = self.loadf(self.config_file_path(self.options_fn))
  def load_module_groups(self):
    self.combiner_module_group = self.loadf(self.config_file_path(self.options['CombinerModuleGroup']))
    self.source_modules = {}
    if 'DefaultModuleGroup' in self.options:
      mg_default = self.options['DefaultModuleGroup']
      self.source_modules[mg_default] = self.loadf(self.config_file_path(mg_default))
    for mg_type in [
      'TopBorderModuleGroups',
      'LeftBorderModuleGroups',
      'CentralBorderModuleGroups']:
      if mg_type not in self.options:
        continue
      for mg in self.options[mg_type]:
        mg_fn = mg['Filename']
        if mg_fn not in self.source_modules:
          try:
            self.source_modules[mg_fn] = self.loadf(self.config_file_path(mg_fn))
          except JSONDecodeError:
            print("Error in {0}:\n".format(mg_fn))
            raise
  def check_schemas(self):
    for schema in [
      self.schema_options,
      self.schema_module_group,
      self.schema_tiles,
      self.schema_tilesets,
      self.schema_tile_groups,
      self.schema_terrain_hypergraph
    ]:
      Draft4Validator.check_schema(schema)
  def check_options(self):
    validate(self.options, self.schema_options)
  def check_module_groups(self):
    validate(self.combiner_module_group, self.schema_module_group)
    if 'inputmodules' not in self.combiner_module_group:
      print("Warning: combiner module group requires three input modules")
    for fn, mg in self.source_modules.items():
      try:
        validate(mg, self.schema_module_group)
      except ValidationError:
        print('Error in {0}:\n'.format(fn))
        raise
  def check_images(self):
    for terrain in self.options['Terrains'].values():
      filename = terrain['FileName']
      assert path.exists(self.config_file_path(filename)),"Image not found: {0}\n".format(filename)
  def load_metaoutput(self):
    tiles_fn = self.output_file_path(self.options['MetaOutput']['TileData'])
    tile_groups_fn = self.output_file_path(self.options['MetaOutput']['TileGroups'])
    tilesets_fn = self.output_file_path(self.options['MetaOutput']['TilesetData'])
    terrain_hypergraph_fn = self.output_file_path(self.options['MetaOutput']['TerrainHypergraph'])
    if path.exists(tiles_fn):
      self.tiles = self.loadf(tiles_fn)
    if path.exists(tile_groups_fn):
      self.tile_groups = self.loadf(tile_groups_fn)
    if path.exists(tilesets_fn):
      self.tilesets = self.loadf(tilesets_fn)
    if path.exists(terrain_hypergraph_fn):
      self.terrain_hypergraph = self.loadf(terrain_hypergraph_fn)
  def check_metaoutput(self):
    if hasattr(self, 'tiles'):
      validate(self.tiles, self.schema_tiles)
    if hasattr(self, 'tile_groups'):
      validate(self.tile_groups, self.schema_tile_groups)
    if hasattr(self, 'tilesets'):
      validate(self.tilesets, self.schema_tilesets)
    if hasattr(self, 'terrain_hypergraph'):
      validate(self.terrain_hypergraph, self.schema_terrain_hypergraph)
  def check_all(self):
    self.load_schemas()
    self.check_schemas()
    self.load_options()
    self.check_options()
    self.load_module_groups()
    self.check_module_groups()
    self.check_images()
    self.load_metaoutput()
    self.check_metaoutput()
def print_usage():
  print("Usage: python wangcheck.py path/to/options.json path/to/Wangscape/doc/schemas")

if __name__ == '__main__':
  try:
    _, options_path, schema_dir = sys.argv
  except ValueError:
    print_usage()
    raise
  config_dir, options_fn = path.split(options_path)
  wc = Wangcheck(config_dir, options_fn, schema_dir)
  wc.check_all()