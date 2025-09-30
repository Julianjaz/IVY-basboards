import os
from supabase import create_client


class SupabaseConnection:
    """Class for connection to supabase database"""


    def __init__(self):
        """ init module"""
        SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
        SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get(self, table:str):
        """ Get data from table"""
        return self.supabase.table(table).select("*").execute().data
    
    def insert(self, table:str, json:dict):
        """ Insert data"""
        return (self.supabase.table(table).insert(json).execute())