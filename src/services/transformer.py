import pandas as pd


class DataTransformer:
    def __init__(self):
        pass

    def  capitalize_transform(self, df, column:str, new_column:str, operation:str):
        if operation == 'lower':
            df[new_column] = df[column].str.lower()
        elif operation == 'upper':
            df[new_column] = df[column].str.upper()
        return df

    def concat_transform(self, df, new_column:str, column1:str, column2:str):
        df[new_column] = df[column1] + ' ' + df[column2]
        return df

    def date_transform(self, df, column:str, new_column:str, operation:str):
        df[column] = pd.to_datetime(df[column])

        if operation == "year":
            df[new_column] = df[column].dt.year
        elif operation == "month":
            df[new_column] = df[column].dt.month
        elif operation == "day":
            df[new_column] = df[column].dt.day
        return df







