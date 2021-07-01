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
                       QgsProcessingParameterBoolean,
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
    BELP = 'BELP'
    FIU1P = 'FIU1P'
    NATP = 'NATP'    
    FIU2P = 'FIU2P' 
    ALBP = 'ALBP'
    PA1P = 'PA1P'
    PA2P = 'PA2P'    
    PA3P = 'PA3P' 
    GIAP = 'GIAP'
    GIOP = 'GIOP'
    PIAP = 'PIAP'
    CANP = 'CANP'
    CHIP = 'CHIP'
    SERP = 'SERP'
    FONP = 'FONP'
    BELF = 'BELF'
    FIU1F = 'FIU1F'
    NATF = 'NATF'    
    FIU2F = 'FIU2F' 
    ALBF = 'ALBF'
    PA1F = 'PA1F'
    PA2F = 'PA2F'    
    PA3F = 'PA3F' 
    GIAF = 'GIAF'
    GIAF = 'GIAF'
    GIOF = 'GIOF'
    PIAF = 'PIAF'
    CANF = 'CANF'
    CHIF = 'CHIF'
    SERF = 'SERF'
    FONF = 'FONF'
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
        return 'SE  Benefici sociali'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('SE Benefici sociali')

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
        return self.tr("Algoritmo per il calcolo dei benefici sociali, nell'ambito del calcolo dei Servizi Ecosistemici per la Città di Torino")

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
                self.tr('Raster Uso suolo Stato attuale'),
                [QgsProcessing.TypeRaster]
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
            QgsProcessingParameterBoolean(
            self.BELP,
            self.tr('Presenza di Belvedere (punto panoramico)'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FIU1P,
            self.tr('Presenza di Corso acqua primario nell area o entro 200m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.NATP,
            self.tr('Presenza di Area Natura 2000 o area protetta'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FIU2P,
            self.tr('Presenza di Corso acqua secondario nell area o entro 200m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.ALBP,
            self.tr('Presenza di Albero Monumentale'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA1P,
            self.tr('Presenza di Parco urbano >2 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA2P,
            self.tr('Presenza di Parco urbano tra 0,5 e 2 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA3P,
            self.tr('Presenza di Parco urbano < 0,5 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.GIAP,
            self.tr('Presenza di un Giardino storico'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.GIOP,
            self.tr('Presenza di Area giochi in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PIAP,
            self.tr('Presenza di Piastra sportiva attrazzata in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.CANP,
            self.tr('Presenza di Area cani in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.CHIP,
            self.tr('Presenza di Chiosco in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.SERP,
            self.tr('Presenza di Servizi igienici in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FONP,
            self.tr('Presenza di Fontana in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUTRF,
                self.tr('Raster Uso suolo Stato di progetto'),
                [QgsProcessing.TypeRaster]
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
            QgsProcessingParameterBoolean(
            self.BELF,
            self.tr('Presenza di Belvedere (punto panoramico)'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FIU1F,
            self.tr('Presenza di Corso acqua primario nell area o entro 200m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.NATF,
            self.tr('Presenza di Area Natura 2000 o area protetta'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FIU2F,
            self.tr('Presenza di Corso acqua secondario nell area o entro 200m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.ALBF,
            self.tr('Presenza di Albero Monumentale'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA1F,
            self.tr('Presenza di Parco urbano >2 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA2F,
            self.tr('Presenza di Parco urbano tra 0,5 e 2 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PA3F,
            self.tr('Presenza di Parco urbano < 0,5 ha'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.GIAF,
            self.tr('Presenza di un Giardino storico'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.GIOF,
            self.tr('Presenza di Area giochi in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.PIAF,
            self.tr('Presenza di Piastra sportiva attrazzata in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.CANF,
            self.tr('Presenza di Area cani in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.CHIF,
            self.tr('Presenza di Chiosco in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.SERF,
            self.tr('Presenza di Servizi igienici in un buffer di 100m'),
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
            self.FONF,
            self.tr('Presenza di Fontana in un buffer di 100m'),
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

        # # Load natural aspects raster
        # natural_aspects_raster = self.parameterAsRasterLayer(parameters, self.ASPNAT, context)
        # ds_natural_aspects = gdal.Open(natural_aspects_raster.dataProvider().dataSourceUri())
        # arr_natural_aspects = ds_natural_aspects.GetRasterBand(1).ReadAsArray()
        # # Clean negative values
        # arr_natural_aspects[arr_natural_aspects < 0] = 0
        #
        # # Load urban green raster
        # urban_green_raster = self.parameterAsRasterLayer(parameters, self.VERDURB, context)
        # ds_urban_green = gdal.Open(urban_green_raster.dataProvider().dataSourceUri())
        # arr_urban_green = ds_urban_green.GetRasterBand(1).ReadAsArray()
        # # Clean negative values
        # arr_urban_green[arr_urban_green < 0] = 0

        # Load future raster
        future_raster = self.parameterAsRasterLayer(parameters, self.INPUTRF, context)
        ds_future = gdal.Open(future_raster.dataProvider().dataSourceUri())
        arr_future = ds_future.GetRasterBand(1).ReadAsArray()
        # Clean negative values
        arr_future[arr_future < 0] = 0

        # Load natural aspects booleans present
        natural_aspects_bool_pres = []
        natural_aspects_bool_pres.append(self.parameterAsBool(parameters, self.BELP, context))
        natural_aspects_bool_pres.append(self.parameterAsBool(parameters, self.FIU1P, context))
        natural_aspects_bool_pres.append(self.parameterAsBool(parameters, self.NATP, context))
        natural_aspects_bool_pres.append(self.parameterAsBool(parameters, self.FIU2P, context))
        natural_aspects_bool_pres.append(self.parameterAsBool(parameters, self.ALBP, context))

        # Load urban green booleans present
        urban_green_bool_pres = []
        urban_green_bool_pres.append(self.parameterAsBool(parameters, self.PA1P, context))
        urban_green_bool_pres.append(self.parameterAsBool(parameters, self.PA2P, context))
        urban_green_bool_pres.append(self.parameterAsBool(parameters, self.PA3P, context))
        urban_green_bool_pres.append(self.parameterAsBool(parameters, self.GIAP, context))

        # Load fruibility booleans present
        fruibility_bool_pres = []
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.GIOP, context))
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.PIAP, context))
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.CANP, context))
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.CHIP, context))
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.SERP, context))
        fruibility_bool_pres.append(self.parameterAsBool(parameters, self.FONP, context))

        # Load natural aspects booleans future
        natural_aspects_bool_fut = []
        natural_aspects_bool_fut.append(self.parameterAsBool(parameters, self.BELF, context))
        natural_aspects_bool_fut.append(self.parameterAsBool(parameters, self.FIU1F, context))
        natural_aspects_bool_fut.append(self.parameterAsBool(parameters, self.NATF, context))
        natural_aspects_bool_fut.append(self.parameterAsBool(parameters, self.FIU2F, context))
        natural_aspects_bool_fut.append(self.parameterAsBool(parameters, self.ALBF, context))

        # Load urban green booleans future
        urban_green_bool_fut = []
        urban_green_bool_fut.append(self.parameterAsBool(parameters, self.PA1F, context))
        urban_green_bool_fut.append(self.parameterAsBool(parameters, self.PA2F, context))
        urban_green_bool_fut.append(self.parameterAsBool(parameters, self.PA3F, context))
        urban_green_bool_fut.append(self.parameterAsBool(parameters, self.GIAF, context))

        # Load fruibility booleans future
        fruibility_bool_fut = []
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.GIOF, context))
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.PIAF, context))
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.CANF, context))
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.CHIF, context))
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.SERF, context))
        fruibility_bool_fut.append(self.parameterAsBool(parameters, self.FONF, context))

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        # Scores of single lucode
        score_lucode = {}
        score_lucode[1] = 0.4
        score_lucode[2] = 0.4
        score_lucode[3] = 0.1
        score_lucode[4] = 0.1
        score_lucode[5] = 0.4
        score_lucode[6] = 0.4
        score_lucode[7] = 0.1
        score_lucode[8] = 0
        score_lucode[9] = 0.2
        score_lucode[10] = 0.2
        score_lucode[11] = 0.2
        score_lucode[12] = 0.2
        score_lucode[13] = 0.2
        score_lucode[14] = 0.2
        score_lucode[15] = 0.1
        score_lucode[16] = 0.1
        score_lucode[17] = 0.3
        score_lucode[18] = 0.2
        score_lucode[19] = 0.3
        score_lucode[20] = 0
        score_lucode[21] = 0.9
        score_lucode[22] = 0.8
        score_lucode[23] = 0.7
        score_lucode[24] = 0.5
        score_lucode[25] = 0.2
        score_lucode[26] = 0.6
        score_lucode[27] = 0.5
        score_lucode[28] = 0.6
        score_lucode[29] = 0.5
        score_lucode[30] = 0.4
        score_lucode[31] = 0.9
        score_lucode[32] = 0
        score_lucode[33] = 0
        score_lucode[34] = 0.1
        score_lucode[35] = 0
        score_lucode[36] = 0
        score_lucode[37] = 0.4
        score_lucode[38] = 0.6
        score_lucode[39] = 0.5
        score_lucode[40] = 0.4
        score_lucode[41] = 0.4
        score_lucode[42] = 0.4
        score_lucode[43] = 0.3
        score_lucode[44] = 0.2
        score_lucode[45] = 0.7
        score_lucode[46] = 0
        score_lucode[47] = 0
        score_lucode[48] = 0.1
        score_lucode[49] = 0.1
        score_lucode[50] = 0
        score_lucode[51] = 0
        score_lucode[52] = 0
        score_lucode[53] = 0.2
        score_lucode[54] = 0.1
        score_lucode[55] = 0
        score_lucode[56] = 0.1
        score_lucode[57] = 0.4
        score_lucode[58] = 0.3
        score_lucode[59] = 0.4
        score_lucode[60] = 0
        score_lucode[61] = 0.7
        score_lucode[62] = 0.8
        score_lucode[63] = 0.7
        score_lucode[64] = 0.4
        score_lucode[65] = 0.4
        score_lucode[66] = 0
        score_lucode[67] = 0
        score_lucode[68] = 0.6
        score_lucode[69] = 0.8
        score_lucode[70] = 0.6
        score_lucode[71] = 0.1
        score_lucode[72] = 0
        score_lucode[73] = 0.4
        score_lucode[74] = 0.4
        score_lucode[75] = 0.4
        score_lucode[76] = 0.4
        score_lucode[77] = 0
        score_lucode[78] = 0.8
        score_lucode[79] = 0.4
        score_lucode[80] = 0
        score_lucode[81] = 0
        score_lucode[82] = 0.8
        score_lucode[83] = 0.9
        score_lucode[84] = 0.9
        score_lucode[85] = 0.75
        score_lucode[86] = 0.6
        score_lucode[87] = 0.9

        # Economic values of each lucode
        value_lucode = {}
        value_lucode[1] = 1.44
        value_lucode[2] = 1.44
        value_lucode[3] = 0
        value_lucode[4] = 1.44
        value_lucode[5] = 1.44
        value_lucode[6] = 1.44
        value_lucode[7] = 1.44
        value_lucode[8] = 0
        value_lucode[9] = 2.36
        value_lucode[10] = 2.36
        value_lucode[11] = 0
        value_lucode[12] = 0
        value_lucode[13] = 0
        value_lucode[14] = 0
        value_lucode[15] = 0
        value_lucode[16] = 0
        value_lucode[17] = 2.36
        value_lucode[18] = 0
        value_lucode[19] = 1.44
        value_lucode[20] = 0
        value_lucode[21] = 2.36
        value_lucode[22] = 2.36
        value_lucode[23] = 2.36
        value_lucode[24] = 2.36
        value_lucode[25] = 0
        value_lucode[26] = 2.36
        value_lucode[27] = 2.36
        value_lucode[28] = 0
        value_lucode[29] = 1.44
        value_lucode[30] = 1.44
        value_lucode[31] = 0
        value_lucode[32] = 0
        value_lucode[33] = 0
        value_lucode[34] = 0
        value_lucode[35] = 0
        value_lucode[36] = 0
        value_lucode[37] = 1.44
        value_lucode[38] = 1.44
        value_lucode[39] = 1.44
        value_lucode[40] = 1.44
        value_lucode[41] = 1.44
        value_lucode[42] = 1.44
        value_lucode[43] = 1.44
        value_lucode[44] = 1.44
        value_lucode[45] = 0
        value_lucode[46] = 0
        value_lucode[47] = 0
        value_lucode[48] = 0
        value_lucode[49] = 0
        value_lucode[50] = 0
        value_lucode[51] = 0
        value_lucode[52] = 0
        value_lucode[53] = 0
        value_lucode[54] = 0
        value_lucode[55] = 0
        value_lucode[56] = 0
        value_lucode[57] = 1.44
        value_lucode[58] = 1.44
        value_lucode[59] = 1.44
        value_lucode[60] = 0
        value_lucode[61] = 1.44
        value_lucode[62] = 1.44
        value_lucode[63] = 1.44
        value_lucode[64] = 1.44
        value_lucode[65] = 1.44
        value_lucode[66] = 0
        value_lucode[67] = 0
        value_lucode[68] = 1.44
        value_lucode[69] = 1.44
        value_lucode[70] = 1.44
        value_lucode[71] = 0
        value_lucode[72] = 0
        value_lucode[73] = 1.44
        value_lucode[74] = 1.44
        value_lucode[75] = 1.44
        value_lucode[76] = 1.44
        value_lucode[77] = 0
        value_lucode[78] = 0
        value_lucode[79] = 1.44
        value_lucode[80] = 0
        value_lucode[81] = 0
        value_lucode[82] = 1.49
        value_lucode[83] = 1.49
        value_lucode[84] = 1.49
        value_lucode[85] = 1.49
        value_lucode[86] = 1.49
        value_lucode[87] = 1.49

        score_natural_aspects = np.array([0.9, 0.8, 0.8, 0.65, 0.7])

        score_urban_green = [1, 0.9, 0.8, 0.7]

        score_acc ={}
        score_acc[11] = 0.9
        score_acc[13] = 0.7
        score_acc[3] = 0.7

        score_fr = [0.9, 0.8, 0.7, 0.5, 0.4, 0.7]

        [rows, cols] = arr_present.shape

        # Compute total score natural aspects present
        natural_aspects_norm_pres = np.sum(np.array(natural_aspects_bool_pres) * score_natural_aspects) / 2.95

        # Compute total score urban green present
        urban_green_norm_pres = np.sum(np.array(urban_green_bool_pres) * score_urban_green) / 1.7

        # Compute total score fruibility present
        fruibility_norm_pres = np.sum(np.array(fruibility_bool_pres) * score_fr) / 3.6

        # Compute total score natural aspects future
        natural_aspects_norm_fut = np.sum(np.array(natural_aspects_bool_fut) * score_natural_aspects) / 2.95

        # Compute total score urban green future
        urban_green_norm_fut = np.sum(np.array(urban_green_bool_fut) * score_urban_green) / 1.7

        # Compute total score fruibility future
        fruibility_norm_fut = np.sum(np.array(fruibility_bool_fut) * score_fr) / 3.6

        # Value euro per squared meter
        score_lucode_tot_present = 0
        acc_score_tot = 0
        ROS_present_array = np.zeros((rows, cols))
        # Summing scores for each distinct lucode
        for lucode in np.unique(arr_present):
            try:
                score_lucode_tot_present += score_lucode[lucode]
                acc_score_tot += score_acc[lucode]
                ROS_present_array[np.where(arr_present == lucode)] = 1
            except:
                pass
        acc_score_tot = acc_score_tot / 2.3
        PR_present = (score_lucode_tot_present + natural_aspects_norm_pres + urban_green_norm_pres) / 3
        acc_fr_present = (acc_score_tot + fruibility_norm_pres) / 2
        ROS_present = PR_present * 0.3 + (acc_fr_present * 0.7)
        ROS_present_array = ROS_present_array * ROS_present
        value_tot_present = 0
        n_pixel_valid_present = 0
        for lucode in np.unique(arr_present):
            try:
                area_lucode = np.sum(arr_present == lucode) * area_pixel
                value_tot_present += area_lucode * ROS_present * value_lucode[lucode]
                n_pixel_valid_present += np.sum(arr_present == lucode)
            except:
                pass

        # Value euro per squared meter
        score_lucode_tot_future = 0
        acc_score_tot = 0
        ROS_future_array = np.zeros((rows, cols))
        for lucode in np.unique(arr_future):
            try:
                score_lucode_tot_future += score_lucode[lucode]
                acc_score_tot += score_acc[lucode]
                ROS_future_array[np.where(arr_future == lucode)] = 1
            except:
                pass
        acc_score_tot = acc_score_tot / 2.3
        PR_future = (score_lucode_tot_future + natural_aspects_norm_fut + urban_green_norm_fut) / 3
        acc_fr_future = (acc_score_tot + fruibility_norm_fut) / 2
        ROS_future = PR_future * 0.3 + (acc_fr_future * 0.7)
        ROS_future_array = ROS_future_array * ROS_future
        value_tot_future = 0
        n_pixel_valid_future = 0
        for lucode in np.unique(arr_future):
            try:
                area_lucode = np.sum(arr_future == lucode) * area_pixel
                value_tot_future += area_lucode * ROS_future * value_lucode[lucode]
                n_pixel_valid_future += np.sum(arr_future == lucode)
            except:
                pass
        # Years
        present = self.parameterAsInt(parameters, self.INPUTPRE, context)
        future = self.parameterAsInt(parameters, self.INPUTFUT, context)
        # Initialize and write on output raster present
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/06_benefici_sociali_presente_ROS.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows,  1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(ROS_present_array)
        outdata.FlushCache()
        # Initialize and write on output raster future
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/06_benefici_sociali_futuro_ROS.tiff'
        driver = gdal.GetDriverByName("GTiff")
        outdata = driver.Create(file_output, cols, rows,  1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(ROS_future_array)
        outdata.FlushCache()
        # Initialize and write on output raster
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        file_output = path_output + '/SE_06_benefici_sociali_delta_euro.tiff'
        driver = gdal.GetDriverByName("GTiff")
        arr_output = np.zeros((rows, cols))
        arr_output[np.where(arr_present < 88)] = value_tot_future - value_tot_present
        outdata = driver.Create(file_output, cols, rows,  1, gdal.GDT_Float64)
        outdata.SetGeoTransform(ds_present.GetGeoTransform())  ##sets same geotransform as input
        outdata.SetProjection(ds_present.GetProjection())  ##sets same projection as input
        outdata.GetRasterBand(1).WriteArray(arr_output)
        print(np.max(outdata.GetRasterBand(1).ReadAsArray()))
        outdata.FlushCache()  ##saves to disk!!
        outdata = None
        band = None
        ds = None
        report_output = path_output + '/SE_benefici_sociali.txt'
        f = open(report_output, "w+")
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        f.write("Sommario dell'analisi dei benefici_sociali\n")
        f.write("Data: " + today + "\n\n\n")
        f.write("Analisi stato di fatto\n\n")
        f.write("Anno corrente: %i \n" % present)
        f.write(
            "Valore ROS - Stato attuale : : %f \n" % (
                ROS_present))
        f.write(
            "Valore ROS medio - Stato attuale : : %f \n" % (
                np.sum(ROS_present_array) / n_pixel_valid_present))
        f.write(
            "Valore medio dei benefici_sociali per unità di superficie - Stato attuale (€/ha): : %f \n" % (
                (value_tot_present / (n_pixel_valid_present * area_pixel)) * 10000))
        f.write("Valore totale dei SE culturali (€): %f \n\n\n" % value_tot_present)
        f.write("Analisi stato di progetto\n\n")
        f.write("Anno progetto: %i \n" % future)
        f.write(
            "Valore ROS - Stato progetto : : %f \n" % (
                ROS_future))
        f.write(
            "Valore ROS medio - Stato progetto : : %f \n" % (
                np.sum(ROS_future_array) / n_pixel_valid_future))
        f.write(
            "Valore medio dei benefici_sociali per unità di superficie - Stato di progetto (€/ha): %f \n" % (
                    (value_tot_future / (n_pixel_valid_future * area_pixel)) * 10000))
        f.write("Valore totale del dei benefici_sociali (€): %f \n\n\n" % value_tot_future)
        f.write("Differenze tra stato di progetto e stato attuale\n\n")
        f.write("Anno progetto: %i - %i\n" % (present, future))
        f.write("Differenza dei benefici_sociali per unità di superficie (€/ha): %f \n" % (
            ((value_tot_future - value_tot_present) / (n_pixel_valid_present * area_pixel)) * 10000))
        f.write(
            "Differenza in termini economici dei benefici_sociali (stato di progetto – stato attuale) (€):%d \n" % (
                (value_tot_future - value_tot_present)))

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

