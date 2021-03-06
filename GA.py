import bpy, bmesh, time, random
from bpy.types import Operator

from .GA_shader import DEF_pointinessShader_add 
from .GA_shader import DEF_ambientocclusionShader_add
from .GA_shader import DEF_albedoShader_add
from .GA_shader import DEF_normalShader_add 
from .GA_shader import DEF_pbrShader_add 
from .GA_shader import DEF_roughnessShader_add 
from .GA_shader import DEF_albedodetailsShader_add 
from .GA_shader import DEF_diffuseShader_add
from .GA_shader import DEF_maskShader_add
from .GA_shader import DEF_bentShader_add
from .GA_shader import DEF_opacityShader_add
from .GA_shader import DEF_gradientShader_add
from .GA_shader import DEF_bumpShader_add


from .GA_material import DEF_image_save 
from .GA_material import DEF_remove_all

from .GA_composite import DEF_NormalToCurvature



from progress_report import ProgressReport, ProgressReportSubstep



class GA_Start(Operator):
    """Will generate your game asset, open the terminal to follow the progress"""

    bl_idname = "scene.ga_start"
    bl_label = "Generate Asset"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self,context, event):
        if bpy.data.is_saved == False:
           bpy.ops.wm.save_as_mainfile("INVOKE_AREA")
           return {'RUNNING_MODAL'}
        return self.execute(context)


    def execute(self, context):


        #REMOVE ALL Layer 1
        ######################################
        DEF_remove_all()

        #Load GA property
        ######################################
        
        myscene = context.scene.ga_property
        
        then = time.time() #Calculate time
        
        print("\n- GAME ASSET GENERATOR beta EXECUTED -\n")

        #Init value
        ######################################
        
        selected_to_active = myscene.D_selected_to_active
        
        LOD0 = myscene.D_LOD0
        LOD1 = myscene.D_LOD1
        LOD2 = myscene.D_LOD2
        name = myscene.D_name

        size = 1024, 1024

        if myscene.D_texture == '256':
           size = 256, 256

        if myscene.D_texture == '512':
           size = 512, 512

        if myscene.D_texture == '1K':
           size = 1024, 1024

        if myscene.D_texture == '2K':
           size = 2048, 2048

        if myscene.D_texture == '4K':
           size = 4096, 4096
        
        greyscale = 0   #Will apply a diffuse grey 0.735 on the high poly (and remove every other material

        make_stylized = 0 
        AO_samples = myscene.D_samples
        unfold_half = myscene.D_unfoldhalf #Unfold half for symmetrical assets
        cage_size = myscene.D_cage_size
        
        calculate_edge_padding = 0
        edge_padding = myscene.D_edge_padding
        
        calculate_LODs = 0

        uv_margin = myscene.D_uv_margin
        uv_angle = myscene.D_uv_angle
        
        ground_AO = myscene.D_groundAO
        rmv_underground = myscene.D_removeunderground
        
        T_enabled = 0

        GPU_baking = 1


        #Create Shader
        ######################################

        

        DEF_pointinessShader_add(context,size,name)
        DEF_ambientocclusionShader_add(context,size,name)
        DEF_albedoShader_add(context,size,name)
        DEF_normalShader_add(context,size,name)
        DEF_albedodetailsShader_add(context,size,name)
        DEF_diffuseShader_add(context,size,name)
        DEF_roughnessShader_add(context,size,name)
        DEF_maskShader_add(context,size,name)
        DEF_bentShader_add(context,size,name)
        DEF_opacityShader_add(context,size,name)
        DEF_gradientShader_add(context,size,name)
        DEF_bumpShader_add(context,size,name)






        ###########################################################
        #Game Asset start  YOURrrrrrrrrrrrrrrrrrrrrrrrrrrr
        ###########################################################


        if calculate_edge_padding == 1:
            if size[0] <= size[1]:
                edge_padding = size[0] / 128
            else:
                edge_padding = size[1] / 128
                
        if calculate_LODs == 1:

            LOD1 = 0.6 * LOD0
            LOD2 = 0.3 * LOD0



        if GPU_baking == 0:
           bpy.context.scene.cycles.device = 'CPU'
        if GPU_baking == 1:
           bpy.context.scene.cycles.device = 'GPU'



        #todo: save original by moving it in another collection

        bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
        
        bpy.ops.object.move_to_layer(layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.scene.layers[1] = True
        bpy.context.scene.layers[0] = False
        
        if selected_to_active == 1:
            print("\n> Selected to Active mode enabled\n")
            
            if len(bpy.context.selected_objects) == 2: 
               
               target_object = bpy.context.active_object.name
                         
               
               if bpy.context.selected_objects[0].name  == target_object:              
                  bpy.context.selected_objects[0].name = "old1" 
                  bpy.context.selected_objects[1].name = "old2"  
             
                  bpy.context.selected_objects[1].name = "tmpHP"
                  bpy.context.selected_objects[0].name = "tmpLP"   
                  
               else: 

                  bpy.context.selected_objects[0].name = "old1"
                  bpy.context.selected_objects[0].name = "old2"
                  
                  bpy.context.selected_objects[1].name = "tmpLP"
                  bpy.context.selected_objects[0].name = "tmpHP"




        #If we want to generate the low poly
        ###################################
        if selected_to_active == 0:
    
            #Prepare the high poly
            ######################
            bpy.ops.object.convert(target='MESH')
            bpy.ops.object.join()

            bpy.ops.object.shade_smooth()
            bpy.context.object.data.use_auto_smooth = False

            #bpy.ops.object.convert(target='MESH')
            bpy.ops.object.join()


            if make_stylized == 1:

                bpy.ops.object.modifier_add(type='BEVEL')
                bpy.context.object.modifiers["Bevel"].limit_method = 'ANGLE'
                bpy.context.object.modifiers["Bevel"].width = 0.025

                bpy.ops.object.modifier_add(type='BEVEL')
                bpy.context.object.modifiers["Bevel.001"].width = 0.005
                bpy.context.object.modifiers["Bevel.001"].segments = 2
                bpy.context.object.modifiers["Bevel.001"].profile = 1
                bpy.context.object.modifiers["Bevel.001"].limit_method = 'ANGLE'

                bpy.ops.object.modifier_add(type='SUBSURF')
                bpy.context.object.modifiers["Subsurf"].levels = 3

                bpy.ops.object.convert(target='MESH')



            bpy.context.object.name = "tmpHP"

            #creating the low poly
            ######################
            print("\n----- GENERATING LOW POLY -----\n")
            
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})

            #remove every material slot of the low poly

            for ob in bpy.context.selected_editable_objects:
                ob.active_material_index = 0
                for i in range(len(ob.material_slots)):
                    bpy.ops.object.material_slot_remove({'object': ob})
                    
            #Remove parts of the mesh bellow the grid if enabled
            if rmv_underground == 1:
                bpy.ops.object.mode_set(mode = 'EDIT') 
                        
                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.bisect(plane_co=(0.00102639, 0.0334111, 0), plane_no=(0, 0, 0.999663), use_fill=False, clear_inner=True, xstart=295, xend=444, ystart=464, yend=461)

                bpy.ops.mesh.edge_face_add()

                bpy.ops.object.mode_set(mode = 'OBJECT')

            #Decimation 1
            #############
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

            obj = bpy.context.active_object
            HP_polycount = len(obj.data.polygons)

            decimation = (LOD0 / HP_polycount)

            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = decimation
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

            #Create envelop by doing an Union boolean between every meshes
            ##############################################################
            if myscene.D_create_envelop == 1:
        
                print("\n> Creating the envelop\n")

                bpy.ops.object.mode_set(mode = 'EDIT') 
                
                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.region_to_loop()

                bpy.ops.mesh.edge_face_add()

                bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')        

                #Separate meshes

                bpy.ops.mesh.select_all(action = 'DESELECT')

                bpy.ops.mesh.select_mode(type="EDGE")

                bpy.ops.mesh.separate(type='LOOSE')

                bpy.ops.object.mode_set(mode = 'OBJECT')

                for obj in bpy.context.selected_objects:

                    bpy.context.scene.objects.active = obj

                i = 0   #will count the number of mesh, an x letter will be added to each mesh: mx, mxx, then it will countdown to select every mesh
                m = 'm'
                x = 'x'

                for obj in bpy.context.selected_objects:
                    bpy.context.scene.objects.active = obj

                    m = m + x
                    i = i + 1
                    bpy.context.object.name = m
                 
                 
                bpy.ops.object.select_all(action= 'DESELECT')
                bpy.ops.object.select_pattern(pattern="mx")
                bpy.context.scene.objects.active = bpy.data.objects["mx"]

                m = 'mx'

                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
                bpy.ops.object.mode_set(mode = 'OBJECT')

                while i > 1:
                    i = i - 1

                    m = m + x
                    bpy.ops.object.select_pattern(pattern=m)

                    bpy.ops.object.join()

                    bpy.ops.object.mode_set(mode = 'EDIT')

                    bpy.ops.mesh.intersect_boolean(operation='UNION')
                    bpy.ops.mesh.mark_sharp()
                    bpy.ops.mesh.select_all(action = 'SELECT')
                    bpy.ops.object.mode_set(mode = 'OBJECT')

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.normals_make_consistent(inside=False)

            bpy.ops.object.mode_set(mode = 'OBJECT')

            bpy.context.object.name = "tmpLP"
    
            if unfold_half == 1:
                bpy.ops.object.mode_set(mode = 'EDIT')
                bpy.ops.mesh.select_all(action = 'SELECT')
        
                bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(1, 0, 0), clear_inner=True, clear_outer=False, xstart=849, xend=849, ystart=637, yend=473)
                bpy.ops.object.mode_set(mode = 'OBJECT')
                
            #Remove underground a second time, but this time remove the botton face (was needed for the create envelop)
            if rmv_underground == 1:
                bpy.ops.object.mode_set(mode = 'EDIT') 
                        
                bpy.ops.mesh.select_all(action = 'SELECT')

                bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), use_fill=False, clear_inner=True, clear_outer=False, threshold=0.01, xstart=373, xend=525, ystart=363, yend=369)

                bpy.ops.mesh.delete(type='FACE')

                bpy.ops.object.mode_set(mode = 'OBJECT')

            #Decimation 2
            #############
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

            obj = bpy.context.active_object
            HP_polycount = len(obj.data.polygons)

            if unfold_half == 0:
                decimation = (LOD0 / HP_polycount)
            if unfold_half == 1:
                decimation = (LOD0 / HP_polycount) / 2

            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = decimation
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")

            #Cleaning the doubles
            #####################
            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.mark_sharp(clear=True)
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode = 'OBJECT')

            #Unfold UVs
            ###########
    
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            bpy.context.object.modifiers["EdgeSplit"].use_edge_angle = False
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")

            bpy.ops.uv.smart_project(angle_limit=uv_angle, island_margin=uv_margin)
    
            if unfold_half == 1:
                bpy.ops.object.modifier_add(type='MIRROR')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Mirror")

            bpy.ops.object.mode_set(mode = 'EDIT')
            bpy.ops.mesh.select_all(action = 'SELECT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.mark_sharp(clear=True)

            bpy.ops.object.mode_set(mode = 'OBJECT')

            HP_polycount = len(obj.data.polygons)
            print("\n> LOD0 generated with", HP_polycount, "tris\n")



        #BAKING
        ##############################################################################################################################################################################################################
        
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)        
        
        #Remove parts of the mesh bellow the grid if enabled
        if selected_to_active == 1:
            if rmv_underground == 1:
                bpy.ops.object.mode_set(mode = 'EDIT') 
                            
                bpy.ops.mesh.select_all(action = 'SELECT')
                
                bpy.ops.mesh.bisect(plane_co=(0, 0, 0), plane_no=(0, 0, 1), use_fill=False, clear_inner=True, clear_outer=False, xstart=424, xend=553, ystart=340, yend=333)
                
                bpy.ops.object.mode_set(mode = 'OBJECT')
        
        if ground_AO == 1:
            bpy.ops.mesh.primitive_plane_add(radius=1, view_align=False, enter_editmode=False, location=(0, 0, 0), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
            bpy.ops.transform.resize(value=(100, 100, 100), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
            bpy.context.object.name = "ground_AO"
        
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]

        #Check if the low poly has UVs
        if not len( bpy.context.object.data.uv_layers ):
            print("\n> Infos: the low poly has no UV, performing a Smart UV Project\n")
            bpy.ops.uv.smart_project() # Perform smart UV projection
        
        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]
        
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.samples = 1

        print("\n----- GENERATING TEXTURES -----\n")
        
        #Mask map
        
        if myscene.T_mask == 1:
            print("\n> Baking: mask map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'MASK']
            bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))
    
        
        #Albedo map
        
        if myscene.T_albedo == 1:
            print("\n> Baking: albedo map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'ALBEDO']
            bpy.ops.object.bake(type="DIFFUSE", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))
    
        
    
    
        #Normal map
        
        if myscene.T_normal == 1:
            print("\n> Baking: normal map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'NORMAL']
            bpy.ops.object.bake(type="NORMAL", normal_space ='TANGENT', use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)
            
            
            
        #Bent map
        if myscene.T_bent == 1:
            print("\n> Baking: bent map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'BENT']
            bpy.ops.object.bake(type="NORMAL", normal_space ='OBJECT', use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, normal_r = 'POS_X', normal_g = 'POS_Z', normal_b = 'NEG_Y', use_clear = True)
            

        #Ambient Occlusion map

        if myscene.T_ao == 1:

            bpy.context.scene.cycles.samples = AO_samples
            bpy.context.scene.world.light_settings.distance = 10

            print("\n> Baking: ambient occlusion map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'AMBIENT OCCLUSION']
            bpy.ops.object.bake(type="AO", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)
            
            bpy.context.scene.cycles.samples = 1
            
        #remove every material slot of the high poly
        bpy.ops.object.select_all(action = 'DESELECT')

        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpHP"]

        for ob in bpy.context.selected_editable_objects:
            ob.active_material_index = 0
            for i in range(len(ob.material_slots)):
                bpy.ops.object.material_slot_remove({'object': ob})
                
        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]


        #Pointiness map

        if myscene.T_pointiness == 1:
            print("\n> Baking: pointiness map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'POINTINESS']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'POINTINESS']        
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)

        #Roughness map
        
        if myscene.T_roughness == 1:
            print("\n> Baking: roughness map\n")
            
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'ROUGHNESS']
            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'ROUGHNESS']
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True)



        #Gradient map
        if myscene.T_gradient == 1:
            print("\n> Baking: gradient map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'GRADIENT']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'GRADIENT']
                    
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))

        #Opacity map
        if myscene.T_opacity == 1:
            print("\n> Baking: opacity map\n")

            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'OPACITY']
            bpy.data.objects['tmpHP'].active_material = bpy.data.materials[name+"_"+'OPACITY']
            
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = True, use_cage = True, cage_extrusion = cage_size, margin = edge_padding, use_clear = True, pass_filter=set({'COLOR'}))



        #Albedo detailled map
        
        if T_enabled == 1:
                
            print("\n> Baking: albedo details map\n")
            
            
            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'ALBEDO_DETAILS']
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = False, use_cage = False, margin = edge_padding, use_clear = True)

        
        #Diffuse map
        
        if T_enabled == 1:
        
            bpy.context.scene.cycles.samples = 1
            
            print("\n> Baking: diffuse map\n")
            
            bpy.ops.object.select_all(action = 'DESELECT')

            bpy.ops.object.select_pattern(pattern="tmpLP")
            bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]
            
            bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'DIFFUSE']
            bpy.ops.object.bake(type="EMIT", use_selected_to_active = False, use_cage = False, margin = edge_padding, use_clear = True)

            bpy.context.scene.render.engine = 'BLENDER_RENDER'

            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.viewport_shade = 'MATERIAL'


        #Curvature map
        
        if myscene.T_curvature == 1:
        
            print("\n> Compositing: curvature map from normal map\n")

            DEF_NormalToCurvature(context,size,name)
        



        #Create the lighting
        ####################
        bpy.ops.object.lamp_add(type='HEMI', view_align=False, location=(0, 0, 5),      layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
        bpy.context.object.data.energy = 0.5

        bpy.ops.object.lamp_add(type='HEMI', view_align=False, location=(0, 0, -5), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))

        bpy.ops.transform.rotate(value=-3.14159, axis=(-0, 1, 1.34359e-007), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)
        bpy.context.object.data.energy = 0.1

        bpy.ops.object.lamp_add(type='POINT', radius=1, view_align=False, location=(0.5, -1.5, 1), layers=(False, True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))




        #delete the high poly
        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpHP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpHP"]

        bpy.ops.object.delete(use_global=False)
        
        #delete the ground        
        if ground_AO == 1:
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.ops.object.select_pattern(pattern="ground_AO")
            bpy.context.scene.objects.active = bpy.data.objects["ground_AO"]

            bpy.ops.object.delete(use_global=False)
            

        bpy.ops.object.select_all(action = 'DESELECT')
        bpy.ops.object.select_pattern(pattern="tmpLP")
        bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]




        #Create the PBR material, need to update it in the future for EEVEE
        #################################
        DEF_pbrShader_add(context,size,name)



        bpy.data.objects['tmpLP'].active_material = bpy.data.materials[name+"_"+'PBR']


        #Generating the LODs
        ####################
        if LOD1 > 0:
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 3, 0), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
            bpy.context.object.name = name + "_LOD1"
            bpy.context.object.data.name = name + "_LOD1"
        
            #decimation of the LOD1
            #######################
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

            obj = bpy.context.active_object
            HP_polycount = len(obj.data.polygons)

            decimation = (LOD1 / HP_polycount)


            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = decimation
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
            #TODO: Export LOD1 in OBJ

            HP_polycount = len(obj.data.polygons)
            print("\n> LOD1 generated with", HP_polycount, "tris\n")

        if LOD2 > 0:
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 3, 0), "constraint_axis":(False, True, False), "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False})
            bpy.context.object.name = name + "_LOD2"
            bpy.context.object.data.name = name + "_LOD2"
        
            #decimation of the LOD2
            #######################
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")

            obj = bpy.context.active_object
            HP_polycount = len(obj.data.polygons)

            HP_polycount = len(obj.data.polygons)
            decimation = (LOD2 / HP_polycount)


            bpy.ops.object.modifier_add(type='DECIMATE')
            bpy.context.object.modifiers["Decimate"].ratio = decimation
            bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
        
            #TODO: Export LOD2 in OBJ
        
            HP_polycount = len(obj.data.polygons)
            print("\n> LOD2 generated with", HP_polycount, "tris\n")
        
            bpy.ops.object.select_all(action = 'DESELECT')
            bpy.ops.object.select_pattern(pattern="tmpLP")
            bpy.context.scene.objects.active = bpy.data.objects["tmpLP"]


        bpy.context.object.name = name + "_LOD0"
        bpy.context.object.data.name = name + "_LOD0"
        
        print("\n> Saving maps\n") 
        


        DEF_image_save( name )

        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.viewport_shade = 'MATERIAL'
                        area.spaces[0].fx_settings.use_ssao = False
        
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        
        now = time.time() #Time after it finished

        print("\n----- GAME ASSET READY -----") 
        print("\n(Execution time:", now-then, "seconds)\n\n")



        return {'FINISHED'}





