# -*- coding: utf-8 -*-

import arcpy
import os
import shutil
import gc


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Infiltration Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CurveNumber]


class CurveNumber(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Curve Number"
        self.description = "Find curve numbers of subcatchments"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # first parameter
        param0 = arcpy.Parameter(
            displayName = 'Landcover shapefile',
            name= 'landcover_full',
            datatype = 'GPFeatureLayer',
            parameterType = 'Required',
            direction = 'Input')

        # second parameter
        param1 = arcpy.Parameter(
            displayName = 'Soil data shapefile',
            name= 'soils_full',
            datatype = 'GPFeatureLayer',
            parameterType = 'Required',
            direction = 'Input')

        # third parameter
        param2 = arcpy.Parameter(
            displayName = 'Subwatersheds shapefile',
            name= 'subwatersheds',
            datatype = 'GPFeatureLayer',
            parameterType = 'Required',
            direction = 'Input')

        # fourth parameter
        param3 = arcpy.Parameter(
            displayName = 'Scratch workspace',
            name= 'workspace',
            datatype = 'DEFolder',
            parameterType = 'Required',
            direction = 'Input')

        # fifth parameter
        param4 = arcpy.Parameter(
            displayName = 'Output shapefile',
            name= 'output',
            datatype = 'GPFeatureLayer',
            parameterType = 'Required',
            direction = 'Output')

        # Sixth parameter
        param5 = arcpy.Parameter(
            displayName = 'Hydrologic Soil Group Fieldname',
            name= 'hsg_field',
            datatype = 'Field',
            parameterType = 'Required',
            direction = 'Input')

        # Seventh parameter
        param6 = arcpy.Parameter(
            displayName = 'Landcover Classification Fieldname',
            name= 'lu_field',
            datatype = 'Field',
            parameterType = 'Required',
            direction = 'Input')

        # Set the filter to only accept fields that are Text type
        param6.filter.list = ['Text']
        param6.parameterDependencies = [param0.name]
        param5.filter.list = ['Text']
        param5.parameterDependencies = [param1.name]

        params = [param0, param1, param2, param3, param4, param5, param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # get parameters
        arcpy.env.overwriteOutput = True


        # This tool uses soil data, landcover data, and watershed outlines to calculate curve numbers and impervious areas for use in infiltration calculations.
        #
        # Soil data can be downloaded from the web soil survey or SSURGO (https://www.arcgis.com/apps/View/index.html?appid=cdc49bd63ea54dd2977f3f2853e07fff) and landcover data can be obtained from the NLCD.

        # # File paths

        # In[2]:


        landcover_full = parameters[0].valueAsText
        soils_full = parameters[1].valueAsText
        subwatersheds = parameters[2].valueAsText
        workspace = parameters[3].valueAsText
        output = parameters[4].valueAsText


        # In[3]:


        # Variables
        hsg_field = parameters[5].valueAsText
        lu_field= parameters[6].valueAsText
        cn_field="CN"
        pimperv_field="P_Imperv"
        area_field = "POLY_AREA"
        cnarea_field = "CNAREA"
        impervarea_field="IpArea"
        totalcn_field = "CN_Total"
        totalpimperv_field="PercImperv"
        totalarea_field="Area_ac"

        sumcnarea = "SUM_" + cnarea_field[0:6]
        sumiparea= "SUM_" + impervarea_field[0:6]
        sumpolyarea = "SUM_" + area_field[0:6]

        # Curve number assignment [[zone, CN for HSG A, CN for HSG B, CN for HSG C, %Impervious]]
        cn_assignment = [["A",61,74,80,35],["CG",92,94,95,85],
                         ["P",69,79,84,0],["PUD",85,90,92,90],
                         ["R5",75,83,87,35],["R10",85,90,92,50],
                         ["RMH",85,90,92,50],["RR",68,79,84,12],
                         ["RT",92,94,95,75],["ROW",98,98,98,98]]


        # In[4]:


        # Intermediate file names
        temp_folder = os.path.join(workspace, "Scratch")
        arcpy.env.scratchWorkspace = temp_folder
        landcover = os.path.join(temp_folder, "landcover.shp")
        soils = os.path.join(temp_folder, "soils.shp")
        soils_dissolved = os.path.join(temp_folder, "soilsdissolved.shp")
        intersected_catchments = os.path.join(temp_folder, "intws.shp")
        intersected_catchments2 = os.path.join(temp_folder, "intwslc.shp")
        dissolved_catchments = os.path.join(temp_folder, "dissws.shp")


        # In[5]:


        # Create scratch folder
        try:
            os.mkdir(temp_folder)
        except:
            messages.addMessage('Scratch folder exists')


        # # Clip landcover and soils

        # In[6]:


        arcpy.Clip_analysis(in_features=soils_full, clip_features=subwatersheds, out_feature_class=soils)
        arcpy.Clip_analysis(in_features=landcover_full, clip_features=subwatersheds, out_feature_class=landcover)


        # # Add an ID field to subcatchments for joins

        # In[7]:


        arcpy.AddField_management(in_table=subwatersheds, field_name="WSID", field_type="LONG", field_precision=10)
        arcpy.CalculateField_management(in_table=subwatersheds, field="WSID", expression="!FID!", expression_type="PYTHON3")


        # # Dissolve soils

        # In[8]:


        # For rows with two hydrologic soil groups, keep the most stringent
        with arcpy.da.UpdateCursor(in_table=soils, field_names=[hsg_field]) as cursor:
            for row in cursor:
                if len(row[0])>1:
                    row[0] = str(row[0])[-1]
                    cursor.updateRow(row)
        # Dissolve soils based on HSG
        arcpy.Dissolve_management(in_features=soils, out_feature_class=soils_dissolved, dissolve_field=hsg_field, multi_part="MULTI_PART")


        # # Intersect Soils, Landcover, and Subwatersheds

        # In[9]:


        arcpy.Intersect_analysis(in_features=[subwatersheds, soils_dissolved], out_feature_class=intersected_catchments)
        arcpy.Intersect_analysis(in_features=[intersected_catchments, landcover], out_feature_class=intersected_catchments2)


        # # Calculate curve number and impervious area for each intersection

        # In[10]:


        # Add percent impervious and curve number fields
        try:
            arcpy.AddField_management(in_table=intersected_catchments2, field_name=cn_field, field_type="LONG", field_precision=3)
        except:
            messages.addMessage('CN field already present')
            arcpy.CalculateField_management(in_table=intersected_catchments2, field=cn_field, expression="0", expression_type="PYTHON3")
        try:
            arcpy.AddField_management(in_table=intersected_catchments2, field_name=pimperv_field, field_type="LONG", field_precision=3)
        except:
            messages.addMessage('PImperv field already present')
            arcpy.CalculateField_management(in_table=intersected_catchments2, field=pimperv_field, expression="0", expression_type="PYTHON3")
        try:
            arcpy.AddField_management(in_table=intersected_catchments2, field_name=impervarea_field, field_type="DOUBLE", field_precision=15, field_scale=4)
        except:
            messages.addMessage('PImpervArea field already present')
            arcpy.CalculateField_management(in_table=intersected_catchments2, field=impervarea_field, expression="0", expression_type="PYTHON3")
        # Add area field
        arcpy.AddGeometryAttributes_management(Input_Features=intersected_catchments2,Geometry_Properties="AREA", Area_Unit="ACRES")
        # Add weighted curve number field
        try:
            arcpy.AddField_management(in_table=intersected_catchments2, field_name=cnarea_field, field_type="DOUBLE", field_precision=15, field_scale=4)
        except:
            messages.addMessage('CNArea field already present')
            arcpy.CalculateField_management(in_table=intersected_catchments2, field=cnarea_field, expression="0", expression_type="PYTHON3")


        # In[11]:

        # Calculate curve number and impervious area
        with arcpy.da.UpdateCursor(in_table=intersected_catchments2, field_names=[lu_field, hsg_field, cn_field, pimperv_field, area_field, cnarea_field, impervarea_field]) as cursor:
            for row in cursor:
                for zone in cn_assignment:
                    if row[0]==zone[0]:
                        if row[1]=="B":
                            row[2]=zone[1]
                        elif row[1]=="C":
                            row[2]=zone[2]
                        else:
                            row[2]=zone[3]
                        row[3]=zone[4]
                        row[5]=row[4]*row[2]
                        row[6]=0.01*row[4]*row[3]
                        cursor.updateRow(row)

        del cursor
        gc.collect()


        # # Dissolve and calculate weighted CN and % Impervious

        # In[12]:


        # Dissolve and sum area, impervious area, and curve number * area
        arcpy.Dissolve_management(in_features=intersected_catchments2,out_feature_class=dissolved_catchments, dissolve_field=["WSID"],statistics_fields=[[cnarea_field, "SUM"], [impervarea_field, "SUM"], [area_field, "SUM"]])
        # Add total area, percent impervious, and weighted curve number fields
        try:
            arcpy.AddField_management(in_table=dissolved_catchments, field_name=totalcn_field, field_type="LONG", field_precision=3)
        except:
            messages.addMessage('CN field already present')
            arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalcn_field, expression="0", expression_type="PYTHON3")
        try:
            arcpy.AddField_management(in_table=dissolved_catchments, field_name=totalpimperv_field, field_type="DOUBLE", field_precision=5, field_scale=2)
        except:
            messages.addMessage('%Impervious field already present')
            arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalpimperv_field, expression="0", expression_type="PYTHON3")
        try:
            arcpy.AddField_management(in_table=dissolved_catchments, field_name=totalarea_field, field_type="DOUBLE", field_precision=15, field_scale=2)
        except:
            messages.addMessage('Area field already present')
            arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalarea_field, expression="0", expression_type="PYTHON3")

        arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalarea_field, expression="!"+sumpolyarea+"!", expression_type="PYTHON3")
        arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalcn_field, expression="round(!"+sumcnarea+"!/!"+sumpolyarea+"!,0)", expression_type="PYTHON3")
        arcpy.CalculateField_management(in_table=dissolved_catchments, field=totalpimperv_field, expression="(!"+sumiparea+"!/!"+sumpolyarea+"!)*100", expression_type="PYTHON3")


        # # Join fields to final shapefile

        # In[13]:


        arcpy.CopyFeatures_management(subwatersheds, output)
        arcpy.JoinField_management(in_data=output, in_field="WSID", join_table=dissolved_catchments, join_field="WSID", fields=[totalcn_field, totalpimperv_field, totalarea_field])


        # # Delete intermediate files

        # In[14]:


        try:
            shutil.rmtree(temp_folder)
        except:
            messages.addMessage('Temporary storage not removed')

        messages.addMessage('Done!')
        return
