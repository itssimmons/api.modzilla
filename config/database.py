import sqlite3
from os import getcwd
from typing import List, Tuple, Any, Dict, Literal, overload

DATABASE_PATH = f"{getcwd()}/database/db.sqlite3"
SQL_TEMPLATE = ["", "", "", "", "", ""]

class Builder:
    __t: str = ""
    __f: Literal["*"] | List[str] = "*"
    __v: Tuple[Any, ...] = ()
    __rel: List[str] = []

    __con: sqlite3.Connection | None = None
    __cur: sqlite3.Cursor | None = None

    @staticmethod
    def connect() -> sqlite3.Connection:
        con = sqlite3.connect(DATABASE_PATH)
        return con

    @staticmethod
    def query(t: str, debug: bool = True):
        builder = Builder(t, debug)
        return builder

    @staticmethod
    def raw_query(sql: str):
        con = Builder.connect()
        cur = con.execute(sql)
        con.commit()
        res = cur.fetchall()
        con.close()
        return res

    @staticmethod
    def parse_sql(sql: List[str]):
        print(sql)
        sql_filtered = filter(lambda x: x != "", sql)
        raw_sql = "\n".join(sql_filtered)
        return raw_sql

    @staticmethod
    @overload
    def parse_fields( # type: ignore
        fields: Literal["*"] | List[str],
        t: str | None = None,
        cast: Literal["str"] = "str",
        prefix: bool = False,
    ) -> str: ...
    @staticmethod
    @overload
    def parse_fields( # type: ignore
        fields: Literal["*"] | List[str],
        t: str | None = None,
        cast: Literal["list"] = "list",
        prefix: bool = False,
    ) -> List[str]: ...
    @staticmethod
    def parse_fields(
        fields: Literal["*"] | List[str],
        t: str | None = None,
        cast: Literal["list", "str"] = "str", # type: ignore
        prefix: bool = False,
    ) -> List[str] | str:
        f: List[str] | Literal["*"] = fields

        if f == "*" and t is not None:
            f = Builder.resolve_asterisk(t)

        if f != "*" and cast == "list":
            if prefix is not False:
                return [f"{t}.{f} AS '{t}:{f}'" for f in f]
            return [f"{t}.{f}" for f in f]
        
        if prefix is not False:
            return ", ".join([f"{t}.{f} AS '{t}:{f}'" for f in f])

        return ", ".join([f"{t}.{f}" for f in f])

    @staticmethod
    def parse_values(values: Tuple[Any, ...]) -> str:
        """Deprecated ⛔️"""
        v = [f"'{v}'" for v in values]
        return ", ".join(v)

    @staticmethod
    def parse_sets(fields: List[str], values: Tuple[Any, ...]) -> str:
        fields = [f"{fields[i]} = ?" for i in range(len(fields))]
        return ", ".join(fields)

    @staticmethod
    def parse_rows(fields: List[str], rows: List[Any]) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []

        for row in rows:
            json: Dict[str , Any] = dict()
            for i in range(len(row)):
                if ':' in fields[i]:
                    x = fields[i].split(':')
                    if x[0] not in json or type(json[x[0]]) is not dict:
                        json[x[0]] = dict()
                    json[x[0]][x[1]] = row[i]
                else:
                    x = fields[i].split('.')
                    json[x[1]] = row[i]
            result.append(json)

        return result

    @staticmethod
    def parse_row(fields: List[str], row: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        for i in range(len(fields)):
            if ':' in fields[i]:
                x = fields[i].split(':')
                if x[0] not in result or type(result[x[0]]) is not dict:
                    result[x[0]] = dict()
                result[x[0]][x[1]] = row[i]
            else:
                x = fields[i].split('.')
                result[x[1]] = row[i]

        return result

    @staticmethod
    def resolve_asterisk(t: str) -> List[str]:
        table_info = Builder.raw_query(sql=f"PRAGMA table_info({t})")
        f = [info[1] for info in table_info]
        return f

    @staticmethod
    def resolve_question_mark(max_bound: int):
        return ", ".join([f"?" for _ in range(max_bound)])

    def __run(self, params: Tuple[Any, ...] | None = None):
        sql = Builder.parse_sql(self.__sql)
        con = Builder.connect()
        cur = None

        if self.__debug:
            print("\n--- [BEGIN | DEBUG SQL] ---")
            print(sql)
            print("--- [END | DEBUG SQL] ---\n")

        if params is not None:
            cur = con.execute(sql, params)
        else:
            cur = con.execute(sql)

        con.commit()

        self.__rows = cur.fetchall()
        rowcount = len(self.__rows)
        self.count: int = rowcount
        self.exists = rowcount > 0
        self.__con = con
        self.__cur = cur
        return self

    # constructor
    def __init__(self, t: str, debug: bool = False):
        # private attributes
        self.__t = t
        self.__sql = list(SQL_TEMPLATE)
        self.__debug = debug
        self.__rows: List[Dict[str, Any]] = []

        # public attributes
        self.count: int = 0
        self.exists: bool = False

    def close(self):
        if (self.__con is not None) and (self.__cur is not None):
            self.__cur.close()
            self.__con.close()
        self.__cur = None
        self.__con = None

    def fetchall(self) -> List[Dict[str, Any]]:
        """Fetch & parse all rows and finally close the connection to the database"""

        if self.__cur is None:
            raise TypeError("Unexpected error: the cursor is None")

        f: List[str] = self.__f # type: ignore
        entries = Builder.parse_rows(f, self.__rows)

        self.close()
        return entries

    def fetchone(self) -> Dict[str, Any]:
        """Fetch & parse only one row and finally close the connection to the database"""

        if self.__cur is None:
            raise TypeError("Unexpected error: the cursor is None")

        f = Builder.parse_fields(self.__f, self.__t, cast="list")
        entry = Builder.parse_row(f, self.__rows[0])

        self.close()
        return entry

    def fields(self, f: List[str] | Literal["*"] = "*"):
        self.__f = f
        return self

    def values(self, v: Tuple[Any, ...]):
        self.__v = v
        return self

    def create(self):
        """Insert a new row into the table and returns the `lastrowid`
        of the inserted row or `-1` if the row isn't created"""

        f = Builder.parse_fields(self.__f, self.__t)
        v = self.__v
        placeholders = Builder.resolve_question_mark(len(v))
        self.__sql[0] = f"INSERT INTO {self.__t} ( {f} ) VALUES ( {placeholders} )"
        self.__run(v)
        lastrowid = (
            self.__cur.lastrowid
            if self.__cur is not None and self.__cur.lastrowid is not None
            else -1
        )
        self.close()
        return lastrowid

    def read(self):
        """Read all rows from the table"""
        
        f = [Builder.parse_fields(self.__f, self.__t)]

        if len(self.__rel) > 0:
            for rel in self.__rel:
                f.append(Builder.parse_fields('*', rel, prefix=True))
        
        f = ', '.join(f).split(', ')
        self.__f = [x.split(' AS ')[0].replace('.', ':') if ' AS ' in x else x for x in f]
        self.__sql[0] = f"SELECT {', '.join(f)} FROM {self.__t}"
        return self.__run()

    def update(self):
        """Update a row in the table"""

        if self.__f == "*":
            raise AssertionError("You can't update a row without specifying all fields")

        s = Builder.parse_sets(self.__f, self.__v)
        v = self.__v
        self.__sql[0] = f"UPDATE {self.__t} SET {s}"
        self.__run(v)
        self.close()

    def delete(self):
        """Delete a row from the table"""

        """Unstable ⚠️"""
        self.__sql[0] = f"DELETE FROM {self.__t}"
        self.__run()
        self.close()

    def relation(
        self,
        t1: str,
        fk: str | None = None,
    ):
        if fk is None:
            fk = f"{t1[:-1]}_id"

        self.__rel.append(t1)
        
        if len(self.__sql[1]) > 0:
            self.__sql[1] += f"\nINNER JOIN {t1} ON {self.__t}.{fk} = {t1}.id"
            
        self.__sql[1] = f"INNER JOIN {t1} ON {self.__t}.{fk} = {t1}.id"
        return self

    def where(self, criteria: str):
        self.__sql[2] = f"WHERE {criteria}"
        return self

    def order_by(self, f: str, order: str):
        """Not tested yet ⚠️"""
        self.__sql[3] = f"ORDER BY {f} {order}"
        return self

    def group_by(self, f: str):
        """Not tested yet ⚠️"""
        self.__sql[4] = f"GROUP BY {f}"
        return self

    def limit(self, n: int):
        """Not tested yet ⚠️"""
        self.__sql[5] = f"LIMIT {n}"
        return self
