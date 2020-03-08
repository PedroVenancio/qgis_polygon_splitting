"""
***************************************************************************
    QGISPolygonSplitting.py
    ---------------------
    Date                 : March 2020
    Copyright            : (C) 2020 by Pedro Venancio
    Email                : pedrongvenancio at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PolygonSplitting(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('poligonfeatures', 'Polygon to Split', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('numberofpoints', 'Number of Random Points', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=100000, defaultValue=10000))
        self.addParameter(QgsProcessingParameterNumber('numberofparts', 'Number of Parts to Split Polygon', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=100, defaultValue=5))
        self.addParameter(QgsProcessingParameterFeatureSink('splittedpolygon', 'Splitted Polygon', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(6, model_feedback)
        results = {}
        outputs = {}

        # Random points inside polygons
        alg_params = {
            'INPUT': parameters['poligonfeatures'],
            'MIN_DISTANCE': None,
            'STRATEGY': 0,
            'VALUE': parameters['numberofpoints'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RandomPointsInsidePolygons'] = processing.run('qgis:randompointsinsidepolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # K-means clustering
        alg_params = {
            'CLUSTERS': parameters['numberofparts'],
            'FIELD_NAME': 'CLUSTER_ID',
            'INPUT': outputs['RandomPointsInsidePolygons']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['KmeansClustering'] = processing.run('native:kmeansclustering', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Concave hull (k-nearest neighbor)
        alg_params = {
            'FIELD': 'CLUSTER_ID',
            'INPUT': outputs['KmeansClustering']['OUTPUT'],
            'KNEIGHBORS': 3,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ConcaveHullKnearestNeighbor'] = processing.run('qgis:knearestconcavehull', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Centroids
        alg_params = {
            'ALL_PARTS': False,
            'INPUT': outputs['ConcaveHullKnearestNeighbor']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Centroids'] = processing.run('native:centroids', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Voronoi polygons
        alg_params = {
            'BUFFER': 100,
            'INPUT': outputs['Centroids']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['VoronoiPolygons'] = processing.run('qgis:voronoipolygons', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Intersection
        alg_params = {
            'INPUT': parameters['poligonfeatures'],
            'INPUT_FIELDS': [''],
            'OVERLAY': outputs['VoronoiPolygons']['OUTPUT'],
            'OVERLAY_FIELDS': [''],
            'OVERLAY_FIELDS_PREFIX': '',
            'OUTPUT': parameters['splittedpolygon']
        }
        outputs['Intersection'] = processing.run('native:intersection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['splittedpolygon'] = outputs['Intersection']['OUTPUT']
        return results

    def name(self):
        return 'Polygon Splitting'

    def displayName(self):
        return 'Polygon Splitting'

    def group(self):
        return 'Polygon Splitting'

    def groupId(self):
        return 'Polygon Splitting'

    def createInstance(self):
        return PolygonSplitting()
