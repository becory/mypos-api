def fieldDict():
    return {
        "CharField": "text",
        "IntegerField": "number",
        "DecimalField": "decimal",
        "DateField": "date",
        "TimeField": "date",
        "DateTimeField": "date",
        "AutoField": "text",
        "BooleanField": "text",
        "ForeignKey": "text",
        "FileField": "file",
        "ManyToManyField": "select"
    }


def inputFieldDict():
    return {
        "CharField": "text",
        "IntegerField": "number",
        "DecimalField": "decimal",
        "DateField": "date",
        "TimeField": "time",
        "DateTimeField": "datetime",
        "AutoField": "text",
        "BooleanField": "text",
        "ForeignKey": "text",
        "FileField": "file",
        "ManyToManyField": "select"
    }


def dateFormat(type):
    if type == 'DateField':
        return {"dateInputFormat": 'yyyy-MM-dd', "dateOutputFormat": 'yyyy-MM-dd',
                "formatFn": "function (value) { return value != null ? value : null}"}
    elif type == 'TimeField':
        return {"dateInputFormat": 'HH:mm:ss', "dateOutputFormat": 'HH:mm:ss',
                "formatFn": "function (value) { return value != null ? value : null}"}
    elif type == 'DateTimeField':
        return {
            "dateInputFormat": 'yyyy-MM-dd\'T\'HH:mm:ss',
            "dateOutputFormat": 'yyyy-MM-dd',
            "formatFn": "function (value) { return value != null ? value : null}"
        }
    else:
        return {}
