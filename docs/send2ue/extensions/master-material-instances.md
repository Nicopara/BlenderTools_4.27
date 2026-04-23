# Master Material Instances
Creates and assigns a `MaterialInstanceConstant` for imported static/skeletal mesh material slots when the corresponding
Blender material has a custom property named `unreal_master_material`.

## Blender setup
1. Open the Blender material.
2. Add a custom property:
   - Key: `unreal_master_material`
   - Value example: `/Game/Materials/M_Master_Surface`

## Import behavior
During `post_import`, for each imported mesh material slot:
- Read `unreal_master_material` from the corresponding Blender material.
- Load the master material in Unreal.
- Create or reuse a deterministic MI in the imported mesh folder (`MI_<MeshAssetName>_<MaterialName>`).
- Set the MI parent to the master material.
- Assign the MI to the matching mesh slot and save assets.

Re-importing the same mesh/material combination reuses the same MI asset path, so duplicate MI assets are not created.
