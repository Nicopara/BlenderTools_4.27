# Copyright Epic Games, Inc. All Rights Reserved.

import re
import bpy
from send2ue.constants import RegexPresets, UnrealTypes
from send2ue.core.extension import ExtensionBase
from send2ue.dependencies.unreal import UnrealRemoteCalls as UnrealCalls
from send2ue.dependencies.rpc.factory import make_remote


class AssignMasterMaterialInstancesExtension(ExtensionBase):
    name = 'assign_master_material_instances'

    material_instance_folder: bpy.props.StringProperty(
        name='Material instance folder',
        default='',
        description=(
            'Optional Unreal folder path for generated material instances. '
            'If empty, material instances are created next to the imported mesh asset.'
        )
    )

    @staticmethod
    def _get_material_instance_name(material):
        override_name = material.get('unreal_material_instance_name')
        if isinstance(override_name, str) and override_name.strip():
            material_instance_name = override_name.strip()
        else:
            material_instance_name = f'MI_{material.name.strip()}'

        return re.sub(RegexPresets.INVALID_NAME_CHARACTERS, "_", material_instance_name)

    @staticmethod
    def _normalize_folder_path(folder_path):
        normalized_path = (folder_path or '').strip().replace('\\', '/')
        if not normalized_path:
            return ''
        return normalized_path if normalized_path.endswith('/') else f'{normalized_path}/'

    def _get_material_instance_asset_path(self, asset_data, material):
        material_instance_name = self._get_material_instance_name(material)
        if not material_instance_name:
            return None

        folder_path = self._normalize_folder_path(self.material_instance_folder)
        if not folder_path:
            folder_path = self._normalize_folder_path(asset_data.get('asset_folder'))
        if not folder_path:
            asset_path = asset_data.get('asset_path', '')
            folder_path = self._normalize_folder_path(asset_path.rsplit('/', 1)[0])

        return f'{folder_path}{material_instance_name}' if folder_path else None

    def post_import(self, asset_data, properties):
        """
        Defines the post import logic that creates and assigns material instances from blender material metadata.

        :param dict asset_data: A mutable dictionary of asset data for the current asset.
        :param Send2UeSceneProperties properties: The scene property group that contains all the addon properties.
        """
        if asset_data.get('skip'):
            return

        if asset_data.get('_asset_type') not in [UnrealTypes.STATIC_MESH, UnrealTypes.SKELETAL_MESH]:
            return

        mesh_object = bpy.data.objects.get(asset_data.get('_mesh_object_name'))
        if not mesh_object:
            return

        mesh_asset_path = asset_data.get('asset_path')
        if not mesh_asset_path:
            return

        unreal_remote_calls = make_remote(UnrealCalls)

        for index, slot in enumerate(mesh_object.material_slots):
            material = slot.material
            if not material:
                continue

            master_material_path = material.get('unreal_master_material')
            if not isinstance(master_material_path, str) or not master_material_path.strip():
                continue

            material_instance_asset_path = self._get_material_instance_asset_path(asset_data, material)
            if not material_instance_asset_path:
                continue

            unreal_remote_calls.assign_material_instance_to_mesh_slot(
                mesh_asset_path=mesh_asset_path,
                slot_index=index,
                material_instance_asset_path=material_instance_asset_path,
                master_material_asset_path=master_material_path.strip()
            )

    def draw_paths(self, dialog, layout, properties):
        """
        Draws an interface for material instance assignment options in the paths tab.

        :param Send2UnrealDialog dialog: The dialog class.
        :param bpy.types.UILayout layout: The extension layout area.
        :param Send2UeSceneProperties properties: The scene property group that contains all the addon properties.
        """
        box = layout.box()
        box.label(text='Assign master material instances:')
        dialog.draw_property(self, box, 'material_instance_folder')
