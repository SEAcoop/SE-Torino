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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterBoolean,
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
    PIXEL_RES = 'PIXEL_RES'
    P1P = 'P1P'
    P2P = 'P2P'
    P3P = 'P3P'
    P4P = 'P4P'
    P5P = 'P5P'
    P6P = 'P6P'
    P7P = 'P7P'
    P8P = 'P8P'
    P9P = 'P9P'
    P10P = 'P10P'
    P1F = 'P1F'
    P2F = 'P2F'
    P3F = 'P3F'
    P4F = 'P4F'
    P5F = 'P5F'
    P6F = 'P6F'
    P7F = 'P7F'
    P8F = 'P8F'
    P9F = 'P9F'
    P10F = 'P10F'
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
        return 'SE Biodiversita'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Biodiversita')

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
        return self.tr("Algoritmo per il calcolo della biodiversità, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        edifici_residenziali = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        edifici_industriali = ['assenti o oltre i 500m', 'tra i 250 e i 500 m', 'tra i 100 e i 250 m', 'entro i 100 m']
        edifici_altri = ['assenti o oltre i 500 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        viabilita_pedonale = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        viabilita_ciclo = ['assenti o oltre i 200 m', 'tra i 100 e i 200 m', 'tra i 50 e i 100 m', 'entro i 50 m']
        viabilita_veicolare = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        viabilita_secondaria = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        attrezzata = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        trasformazione = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        discarica = ['assenti o oltre i 500m', 'tra i 250 e i 500 m', 'tra i 100 e i 250 m', 'entro i 100 m']
                
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT1,
                self.tr('Raster Stato attuale'),
                [QgsProcessing.TypeRaster]
            )
        )
        
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT2,
                self.tr('Raster Stato di progetto'),
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
            QgsProcessingParameterNumber(
            self.INPUT3,
            self.tr('Anno attuale'),
            QgsProcessingParameterNumber.Integer,
            2021
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P1P,
                self.tr('Presenza di EDIFICI RESIDENZIALI stato attuale:'),
                edifici_residenziali,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P2P,
                self.tr('Presenza di EDIFICI INDUSTRIALI nello stato attuale:'),
                edifici_industriali,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P3P,
                self.tr('Presenza di ALTRI EDIFICI nello stato attuale:'),
                edifici_altri,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P4P,
                self.tr('Presenza di AREA CIRCOLAZIONE VEICOLARE nello stato attuale:'),
                viabilita_veicolare,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P5P,
                self.tr('Presenza di AREA DI CIRCOLAZIONE CICLABILE nello stato attuale:'),
                viabilita_ciclo,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P6P,
                self.tr('Presenza di AREA DI CIRCOLAZIONE PEDONALE nello stato attuale:'),
                viabilita_pedonale,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P7P,
                self.tr('Presenza di VIABILITA MISTA SECONDARIA nello stato attuale:'),
                viabilita_secondaria,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P8P,
                self.tr('Presenza di AREA ATTREZZATA DEL SUOLO nello stato attuale:'),
                attrezzata,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P9P,
                self.tr('Presenza di AREA IN TRASFORMAZIONE nello stato attuale:'),
                trasformazione,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P10P,
                self.tr('Presenza di DISCARICA nello stato attuale:'),
                discarica,
                defaultValue=''
            )
        )


        self.addParameter(
            QgsProcessingParameterNumber(
            self.INPUT4,
            self.tr('Anno progetto'),
            QgsProcessingParameterNumber.Integer,
            2030
            )
        )


        self.addParameter(
            QgsProcessingParameterEnum(
                self.P1F,
                self.tr('Presenza di EDIFICI RESIDENZIALI stato di progetto:'),
                edifici_residenziali,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P2F,
                self.tr('Presenza di EDIFICI INDUSTRIALI nello stato di progetto:'),
                edifici_industriali,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P3F,
                self.tr('Presenza di ALTRI EDIFICI nello stato di progetto:'),
                edifici_altri,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P4F,
                self.tr('Presenza di AREA CIRCOLAZIONE VEICOLARE nello stato di progetto:'),
                viabilita_veicolare,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P5F,
                self.tr('Presenza di AREA DI CIRCOLAZIONE CICLABILE nello stato di progetto:'),
                viabilita_ciclo,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P6F,
                self.tr('Presenza di AREA DI CIRCOLAZIONE PEDONALE nello stato di progetto:'),
                viabilita_pedonale,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P7F,
                self.tr('Presenza di VIABILITA MISTA SECONDARIA nello stato di progetto:'),
                viabilita_secondaria,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P8F,
                self.tr('Presenza di AREA ATTREZZATA DEL SUOLO nello stato di progetto:'),
                attrezzata,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P9F,
                self.tr('Presenza di AREA IN TRASFORMAZIONE nello stato di progetto:'),
                trasformazione,
                defaultValue=''
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.P10F,
                self.tr('Presenza di DISCARICA nello stato di progetto:'),
                discarica,
                defaultValue=''
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
        present_raster = self.parameterAsRasterLayer(parameters, self.INPUT1, context)
        ds_present = gdal.Open(present_raster.dataProvider().dataSourceUri())
        arr_present = ds_present.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_present[arr_present < 0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUT2, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()

        # List of options
        edifici_residenziali = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        edifici_industriali = ['assenti o oltre i 500m', 'tra i 250 e i 500 m', 'tra i 100 e i 250 m', 'entro i 100 m']
        edifici_altri = ['assenti o oltre i 500 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        viabilita_pedonale = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        viabilita_ciclo = ['assenti o oltre i 200 m', 'tra i 100 e i 200 m', 'tra i 50 e i 100 m', 'entro i 50 m']
        viabilita_veicolare = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        viabilita_secondaria = ['assenti o oltre i 1000m', 'tra i 500 e i 1000 m', 'tra i 250 e i 500 m', 'entro i 250 m']
        attrezzata = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        trasformazione = ['assenti o oltre i 400 m', 'tra i 200 e i 400 m', 'tra i 100 e i 200 m', 'entro i 100 m']
        discarica = ['assenti o oltre i 500m', 'tra i 250 e i 500 m', 'tra i 100 e i 250 m', 'entro i 100 m']


        # Clean negative values
        arr_future[arr_future < 0] = 0
        values_p = [0, 1, 5, 10]
        p1p_id = self.parameterAsInt(parameters, self.P1P, context)
        p1p = values_p[p1p_id]
        p2p_id = self.parameterAsInt(parameters, self.P2P, context)
        p2p = values_p[p2p_id]
        p3p_id = self.parameterAsInt(parameters, self.P3P, context)
        p3p = values_p[p3p_id]
        p4p_id = self.parameterAsInt(parameters, self.P4P, context)
        p4p = values_p[p4p_id]
        p5p_id = self.parameterAsInt(parameters, self.P5P, context)
        p5p = values_p[p5p_id]
        p6p_id = self.parameterAsInt(parameters, self.P6P, context)
        p6p = values_p[p6p_id]
        p7p_id = self.parameterAsInt(parameters, self.P7P, context)
        p7p = values_p[p7p_id]
        p8p_id = self.parameterAsInt(parameters, self.P8P, context)
        p8p = values_p[p8p_id]
        p9p_id = self.parameterAsInt(parameters, self.P9P, context)
        p9p = values_p[p9p_id]
        p10p_id = self.parameterAsInt(parameters, self.P10P, context)
        p10p = values_p[p10p_id]
        p_sum_p = p1p + p2p + p3p + p4p + p5p + p6p + p7p + p8p + p9p + p10p

        p1f_id = self.parameterAsInt(parameters, self.P1F, context)
        p1f = values_p[p1f_id]
        p2f_id = self.parameterAsInt(parameters, self.P2F, context)
        p2f = values_p[p2f_id]
        p3f_id = self.parameterAsInt(parameters, self.P3F, context)
        p3f = values_p[p3f_id]
        p4f_id = self.parameterAsInt(parameters, self.P4F, context)
        p4f = values_p[p4f_id]
        p5f_id = self.parameterAsInt(parameters, self.P5F, context)
        p5f = values_p[p5f_id]
        p6f_id = self.parameterAsInt(parameters, self.P6F, context)
        p6f = values_p[p6f_id]
        p7f_id = self.parameterAsInt(parameters, self.P7F, context)
        p7f = values_p[p7f_id]
        p8f_id = self.parameterAsInt(parameters, self.P8F, context)
        p8f = values_p[p8f_id]
        p9f_id = self.parameterAsInt(parameters, self.P9F, context)
        p9f = values_p[p9f_id]
        p10f_id = self.parameterAsInt(parameters, self.P10F, context)
        p10f = values_p[p10f_id]
        p_sum_f = p1f + p2f + p3f + p4f + p5f + p6f + p7f + p8f + p9f + p10f

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        # Scores of single lucode
        H_score_lucode = {}
        H_score_lucode[1] = 0.4
        H_score_lucode[2] = 0.4
        H_score_lucode[3] = 0
        H_score_lucode[4] = 0.5
        H_score_lucode[5] = 0.5
        H_score_lucode[6] = 0.5
        H_score_lucode[7] = 0.1
        H_score_lucode[8] = 0
        H_score_lucode[9] = 0.15
        H_score_lucode[10] = 0.05
        H_score_lucode[11] = 0
        H_score_lucode[12] = 0.05
        H_score_lucode[13] = 0
        H_score_lucode[14] = 0.05
        H_score_lucode[15] = 0
        H_score_lucode[16] = 0.05
        H_score_lucode[17] = 0.15
        H_score_lucode[18] = 0
        H_score_lucode[19] = 0.1
        H_score_lucode[20] = 0
        H_score_lucode[21] = 1
        H_score_lucode[22] = 0.85
        H_score_lucode[23] = 0.6
        H_score_lucode[24] = 0.25
        H_score_lucode[25] = 0
        H_score_lucode[26] = 0.15
        H_score_lucode[27] = 0.1
        H_score_lucode[28] = 0
        H_score_lucode[29] = 0.5
        H_score_lucode[30] = 0.4
        H_score_lucode[31] = 1
        H_score_lucode[32] = 0
        H_score_lucode[33] = 0
        H_score_lucode[34] = 0.1
        H_score_lucode[35] = 0
        H_score_lucode[36] = 0
        H_score_lucode[37] = 0.5
        H_score_lucode[38] = 0.75
        H_score_lucode[39] = 0.5
        H_score_lucode[40] = 0.4
        H_score_lucode[41] = 0.4
        H_score_lucode[42] = 0.4
        H_score_lucode[43] = 0.5
        H_score_lucode[44] = 0.3
        H_score_lucode[45] = 0.5
        H_score_lucode[46] = 0.15
        H_score_lucode[47] = 0
        H_score_lucode[48] = 0.35
        H_score_lucode[49] = 0.1
        H_score_lucode[50] = 0
        H_score_lucode[51] = 0
        H_score_lucode[52] = 0
        H_score_lucode[53] = 0.15
        H_score_lucode[54] = 0.05
        H_score_lucode[55] = 0
        H_score_lucode[56] = 0
        H_score_lucode[57] = 0.45
        H_score_lucode[58] = 0.4
        H_score_lucode[59] = 0.4
        H_score_lucode[60] = 0
        H_score_lucode[61] = 0.45
        H_score_lucode[62] = 0.65
        H_score_lucode[63] = 0.55
        H_score_lucode[64] = 0.4
        H_score_lucode[65] = 0.4
        H_score_lucode[66] = 0
        H_score_lucode[67] = 0
        H_score_lucode[68] = 0.5
        H_score_lucode[69] = 0.65
        H_score_lucode[70] = 0.55
        H_score_lucode[71] = 0.05
        H_score_lucode[72] = 0
        H_score_lucode[73] = 0.4
        H_score_lucode[74] = 0.5
        H_score_lucode[75] = 0.4
        H_score_lucode[76] = 0.4
        H_score_lucode[77] = 0
        H_score_lucode[78] = 0.7
        H_score_lucode[79] = 0.55
        H_score_lucode[80] = 0
        H_score_lucode[81] = 0
        H_score_lucode[82] = 0.9
        H_score_lucode[83] = 1
        H_score_lucode[84] = 1
        H_score_lucode[85] = 0.75
        H_score_lucode[86] = 0.6
        H_score_lucode[87] = 1

        [rows, cols] = arr_present.shape


        # Assigning scores for each distinct lucode
        Q_pres = np.zeros((rows, cols))
        Q_fut = np.zeros((rows, cols))
        for lucode in np.unique(np.concatenate((arr_present, arr_future))):
            try:
                if p_sum_p == 0:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode]
                if p_sum_p == 1:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.80
                if p_sum_p == 2:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.75
                if p_sum_p == 3:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.70
                if p_sum_p == 4:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.60
                if p_sum_p == 5:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.50
                if p_sum_p == 6:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.45
                if p_sum_p == 7:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.40
                if p_sum_p == 8:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.30
                if p_sum_p == 9:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.20
                if p_sum_p >= 10:
                    Q_pres[np.where(arr_present == lucode)] = H_score_lucode[lucode] * 0.10
            except:
                pass
            try:
                if p_sum_f == 0:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode]
                if p_sum_f == 1:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.80
                if p_sum_f == 2:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.75
                if p_sum_f == 3:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.70
                if p_sum_f == 4:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.60
                if p_sum_f == 5:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.50
                if p_sum_f == 6:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.45
                if p_sum_f == 7:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.40
                if p_sum_f == 8:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.30
                if p_sum_f == 9:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.20
                if p_sum_f >= 10:
                    Q_fut[np.where(arr_future == lucode)] = H_score_lucode[lucode] * 0.10
            except:
                pass

        # Dictionary of economic value for each lucode
        value_lucode = {}
        value_lucode[1] = 0.16
        value_lucode[2] = 0.16
        value_lucode[3] = 0
        value_lucode[4] = 0.16
        value_lucode[5] = 0.16
        value_lucode[6] = 0.16
        value_lucode[7] = 0.03
        value_lucode[8] = 0
        value_lucode[9] = 0.23
        value_lucode[10] = 0.23
        value_lucode[11] = 0
        value_lucode[12] = 0.01
        value_lucode[13] = 0
        value_lucode[14] = 0.01
        value_lucode[15] = 0
        value_lucode[16] = 0.01
        value_lucode[17] = 0.23
        value_lucode[18] = 0
        value_lucode[19] = 0.03
        value_lucode[20] = 0
        value_lucode[21] = 0.23
        value_lucode[22] = 0.23
        value_lucode[23] = 0.03
        value_lucode[24] = 0.01
        value_lucode[25] = 0
        value_lucode[26] = 0.03
        value_lucode[27] = 0.01
        value_lucode[28] = 0
        value_lucode[29] = 0.16
        value_lucode[30] = 0.16
        value_lucode[31] = 0
        value_lucode[32] = 0.03
        value_lucode[33] = 0.01
        value_lucode[34] = 0.01
        value_lucode[35] = 0
        value_lucode[36] = 0
        value_lucode[37] = 0.16
        value_lucode[38] = 0
        value_lucode[39] = 0.16
        value_lucode[40] = 0.16
        value_lucode[41] = 0.16
        value_lucode[42] = 0.16
        value_lucode[43] = 0.03
        value_lucode[44] = 0.03
        value_lucode[45] = 0
        value_lucode[46] = 0.03
        value_lucode[47] = 0
        value_lucode[48] = 0.03
        value_lucode[49] = 0.01
        value_lucode[50] = 0
        value_lucode[51] = 0
        value_lucode[52] = 0
        value_lucode[53] = 0.03
        value_lucode[54] = 0.01
        value_lucode[55] = 0
        value_lucode[56] = 0
        value_lucode[57] = 0.16
        value_lucode[58] = 0.16
        value_lucode[59] = 0.16
        value_lucode[60] = 0
        value_lucode[61] = 0.16
        value_lucode[62] = 0.16
        value_lucode[63] = 0.16
        value_lucode[64] = 0.16
        value_lucode[65] = 0.16
        value_lucode[66] = 0
        value_lucode[67] = 0
        value_lucode[68] = 0.16
        value_lucode[69] = 0.16
        value_lucode[70] = 0
        value_lucode[71] = 0.03
        value_lucode[72] = 0
        value_lucode[73] = 0.16
        value_lucode[74] = 0.16
        value_lucode[75] = 0.16
        value_lucode[76] = 0.16
        value_lucode[77] = 0
        value_lucode[78] = 0
        value_lucode[79] = 0.16
        value_lucode[80] = 0
        value_lucode[81] = 0.91
        value_lucode[82] = 0.91
        value_lucode[83] = 0.91
        value_lucode[84] = 0.91
        value_lucode[85] = 0.91
        value_lucode[86] = 0.91
        value_lucode[87] = 0.91

        value_pres = np.zeros((rows, cols))
        value_fut = np.zeros((rows, cols))
        for lucode in np.unique(np.concatenate((arr_present, arr_future))):
            try:
                value_pres[np.where(arr_present == lucode)] = value_lucode[lucode] * Q_pres[
                    np.where(arr_present == lucode)] * area_pixel
                value_fut[np.where(arr_future == lucode)] = value_lucode[lucode] * Q_fut[
                    np.where(arr_future == lucode)] * area_pixel
            except:
                pass
        # Years
        present = self.parameterAsInt(parameters, self.INPUT3, context)
        future = self.parameterAsInt(parameters, self.INPUT4, context)
        
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/07_biodiversità_presente_Q.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(Q_pres)

        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/07_biodiversità_futuro_Q.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(Q_fut)

        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_07_biodiversità_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(value_fut - value_pres)

        outdata.FlushCache() ##saves to disk!!
        outdata = None
        band = None
        ds = None
        report_output = path_output + '/SE_biodiversità.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi della biodiversità\n")
        f.write("Data: " + today +"\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % (present))
        f.write("Edifici residenziali: %s \n" % (edifici_residenziali[p1p_id]))
        f.write("Edifici industriali: %s \n" % (edifici_industriali[p2p_id]))
        f.write("Edifici altri: %s \n" % (edifici_altri[p3p_id]))
        f.write("Viabilita pedonale: %s \n" % (viabilita_pedonale[p4p_id]))
        f.write("Viabilita ciclo: %s \n" % (viabilita_ciclo[p5p_id]))
        f.write("Viabilita veicolare: %s \n" % (viabilita_veicolare[p6p_id]))
        f.write("Viabilita secondaria: %s \n" % (viabilita_secondaria[p7p_id]))
        f.write("Attrezzata: %s \n" % (attrezzata[p8p_id]))
        f.write("Trasformazione: %s \n" % (trasformazione[p9p_id]))
        f.write("Discarica: %s \n" % (discarica[p10p_id]))
        f.write("\n\n")
        f.write("Valore della biodiversità nello stato attuale (0-1): %f \n" % (np.mean(Q_pres)))
        f.write("Valore totale della biodiversità (€): %f \n\n\n" % (np.sum(value_pres)))
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % (future))
        f.write("Edifici residenziali: %s \n" % (edifici_residenziali[p1f_id]))
        f.write("Edifici industriali: %s \n" % (edifici_industriali[p2f_id]))
        f.write("Edifici altri: %s \n" % (edifici_altri[p3f_id]))
        f.write("Viabilita pedonale: %s \n" % (viabilita_pedonale[p4f_id]))
        f.write("Viabilita ciclo: %s \n" % (viabilita_ciclo[p5f_id]))
        f.write("Viabilita veicolare: %s \n" % (viabilita_veicolare[p6f_id]))
        f.write("Viabilita secondaria: %s \n" % (viabilita_secondaria[p7f_id]))
        f.write("Attrezzata: %s \n" % (attrezzata[p8f_id]))
        f.write("Trasformazione: %s \n" % (trasformazione[p9f_id]))
        f.write("Discarica: %s \n" % (discarica[p10f_id]))
        f.write("\n\n")
        f.write("Valore della biodiversità nello stato di progetto (0-1): %f \n" % (np.mean(Q_fut)))
        f.write("Valore totale della biodiversità (€): %f \n\n\n" % (np.sum(value_fut)))
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza di valore della biodiversità: %f \n" % (np.mean(Q_fut-Q_pres)))
        f.write("Differenza in termini economici del SE di biodiversità (stato di progetto – stato attuale) (€):%d \n" % (
            np.sum(value_fut - value_pres)))
        return {self.OUTPUT: 'completed'}

        
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

