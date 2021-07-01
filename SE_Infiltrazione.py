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

    INPUTRP = 'INPUTRP'
    INPUTPRE = 'INPUTPRE'
    INPUTRF = 'INPUTRF'
    INPUTFUT = 'INPUTFUT'
    INPUTTREEP = 'INPUTTREEP'
    INPUTTREEF = 'INPUTTREEF'
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
        return 'SE Infiltrazione'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Infiltrazione')

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
        return self.tr("Algoritmo per il calcolo del sequesto del carbonio, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRP,
                self.tr('Raster Infiltrazione Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTTREEP,
            self.tr('Numero alberi complessivo stato attuale'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTPRE,
            self.tr('Anno attuale'),
            QgsProcessingParameterNumber.Integer,
            2021
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRF,
                self.tr('Raster Infiltrazione Stato di progetto'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTTREEF,
            self.tr('Numero alberi complessivo stato di progetto'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUTFUT,
            self.tr('Anno progetto'),
            QgsProcessingParameterNumber.Integer,
            2030
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
        # Load present raster
        present_raster = self.parameterAsRasterLayer(parameters, self.INPUTRP, context)
        ds_present = gdal.Open(present_raster.dataProvider().dataSourceUri())
        arr_present = ds_present.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_present[arr_present < 0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUTRF, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_future[arr_future < 0] = 0

        [rows, cols] = arr_present.shape

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)
        # Value euro per squared meter
        value_coeff = 300
        # Convert to squared meters and assign value
        arr_value_present = value_coeff * (arr_present / 1000) * area_pixel
        arr_value_future = value_coeff * (arr_future / 1000) * area_pixel
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_05_infiltrazione.tiff'
        driver = gdal.GetDriverByName("GTiff")
        arr_diff_tot = arr_value_future - arr_value_present
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_diff_tot)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache()
        print(path_output)
        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        report_output = path_output + '/SE_infiltrazione.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi dell'infiltrazione'\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % present)
        f.write("Infiltrazione stato attuale (mm): %f \n" % (np.sum(arr_present)))
        f.write("Infiltrazione sulla superficie totale - Stato attuale (mc): %f \n" % (
                np.sum((arr_present / 1000) * area_pixel)))
        f.write("Valore totale dell'infiltrazione (€/anno): %f \n\n" % (np.sum(arr_value_present)))
        f.write("RIEPILOGO DATI INPUT stato di fatto\n")
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % future)
        f.write("Infiltrazione stato di progetto (mm): %f \n" % (np.sum(arr_future)))
        f.write("Infiltrazione sulla superficie totale - Stato di progetto (mc): %f \n" % (
                np.sum((arr_future / 1000) * area_pixel)))
        f.write("Valore totale della infiltrazione (€/anno): %f \n\n" % (np.sum(arr_value_future)))
        f.write("RIEPILOGO DATI INPUT stato di progetto\n")
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza della infiltrazione (mm):: %f \n" % (np.sum(
            arr_future - arr_present)))
        f.write("Differenza della infiltrazione sulla superficie totale (mc): %f \n" % (
            np.sum((arr_future - arr_present) / 1000 * area_pixel)))
        f.write("Differenza in termini economici del SE di infiltrazione (stato di progetto – stato attuale) (€):%d \n" % (
            np.sum(arr_diff_tot)))
        return {self.OUTPUT: 'Completed'}

        
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


