from unittest import TestCase

from pydbml.schema import Schema
from pydbml.classes import Column
from pydbml.classes import Table
from pydbml.classes import Reference
from pydbml.classes import Note
from pydbml.exceptions import TableNotFoundError


class TestColumn(TestCase):
    def test_attributes(self) -> None:
        name = 'name'
        type_ = 'type'
        unique = True
        not_null = True
        pk = True
        autoinc = True
        default = '1'
        note = Note('note')
        comment = 'comment'
        col = Column(
            name=name,
            type_=type_,
            unique=unique,
            not_null=not_null,
            pk=pk,
            autoinc=autoinc,
            default=default,
            note=note,
            comment=comment,
        )
        self.assertEqual(col.name, name)
        self.assertEqual(col.type, type_)
        self.assertEqual(col.unique, unique)
        self.assertEqual(col.not_null, not_null)
        self.assertEqual(col.pk, pk)
        self.assertEqual(col.autoinc, autoinc)
        self.assertEqual(col.default, default)
        self.assertEqual(col.note, note)
        self.assertEqual(col.comment, comment)

    def test_schema_set(self) -> None:
        col = Column('name', 'int')
        table = Table('name')
        self.assertIsNone(col.schema)
        table.add_column(col)
        self.assertIsNone(col.schema)
        schema = Schema()
        schema.add(table)
        self.assertIs(col.schema, schema)

    def test_basic_sql(self) -> None:
        r = Column(name='id',
                   type_='integer')
        expected = '"id" integer'
        self.assertEqual(r.sql, expected)

    def test_pk_autoinc(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   pk=True,
                   autoinc=True)
        expected = '"id" integer PRIMARY KEY AUTOINCREMENT'
        self.assertEqual(r.sql, expected)

    def test_unique_not_null(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   unique=True,
                   not_null=True)
        expected = '"id" integer UNIQUE NOT NULL'
        self.assertEqual(r.sql, expected)

    def test_default(self) -> None:
        r = Column(name='order',
                   type_='integer',
                   default=0)
        expected = '"order" integer DEFAULT 0'
        self.assertEqual(r.sql, expected)

    def test_comment(self) -> None:
        r = Column(name='id',
                   type_='integer',
                   unique=True,
                   not_null=True,
                   comment="Column comment")
        expected = \
'''-- Column comment
"id" integer UNIQUE NOT NULL'''
        self.assertEqual(r.sql, expected)

    def test_dbml_simple(self):
        c = Column(
            name='order',
            type_='integer'
        )
        t = Table(name='Test')
        t.add_column(c)
        s = Schema()
        s.add(t)
        expected = '"order" integer'

        self.assertEqual(c.dbml, expected)

    def test_dbml_full(self):
        c = Column(
            name='order',
            type_='integer',
            unique=True,
            not_null=True,
            pk=True,
            autoinc=True,
            default='Def_value',
            note='Note on the column',
            comment='Comment on the column'
        )
        t = Table(name='Test')
        t.add_column(c)
        s = Schema()
        s.add(t)
        expected = \
'''// Comment on the column
"order" integer [pk, increment, default: 'Def_value', unique, not null, note: 'Note on the column']'''

        self.assertEqual(c.dbml, expected)

    def test_dbml_multiline_note(self):
        c = Column(
            name='order',
            type_='integer',
            not_null=True,
            note='Note on the column\nmultiline',
            comment='Comment on the column'
        )
        t = Table(name='Test')
        t.add_column(c)
        s = Schema()
        s.add(t)
        expected = \
"""// Comment on the column
"order" integer [not null, note: '''Note on the column
multiline''']"""

        self.assertEqual(c.dbml, expected)

    def test_dbml_default(self):
        c = Column(
            name='order',
            type_='integer',
            default='String value'
        )
        t = Table(name='Test')
        t.add_column(c)
        s = Schema()
        s.add(t)

        expected = "\"order\" integer [default: 'String value']"
        self.assertEqual(c.dbml, expected)

        c.default = 3
        expected = '"order" integer [default: 3]'
        self.assertEqual(c.dbml, expected)

        c.default = 3.33
        expected = '"order" integer [default: 3.33]'
        self.assertEqual(c.dbml, expected)

        c.default = "(now() - interval '5 days')"
        expected = "\"order\" integer [default: `now() - interval '5 days'`]"
        self.assertEqual(c.dbml, expected)

        c.default = 'NULL'
        expected = '"order" integer [default: null]'
        self.assertEqual(c.dbml, expected)

        c.default = 'TRue'
        expected = '"order" integer [default: true]'
        self.assertEqual(c.dbml, expected)

        c.default = 'false'
        expected = '"order" integer [default: false]'
        self.assertEqual(c.dbml, expected)

    def test_schema(self):
        c1 = Column(name='client_id', type_='integer')
        t1 = Table(name='products')

        self.assertIsNone(c1.schema)
        t1.add_column(c1)
        self.assertIsNone(c1.schema)
        s = Schema()
        s.add(t1)
        self.assertIs(c1.schema, s)

    def test_get_refs(self) -> None:
        c1 = Column(name='client_id', type_='integer')
        with self.assertRaises(TableNotFoundError):
            c1.get_refs()
        t1 = Table(name='products')
        t1.add_column(c1)
        c2 = Column(name='id', type_='integer', autoinc=True, pk=True)
        t2 = Table(name='clients')
        t2.add_column(c2)

        ref = Reference(type_='>', col1=c1, col2=c2, inline=True)
        s = Schema()
        s.add(t1)
        s.add(t2)
        s.add(ref)

        self.assertEqual(c1.get_refs(), [ref])

    def test_dbml_with_ref(self) -> None:
        c1 = Column(name='client_id', type_='integer')
        t1 = Table(name='products')
        t1.add_column(c1)
        c2 = Column(name='id', type_='integer', autoinc=True, pk=True)
        t2 = Table(name='clients')
        t2.add_column(c2)

        ref = Reference(type_='>', col1=c1, col2=c2)
        s = Schema()
        s.add(t1)
        s.add(t2)
        s.add(ref)

        expected = '"client_id" integer'
        self.assertEqual(c1.dbml, expected)
        ref.inline = True
        expected = '"client_id" integer [ref: > "clients"."id"]'
        self.assertEqual(c1.dbml, expected)
        expected = '"id" integer [pk, increment]'
        self.assertEqual(c2.dbml, expected)

    def test_dbml_with_ref_and_properties(self) -> None:
        c1 = Column(name='client_id', type_='integer')
        t1 = Table(name='products')
        t1.add_column(c1)
        c2 = Column(name='id', type_='integer', autoinc=True, pk=True)
        t2 = Table(name='clients')
        t2.add_column(c2)

        ref = Reference(type_='<', col1=c2, col2=c1)
        s = Schema()
        s.add(t1)
        s.add(t2)
        s.add(ref)

        expected = '"id" integer [pk, increment]'
        self.assertEqual(c2.dbml, expected)
        ref.inline = True
        expected = '"id" integer [ref: < "products"."client_id", pk, increment]'
        self.assertEqual(c2.dbml, expected)
        expected = '"client_id" integer'
        self.assertEqual(c1.dbml, expected)
