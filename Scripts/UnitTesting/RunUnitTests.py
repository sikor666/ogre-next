#!/usr/bin/env python3

import sys
import os
from subprocess import run
import filecmp
import platform
import shutil
import pathlib

g_unitTests = \
[
	['Sample_AnimationTagPoint', 'Sample_AnimationTagPoint.json'],
	['Sample_AreaApproxLights', 'Sample_AreaApproxLights.json'],
	['Sample_CustomRenderable', 'Sample_CustomRenderable.json'],
	['Sample_Decals', 'Sample_Decals.json'],
	['Sample_DynamicGeometry', 'Sample_DynamicGeometry.json'],
	['Sample_Forward3D', 'Sample_Forward3D.json'],
	['Sample_Hdr', 'Sample_Hdr.json'],
	['Sample_HdrSmaa', 'Sample_Hdr.json'],
	['Sample_IesProfiles', 'Sample_IesProfiles.json'],
	['Sample_ImportAnimationsShareSkeletonInstance', 'Sample_ImportAnimationsShareSkeletonInstance.json'],
	['Sample_InstancedStereo', 'Sample_InstancedStereo.json'],
	['Sample_LocalCubemaps', 'Sample_LocalCubemaps.json'],
	['Sample_LocalCubemapsManualProbes', 'Sample_LocalCubemapsManualProbes.json'],
	['Sample_MorphAnimations', 'Sample_MorphAnimations.json'],
	['Sample_PbsMaterials', 'Sample_PbsMaterials.json'],
	['Sample_PccPerPixelGridPlacement', 'Sample_PccPerPixelGridPlacement.json'],
	['Sample_Postprocessing', 'Sample_Postprocessing.json'],
	['Sample_Refractions', 'Sample_Refractions.json'],
	['Sample_SceneFormat', 'Sample_SceneFormat.json'],
	['Sample_ScreenSpaceReflections', 'Sample_ScreenSpaceReflections.json'],
	['Sample_ShadowMapDebugging', 'Sample_ShadowMapDebugging.json'],
	['Sample_ShadowMapFromCode', 'Sample_ShadowMapFromCode.json'],
	['Sample_StencilTest', 'Sample_StencilTest.json'],
	['Sample_StereoRendering', 'Sample_StereoRendering.json'],
	['Sample_Tutorial_Distortion', 'Sample_Tutorial_Distortion.json'],
	['Sample_Tutorial_DynamicCubemap', 'Sample_Tutorial_DynamicCubemap.json'],
	['Sample_Tutorial_ReconstructPosFromDepth', 'Sample_Tutorial_ReconstructPosFromDepth.json'],
	['Sample_Tutorial_SMAA', 'Sample_Tutorial_SMAA.json'],
	['Sample_Tutorial_SSAO', 'Sample_Tutorial_SSAO.json'],
	['Sample_Tutorial_Terrain', 'Sample_Tutorial_Terrain.json'],
	['Sample_Tutorial_TextureBaking', 'Sample_Tutorial_TextureBaking.json'],
	['Sample_TutorialCompute01_UavTexture', 'Sample_TutorialCompute01_UavTexture.json'],
	['Sample_TutorialCompute02_UavBuffer', 'Sample_TutorialCompute01_UavTexture.json'],
	['Sample_TutorialSky_Postprocess', 'Sample_TutorialSky_Postprocess.json'],
	['Sample_TutorialUav01_Setup', 'Sample_TutorialUav01_Setup.json'],
	['Sample_TutorialUav02_Setup', 'Sample_TutorialUav01_Setup.json'],
	['Sample_UpdatingDecalsAndAreaLightTex', 'Sample_UpdatingDecalsAndAreaLightTex.json'],
	['Sample_V1Interfaces', 'Sample_V1Interfaces.json'],
	['Sample_V2ManualObject', 'Sample_V1Interfaces.json'],
	['Sample_V2Mesh', 'Sample_V1Interfaces.json']
]

print( 'Launched with ' + str( sys.argv ) )

if len( sys.argv ) != 5 and len( sys.argv ) != 6:
	print( 'Usage: ')
	print( '    python3 RunUnitTests.py metal|gl|d3d11 /pathTo/built/exes /pathTo/json_files ' \
			'/pathTo/binary_output /pathTo/old_cmp_binary_output' )
	print( 'Last argument can be skipped if generating the output (i.e. first run)' )
	exit( -1 )

