import logging

from great_expectations.datasource.batch_kwargs_generator.batch_kwargs_generator import BatchKwargsGenerator

logger = logging.getLogger(__name__)

try:
    from pyspark.sql import SparkSession
except ImportError:
    logger.debug("Unable to load spark context; install optional spark dependency for support.")


class DatabricksTableBatchKwargsGenerator(BatchKwargsGenerator):
    """Meant to be used in a Databricks notebook
    """

    def __init__(self, name="default",
                 datasource=None,
                 database="default"):
        super(DatabricksTableBatchKwargsGenerator, self).__init__(name, datasource=datasource)
        self.database = database
        try:
            self.spark = SparkSession.builder.getOrCreate()
        except Exception:
            logger.error("Unable to load spark context; install optional spark dependency for support.")
            self.spark = None

    def get_available_data_asset_names(self):
        if self.spark is None:
            logger.warning("No sparkSession available to query for tables.")
            return {"names": []}

        tables = self.spark.sql('show tables in {}'.format(self.database))
        return {"names": [(row.tableName, "table") for row in tables.collect()]}

    def _get_iterator(self, generator_asset, **kwargs):
        query = 'select * from {}.{}'.format(self.database, generator_asset)
        if kwargs.get('partition'):
            if not kwargs.get('date_field'):
                raise Exception('Must specify date_field when using partition.')
            query += ' where {} = "{}"'.format(kwargs.get('date_field'), kwargs.get('partition'))
        return iter([
            {
                "query": query
            }
        ])
