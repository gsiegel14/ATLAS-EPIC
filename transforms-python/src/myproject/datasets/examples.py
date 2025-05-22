# from pyspark.sql import DataFrame
# 
# # from pyspark.sql import functions as F
# from transforms.api import Input, Output, transform_df
# 
# from myproject.datasets import utils
# 
# 
# @transform_df(
#     Output("/Atlas Engine-2cacb0/ATLAS/TARGET_DATASET_PATH"),
#     source_df=Input("/Atlas Engine-2cacb0/ATLAS/SOURCE_DATASET_PATH"),
# )
# def compute(source_df: DataFrame) -> DataFrame:
#     return utils.identity(source_df)
