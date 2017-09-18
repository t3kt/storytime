import csv


def _initCsvDATDialect():
	if 'DAT' not in csv.list_dialects():
		csv.register_dialect(
			'DAT',
			delimiter='\t',
			doublequote=False,
			escapechar=None,
			lineterminator='\n',
			quoting=csv.QUOTE_NONE)

def DATDictWriter(f, fieldnames, restval='', *args, **kwargs) -> csv.DictWriter:
	_initCsvDATDialect()
	return csv.DictWriter(f, fieldnames, dialect='DAT', restval=restval, *args, **kwargs)

def DATDictReader(f, fieldnames=None, restkey=None, restval=None, *args, **kwargs) -> csv.DictReader:
	_initCsvDATDialect()
	reader = csv.DictReader(f, fieldnames=fieldnames, dialect='DAT', restkey=restkey, restval=restval, *args, **kwargs)
	reader.fieldnames  # loads and parses the first line as a side-effect
	return reader

def DATReader(f, *args, **kwargs) -> csv.reader:
	_initCsvDATDialect()
	return csv.reader(f, dialect='DAT', *args, **kwargs)

def DATWriter(f, *args, **kwargs) -> csv.writer:
	_initCsvDATDialect()
	return csv.writer(f, dialect='DAT', *args, **kwargs)
