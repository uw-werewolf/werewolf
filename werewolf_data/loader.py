import os
import pandas as pd
import pprint
from terminaltables import SingleTable
from textwrap import wrap
from werewolf_data import *


class WerewolfLoader:

    _versions = {"epa_2019": epa_needs_093019, "wi_psc": wi_psc}

    def __init__(self, data_dir, version=None):
        if version is None:
            version = "wi_psc"
        if version not in self._versions:
            raise ValueError(f"Unknown WEREWOLF version: {version}")

        self.version = version
        self.data_dir = os.path.abspath(data_dir)

        self.data = {}
        for i in dir(self._versions[version]):
            if callable(getattr(self._versions[version], i)):
                print(f"Loading data from... {i}")
                self.data[i] = getattr(self._versions[version], i)(data_dir)

    #     # standardize column names for all data
    #     self.__rename_columns__()
    #
    #     # drop columns not in the minimal column set
    #     self.__drop_columns__()
    #
    #     # harmonize all data types
    #     self.__col_dtypes__()
    #
    #     # container for notation
    #     self.add_notation = {}
    #
    #     # find all unique columns
    #     self.__all_cols__ = []
    #     for k, v in self.data.__dict__.items():
    #         self.__all_cols__.extend(v.columns.tolist())
    #     self.__all_cols__ = list(set(self.__all_cols__))
    #     self.__all_cols__.sort()
    #
    # def __rename_columns__(self):
    #     import werewolf_data.rename_cols as cols
    #
    #     for k, v in self.data.__dict__.items():
    #         v.rename(columns=cols._rename_cols[self.version][k], inplace=True)
    #
    # def __drop_columns__(self):
    #     import werewolf_data.rename_cols as cols
    #
    #     for k, v in self.data.__dict__.items():
    #         drop_me = set(v.columns) - set(cols._col_dtypes[self.version].keys())
    #         if not (not drop_me):
    #             print(f"dropping columns {drop_me} from {k}")
    #             v.drop(columns=drop_me, inplace=True)
    #
    # def __col_dtypes__(self):
    #     import werewolf_data.rename_cols as cols
    #
    #     for k, v in self.data.__dict__.items():
    #         for i in v.columns.to_list():
    #             if i not in {"timestamp"}:
    #                 print(
    #                     f"converting '{i}' in '{k}' from '{v[i].dtype}' --> '{cols._col_dtypes[self.version][i]}'"
    #                 )
    #                 v[i] = v[i].map(cols._col_dtypes[self.version][i])
    #             else:
    #                 v[i] = pd.to_datetime(v[i], unit="s")
    #                 v[i] = v[i].map(str)
    #
    # def bulk_replace(self, convert):
    #     for k, v in self.data.__dict__.items():
    #         v.replace(convert, inplace=True)
    #
    # def bulk_drop_rows(self):
    #     for k, v in self.__to_drop__.items():
    #         for col, v2 in v.items():
    #
    #             if v2 != []:
    #                 idx = self.data.__dict__[k][
    #                     self.data.__dict__[k][col].isin(v2) == True
    #                 ].index
    #
    #                 print(f"dropping {len(idx)} rows from '{col}' in '{k}'")
    #                 self.data.__dict__[k].drop(idx, inplace=True)
    #
    #     for k, v in self.data.__dict__.items():
    #         v.reset_index(drop=True, inplace=True)
    #
    # def test_notation(self):
    #     if self.add_notation == {}:
    #         raise Exception("notation is empty!")
    #
    #     self.__to_drop__ = {}
    #
    #     for k, v in self.data.__dict__.items():
    #         self.__to_drop__[k] = {}
    #         for i in v.columns:
    #
    #             self.__to_drop__[k][i] = []
    #
    #             # set up new table
    #             table_data = []
    #             table_title = f"{i} :: {k}"
    #
    #             if i not in self.add_notation.keys():
    #                 # table_data.append([f"Notation not specified for {i}"])
    #                 # table = SingleTable(table_data)
    #                 # table.title = table_title
    #                 # print(table.table)
    #                 print(f"Notation not specified for... {i} :: {k}")
    #
    #             else:
    #
    #                 data = set(v[i])
    #                 notation = self.add_notation[i]
    #
    #                 diff_data = data - notation
    #                 diff_notation = notation - data
    #
    #                 # if sets are equal
    #                 if data == notation:
    #                     table_data.append(["Valid dense data detected..."])
    #                     table_data.append(["{data} == {notation}"])
    #                     table = SingleTable(table_data)
    #                     table.title = table_title
    #                     print(table.table)
    #
    #                 # if data is a subset of notation
    #                 elif data.issubset(notation) and data != notation:
    #                     print(
    #                         "Valid sparse data detected... ({data} is a proper subset of {notation})"
    #                     )
    #
    #                     table_data.append(
    #                         [
    #                             f"{len(diff_notation)} Notation elements not in Data",
    #                             f"{len(diff_data)} Data elements not in Notation",
    #                         ]
    #                     )
    #                     table = SingleTable(table_data)
    #                     max_widths = table.column_widths
    #
    #                     col1 = list(diff_notation)
    #                     col1.sort()
    #                     col1 = "\n".join(wrap(f"{col1}", max_widths[0]))
    #
    #                     col2 = list(diff_data)
    #                     col2.sort()
    #                     col2 = "\n".join(wrap(f"{col2}", max_widths[1]))
    #
    #                     table_data.append([col1, col2])
    #
    #                     table.title = table_title
    #                     print(table.table)
    #
    #                 # if data is a superset of notation
    #                 elif data.issuperset(notation) and data != notation:
    #                     self.__to_drop__[k][i].extend(diff_data)
    #                     print(
    #                         "**** Drop detected... ({data} is a proper superset of {notation})"
    #                     )
    #
    #                     table_data.append(
    #                         [
    #                             f"{len(diff_notation)} Notation elements not in Data",
    #                             f"** {len(diff_data)} Drop Candidates **",
    #                         ]
    #                     )
    #                     table = SingleTable(table_data)
    #                     max_widths = table.column_widths
    #
    #                     col1 = list(diff_notation)
    #                     col1.sort()
    #                     col1 = "\n".join(wrap(f"{col1}", max_widths[0]))
    #
    #                     col2 = list(diff_data)
    #                     col2.sort()
    #                     col2 = "\n".join(wrap(f"{col2}", max_widths[1]))
    #
    #                     table_data.append([col1, col2])
    #
    #                     table.title = table_title
    #                     print(table.table)
    #
    #                 # if symmetric difference is not empty and the length of differences are ==
    #                 elif data.symmetric_difference(notation) != set() and len(
    #                     diff_notation
    #                 ) == len(diff_data):
    #                     print("**** Potential 1:1 map detected...")
    #
    #                     table_data.append(
    #                         [
    #                             f"{len(diff_notation)} Notation elements not in Data",
    #                             f"{len(diff_data)} Data elements not in Notation",
    #                         ]
    #                     )
    #                     table = SingleTable(table_data)
    #                     max_widths = table.column_widths
    #
    #                     col1 = list(diff_notation)
    #                     col1.sort()
    #                     col1 = "\n".join(wrap(f"{col1}", max_widths[0]))
    #
    #                     col2 = list(diff_data)
    #                     col2.sort()
    #                     col2 = "\n".join(wrap(f"{col2}", max_widths[1]))
    #
    #                     table_data.append([col1, col2])
    #
    #                     table.title = table_title
    #                     print(table.table)
    #
    #                 # if the left and right differences are != and diff_notation not empty
    #                 elif (
    #                     len(diff_notation) != len(diff_data) and diff_notation != set()
    #                 ):
    #                     self.__to_drop__[k][i].extend(diff_data)
    #
    #                     print("**** Drop detected (from a sparse data structure)... ")
    #
    #                     table_data.append(
    #                         [
    #                             f"{len(diff_notation)} Notation elements not in Data",
    #                             f"** {len(diff_data)} Drop Candidates **",
    #                         ]
    #                     )
    #                     table = SingleTable(table_data)
    #                     max_widths = table.column_widths
    #
    #                     col1 = list(diff_notation)
    #                     col1.sort()
    #                     col1 = "\n".join(wrap(f"{col1}", max_widths[0]))
    #
    #                     col2 = list(diff_data)
    #                     col2.sort()
    #                     col2 = "\n".join(wrap(f"{col2}", max_widths[1]))
    #
    #                     table_data.append([col1, col2])
    #
    #                     table.title = table_title
    #                     print(table.table)
    #
    #                 # totally disjoint
    #                 elif notation.isdisjoint(data):
    #                     print(f"**** DISJOINT: '{i}' for '{k}'")
    #                     if len(data) < 200 and len(notation) < 200:
    #                         print(f"in data: {set(v[i])}")
    #                         print(f"in notation: {notation}")
    #                     elif len(data) > 200 or len(notation) > 200:
    #                         print("**** (too many to show)")
    #
    #                 else:
    #                     print(f"**** UNKNOWN ISSUE: '{i}' for '{k}'")
    #
    # def bulk_map_column(self, from_col, to_col, mapping):
    #     for k, v in self.data.__dict__.items():
    #         if from_col in v.columns:
    #             print(f"mapping column '{to_col}' in table '{k}'...")
    #             v[to_col] = v[from_col].map(mapping)
    #
    # def bulk_drop_columns(self, header):
    #     for i in header:
    #         for k, v in self.data.__dict__.items():
    #             if i in v.columns:
    #                 print(f"dropping column '{i}' from table '{k}'...")
    #                 v.drop(columns=i, inplace=True)
    #
    # def unique_columns(self):
    #     col = set()
    #     for k, v in self.data.__dict__.items():
    #         col.update(v.columns)
    #     return col
    #
    # def column_view(self):
    #     pp = pprint.PrettyPrinter(indent=2)
    #     cv = {}
    #     for k, v in self.data.__dict__.items():
    #         cv[k] = v.columns.tolist()
    #     return pp.pprint(cv)
    #
    # def needs_notation(self):
    #     return self.unique_columns() - set(self.add_notation.keys())
    #
    # def to_csv(self, output_dir=None):
    #     if output_dir == None:
    #         self.output_dir = os.path.join(os.getcwd(), "standard_data")
    #     else:
    #         self.output_dir = os.path.abspath(output_dir)
    #
    #     if os.path.isdir(self.output_dir) == False:
    #         os.mkdir(self.output_dir)
    #
    #     for k, v in self.data.__dict__.items():
    #         v.to_csv(os.path.join(self.output_dir, f"{k}.csv"))
