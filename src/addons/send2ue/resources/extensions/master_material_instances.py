# Copyright Epic Games, Inc. All Rights Reserved.

import re
import bpy
from send2ue.constants import UnrealTypes, RegexPresets
from send2ue.core.extension import ExtensionBase
from send2ue.dependencies.unreal import UnrealRemoteCalls as UnrealCalls
from send2ue.dependencies.rpc.factory import make_remote


class MasterMaterialInstancesExtension(ExtensionBase):
    name = 'master_material_instances'
    property_key = 'unreal_master_material'

    @staticmethod
    def get_material_instance_path(mesh_asset_path, material_name, slot_index):
        """
        Builds a deterministic material instance asset path for a mesh + material name pair.

        :param str mesh_asset_path: The unreal project path to the imported mesh.
        :param str material_name: The blender material name.
        :param int slot_index: The material slot index on the mesh.
        :return str: The material instance asset path.
        """
        material_name = material_name.strip()
        material_asset_name = re.sub(
            RegexPresets.INVALID_NAME_CHARACTERS,
            '_',
            material_name
        )
        if not material_asset_name:
            material_asset_name = f'Material_{slot_index}'

        if '/' in mesh_asset_path:
            mesh_folder_path, mesh_asset_name = mesh_asset_path.rsplit('/', 1)
        else:
            mesh_folder_path = '/Game'
            mesh_asset_name = mesh_asset_path.strip('/') or f'Mesh_{slot_index}'
        return f'{mesh_folder_path}/MI_{mesh_asset_name}_{material_asset_name}'

    def post_import(self, asset_data, properties):
        """
        Creates/reuses and assigns material instances based on per-material master material references.

        :param dict asset_data: A mutable dictionary of asset data for the current asset.
        :param Send2UeSceneProperties properties: The scene property group that contains all the addon properties.
        """
        if asset_data.get('_asset_type') not in [UnrealTypes.STATIC_MESH, UnrealTypes.SKELETAL_MESH]:
            return

        mesh_asset_path = asset_data.get('asset_path')
        mesh_object = bpy.data.objects.get(asset_data.get('_mesh_object_name'))
        if not mesh_asset_path or not mesh_object:
            return

        unreal_calls = make_remote(UnrealCalls)
        for slot_index, material_slot in enumerate(mesh_object.material_slots):
            blender_material = material_slot.material
            if not blender_material:
                continue

            master_material_path = blender_material.get(self.property_key)
            if not isinstance(master_material_path, str):
                continue

            master_material_path = master_material_path.strip()
            if not master_material_path:
                continue

            material_instance_path = self.get_material_instance_path(
                mesh_asset_path,
                blender_material.name,
                slot_index
            )
            unreal_calls.create_or_update_material_instance_asset(
                mesh_asset_path,
                slot_index,
                master_material_path,
                material_instance_path
            )
