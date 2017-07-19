# -*- coding: utf8 -*-
# python
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {"name": "EZ Draw Pie",
            "author": "CDMJ, Spirou4D",
            "version": (1, 2),
            "blender": (2, 77, 0),
            "location": "F7 in Texture Paint Mode",
            "description": "Pie Menu for EZ Draw addon",
            "warning": "Run only in BI now",
            "wiki_url": "",
            "category": "Paint"}

import bpy
from bpy.types import   AddonPreferences,\
                        Menu,\
                        Panel,\
                        UIList,\
                        Operator
import math
import os
SEP = os.sep

#-------------------------------------------New: get the addon preferences
def get_addon_prefs_corr():
    Addons = bpy.context.user_preferences.addons
    for i in Addons:
        if Addons.find('ez_draw') != -1:
            key = 'ez_draw'
            break
        elif Addons.find('ez_draw-master') != -1:
            key = 'ez_draw-master'
            break
        else:
            return -1
    return Addons[key].preferences

def pollAPT(self, context):
    scene = context.scene
    obj =  context.active_object
    empty = scene.maincanvas_is_empty
    main_canvas_name = ""

    if not(empty):
        if scene.artist_paint is not None:
            if len(scene.artist_paint) !=0:
                for main_canvas in scene.artist_paint:
                    main_canvas_name = (main_canvas.filename)[:-4]
    else:
        return False

    if obj is not None:
        return obj.name == main_canvas_name

