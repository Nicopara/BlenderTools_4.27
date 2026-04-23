# Assign Master Material Instances

This extension creates and assigns Unreal `MaterialInstanceConstant` assets after mesh import.

## Blender Material Metadata

Set custom properties on your Blender materials:

- `unreal_master_material` (required)
  - Unreal asset path to the master material.
  - Example: `/Game/Materials/M_Master_Surface`
- `unreal_material_instance_name` (optional)
  - Overrides the generated material instance asset name.

If `unreal_material_instance_name` is not provided, the extension uses a deterministic name:

- `MI_<BlenderMaterialName>`

Invalid Unreal characters are replaced with `_`.

## Import Behavior

For each imported static or skeletal mesh slot:

1. Read the Blender material assigned to that slot.
2. If `unreal_master_material` is set, create or reuse a material instance.
3. Set the material instance parent to the specified master material.
4. Assign the material instance to the corresponding imported mesh slot.

Created/updated material instances and meshes are saved in Unreal.

## Material Instance Location

Extension setting:

- `Material instance folder` (optional)
  - If set, this folder is used for generated material instances.
  - If empty, instances are created next to the imported mesh asset.
