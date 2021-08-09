# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFolderDestination)
from qgis import processing
import gdal
import numpy as np
from datetime import datetime

class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT1 = 'INPUT1'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    INPUT4 = 'INPUT4'
    INPUT5 = 'INPUT5'
    INPUT6 = 'INPUT6'
    INPUT7 = 'INPUT7'
    INPUT8 = 'INPUT8'
    INPUT9 = 'INPUT9'
    PIXEL_RES = 'PIXEL_RES'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'SE Calcolo Complessivo'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Calcolo Complessivo')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('SE Torino')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Algoritmo per il calcolo complessivo dei Servizi Ecosistemici")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT1,
                self.tr('Input Raster Output SEQUESTRO DI CARBONIO'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT2,
                self.tr('Input Raster Output RIMOZIONE INQUINANTI'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT3,
                self.tr('Input Raster Output REGOLAZIONE DELLA TEMPERATURA'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT4,
                self.tr('Input Raster Output PROTEZIONE IDROGEOLOGICA'),
                [QgsProcessing.TypeRaster]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT5,
                self.tr('Input Raster Output CAPACITA DI INFILTRAZIONE'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT6,
                self.tr('Input Raster Output BENEFICI CULTURALI'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT7,
                self.tr('Input Raster Output BIODIVERSITA'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT8,
                self.tr('Input Raster Output PRODUZIONE AGRICOLA'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT9,
                self.tr('Input Raster Output IMPOLLINAZIONE'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
            self.PIXEL_RES,
            self.tr('Risoluzione spaziale raster (m)'),
            QgsProcessingParameterNumber.Integer,
            2
            )
        ) 

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT,
                self.tr('Salva nella cartella')
            )
        )
        
    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Load all rasters
        input1_raster = self.parameterAsRasterLayer(parameters, self.INPUT1, context)
        ds_input1 = gdal.Open(input1_raster.dataProvider().dataSourceUri())
        arr_input1 = ds_input1.GetRasterBand(1).ReadAsArray()

        input2_raster = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        ds_input2 = gdal.Open(input2_raster.dataProvider().dataSourceUri())
        arr_input2 = ds_input2.GetRasterBand(1).ReadAsArray()

        input3_raster = self.parameterAsRasterLayer(parameters, self.INPUT3, context)
        ds_input3 = gdal.Open(input3_raster.dataProvider().dataSourceUri())
        arr_input3 = ds_input3.GetRasterBand(1).ReadAsArray()

        input4_raster = self.parameterAsRasterLayer(parameters, self.INPUT4, context)
        ds_input4 = gdal.Open(input4_raster.dataProvider().dataSourceUri())
        arr_input4 = ds_input4.GetRasterBand(1).ReadAsArray()

        input5_raster = self.parameterAsRasterLayer(parameters, self.INPUT5, context)
        ds_input5 = gdal.Open(input5_raster.dataProvider().dataSourceUri())
        arr_input5 = ds_input5.GetRasterBand(1).ReadAsArray()

        input6_raster = self.parameterAsRasterLayer(parameters, self.INPUT6, context)
        ds_input6 = gdal.Open(input6_raster.dataProvider().dataSourceUri())
        arr_input6 = ds_input6.GetRasterBand(1).ReadAsArray()

        input7_raster = self.parameterAsRasterLayer(parameters, self.INPUT7, context)
        ds_input7 = gdal.Open(input7_raster.dataProvider().dataSourceUri())
        arr_input7 = ds_input7.GetRasterBand(1).ReadAsArray()

        input8_raster = self.parameterAsRasterLayer(parameters, self.INPUT8, context)
        ds_input8 = gdal.Open(input8_raster.dataProvider().dataSourceUri())
        arr_input8 = ds_input8.GetRasterBand(1).ReadAsArray()

        input9_raster = self.parameterAsRasterLayer(parameters, self.INPUT9, context)
        ds_input9 = gdal.Open(input9_raster.dataProvider().dataSourceUri())
        arr_input9 = ds_input9.GetRasterBand(1).ReadAsArray()

        arr_total = arr_input1 + arr_input2 + arr_input3 + arr_input4 + arr_input5 + arr_input6 + arr_input7 + \
                    arr_input8 + arr_input9

        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_10_SE_total.tiff'
        driver = gdal.GetDriverByName("GTiff")
        [rows, cols] = arr_total.shape
        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)
        total_area = np.sum(arr_total) / (cols * rows * area_pixel)
        outdata = driver.Create(file_output, cols, rows,  1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_input1.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_input1.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_total)
        outdata.FlushCache() ##saves to disk!!
        report_output = path_output + '/SE_totale.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi dei servizi ecosistemici\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Differenza di valore totale (€): %f \n" % (np.sum(arr_total)))
        f.write("Differenza per unità di superficie (€/ha): %f \n" % (
            total_area * 10000))
        return {self.OUTPUT: total_area}

        
        # -----------------------------------------------------------------------------------  
        # Copyright (c) 2021 Città di Torino.
        # 
        # This material is free software: you can redistribute it and/or modify
        # it under the terms of the GNU General Public License as published by
        # the Free Software Foundation, either version 2 of the License, or
        # (at your option) any later version.
        # 
        # This program is distributed in the hope that it will be useful,
        # but WITHOUT ANY WARRANTY; without even the implied warranty of
        # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        # GNU General Public License for more details.
        # 
        # You should have received a copy of the GNU General Public License
        # along with this program. If not, see http://www.gnu.org/licenses.
        # -----------------------------------------------------------------------------------  

