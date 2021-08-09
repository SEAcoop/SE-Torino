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
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFolderDestination)
import numpy as np
import gdal

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

    INPUT = 'INPUT'
    CONCNO2='CONCNO2'
    CONCPM10='CONCPM10'
    VEL='VEL'
    SPECIE1 = 'SPECIE1'
    ESEMPL1 = 'ESEMPL1'
    SPECIE2 = 'SPECIE2'
    ESEMPL2 = 'ESEMPL2'    
    SPECIE3 = 'SPECIE3'
    ESEMPL3 = 'ESEMPL3'
    SPECIE4 = 'SPECIE4'
    ESEMPL4 = 'ESEMPL4'    
    SPECIE5 = 'SPECIE5'
    ESEMPL5 = 'ESEMPL5'
    OUTPUT = 'OUTPUT'
    STATO = 'STATO'
    PIXEL_RES = 'PIXEL_RES'

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
        return 'Calcolo Rimozione Inquinanti'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Calcolo Rimozione Inquinanti')

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
        return self.tr("Calcolo Rimozione Inquinanti")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        all_species = ['Abete (Picea abies, glauca, omorika, orientalis, pungens)', 'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)', 'Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)', 'Bagolaro (Celtis australis, occidentalis)',
                       'Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)', 'Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)', 'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)', 'Frassino (Fraxinus americana, excelsior, excelsior Pendula)',
                       'Ippocastano (Aesculus hippocastanum, pavia)', 'Olmo  (Ulmus laevis, minor,parvifolia,pumila)', 'Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)', 'Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)',
                       'Platano (Platanus orientalis, occidentalis, hybrida)', 'Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)', 'Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)']
        stati_list = ['Presente', 'Futuro']
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Raster Uso suolo'),
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

        double_param = QgsProcessingParameterNumber(
            self.CONCNO2,
            self.tr('Concentrazione NO2 [μg/mc]'),
            QgsProcessingParameterNumber.Double,
            43.72
        )
        double_param.setMetadata( {'widget_wrapper': { 'decimals': 2 }} )
        self.addParameter(double_param)

        double_param = QgsProcessingParameterNumber(
            self.CONCPM10,
            self.tr('Concentrazione PM10 [μg/mc]'),
            QgsProcessingParameterNumber.Double,
            30
        )
        double_param.setMetadata( {'widget_wrapper': { 'decimals': 2 }} )
        self.addParameter(double_param)

        double_param = QgsProcessingParameterNumber(
            self.VEL,
            self.tr('Velocità del vento [m/s]'),
            QgsProcessingParameterNumber.Double,
            1.4
        )
        double_param.setMetadata( {'widget_wrapper': { 'decimals': 2 }} )
        self.addParameter(double_param)

        self.addParameter(
            QgsProcessingParameterEnum(
                self.STATO,
                self.tr('Fase'),
                stati_list,
                defaultValue='Presente'
                )
                )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE1,
                self.tr('Specie 1'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL1,
            self.tr('Numero Esemplari Specie 1'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE2,
                self.tr('Specie 2'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL2,
            self.tr('Numero Esemplari Specie 2'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE3,
                self.tr('Specie 3'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL3,
            self.tr('Numero Esemplari Specie 3'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE4,
                self.tr('Specie 4'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL4,
            self.tr('Numero Esemplari Specie 4'),
            QgsProcessingParameterNumber.Integer,
            0
            )
        )
    
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SPECIE5,
                self.tr('Specie 5'),
                all_species,
                defaultValue=''
                )
                )

        self.addParameter(
            QgsProcessingParameterNumber(
            self.ESEMPL5,
            self.tr('Numero Esemplari Specie 5'),
            QgsProcessingParameterNumber.Integer,
            0
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
        # List of all species
        all_species = ['Abete (Picea abies, glauca, omorika, orientalis, pungens)',
                       'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)',
                       'Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)',
                       'Bagolaro (Celtis australis, occidentalis)',
                       'Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)',
                       'Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)',
                       'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)',
                       'Frassino (Fraxinus americana, excelsior, excelsior Pendula)',
                       'Ippocastano (Aesculus hippocastanum, pavia)', 'Olmo  (Ulmus laevis, minor,parvifolia,pumila)',
                       'Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)',
                       'Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)',
                       'Platano (Platanus orientalis, occidentalis, hybrida)',
                       'Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)',
                       'Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)']
        # List of all lucodes with trees
        lucode_list = [7, 9, 17, 19, 21, 23, 26, 29, 32, 38, 43, 44, 46, 48, 53, 57, 62, 69, 70, 74, 82, 83, 84, 85, 86, 87]
        # Collect species and number of plants
        esempl1 = self.parameterAsInt(parameters, self.ESEMPL1, context)
        specie1 = self.parameterAsInt(parameters, self.SPECIE1, context)
        esempl2 = self.parameterAsInt(parameters, self.ESEMPL2, context)
        specie2 = self.parameterAsInt(parameters, self.SPECIE2, context)
        esempl3 = self.parameterAsInt(parameters, self.ESEMPL3, context)
        specie3 = self.parameterAsInt(parameters, self.SPECIE3, context)
        esempl4 = self.parameterAsInt(parameters, self.ESEMPL4, context)
        specie4 = self.parameterAsInt(parameters, self.SPECIE4, context)
        esempl5 = self.parameterAsInt(parameters, self.ESEMPL5, context)
        specie5 = self.parameterAsInt(parameters, self.SPECIE5, context)
        # Conc pm10
        concpm10 = self.parameterAsDouble(parameters, self.CONCPM10, context)
        Vd = 0.064
        # Load lucode raster
        lucode_raster = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        lucode_data_source = gdal.Open(lucode_raster.dataProvider().dataSourceUri())
        arr_lucode = lucode_data_source.GetRasterBand(1).ReadAsArray()
        [rows, cols] = arr_lucode.shape

        # Output parameters
        stati_list = ['Presente', 'Futuro']
        path_output = self.parameterAsString(parameters, self.OUTPUT, context)
        stato = stati_list[self.parameterAsInt(parameters, self.STATO, context)]
        driver = gdal.GetDriverByName("GTiff")
        arr_ozono = np.zeros((rows, cols))
        arr_q = np.zeros((rows, cols))

        area_pixel = self.parameterAsInt(parameters, self.PIXEL_RES, context) * self.parameterAsInt(
            parameters, self.PIXEL_RES, context)

        if (esempl1 > 0):
            arr_lucode_list = np.zeros((rows, cols))
            n_pixel_lucode = 0
            for lucode in np.unique(arr_lucode):
                if lucode in lucode_list:
                    n_pixel_lucode += np.sum(np.where(arr_lucode == lucode))
                    arr_lucode_list[np.where(arr_lucode == lucode)] = 1
            # Initialize dicionary of c sequestration per species
            ozono_species = {}
            ozono_species['Abete (Picea abies, glauca, omorika, orientalis, pungens)'] = 131.01
            ozono_species['Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)'] = 89,10
            ozono_species['Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)'] = 82.33
            ozono_species['Bagolaro (Celtis australis, occidentalis)'] = 207.25
            ozono_species['Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)'] = 56.98
            ozono_species['Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)'] = 206.24
            ozono_species['Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)'] = 23.76
            ozono_species['Frassino (Fraxinus americana, excelsior, excelsior Pendula)'] = 100.70
            ozono_species['Ippocastano (Aesculus hippocastanum, pavia)'] = 115.94
            ozono_species['Olmo  (Ulmus laevis, minor,parvifolia,pumila)'] = 116.61
            ozono_species['Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)'] = 90.25
            ozono_species['Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)'] = 85.20
            ozono_species['Platano (Platanus orientalis, occidentalis, hybrida)'] = 209.79
            ozono_species['Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)'] = 89.54
            ozono_species['Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)'] = 122.20

            # Calculate total carbon sequestration
            ozono = (ozono_species[all_species[specie1]] * esempl1 +\
                ozono_species[all_species[specie2]] * esempl2 +\
                ozono_species[all_species[specie3]] * esempl3 + \
                ozono_species[all_species[specie4]] * esempl4 +\
                ozono_species[all_species[specie5]] * esempl5) / 10e6

            # Sequestration per mq
            ozono_area = ozono / (n_pixel_lucode)
            arr_ozono = arr_lucode_list * ozono_area

            # Initialize dicionary of c sequestration per species
            lai_species = {}
            lai_species['Abete (Picea abies, glauca, omorika, orientalis, pungens)'] = 7.73
            lai_species[
                'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)'] = 5, 41
            lai_species['Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)'] = 4.48
            lai_species['Bagolaro (Celtis australis, occidentalis)'] = 7.52
            lai_species['Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)'] = 4.71
            lai_species['Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)'] = 8.25
            lai_species[
                'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)'] = 3.9
            lai_species['Frassino (Fraxinus americana, excelsior, excelsior Pendula)'] = 4.54
            lai_species['Ippocastano (Aesculus hippocastanum, pavia)'] = 6.13
            lai_species['Olmo  (Ulmus laevis, minor,parvifolia,pumila)'] = 6.66
            lai_species['Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)'] = 5.24
            lai_species['Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)'] = 4.61
            lai_species['Platano (Platanus orientalis, occidentalis, hybrida)'] = 6.38
            lai_species['Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)'] = 0.44
            lai_species['Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)'] = 6.41

            # Initialize dicionary of c sequestration per species
            T_species = {}
            T_species['Abete (Picea abies, glauca, omorika, orientalis, pungens)'] = 365
            T_species[
                'Acero seconda grandezza (Acer campestre, cappadocicum, pseudoplatanus, platanoides, platanoides Schwedleri, platanoides Crimson King, rubrum, saccharinum)'] = 215
            T_species['Acero terza grandezza (Acer negundo, opalus,palmatum, palmatum v. dissectum, x freemanii)'] = 215
            T_species['Bagolaro (Celtis australis, occidentalis)'] = 215
            T_species['Carpino (Carpinus betulus, betulus fastigiata,Ostrya carpinifolia)'] = 215
            T_species['Cedro (Cedrus atlantica, atlantica v. glauca, deodara, libani)'] = 365
            T_species[
                'Ciliegio da fiore (Prunus cerasifera, domestica, fruticosa, Kanzan,pissardii, serrulata, subhirtella)'] = 265
            T_species['Frassino (Fraxinus americana, excelsior, excelsior Pendula)'] = 215
            T_species['Ippocastano (Aesculus hippocastanum, pavia)'] = 215
            T_species['Olmo  (Ulmus laevis, minor,parvifolia,pumila)'] = 215
            T_species['Pino (Pinus halepensis, nigra, pinea, strobus, sylvestris, wallichiana)'] = 365
            T_species['Pioppo (Populus alba,canescens, nigra, nigra var. italica, tremula, x canadensis)'] = 215
            T_species['Platano (Platanus orientalis, occidentalis, hybrida)'] = 215
            T_species['Quercia (Quercus coccinea, ilex, petraea, pubescens, robur, robur Fastigiata, rubra)'] = 215
            T_species['Tiglio (Tilia cordata, cordata Greenspire, platyphyllos, x europaea)'] = 215

            # Calculate total pm10 sequestration
            q_tot = concpm10 * Vd * (T_species[all_species[specie1]] * lai_species[all_species[specie1]] * esempl1 + \
                                 T_species[all_species[specie2]] * lai_species[all_species[specie2]] * esempl2 + \
                                 T_species[all_species[specie3]] * lai_species[all_species[specie3]] * esempl3 + \
                                 T_species[all_species[specie4]] * lai_species[all_species[specie4]] * esempl4 + \
                                 T_species[all_species[specie5]] * lai_species[all_species[specie5]] * esempl5)
            # Calculate total pm10 sequestration
            q_area = q_tot / n_pixel_lucode
            arr_q = arr_lucode_list * q_area
        else:
            ozono_lucode = {}
            ozono_lucode[1] = 0
            ozono_lucode[2] = 0
            ozono_lucode[3] = 0
            ozono_lucode[4] = 0
            ozono_lucode[5] = 0
            ozono_lucode[6] = 0
            ozono_lucode[7] = 4.27
            ozono_lucode[8] = 0
            ozono_lucode[9] = 1.42
            ozono_lucode[10] = 0
            ozono_lucode[11] = 0
            ozono_lucode[12] = 0
            ozono_lucode[13] = 0
            ozono_lucode[14] = 0
            ozono_lucode[15] = 0
            ozono_lucode[16] = 0
            ozono_lucode[17] = 7.24
            ozono_lucode[18] = 0
            ozono_lucode[19] = 0.55
            ozono_lucode[20] = 0
            ozono_lucode[21] = 18.87
            ozono_lucode[22] = 0
            ozono_lucode[23] = 0.55
            ozono_lucode[24] = 0
            ozono_lucode[25] = 0
            ozono_lucode[26] = 0.55
            ozono_lucode[27] = 0
            ozono_lucode[28] = 0
            ozono_lucode[29] = 0.55
            ozono_lucode[30] = 0
            ozono_lucode[31] = 0
            ozono_lucode[32] = 0.55
            ozono_lucode[33] = 0
            ozono_lucode[34] = 0
            ozono_lucode[35] = 0
            ozono_lucode[36] = 0
            ozono_lucode[37] = 0
            ozono_lucode[38] = 0.55
            ozono_lucode[39] = 0
            ozono_lucode[40] = 0
            ozono_lucode[41] = 0
            ozono_lucode[42] = 0
            ozono_lucode[43] = 24.12
            ozono_lucode[44] = 24.12
            ozono_lucode[45] = 0
            ozono_lucode[46] = 9.33
            ozono_lucode[47] = 0
            ozono_lucode[48] = 9.33
            ozono_lucode[49] = 0
            ozono_lucode[50] = 0
            ozono_lucode[51] = 0
            ozono_lucode[52] = 0
            ozono_lucode[53] = 0.55
            ozono_lucode[54] = 0
            ozono_lucode[55] = 0
            ozono_lucode[56] = 0
            ozono_lucode[57] = 0.03
            ozono_lucode[58] = 0
            ozono_lucode[59] = 0
            ozono_lucode[60] = 0
            ozono_lucode[61] = 0
            ozono_lucode[62] = 0.55
            ozono_lucode[63] = 0
            ozono_lucode[64] = 0
            ozono_lucode[65] = 0
            ozono_lucode[66] = 0
            ozono_lucode[67] = 0
            ozono_lucode[68] = 0
            ozono_lucode[69] = 0.55
            ozono_lucode[70] = 0.55
            ozono_lucode[71] = 0
            ozono_lucode[72] = 0
            ozono_lucode[73] = 0
            ozono_lucode[74] = 0.55
            ozono_lucode[75] = 0
            ozono_lucode[76] = 0
            ozono_lucode[77] = 0
            ozono_lucode[78] = 0
            ozono_lucode[79] = 0
            ozono_lucode[80] = 0
            ozono_lucode[81] = 0
            ozono_lucode[82] = 18.87
            ozono_lucode[83] = 18.87
            ozono_lucode[84] = 18.87
            ozono_lucode[85] = 18.87
            ozono_lucode[86] = 18.87
            ozono_lucode[87] = 18.87
            T_lucode = {}
            T_lucode[1] = 0
            T_lucode[2] = 0
            T_lucode[3] = 0
            T_lucode[4] = 0
            T_lucode[5] = 0
            T_lucode[6] = 0
            T_lucode[7] = 18489600
            T_lucode[8] = 0
            T_lucode[9] = 18489600
            T_lucode[10] = 0
            T_lucode[11] = 0
            T_lucode[12] = 0
            T_lucode[13] = 0
            T_lucode[14] = 0
            T_lucode[15] = 0
            T_lucode[16] = 0
            T_lucode[17] = 18489600
            T_lucode[18] = 0
            T_lucode[19] = 18489600
            T_lucode[20] = 0
            T_lucode[21] = 18489600
            T_lucode[22] = 0
            T_lucode[23] = 18489600
            T_lucode[24] = 0
            T_lucode[25] = 0
            T_lucode[26] = 18489600
            T_lucode[27] = 0
            T_lucode[28] = 0
            T_lucode[29] = 18489600
            T_lucode[30] = 0
            T_lucode[31] = 0
            T_lucode[32] = 18489600
            T_lucode[33] = 0
            T_lucode[34] = 0
            T_lucode[35] = 0
            T_lucode[36] = 0
            T_lucode[37] = 0
            T_lucode[38] = 18489600
            T_lucode[39] = 0
            T_lucode[40] = 0
            T_lucode[41] = 0
            T_lucode[42] = 0
            T_lucode[43] = 18489600
            T_lucode[44] = 18489600
            T_lucode[45] = 0
            T_lucode[46] = 18489600
            T_lucode[47] = 0
            T_lucode[48] = 18489600
            T_lucode[49] = 0
            T_lucode[50] = 0
            T_lucode[51] = 0
            T_lucode[52] = 0
            T_lucode[53] = 18489600
            T_lucode[54] = 0
            T_lucode[55] = 0
            T_lucode[56] = 0
            T_lucode[57] = 18489600
            T_lucode[58] = 0
            T_lucode[59] = 0
            T_lucode[60] = 0
            T_lucode[61] = 0
            T_lucode[62] = 18489600
            T_lucode[63] = 0
            T_lucode[64] = 0
            T_lucode[65] = 0
            T_lucode[66] = 0
            T_lucode[67] = 0
            T_lucode[68] = 0
            T_lucode[69] = 18489600
            T_lucode[70] = 0
            T_lucode[71] = 0
            T_lucode[72] = 0
            T_lucode[73] = 0
            T_lucode[74] = 18489600
            T_lucode[75] = 0
            T_lucode[76] = 0
            T_lucode[77] = 0
            T_lucode[78] = 0
            T_lucode[79] = 0
            T_lucode[80] = 0
            T_lucode[81] = 0
            T_lucode[82] = 18489600
            T_lucode[83] = 18489600
            T_lucode[84] = 18489600
            T_lucode[85] = 18489600
            T_lucode[86] = 18489600
            T_lucode[87] = 18489600
            lai_lucode = {}
            lai_lucode[1] = 0
            lai_lucode[2] = 0
            lai_lucode[3] = 0
            lai_lucode[4] = 0
            lai_lucode[5] = 0
            lai_lucode[6] = 0
            lai_lucode[7] = 0.21
            lai_lucode[8] = 0
            lai_lucode[9] = 0.08
            lai_lucode[10] = 0
            lai_lucode[11] = 0
            lai_lucode[12] = 0
            lai_lucode[13] = 0
            lai_lucode[14] = 0
            lai_lucode[15] = 0
            lai_lucode[16] = 0
            lai_lucode[17] = 0.39
            lai_lucode[18] = 0
            lai_lucode[19] = 0.02
            lai_lucode[20] = 0
            lai_lucode[21] = 0.88
            lai_lucode[22] = 0
            lai_lucode[23] = 0.02
            lai_lucode[24] = 0
            lai_lucode[25] = 0
            lai_lucode[26] = 0.02
            lai_lucode[27] = 0
            lai_lucode[28] = 0
            lai_lucode[29] = 0.02
            lai_lucode[30] = 0
            lai_lucode[31] = 0
            lai_lucode[32] = 0.02
            lai_lucode[33] = 0
            lai_lucode[34] = 0
            lai_lucode[35] = 0
            lai_lucode[36] = 0
            lai_lucode[37] = 0
            lai_lucode[38] = 0.02
            lai_lucode[39] = 0
            lai_lucode[40] = 0
            lai_lucode[41] = 0
            lai_lucode[42] = 0
            lai_lucode[43] = 1.22
            lai_lucode[44] = 1.22
            lai_lucode[45] = 0
            lai_lucode[46] = 0.53
            lai_lucode[47] = 0
            lai_lucode[48] = 0.53
            lai_lucode[49] = 0
            lai_lucode[50] = 0
            lai_lucode[51] = 0
            lai_lucode[52] = 0
            lai_lucode[53] = 0.02
            lai_lucode[54] = 0
            lai_lucode[55] = 0
            lai_lucode[56] = 0
            lai_lucode[57] = 0
            lai_lucode[58] = 0
            lai_lucode[59] = 0
            lai_lucode[60] = 0
            lai_lucode[61] = 0
            lai_lucode[62] = 0.02
            lai_lucode[63] = 0
            lai_lucode[64] = 0
            lai_lucode[65] = 0
            lai_lucode[66] = 0
            lai_lucode[67] = 0
            lai_lucode[68] = 0
            lai_lucode[69] = 0.02
            lai_lucode[70] = 0.02
            lai_lucode[71] = 0
            lai_lucode[72] = 0
            lai_lucode[73] = 0
            lai_lucode[74] = 0.02
            lai_lucode[75] = 0
            lai_lucode[76] = 0
            lai_lucode[77] = 0
            lai_lucode[78] = 0
            lai_lucode[79] = 0
            lai_lucode[80] = 0
            lai_lucode[81] = 0
            lai_lucode[82] = 0.88
            lai_lucode[83] = 0.88
            lai_lucode[84] = 0.88
            lai_lucode[85] = 0.88
            lai_lucode[86] = 0.88
            lai_lucode[87] = 0.88
            for lucode in np.unique(arr_lucode):
                try:
                    arr_ozono[np.where(arr_lucode == lucode)] = (ozono_lucode[lucode] * area_pixel) / 1e6 * 1000
                    arr_q[np.where(arr_lucode == lucode)] = (concpm10 * Vd * (
                            T_lucode[lucode] * lai_lucode[lucode] * area_pixel * 0.5))/1e12 * 1000
                except:
                    pass

        # Initialize and write on output raster
        file_output = path_output + '/02_concentrazione_Ozono_' + stato + '_kg.tiff'
        outdata_ozono = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata_ozono.SetGeoTransform(lucode_data_source.GetGeoTransform())  ##sets same geotransform as input
        outdata_ozono.SetProjection(lucode_data_source.GetProjection())  ##sets same projection as input
        outdata_ozono.GetRasterBand(1).WriteArray(arr_ozono)
        outdata_ozono.FlushCache()

        # Initialize and write on output raster
        file_output = path_output + '/02_concentrazione_PM10_' + stato + '_kg.tiff'
        outdata_pm10 = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata_pm10.SetGeoTransform(lucode_data_source.GetGeoTransform())  ##sets same geotransform as input
        outdata_pm10.SetProjection(lucode_data_source.GetProjection())  ##sets same projection as input
        outdata_pm10.GetRasterBand(1).WriteArray(arr_q)
        outdata_pm10.FlushCache()
        # Define alpha beta coefficient for each lucode
        alpha = {}
        beta = {}
        alpha[1], beta[1] = [0, 0.0006]
        alpha[2], beta[2] = [0, 0.0006]
        alpha[3], beta[3] = [0, 0]
        alpha[4], beta[4] = [0, 0.0006]
        alpha[5], beta[5] = [0, 0.0006]
        alpha[6], beta[6] = [0, 0.0006]
        alpha[7], beta[7] = [0, 0.0015]
        alpha[8], beta[8] = [0, 0]
        alpha[9], beta[9] = [0, 0.00015]
        alpha[10], beta[10] = [0, 0.0006]
        alpha[11], beta[11] = [0, 0]
        alpha[12], beta[12] = [0, 0.0006]
        alpha[13], beta[13] = [0, 0]
        alpha[14], beta[14] = [0, 0.0006]
        alpha[15], beta[15] = [0, 0]
        alpha[16], beta[16] = [0, 0.0006]
        alpha[17], beta[17] = [0, 0.0015]
        alpha[18], beta[18] = [0, 0]
        alpha[19], beta[19] = [0, 0.0015]
        alpha[20], beta[20] = [0, 0]
        alpha[21], beta[21] = [0, 0.0015]
        alpha[22], beta[22] = [0, 0.0006]
        alpha[23], beta[23] = [0, 0.0015]
        alpha[24], beta[24] = [0, 0.0006]
        alpha[25], beta[25] = [0, 0]
        alpha[26], beta[26] = [0, 0.0015]
        alpha[27], beta[27] = [0, 0.0006]
        alpha[28], beta[28] = [0, 0]
        alpha[29], beta[29] = [0, 0.0015]
        alpha[30], beta[30] = [0, 0.0006]
        alpha[31], beta[31] = [0, 0]
        alpha[32], beta[32] = [0, 0.0015]
        alpha[33], beta[33] = [0, 0.0006]
        alpha[34], beta[34] = [0, 0.0006]
        alpha[35], beta[35] = [0, 0]
        alpha[36], beta[36] = [0, 0]
        alpha[37], beta[37] = [0, 0.0006]
        alpha[38], beta[38] = [0, 0.0015]
        alpha[39], beta[39] = [0, 0.0006]
        alpha[40], beta[40] = [0, 0.0006]
        alpha[41], beta[41] = [0, 0.0006]
        alpha[42], beta[42] = [0, 0.0006]
        alpha[43], beta[43] = [0, 0.0015]
        alpha[44], beta[44] = [0, 0.0015]
        alpha[45], beta[45] = [0, 0]
        alpha[46], beta[46] = [0, 0.0015]
        alpha[47], beta[47] = [0, 0]
        alpha[48], beta[48] = [0, 0.0015]
        alpha[49], beta[49] = [0, 0.0006]
        alpha[50], beta[50] = [0, 0]
        alpha[51], beta[51] = [0, 0]
        alpha[52], beta[52] = [0, 0]
        alpha[53], beta[53] = [0, 0.0015]
        alpha[54], beta[54] = [0, 0]
        alpha[55], beta[55] = [0, 0]
        alpha[56], beta[56] = [0, 0]
        alpha[57], beta[57] = [0, 0.0015]
        alpha[58], beta[58] = [0, 0.0006]
        alpha[59], beta[59] = [0, 0.0006]
        alpha[60], beta[60] = [0, 0]
        alpha[61], beta[61] = [0, 0.0006]
        alpha[62], beta[62] = [0, 0.0015]
        alpha[63], beta[63] = [0, 0.0006]
        alpha[64], beta[64] = [0, 0.0006]
        alpha[65], beta[65] = [0, 0.0006]
        alpha[66], beta[66] = [0, 0]
        alpha[67], beta[67] = [0, 0]
        alpha[68], beta[68] = [0, 0.0006]
        alpha[69], beta[69] = [0, 0.0015]
        alpha[70], beta[70] = [0, 0.0006]
        alpha[71], beta[71] = [0, 0.0006]
        alpha[72], beta[72] = [0, 0]
        alpha[73], beta[73] = [0, 0.0006]
        alpha[74], beta[74] = [0, 0.0015]
        alpha[75], beta[75] = [0, 0.0006]
        alpha[76], beta[76] = [0, 0.0006]
        alpha[77], beta[77] = [0, 0]
        alpha[78], beta[78] = [0, 0]
        alpha[79], beta[79] = [0, 0.0006]
        alpha[80], beta[80] = [0, 0]
        alpha[81], beta[81] = [0, 0]
        alpha[82], beta[82] = [0, 0.0015]
        alpha[83], beta[83] = [0, 0.0015]
        alpha[84], beta[84] = [0, 0.0015]
        alpha[85], beta[85] = [0, 0.0015]
        alpha[86], beta[86] = [0, 0.0015]
        alpha[87], beta[87] = [0, 0.0015]

        # Concetration input value
        concno2 = self.parameterAsDouble(parameters, self.CONCNO2, context)
        # Wind speed input value
        vel = self.parameterAsDouble(parameters, self.VEL, context)
        arr_F = np.zeros((rows, cols))
        for lucode in alpha.keys():
            arr_F[np.where(arr_lucode == lucode)] = ((alpha[lucode] + beta[lucode] * vel) * concno2 * 0.365) / 1e4 * 1000
        # Initialize and write on output raster
        file_output = path_output + '/02_concentrazione_NO2_' + stato + '_kg.tiff'
        outdata_no2 = driver.Create(file_output, cols, rows, 1, gdal.GDT_Float64)
        outdata_no2.SetGeoTransform(lucode_data_source.GetGeoTransform())##sets same geotransform as input
        outdata_no2.SetProjection(lucode_data_source.GetProjection())##sets same projection as input
        outdata_no2.GetRasterBand(1).WriteArray(arr_F)
        outdata_no2.FlushCache()
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