class canvasPopup(Operator):
    bl_idname = "ez_draw.popup"
    bl_label = "EZ Draw Popup"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        A = obj is not None
        B = context.mode == 'PAINT_TEXTURE'
        C = context.mode == 'EDIT_CURVE'
        return A and (B or C)

    def check(self, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        #"EASY_DRAW_OT_popup"
        addon_prefs = get_addon_prefs_corr()
        if addon_prefs == -1:
            print("You must install the 'EZ DRAW' Add-On, please")
            return {'FINISHED'}

        scene =context.scene
        CustomAngle  = str(addon_prefs.customAngle)
        toolsettings = context.tool_settings
        ipaint = toolsettings.image_paint
        
        stencil_text = ""
        if context.active_object is not None :
            ob = context.active_object
            if ob.type == 'MESH' and ob.data.uv_texture_stencil is not None :
                stencil_text = ob.data.uv_texture_stencil.name

        mask_V_align = scene.mask_V_align
        buttName_1 = CustomAngle +"°"
        buttName_2 = CustomAngle +"°"

        layout = self.layout
        layout.active = context.scene.UI_is_activated

        row = layout.row(align = True)
        row1 = row.split(align=True)
        row1.label(" ")
        row2 = row.split(align=True)
        if scene.game_settings.material_mode == 'GLSL':
            row2.operator("artist_paint.multitexture",
                    text='Shading', icon="RADIO")
        else:
            row2.operator("artist_paint.glsl",
                    text='Shading', icon="RENDERLAYERS")
        row2.scale_x = 0.40


        box = layout.box()
        col = box.column(align=True)
        col.label("CANVAS MASKING TOOLS")
        col.prop(ipaint, "use_stencil_layer", text="Stencil mask")
        if ipaint.use_stencil_layer:
            col.menu("VIEW3D_MT_tools_projectpaint_stencil", text=stencil_text, translate=False)
            col.template_ID(ipaint, "stencil_image", open="image.open")
            col.operator("image.new", text="New stencil").gen_context = 'PAINT_STENCIL'
            row = col.row(align = True)
            row.prop(ipaint, "stencil_color", text="")
            row.prop(ipaint, "invert_stencil",
                        text="Invert the mask",
                        icon='IMAGE_ALPHA')
        
        
        col.separator()                             #empty line
        
        row = col.row(align = True)
        row.operator("artist_paint.sculpt_duplicate", text = "Sculpt Duplicate", icon = 'COPY_ID')
        row.operator("artist_paint.sculpt_liquid", text = "Sculpt Liquid", icon = 'MOD_WAVE')
        
        col.separator()                             #empty line
        
        col.operator("artist_paint.trace_selection",
                    text = "Mask from Gpencil",
                    icon = 'OUTLINER_OB_MESH')

        col.separator()                             #empty line

        col.operator("artist_paint.curve_2dpoly",
                    text = "Make Vector Contour",
                    icon = 'PARTICLE_POINT')

        row = col.row(align = True)
        row.operator("artist_paint.curve_unwrap",
                    text = "To Mesh Mask",
                    icon = 'OUTLINER_OB_MESH')
        row.operator("artist_paint.inverted_mask",
                    text = "To Inverted Mesh Mask",
                    icon = 'MOD_TRIANGULATE')

        col.separator()                             #empty line
        
        row = col.row(align = True)                        #BOOL MASK AND REUSE
        row1 = row.split(align=True)
        row1.label(text="Bool")
        row1.scale_x = 0.30
        row2 = row.split(align=True)
        row2.operator("artist_paint.solidfy_difference", text=" Difference", icon = 'ROTACTIVE')
        row2.operator("artist_paint.solidfy_union", text=" Union", icon = 'ROTATECOLLECTION')
        row2.scale_x = 1.00
        row.separator()
        row3 = row.split(align=True)
        row3.operator("artist_paint.reproject_mask",
                          text=" Reproject", icon = 'NODE_SEL')
        row3.scale_x = 1.10
        row4 = row.split(align=True)
        row4.operator("artist_paint.remove_modifiers", icon='RECOVER_LAST')
    
        col.separator()        #ALIGNEMENT
        
        col.label("Masks Alignment")        #ALIGNEMENT
        row = col.row(align = True)        #TABLEAU
    
        row1 = row.split(align = True)                         #Column 1
        row1.scale_x = 1.00
        col1 = row1.column(align = True)
        col1.label("")
        col1.operator("object.align_left",
                          text="Left", icon = 'TRIA_LEFT_BAR')
        col1.label("")
    
    
        row2 = row.split(align = True)                         #column 2
        row2.scale_x = 1.00
        col2 = row2.column(align = True)
        col2.operator("object.align_top", text="Top", icon = 'TRIA_UP_BAR')
        if mask_V_align:
            col2.operator("object.align_hcenter",
                              text="Center V", icon = 'GRIP')
        else:
            col2.operator("object.align_center",
                              text="Center H", icon = 'PAUSE')
        col2.operator("object.align_bottom",
                          text="Bottom", icon = 'TRIA_DOWN_BAR')
        col2.operator("object.center_align_reset", icon='RECOVER_LAST')
    
    
        row3 = row.split(align = True)                         #column 3
        row3.scale_x = 1.00
        col3 = row3.column(align = True)
        col3.label("")
        col3.operator("object.align_right",
                          text="Right", icon = 'TRIA_RIGHT_BAR')
        col3.label("")
        
        col.separator()                             #empty line

        box = layout.box()                        #CANVAS FRAME CONSTRAINT
        col = box.column(align = True)
        col.label(text="CANVAS MOVEMENT")
        row = col.row(align = True)
        row1 = row.split(align=True)
        row1.label(text="Mirror")
        row1.scale_x = 0.60
        row.separator()
        row2 = row.split(align=True)
        row2.prop(ipaint, "use_symmetry_x", text="Hor.", toggle=True)
        row2.prop(ipaint, "use_symmetry_y", text="Ver.", toggle=True)
        row2.scale_x = 0.70
        row.separator()
        row3 = row.split(align=True)
        row3.operator("artist_paint.set_symmetry_origin",
                    text="New", icon='VIEW3D_VEC')
        row3.scale_x = 0.60
        row4 = row.split(align=True)
        row4.operator("artist_paint.reset_origin",
                    text="", icon='RECOVER_AUTO')

        col.separator()

        row = col.row(align = True)
        row.operator("artist_paint.canvas_horizontal",
                    text="Canvas Flip Horizontal",
                    icon='ARROW_LEFTRIGHT')
        row.operator("artist_paint.canvas_vertical",
                    text = "Canvas Flip Vertical",
                    icon = 'FILE_PARENT')


        row = col.row(align = True)                    #ROTATION
        row.label(text="Rotation")
        row.prop(context.scene, "canvas_in_frame" ,
                                    text="Frame Constraint")
        row.enabled = pollAPT(self, context)

        row = col.row(align = True)
        row.operator("artist_paint.rotate_ccw_15",
                    text = "Rotate -" + buttName_1, icon = 'TRIA_LEFT')
        row.operator("artist_paint.rotate_cw_15",
                    text = "Rotate +" + buttName_2, icon = 'TRIA_RIGHT')

        row = col.row(align = True)
        row.operator("artist_paint.rotate_ccw_90",
                    text = "Rotate 90° CCW", icon = 'PREV_KEYFRAME')
        row.operator("artist_paint.rotate_cw_90",
                    text = "Rotate 90° CW", icon = 'NEXT_KEYFRAME')

        col.operator("artist_paint.canvas_resetrot",
                    text = "Reset Rotation", icon = 'CANCEL')

#nested pie
class OperNested(Operator):
    """Tooltip"""
    bl_idname = "object.oper_nested"
    bl_label = "Operator Nested"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_PIE_drawtypes")
        return {'FINISHED'}


#------------------------------------#pie for paint2d
class VIEW3D_PIE_artistpaint(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "PAINTER"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        pie.operator("view3d.texture_popup", text='Tex Mapping', icon='TEXTURE')
        pie.operator("view3d.brush_popup", text='Paint Brush', icon='BRUSH_DATA')
        pie.operator("object.oper_nested", text='Drawtype', icon='CANCEL')
        pie.operator("ez_draw.popup", text='Canvas Control', icon='TEXTURE')
        pie.operator("view3d.projectpaint", text='Slots', icon='COLLAPSEMENU')



def register():
    bpy.utils.register_module(__name__)

    km_list = ['3D View']
    for i in km_list:
        sm = bpy.context.window_manager
        km = sm.keyconfigs.default.keymaps[i]
        kmi = km.keymap_items.new('wm.call_menu_pie', 'F7', 'PRESS')
        kmi.properties.name = "VIEW3D_PIE_artistpaint"



def unregister():
    bpy.utils.unregister_module(__name__)

    km_list = ['3D View']
    for i in km_list:
        sm = bpy.context.window_manager
        km = sm.keyconfigs.default.keymaps[i]
        for kmi in (kmi for kmi in km.keymap_items \
                            if (kmi.idname == "VIEW3D_PIE_artistpaint")):
            km.keymap_items.remove(kmi)



if __name__ == "__main__":
    register()