g_api = sys.argv[1]
g_exeFolder = sys.argv[2]
g_jsonFolder = sys.argv[3]
g_outputFolder = sys.argv[4]
if len( sys.argv ) > 5:
	g_cmpFolder = sys.argv[5]
else:
	g_cmpFolder = ''

g_hasDifferentFiles = False
g_system = platform.system().lower()


def compareResults( oldFolder, newFolder ):
	global g_hasDifferentFiles
	try:
		cmpResult = filecmp.dircmp( oldFolder, newFolder )
		if len( cmpResult.left_only ) > 0:
			g_hasDifferentFiles = True
			print( 'WARNING: these files were not generated by this unit test but should have been:' )
			print( str( cmpResult.left_only ) )
		if len( cmpResult.right_only ) > 0:
			g_hasDifferentFiles = True
			print( 'WARNING: these files were not in the original cmp folder:' )
			print( str( cmpResult.right_only ) )
		
		if len( cmpResult.diff_files ) == 0:
			print( 'All files equal' )
		else:
			g_hasDifferentFiles = True
			print( 'ERROR: Different files: ' + str( cmpResult.diff_files ) )
	except FileNotFoundError as err:
		g_hasDifferentFiles = True
		print( 'ERROR: {0}'.format( err ) )

def runUnitTest( exeName, jsonName ):
	exeFullpath = os.path.abspath( os.path.join( g_exeFolder, exeName ) )
	jsonFullpath = os.path.abspath( os.path.join( g_jsonFolder, jsonName ) )
	outputFolder = os.path.abspath( os.path.join( g_outputFolder, exeName ) )
	cmpFolder = os.path.abspath( os.path.join( g_cmpFolder, exeName ) )

	if g_system == 'darwin':
		shutil.copyfile( './ogreMetal.cfg', os.path.join( exeFullpath + '.app/Contents/Resources', 'ogre.cfg' ) )
		exeFullpath += '.app/Contents/MacOS/' + exeName
	elif g_system == 'linux' and g_api == 'd3d11':
		exeFullpath += '.exe'

	args = [exeFullpath, '--ut_playback=' + jsonFullpath, '--ut_output=' + outputFolder]

	if g_system == 'linux' and g_api == 'd3d11':
		args = ['wine'] + args[:]
	#if g_system == 'darwin':
	#	args = ['open', '-W', '-n', '-a' ] + [args[0]] + ['--args'] + args[1:]

	print( '=== NEW UNIT TEST ===' )
	print( 'Trying ' + str( args ) )
	print( 'Creating output folder ' + outputFolder )
	pathlib.Path( outputFolder ).mkdir( parents=True, exist_ok=True )
	processResult = run( args, cwd=g_exeFolder )
	processResult.check_returncode()

	if g_cmpFolder != '':
		compareResults( cmpFolder, outputFolder )

if g_system != 'darwin':
	# Setup ogre.cfg
	if g_api == 'gl':
		shutil.copyfile( './ogreGL.cfg', os.path.join( g_exeFolder, 'ogre.cfg' ) )
	elif g_api == 'vk':
		shutil.copyfile( './ogreVk.cfg', os.path.join( g_exeFolder, 'ogre.cfg' ) )
		# Remove samples that don't work w/ Vulkan
		g_unitTests[:] = [unitTest for unitTest in g_unitTests \
			if unitTest[0] != 'Sample_ScreenSpaceReflections' and \
				unitTest[0] != 'Sample_TutorialUav01_Setup' and \
				unitTest[0] != 'Sample_TutorialUav02_Setup']
	else:
		shutil.copyfile( './ogreD3D11.cfg', os.path.join( g_exeFolder, 'ogre.cfg' ) )
else:
	# Remove samples that don't work in macOS
	g_unitTests[:] = [unitTest for unitTest in g_unitTests \
		if unitTest[0] != 'Sample_InstancedStereo' and \
			unitTest[0] != 'Sample_ScreenSpaceReflections' and \
			unitTest[0] != 'Sample_Tutorial_Distortion' and \
			unitTest[0] != 'Sample_TutorialUav01_Setup' and \
			unitTest[0] != 'Sample_TutorialUav02_Setup']

# Iterate through all tests and run it
for unitTest in g_unitTests:
	runUnitTest( unitTest[0], unitTest[1] )

if g_cmpFolder != '':
	if g_hasDifferentFiles:
		print( 'ERROR: Some files in one of the tests were not equal' )
		exit( -2 )
	else:
		print( 'All files in all tests were equal' )
else:
	print( 'No comparison was made as the script was run in generation mode' )
