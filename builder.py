from os import getcwd
from enum import Enum
from typing import List, Self, Tuple, Any, Dict, Literal, TypedDict, overload, Callable

import sqlite3


DATABASE_PATH = f"{getcwd()}/database/db.sqlite3"
SQL_TEMPLATE = ["", "", "", "", "", ""]


class Relationship(Enum):
    HAS_ONE = "has_one"
    HAS_MANY = "has_many"
    BELONGS_TO_ONE = "belongs_to_one"
    BELONGS_TO_MANY = "belongs_to_many"


IRelationship = TypedDict(
    "IRelationship", {"t": str, "type": Relationship, "alias": str | None}
)


class Builder:
    __t1: str = ""
    __f: Literal["*"] | List[str] = "*"
    __v: Tuple[Any, ...] = ()
    __rel: List[IRelationship] = []
    __dml: Literal["INSERT", "SELECT", "UPDATE", "DELETE"] = "INSERT"

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
    def raw_query(script: str):
        """The passed sql query is executed inmmediately and the result is returned as raw data"""
        con = Builder.connect()
        cur = con.executescript(script)
        con.commit()
        res = cur.fetchall()
        con.close()
        return res

    @staticmethod
    def parse_sql(sql: List[str]):
        sql_filtered = filter(lambda x: x != "", sql)
        raw_sql = "\n".join(sql_filtered)
        return raw_sql

    @staticmethod
    @overload
    def parse_fields(  # type: ignore
        fields: Literal["*"] | List[str],
        table: str,
        cast: Literal["str"] = "str",
        prefix: bool = False,
        sep: str | None = None,
        dml: Literal["INSERT", "SELECT", "UPDATE", "DELETE"] = "INSERT",
        alias: str | None = None,
    ) -> str: ...
    @staticmethod
    @overload
    def parse_fields(  # type: ignore
        fields: Literal["*"] | List[str],
        table: str,
        cast: Literal["list"] = "list",
        prefix: bool = False,
        sep: str | None = None,
        dml: Literal["INSERT", "SELECT", "UPDATE", "DELETE"] = "INSERT",
        alias: str | None = None,
    ) -> List[str]: ...
    @staticmethod
    def parse_fields(
        fields: Literal["*"] | List[str],
        table: str,
        cast: Literal["list", "str"] = "str",  # type: ignore
        prefix: bool = False,
        sep: str | None = None,
        dml: Literal["INSERT", "SELECT", "UPDATE", "DELETE"] = "INSERT",
        alias: str | None = None,
    ) -> List[str] | str:
        mutable_fields: List[str] | Literal["*"] = fields
        t = alias if alias is not None else table

        sep_fn: Callable[[str], str] = lambda x: (
            f"{table}.{x}" if dml == "SELECT" else x
        )

        if fields == "*":
            mutable_fields = Builder.resolve_asterisk(table)

        if cast == "list":
            if prefix is not False:
                return [f"{sep_fn(f)} AS '{t}{sep}{f}'" for f in mutable_fields]
            return [f"{sep_fn(f)}" for f in mutable_fields]

        if prefix is not False:
            return ", ".join([f"{sep_fn(f)} AS '{t}{sep}{f}'" for f in mutable_fields])

        return ", ".join([f"{sep_fn(f)}" for f in mutable_fields])

    @staticmethod
    def parse_values(values: Tuple[Any, ...]) -> str:
        v = [f"'{v}'" for v in values]
        return ", ".join(v)

    @staticmethod
    def parse_sets(fields: List[str], values: Tuple[Any, ...]) -> str:
        fields = [f"{fields[i]} = ?" for i in range(len(fields))]
        return ", ".join(fields)

    @staticmethod
    def remove_duplicates(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        unique_data: List[Dict[str, Any]] = []

        for row in data:
            unique_ids: List[str] = [x["id"] for x in unique_data]
            keys_type_list = [x for x in row if type(row[x]) is list]

            if row["id"] not in unique_ids:
                for key in keys_type_list:
                    if row[key][0]["id"] is None:
                        del row[key][0]
                unique_data.append(row)
            else:
                for key in keys_type_list:
                    x = unique_ids.index(row["id"])
                    if row[key][0]["id"] != unique_data[x][key][0]["id"]:
                        unique_data[x][key].append(row[key][0])

        return unique_data

    @staticmethod
    def parse_rows(fields: List[str], rows: List[Any]) -> List[Dict[str, Any]]:
        result: List[Dict[str, Any]] = []

        for row in rows:
            json: Dict[str, Any] = dict()
            for i in range(len(row)):
                if ":" in fields[i]:
                    x = fields[i].split(":")
                    if x[0] not in json or type(json[x[0]]) is not dict:
                        json[x[0]] = {}
                    json[x[0]][x[1]] = row[i]
                elif "@" in fields[i]:
                    x = fields[i].split("@")
                    if x[0] not in json or type(json[x[0]]) is not list:
                        json[x[0]] = [{}]
                    json[x[0]][0][x[1]] = row[i]
                elif "." in fields[i]:
                    x = fields[i].split(".")
                    json[x[1]] = row[i]
                else:
                    json[fields[i]] = row[i]
            result.append(json)

        return Builder.remove_duplicates(result)

    @staticmethod
    def parse_row(fields: List[str], row: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}

        print(row)
        print(fields)

        for i in range(len(fields)):
            if ":" in fields[i]:
                x = fields[i].split(":")
                if x[0] not in result or type(result[x[0]]) is not dict:
                    result[x[0]] = {}
                result[x[0]][x[1]] = row[i]
            elif "@" in fields[i]:
                x = fields[i].split("@")
                if x[0] not in result or type(result[x[0]]) is not list:
                    result[x[0]] = [{}]
                result[x[0]][0][x[1]] = row[i]
            elif "." in fields[i]:
                x = fields[i].split(".")
                result[x[1]] = row[i]
            else:
                result[fields[i]] = row[i]

        return result

    @staticmethod
    def resolve_asterisk(t: str) -> List[str]:
        table_info = Builder.raw_query(script=f"PRAGMA table_info({t})")
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
    def __init__(self, t1: str, debug: bool = False):
        # private attributes
        self.__t1 = t1
        self.__sql = list(SQL_TEMPLATE)
        self.__debug = debug
        self.__rows: List[Dict[str, Any]] = []
        self.__rel: List[IRelationship] = []

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
        f: List[str] = Builder.parse_fields(self.__f, self.__t1, cast="list")
        entries = Builder.parse_rows(f, self.__rows)

        self.close()
        return entries

    def fetchone(self) -> Dict[str, Any]:
        """Fetch & parse only one row and finally close the connection to the database"""

        if self.__cur is None:
            raise TypeError("Unexpected error: the cursor is None")

        f = Builder.parse_fields(self.__f, self.__t1, cast="list")
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
        self.__dml = "INSERT"

        f = Builder.parse_fields(self.__f, self.__t1, dml=self.__dml)
        v = self.__v
        placeholders = Builder.resolve_question_mark(len(v))
        self.__sql[0] = f"INSERT INTO {self.__t1} ( {f} ) VALUES ( {placeholders} )"
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
        self.__dml = "SELECT"

        f = [Builder.parse_fields(self.__f, self.__t1, sep=".", dml=self.__dml)]

        if len(self.__rel) > 0:
            for row in self.__rel:
                t2: str = row["t"]
                type: Relationship = row["type"]
                alias: str | None = row["alias"]

                if type == Relationship.HAS_ONE:
                    f.append(
                        Builder.parse_fields(
                            "*", t2, prefix=True, sep=":", dml=self.__dml, alias=alias
                        )
                    )
                elif type == Relationship.HAS_MANY:
                    f.append(
                        Builder.parse_fields(
                            "*", t2, prefix=True, sep="@", dml=self.__dml, alias=alias
                        )
                    )
                # elif type == Relationship.BELONGS_TO_ONE:
                #     f.append(Builder.parse_fields('*', t2, prefix=True, dml=self.__dml))
                # elif type == Relationship.BELONGS_TO_MANY:
                #     f.append(Builder.parse_fields('*', t2, prefix=True, dml=self.__dml))

            f = ", ".join(f).split(", ")
            self.__f = [x.split(" AS ")[1][1:-1] if " AS " in x else x for x in f]

        self.__sql[0] = f"SELECT {', '.join(f)} FROM {self.__t1}"
        return self.__run()

    def update(self):
        """Update a row in the table"""
        self.__dml = "UPDATE"

        if self.__f == "*":
            raise AssertionError("You can't update a row without specifying all fields")

        s = Builder.parse_sets(self.__f, self.__v)
        v = self.__v
        self.__sql[0] = f"UPDATE {self.__t1} SET {s}"
        self.__run(v)
        self.close()

    def delete(self):
        """Delete a row from the table - Unstable ⚠️"""
        self.__dml = "DELETE"

        self.__sql[0] = f"DELETE FROM {self.__t1}"
        self.__run()
        self.close()

    @overload
    def relation(
        self,
        t2: str,
        fk: str | None = None,
        alias: str | None = None,
        *,
        pivot: str | None = None,
        fk_2: str | None = None,
        relationship: Literal[
            Relationship.BELONGS_TO_MANY
        ] = Relationship.BELONGS_TO_MANY,
    ) -> Self: ...
    @overload
    def relation(
        self,
        t2: str,
        fk: str | None = None,
        alias: str | None = None,
        *,
        relationship: Literal[
            Relationship.HAS_ONE, Relationship.BELONGS_TO_ONE, Relationship.HAS_MANY
        ] = Relationship.HAS_ONE,
    ) -> Self: ...
    def relation(
        self,
        t2: str,
        fk: str | None = None,
        alias: str | None = None,
        pivot: str | None = None,
        fk_2: str | None = None,
        relationship: Relationship = Relationship.HAS_ONE,
    ):
        if fk is None:
            fk = f"{t2[:-1]}_id"
        if fk_2 is None:
            fk_2 = f"{self.__t1[:-1]}_id"

        self.__rel.append({"t": t2, "type": relationship, "alias": alias})

        if len(self.__sql[1]) > 0:
            self.__sql[1] += f"\n"

        if relationship == Relationship.HAS_ONE:
            self.__sql[1] += f"INNER JOIN {t2} ON {self.__t1}.{fk} = {t2}.id"
        elif relationship == Relationship.HAS_MANY:
            self.__sql[1] += f"LEFT JOIN {t2} ON {self.__t1}.id = {t2}.{fk}"
        elif relationship == Relationship.BELONGS_TO_ONE:
            self.__sql[1] += f"INNER JOIN {t2} ON {self.__t1}.{fk} = {t2}.id"
        elif relationship == Relationship.BELONGS_TO_MANY:
            self.__sql[
                1
            ] += f"""INNER JOIN {pivot} ON {self.__t1}.id = {pivot}.{fk_2}
INNER JOIN {t2} ON {pivot}.id = {t2}.{fk}"""

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
        self.__sql[5] = f"LIMIT {n}"
        return self
