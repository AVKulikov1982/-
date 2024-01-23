import re


c_processed = 0
c_unprocessed = 0


def prepare_document(tmp_document):
    document = ''
    if tmp_document.startswith('Отказные'):
        document = 'ОП'
    elif tmp_document.startswith('Доброволка'):
        document = 'дСС'
    elif tmp_document.startswith('Свободная'):
        document = 'прочееСерты'
    document = document.replace(' ТР ТС', '').strip()
    return document


def prepare_name(tmp_data, ):
    global c_processed, c_unprocessed
    name = ''
    if len(tmp_data.split()) <= 4:
        c_unprocessed += 1
        name = tmp_data
        if tmp_data.startswith('ООО '):
            name = tmp_data.split('ООО ')[-1].strip()
    elif tmp_data.startswith('ПАО СБЕРБАНК'):
        c_unprocessed += 1
        name = tmp_data.split('//')[1]
    # print(tmp_data.split('//')[1])
    elif tmp_data.lower().startswith('общество'):
        c_unprocessed += 1
        name = tmp_data.lower().split('общество с ограниченной ответственностью')[-1].strip().split('Р/С')[0]
    # print(tmp_data.split('ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ')[-1].strip().split('Р/С')[0])
    elif tmp_data.lower().startswith('обществу'):
        c_unprocessed += 1
        name = tmp_data.lower().split('обществу с ограниченной ответственностью')[-1].strip().split()[0]
    elif tmp_data.startswith('ООО '):
        c_unprocessed += 1
        if 'Р/С' in tmp_data:
            name = tmp_data.split('ООО ')[-1].strip().split('Р/С')[0]
        else:
            name = tmp_data.split('ООО ')[-1].strip()
    # print(tmp_data.split('ООО ')[-1].strip().split('Р/С')[0])
    elif 'кфх' in tmp_data.lower() or 'глава' in tmp_data.lower():
        name = tmp_data.replace('ИП', '')
        name = (name.lower().replace('глава', '').replace('гкфх', '').replace('кфх', '').replace('крестьянского',
                                                                                                 '').replace(
            'фермерского', '').replace('хозяйства', '')
                .replace('индивидуальный', '').replace('предприниматель', '').replace('-', '').strip())
    elif tmp_data.lower().startswith('индивидуальный'):
        c_unprocessed += 1
        if 'р/с' in tmp_data.lower():
            name = tmp_data.lower().split('индивидуальный предприниматель ')[-1].strip().split('Р/С')[0]
        else:
            name = ' '.join(tmp_data.lower().split('индивидуальный предприниматель ')[-1].strip().split()[:3])
    # print(tmp_data.split('ИНДИВИДУАЛЬНЫЙ ПРЕДПРИНИМАТЕЛЬ ')[-1].strip().split('Р/С')[0])
    elif tmp_data.lower().startswith('индивидуальному'):
        c_unprocessed += 1
        name = tmp_data.lower().split('индивидуальному предпринимателю')[-1].strip().split()[0][:-2]
    elif tmp_data.lower().startswith('ип '):
        c_unprocessed += 1
        if 'р/с' in tmp_data.lower():
            name = tmp_data.lower().split('ип ')[-1].strip().split('р/с')[0]
        else:
            name = tmp_data.lower().split('ип ')[-1].strip().split()[:3]
            if name[0].endswith('ой') or name[0].endswith('у'):
                name = name[0][:-2]
            else:
                name = ' '.join(name)
    # print(tmp_data.split('ИП ')[-1].strip().split('Р/С')[0])
    elif 'Р/С' in tmp_data:
        name = tmp_data.split('ИП ')[-1].strip().split('Р/С')[0]
        if '//' in tmp_data.split('Р/С')[0]:
            c_unprocessed += 1
            name = tmp_data.split('Р/С')[0].split('//')[0]
        # print(tmp_data.split('Р/С')[0].split('//')[0])
        else:
            c_unprocessed += 1
            name = tmp_data.split('Р/С')[0]
    # print(tmp_data.split('Р/С')[0])
    elif '//' in tmp_data:
        c_unprocessed += 1
        name = tmp_data.split('//')[0]
    # print(tmp_data.split('//')[0])
    else:
        name = re.search(r'[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+\s[А-ЯЁ][а-яё]+', tmp_data)
        if name:
            c_unprocessed += 1
            name = name.group()

        else:
            c_unprocessed += 1
            name = None
            print('error - платеж необходимо разнести в ручную')
            print(tmp_data)
    if name:
        name = name.replace('"', '').replace("'", '').replace('(', '').replace(')', '').replace('.',
                                                                                            ' ').strip().lower()
    return name
