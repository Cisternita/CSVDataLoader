import pandas as pd
import matplotlib.pyplot as plt
import os
from pandas_summary import DataFrameSummary
from matplotlib.ticker import PercentFormatter
class CSVDataLoader:
    """
    A class for loading and cleaning CSV data from a specified folder path.

    Attributes:
    -----------
    folder_path : str
        The path to the folder containing the CSV files to be loaded.

    data : dict
        A dictionary containing the loaded CSV data, where the keys are the file names and the values are the corresponding dataframes.
    """

    def __init__(self, folder_path):
        """
        Initializes a CSVDataLoader object with the specified folder path.

        Parameters:
        -----------
        folder_path : str
            The path to the folder containing the CSV files to be loaded.
        """
        self.folder_path = folder_path
        self.data = {}
        self.filename = []
        self.keys = []

    def load_data(self):
        """
        Loads CSV data from the specified folder path into a dictionary.

        Returns:
        --------
        None
        """
        csv_files = [f for f in os.listdir(self.folder_path) if f.endswith('.csv')]
        folders = ("datasets/actuacionesBomberos", "datasets/estaciones", "datasets/accidentalidad")
        for folder in folders:
            df = None
            for file in os.listdir(folder):
                filepath = folder + "/" + file
                df1 = pd.read_csv(filepath, sep=';', encoding='utf-8', low_memory=False)
                df = pd.concat([df, df1])
            self.data[str(folder)] = df

        for file_name in csv_files:
            file_path = os.path.join(self.folder_path, file_name)
            try:
                df = pd.read_csv(file_path, sep=';', encoding='latin-1', low_memory=False)
                self.data[str(file_name)] = df
                self.filename.append(file_name)
            except Exception as e:
                print(f"Error al leer {file_name}: {str(e)}")

        for value in self.data.keys():
            self.keys.append(value)

    def clean_data(self):
        """
        Cleans the loaded CSV data by renaming columns, removing whitespace, dropping null values and duplicates, and converting date columns to datetime format.

        Returns:
        --------
        None
        """
        columna_borrar = "Unnamed"
        for df in self.data:
            for j in self.data[df].columns:
                if columna_borrar in j:
                    while j in self.data[df].columns:
                        self.data[df] = self.data[df].drop(j, axis=1)
                        self.data[df] = self.data[df].dropna(how='all', axis=0)
                        
            self.data[df] = self.data[df].rename(columns = lambda x: x.strip().lower().replace(' ', '_'))
            self.data[df] = self.data[df].map(lambda x: x.strip() if isinstance(x, str) else x)
            self.data[df] = self.data[df].dropna(how='all', axis=0)
            self.data[df] = self.data[df].drop_duplicates()
            self.data[df] = self.data[df].loc[:, ~self.data[df].columns.duplicated()]
            self.data[df].columns = map(str.upper, self.data[df].columns)

            if 'FECHA' in self.data[df].columns:
                self.data[df]['FECHA'] = pd.to_datetime(self.data[df]['FECHA'], format='%d/%m/%Y')

#           num_cols = self.data[i].select_dtypes(include='number').columns
#           for col in num_cols:
#               self.data[i][col] = self.data[i][col].fillna(self.data[i][col].mean())

    def get_info(self, filename):
        print(self.data[filename].isnull().sum())
        print(self.data[filename].info())
        
    def get_nan_columns(self):
        j = 0
        for i in self.data:
            print(self.keys[j])
            self.get_info(i)
            j+=1

    def get_cleaned_data(self):
        """
        Returns the cleaned CSV data as a dictionary.

        Returns:
        --------
        dict
            A dictionary containing the cleaned CSV data, where the keys are the file names and the values are the corresponding dataframes.
        """
        return self.data

    def create_graph(df, colummn, name):
        frec = df[''+str(colummn)].value_counts()
        aux_df = pd.DataFrame(frec)
        aux_df.columns = ["Frecuencia absoluta"]
        aux_df["Frecuencia relativa"] = 100*aux_df["Frecuencia absoluta"] / len(df)
        frec_rel_cumsum = aux_df["Frecuencia relativa"].cumsum()
        aux_df["Frecuencia relativa acumulada"] = frec_rel_cumsum
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.set_title('Distribución de '+ str(name))
        ax.bar(aux_df.index, aux_df['Frecuencia absoluta'], color='blue')
        ax2 = ax.twinx()
        ax2.plot(aux_df.index, aux_df['Frecuencia relativa acumulada'], color='red', marker='o', ms = 5)
        ax2.yaxis.set_major_formatter(PercentFormatter())
        ax.tick_params(axis='y', color = 'blue')
        ax2.tick_params(axis='y', color = 'red')
        ax.set_xticklabels(aux_df.index, rotation=90)
        plt.show()

    def dataframe_summary(self, filename):

        numeric_mask = self.data[filename].select_dtypes(include='number').columns

        # Create a DataFrameSummary object
        summary = DataFrameSummary(self.data[filename][numeric_mask])
    
        # Display summary statistics
        summary_stats = summary.summary()
    
        # Plot correlation matrix for all numeric columns
        self.data[filename][numeric_mask].corr(method='pearson', numeric_only=True)

        # Boxplot of each variable
        #self.data[filename][numeric_mask].boxplot(figsize=(10, 8))

        return summary_stats