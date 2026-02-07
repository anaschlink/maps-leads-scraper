import pandas as pd

class ExportService:

    @staticmethod
    def to_csv(data: list, filename="leads.csv"):
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding="utf-8-sig")

    @staticmethod
    def to_excel(data: list, filename="leads.xlsx"):
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
