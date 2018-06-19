from datetime import datetime

from sqlalchemy import create_engine, or_, and_, desc, func, distinct
from sqlalchemy.orm import sessionmaker
import pandas as pd
import json
import sqlite3
import time
import pymysql
import xlrd
import xlsxwriter
from sqlalchemy.sql.functions import count, char_length

import operator as op


def connectDBgetSesion():
    # engine = create_engine('sqlite:///db.sqlite3', echo=True)
    engine = create_engine('sqlite:///db.sqlite3', echo=False)
    # engine = create_engine("mysql+pymysql://root:123456@localhost:3306/testpymysql?charset=utf8", echo=True)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def close(session):
    session.commit()
    session.close()


def find_all(json_str=False):
    pass


def newCutWordTOdb(newicdword, newperfword):
    try:
        session = connectDBgetSesion()
        # "INSERT INTO custom_icd_desc (icd,word_desc) VALUES (%s,%s) "
        custom_icd_desc = Custom_icd_desc(icd=newicdword, word_desc=newperfword)

        session.add(custom_icd_desc)
    except Exception as e:
        print(e)
    finally:
        close(session)
        updatetempdict()


def updatetempdict():
    try:
        session = connectDBgetSesion()
        # sql = "SELECT DISTINCT word_desc FROM custom_icd_desc"
        all_custom_icd = session.query(distinct(Custom_icd_desc.word_desc)).all()

        fout = open("tempdict.txt", 'w', encoding='utf-8')  # 以写得方式打开文件
        for row in all_custom_icd:
            r1 = row[0]
            fout.write(r1 + '\n')  # 将分词好的结果写入到输出文件
        fout.close()

    except Exception as e:
        print(e)
    finally:
        close(session)


def updateCustom_icd(cid, icd):
    try:
        session = connectDBgetSesion()
        objquery = session.query(Custom_icd_desc).filter(Custom_icd_desc.id == cid)

        obj = objquery.one()
        oldicd = obj.icd

        objquery.update({Custom_icd_desc.icd: icd})

        if icd != oldicd:
            modifyRecord = ModifyRecord(timestamp=datetime.now(), operator='操作人', fromold=oldicd, tonew=icd,
                                        originalid=cid)
            session.add(modifyRecord)

    except Exception as e:
        print(e)
        session.rollback()
    finally:
        close(session)
        updatetempdict()


def updateCustom_icd_word(cid, word_desc):
    try:
        session = connectDBgetSesion()
        # session.query(Custom_icd_desc).filter(Custom_icd_desc.id == cid).update(
        #     {Custom_icd_desc.word_desc: word_desc})
        objquery = session.query(Custom_icd_desc).filter(Custom_icd_desc.id == cid)

        obj = objquery.one()
        oldword_desc = obj.word_desc

        objquery.update({Custom_icd_desc.word_desc: word_desc})
        if oldword_desc != word_desc:
            modifyRecord = ModifyRecord(timestamp=datetime.now(), operator='操作人', fromold=oldword_desc, tonew=word_desc,
                                        originalid=cid)
            session.add(modifyRecord)

    except Exception as e:
        print(e)
        session.rollback()
    finally:
        close(session)
        updatetempdict()


def getCustom_icd():
    try:
        session = connectDBgetSesion()
        rows1 = session.query(Icd_desc.icd, Icd_desc.word_desc).all()
        # how make it to map  and have the index for quickly search
        standard_icds = {}
        for row in rows1:
            standard_icds[row[0]] = row[1]

        print(standard_icds)
        rows2 = session.query(Custom_icd_desc.id, Custom_icd_desc.icd, Custom_icd_desc.word_desc).all()
        l = []
        dict1 = {}
        for row in rows2:
            row = row._asdict()
            icd = row['icd']
            if icd in standard_icds:
                standard_word_desc = standard_icds[icd]
                row['standard_word_desc'] = standard_word_desc
            else:
                row['standard_word_desc'] = ''
            l.append(row)

        return json.dumps(l, ensure_ascii=False)
    except Exception as e:
        print(e)
        l = []
        return json.dumps(l, ensure_ascii=False)
    finally:
        close(session)


def getModify_record():
    try:
        session = connectDBgetSesion()

        rows2 = session.query(ModifyRecord.id, ModifyRecord.timestamp, ModifyRecord.operator,
                              ModifyRecord.fromold, ModifyRecord.tonew).order_by(desc(ModifyRecord.timestamp)).offset(
            0).limit(100).all()
        l = []
        dict1 = {}
        for row in rows2:
            row = row._asdict()
            timestamp = row['timestamp']
            timestamp1 = str(timestamp)[:-7]  # .rstrip('.')
            row['timestamp'] = timestamp1

            l.append(row)

        return json.dumps(l, ensure_ascii=False)
    except Exception as e:
        print(e)
        l = []
        return json.dumps(l, ensure_ascii=False)
    finally:
        close(session)


#  获取未确认的诊断语句
def getAdiagnosis():
    try:
        session = connectDBgetSesion()
        # sql = "SELECT id,diagnosis_desc FROM diagnosis where diagnosed is NULL GROUP BY id DESC LIMIT 0,1"

        # count = session.query(DiagnosisNoRepeat) \
        #     .filter(DiagnosisNoRepeat.diagnosed != None).count()

        query = session.query(DiagnosisNoRepeat.id, DiagnosisNoRepeat.diagnosis_desc) \
            .filter(DiagnosisNoRepeat.diagnosed == None).order_by(desc(DiagnosisNoRepeat.manualicd),
                                                                  desc(DiagnosisNoRepeat.standardicd))
        rows = query.first()

        DiagnosisNoRepeatids = session.query(DiagnosisNoRepeat.id).order_by(desc(DiagnosisNoRepeat.manualicd),
                                                                            desc(DiagnosisNoRepeat.standardicd)).all()
        count = 0
        for row in DiagnosisNoRepeatids:
            count = count + 1
            if rows[0] == row[0]:
                break;

        # count = query.count()
        return count, rows[0], rows[1]

    except Exception as e:
        print(e)
        return 0, 0
    finally:
        close(session)


#  获取未确认的诊断语句
def getdiagnosisby(id):
    try:
        session = connectDBgetSesion()
        # sql = "SELECT id,diagnosis_desc FROM diagnosis where diagnosed is NULL GROUP BY id DESC LIMIT 0,1"

        query = session.query(DiagnosisNoRepeat.id, DiagnosisNoRepeat.diagnosis_desc) \
            .filter(DiagnosisNoRepeat.id == id).order_by(desc(DiagnosisNoRepeat.manualicd),
                                                         desc(DiagnosisNoRepeat.standardicd))
        rows = query.first()
        return rows[0], rows[1]

    except Exception as e:
        print(e)
        return 0, 0
    finally:
        close(session)


def sureiagnosis(diagnosisid, reverseicds):
    try:
        session = connectDBgetSesion()
        # sql = "UPDATE diagnosis SET diagnosed = 1,manualicd=%s WHERE id =%s "
        session.query(DiagnosisNoRepeat).filter(DiagnosisNoRepeat.id == diagnosisid).update(
            {DiagnosisNoRepeat.manualsure: reverseicds, DiagnosisNoRepeat.diagnosed: 1})
    except Exception as e:
        print(e)
        session.rollback()
        return 0, 0
    finally:
        close(session)


def getICDBy(perfword):
    try:
        session = connectDBgetSesion()
        # sql = "SELECT icd FROM icd_desc where word_desc=%s UNION SELECT icd FROM custom_icd_desc where word_desc=%s "
        icd = session.query(Icd_desc.icd).filter(Icd_desc.word_desc == perfword).first()
        if icd == None:
            icd = session.query(Custom_icd_desc.icd).filter(Custom_icd_desc.word_desc == perfword).first()
        if icd != None:
            icd = icd[0]
        return icd
    except Exception as e:
        print(e)
        return 0
    finally:
        close(session)


# 从ICD到多个  描述
def getICDDescBy(icd):
    try:
        session = connectDBgetSesion()
        # sql = "SELECT word_desc FROM icd_desc where icd=%s \
        # UNION SELECT word_desc FROM custom_icd_desc where icd=%s "
        word_desc1 = session.query(Icd_desc.word_desc).filter(Icd_desc.icd == icd).first()
        word_desc2 = session.query(Custom_icd_desc.word_desc).filter(Custom_icd_desc.icd == icd).all()

        word_desc = ""
        for wd in word_desc2:
            r1 = wd[0]
            word_desc = word_desc + r1 + " ; "

        if word_desc1 != None:
            return word_desc1[0] + " ; " + word_desc
        else:
            return word_desc

    except Exception as e:
        print(e)
        return 'something wrong'
    finally:
        close(session)


# diagnosis_desc,manualicd
def read_excel2diagnosis(filepath):
    workbook = xlrd.open_workbook(filepath)
    sheet = workbook.sheet_by_index(0)
    count = sheet.nrows
    datalist = []
    # count = 3
    for i in range(1, count):
        datalist.append([sheet.row_values(i)[0], sheet.row_values(i)[1]])
        # datalist.append([sheet.row_values(i)[0],sheet.row_values(i)[1], sheet.row_values(i)[2], sheet.row_values(i)[3],
        #                sheet.row_values(i)[4],sheet.row_values(i)[5]])
    batch2diagnosis(datalist)


def batch2diagnosis(datalist):
    try:
        setit = set()
        setdict = {}
        session = connectDBgetSesion()
        session.query(Diagnosis).delete()
        session.query(DiagnosisNoRepeat).delete()

        for data in datalist:
            str0 = data[0]
            str1 = data[1]
            d = Diagnosis(diagnosis_desc=str0, manualicd=str1)

            setit.add(str0)
            session.add(d)
            setdict[str0] = str1
        for skey in setit:
            if str(skey).strip(' ') == '':
                continue
            if skey in setdict:
                svalue = setdict[skey]
                d2 = DiagnosisNoRepeat(diagnosis_desc=skey, manualicd=svalue)
            else:
                d2 = DiagnosisNoRepeat(diagnosis_desc=skey)

            session.add(d2)

    except Exception as e:
        print(data)
        print(e)
    finally:
        close(session)


def export2excelfromdiagnosis(filepath):
    try:
        session = connectDBgetSesion()

        results = session.query(Diagnosis.diagnosis_desc, Diagnosis.manualicd, Diagnosis.standardicd,
                                Diagnosis.customicd, Diagnosis.alldesc, Diagnosis.subtyle, Diagnosis.manualsure)
        df = pd.read_sql(sql=results.statement, con=results.session.bind)
        # df.columns = ['诊断文字', '人工转icd', '程序转icd', '描述', '标准转', '自定义转']
        # df.columns = ['诊断文字', '原人工转ICD', '标准句转', '自定义词转', '标准描述', '分类','人工确认']
        df.columns = [COL1, COL2, COL3, COL4, COL5, COL6, COL7]

        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='diagnosis', index=False)

    except Exception as e:
        print(e)
    finally:
        close(session)


def export2excelfromDISTINCTdiagnosis(filepath):
    try:
        session = connectDBgetSesion()

        results = session.query(DiagnosisNoRepeat.diagnosis_desc, DiagnosisNoRepeat.manualicd,
                                DiagnosisNoRepeat.standardicd,
                                DiagnosisNoRepeat.customicd, DiagnosisNoRepeat.alldesc, DiagnosisNoRepeat.subtyle,
                                # DiagnosisNoRepeat.manualsure).order_by(DiagnosisNoRepeat.standardicd)
                                DiagnosisNoRepeat.manualsure).order_by(DiagnosisNoRepeat.manualicd,
                                                                       DiagnosisNoRepeat.standardicd)
        df = pd.read_sql(sql=results.statement, con=results.session.bind)

        # df.columns = ['诊断文字', '原人工转ICD', '标准句转', '自定义词转', '标准描述', '分类', '人工确认']
        df.columns = [COL1, COL2, COL3, COL4, COL5, COL6, COL7]
        # df.columns = ['诊断文字', '人工转icd', '程序转icd', '描述', '标准转', '自定义转']

        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='diagnosis', index=False)

    except Exception as e:
        print(e)
    finally:
        close(session)


def export2excelfromdiagnosisclass(filepath):
    try:
        session = connectDBgetSesion()

        results = session.query(DiagnosisNoRepeat.diagnosis_desc, DiagnosisNoRepeat.manualicd,
                                DiagnosisNoRepeat.programicd,
                                DiagnosisNoRepeat.alldesc, DiagnosisNoRepeat.standardicd, DiagnosisNoRepeat.customicd,
                                DiagnosisNoRepeat.subtyle)
        df = pd.read_sql(sql=results.statement, con=results.session.bind)
        df.columns = ['诊断文字', '人工转icd', '程序转icd', '描述', '标准转', '自定义转', "分类"]

        writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='diagnosis', index=False)

    except Exception as e:
        print(e)
    finally:
        close(session)


def tableheaddiagnosis():
    # sql = "SELECT diagnosis_desc,manualicd,programicd,standardicd,customicd FROM diagnosis ORDER BY id asc  LIMIT 0,4"
    try:
        session = connectDBgetSesion()
        dds = session.query(Diagnosis).order_by('id').offset(0).limit(4).all()
        #
        l = []
        for d in dds:
            # ['诊断文字', '人工转icd', '程序转icd', '描述', '标准转', '自定义转'])
            # 诊断文字	原人工转ICD	标准句转	自定义词转	标准描述	分类	人工确认
            l.append([d.diagnosis_desc, d.manualicd, d.standardicd, d.customicd, d.alldesc, d.subtyle, d.manualsure])

        return l
    except Exception as e:
        print(e)
        return []
    finally:
        close(session)


def tableDISTINCTdiagnosis():
    try:
        session = connectDBgetSesion()
        dds = session.query(DiagnosisNoRepeat.diagnosis_desc, DiagnosisNoRepeat.manualicd,
                            DiagnosisNoRepeat.standardicd,
                            DiagnosisNoRepeat.customicd, DiagnosisNoRepeat.alldesc, DiagnosisNoRepeat.subtyle,
                            DiagnosisNoRepeat.manualsure).order_by(desc(DiagnosisNoRepeat.manualicd),
                                                                   desc(DiagnosisNoRepeat.standardicd)).offset(0).limit(
            500).all()
        l = []
        for d in dds:
            l.append([d.diagnosis_desc, d.manualicd, d.standardicd, d.customicd, d.alldesc, d.subtyle, d.manualsure])

        return l
    except Exception as e:
        print(e)
        return []
    finally:
        close(session)


def getDISTINCTdiagnosis(page, matchstate):
    try:
        pagecount=1
        pagesize = 100
        p = int(page) - 1
        if p < 0:
            p = 0
        p = p * pagesize

        session = connectDBgetSesion()
        # dds = session.query(DiagnosisNoRepeat).order_by(desc(DiagnosisNoRepeat.manualicd),
        #                                                 desc(DiagnosisNoRepeat.standardicd)).offset(p).limit(50).all()

        if matchstate != None and matchstate == 'match':
            dds = session.query(DiagnosisNoRepeat.id, DiagnosisNoRepeat.diagnosis_desc, DiagnosisNoRepeat.manualicd,
                                DiagnosisNoRepeat.standardicd, DiagnosisNoRepeat.customicd, DiagnosisNoRepeat.alldesc,
                                DiagnosisNoRepeat.subtyle, DiagnosisNoRepeat.manualsure) \
                .filter(and_(DiagnosisNoRepeat.alldesc != None, DiagnosisNoRepeat.alldesc != '')) \
                .order_by(desc(DiagnosisNoRepeat.manualicd), desc(DiagnosisNoRepeat.standardicd)).offset(p).limit(
                pagesize).all()
            pagecount = int(session.query(DiagnosisNoRepeat.id).filter(and_(DiagnosisNoRepeat.alldesc != None, DiagnosisNoRepeat.alldesc != '')) \
            .count())/pagesize

        else:
            dds = session.query(DiagnosisNoRepeat.id, DiagnosisNoRepeat.diagnosis_desc, DiagnosisNoRepeat.manualicd,
                                DiagnosisNoRepeat.standardicd, DiagnosisNoRepeat.customicd, DiagnosisNoRepeat.alldesc,
                                DiagnosisNoRepeat.subtyle, DiagnosisNoRepeat.manualsure) \
                .filter(or_(DiagnosisNoRepeat.alldesc == None, DiagnosisNoRepeat.alldesc == '')) \
                .order_by(desc(DiagnosisNoRepeat.manualicd), desc(DiagnosisNoRepeat.standardicd)).offset(p).limit(
                pagesize).all()
            pagecount = int(session.query(DiagnosisNoRepeat.id).filter(or_(DiagnosisNoRepeat.alldesc == None, DiagnosisNoRepeat.alldesc == '')) \
            .count())/pagesize

        l = []
        for row in dds:
            row = row._asdict()
            l.append(row)
        # for d in dds:
        #     l.append([d.diagnosis_desc, d.manualicd, d.standardicd, d.customicd, d.alldesc, d.subtyle, d.manualsure])

        return l,pagecount
    except Exception as e:
        print(e)
        return []
    finally:
        close(session)


def tabletaildiagnosis():
    pass


def matchlistandupdate():
    try:
        session = connectDBgetSesion()
        # getstandardicddict
        # sql = "SELECT icd,word_desc FROM icd_desc ORDER BY LENGTH(word_desc) DESC"
        standardicddict = session.query(Icd_desc.icd, Icd_desc.word_desc).order_by(
            desc(char_length(Icd_desc.word_desc))).all()

        # getcustomicddict
        # sql = "SELECT icd,word_desc FROM custom_icd_desc ORDER BY LENGTH(word_desc) DESC"
        customicddict = session.query(Custom_icd_desc.icd, Custom_icd_desc.word_desc).order_by(
            desc(char_length(Custom_icd_desc.word_desc))).all()

        # getthediagnosis
        # sql = "SELECT id,diagnosis_desc FROM diagnosis"
        thediagnosis = session.query(DiagnosisNoRepeat.id, DiagnosisNoRepeat.diagnosis_desc).all()
        thediagnosisquery = session.query(DiagnosisNoRepeat)
        standardic = []
        customicd = []

        dict = {"可能": "A", "待排": "B", "疑似": "C"}
        begin_time = time.time()
        # i=0
        for id, diagnosis in thediagnosis:
            # i+=1
            # print(id, diagnosis)
            if len(diagnosis) < 1:
                continue

            subtyle = str_change(diagnosis, dict, repl_mode=0, mode=0, cut_str=1, duplicate=0, final_result=1)
            # print('subtyle:' + subtyle)
            thediagnosisquery.filter(DiagnosisNoRepeat.id == id).update(
                {DiagnosisNoRepeat.subtyle: subtyle})

            for icd, word_desc in standardicddict:
                # print(word_desc)
                if len(diagnosis) < 1:
                    break
                if str(diagnosis).__contains__(str(word_desc)):
                    # standardic.append(word_desc)
                    standardic.append(icd)
                    diagnosis = str(diagnosis).replace(word_desc, '')
                    continue
            for icd, word_desc in customicddict:
                # print(word_desc)
                if len(diagnosis) < 1:
                    break
                if str(diagnosis).__contains__(str(word_desc)):
                    # customicd.append(word_desc)
                    customicd.append(icd)
                    diagnosis = str(diagnosis).replace(word_desc, '')
                    continue

            if standardic.__len__() > 0 or customicd.__len__() > 0:
                # sql = "UPDATE diagnosisnorepeat SET standardicd=%s,customicd=%s WHERE id = %s"
                # cursor.execute(sql, [','.join(standardic), ','.join(customicd), id])
                thediagnosisquery.filter(DiagnosisNoRepeat.id == id).update(
                    {DiagnosisNoRepeat.standardicd: ','.join(standardic),
                     DiagnosisNoRepeat.customicd: ','.join(customicd)})
                # print(standardic)
                # print(customicd)

            standardic = []
            customicd = []

        begin_time2 = time.time()
        # print('time:',(begin_time2-begin_time))
        # 0.017 time: 293.01399993896484 time: 282.0129997730255time: 281.6879999637604  time: 327.47899985313416time: 316.5099997520447

    except Exception as e:
        print(e)
        return None
    finally:
        close(session)
        setDiagnosissNoRepeatDesc()
        resetDiagnosis()


#  select    标准匹配 XXX条ICD码； 自定义规则匹配XXX条ICD码
def statisticit():
    try:
        session = connectDBgetSesion()
        # sql = "SELECT COUNT(standardicd) from diagnosis WHERE LENGTH(standardicd)>1"
        # sql2 = "SELECT COUNT(customicd) from diagnosis WHERE LENGTH(customicd)>1"
        COUNT_standardicd = session.query(DiagnosisNoRepeat.id).filter(and_(DiagnosisNoRepeat.standardicd != '', DiagnosisNoRepeat.standardicd != None)).count()
        COUNT_customicd = session.query(DiagnosisNoRepeat.id).filter(and_(DiagnosisNoRepeat.customicd != '', DiagnosisNoRepeat.customicd != None)).count()
        COUNT_distinct = session.query(DiagnosisNoRepeat.id).count()

        return COUNT_distinct,COUNT_standardicd, COUNT_customicd
    except Exception as e:
        print(e)
        return 0, 0
    finally:
        close(session)


def countdiagnosis():
    try:
        session = connectDBgetSesion()
        return session.query(Diagnosis).count()
    except Exception as e:
        print(e)
        return 0
    finally:
        close(session)


def searchICDfromDb(newicdword):
    try:
        session = connectDBgetSesion()
        # sql = "SELECT * from custom_icd_desc  where icd LIKE %s   LIMIT 0,10 UNION \
        #     SELECT * from icd_desc  where icd LIKE %s  LIMIT 0,10"
        rows1 = session.query(Icd_desc.icd, Icd_desc.word_desc).filter(
            Icd_desc.icd.like("%" + newicdword + "%")).offset(0).limit(12).all()
        rows2 = session.query(Custom_icd_desc.icd, Custom_icd_desc.word_desc).filter(
            Custom_icd_desc.icd.like("%" + newicdword + "%")).offset(0).limit(12).all()

        dict1 = {}
        for row in rows1:
            row = row._asdict()
            icd = row['icd']
            oldicdvalue = dict1.get(icd)
            if oldicdvalue == None:
                dict1[icd] = row['word_desc'] + " &nbsp;,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    "
            else:
                dict1[icd] = oldicdvalue + row['word_desc'] + " &nbsp;,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    "
        for row in rows2:
            row = row._asdict()
            icd = row['icd']
            oldicdvalue = dict1.get(icd)
            if oldicdvalue == None:
                dict1[icd] = row['word_desc'] + " &nbsp;,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    "
            else:
                dict1[icd] = oldicdvalue + row['word_desc'] + " &nbsp;,&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;    "
        # return json.dumps([dict(ix) for ix in rows], ensure_ascii=False)
        # return json.dumps(rows, ensure_ascii=False)
        return json.dumps(dict1, ensure_ascii=False)
    except Exception as e:
        print(e)
        dict1 = {}
        return json.dumps(dict1, ensure_ascii=False)
    finally:
        close(session)


# 搜索所有的相关 词
def searchPerfwordfromDb(perfword):
    try:
        session = connectDBgetSesion()
        sql = "SELECT icd,word_desc FROM icd_desc where word_desc like %s LIMIT 0,15 \
            UNION SELECT icd,word_desc FROM custom_icd_desc where word_desc LIKE %s  LIMIT 0,15"
        rows1 = session.query(Icd_desc.icd, Icd_desc.word_desc).filter(
            Icd_desc.word_desc.like("%" + perfword + "%")).offset(0).limit(15).all()
        rows2 = session.query(Custom_icd_desc.icd, Custom_icd_desc.word_desc).filter(
            Custom_icd_desc.word_desc.like("%" + perfword + "%")).offset(0).limit(15).all()
        l = []
        for row in rows1:
            row = row._asdict()
            l.append(row)
        for row in rows2:
            row = row._asdict()
            l.append(row)

        return json.dumps(l, ensure_ascii=False)
    except Exception as e:
        print(e)
        return json.dumps([], ensure_ascii=False)
    finally:
        close(session)


# 搜索所有的相关 词
# 计算与reverse_icds 的id距离， 排序前15个为输出
def searchPerfwordfromDbNew(perfword, reverse_icds):
    try:
        # rlist = reverse_icds.strip(',').split(',')
        reverse_icds = reverse_icds.replace(" ", "")
        reverse_icds = reverse_icds.replace("\xa0", "")
        rlist = reverse_icds.split(',')
        reverse_ids = [1]
        session = connectDBgetSesion()
        reverse = session.query(Icd_desc).filter(Icd_desc.icd.in_(rlist)).all()

        if reverse is None:
            pass
        else:
            for i in reverse:
                reverse_ids.append(i.id)

        print(reverse_ids)
        rows1 = session.query(Icd_desc).filter(Icd_desc.word_desc.like("%" + perfword + "%")).all()

        theresult = []
        for id in reverse_ids:
            # print("nowid: ",id)
            for icdobj in rows1:
                icdobj.absscore = abs(icdobj.id - id)

            resort1 = sorted(rows1, key=lambda icdobj: icdobj.absscore, reverse=False)
            for i in range(15):
                if i >= len(resort1):
                    break
                theresult.append(resort1[i])
                # print(resort1[i].id,resort1[i].absscore)

        theresult = sorted(theresult, key=lambda icdobj: icdobj.absscore, reverse=False)
        l = []
        for i in range(15):
            if i >= len(theresult):
                break
            kv = {"icd": theresult[i].icd, "word_desc": theresult[i].word_desc}
            l.append(kv)

        rows2 = session.query(Custom_icd_desc.icd, Custom_icd_desc.word_desc).filter(
            Custom_icd_desc.word_desc.like("%" + perfword + "%")).offset(0).limit(15).all()
        for row in rows2:
            row = row._asdict()
            l.append(row)

        return json.dumps(l, ensure_ascii=False)
    except Exception as e:
        print(e)
        return json.dumps([], ensure_ascii=False)
    finally:
        close(session)


def setDiagnosissNoRepeatDesc():
    try:
        session = connectDBgetSesion()
        dnorepeat = session.query(DiagnosisNoRepeat).all()

        for d in dnorepeat:
            sids = d.standardicd
            cids = d.customicd
            sets = set()
            set2 = set()
            if sids is None:
                pass
            else:
                sid1ist = str(sids).split(',')
                sets = set(sid1ist)
            if cids is None:
                pass
            else:
                cidlist = str(cids).split(',')
                set2 = set(cidlist)

            sets = sets | set2
            print(sets)
            word_desc = ''
            for icd in sets:
                icd_desc = session.query(Icd_desc).filter(Icd_desc.icd == icd).first()
                if icd_desc is None:
                    continue
                word_desc = word_desc + icd_desc.word_desc + ';'

            d.alldesc = word_desc
            d.programicd = ','.join(sets)
            if str(d.programicd).startswith(','):
                d.programicd = str(d.programicd).strip(',')

    except Exception as e:
        print(e)
    finally:
        close(session)


def resetDiagnosis():
    try:
        session = connectDBgetSesion()
        dnorepeat = session.query(DiagnosisNoRepeat).all()
        bigdiagnosis = session.query(Diagnosis)

        for d in dnorepeat:
            for dd in bigdiagnosis.filter(Diagnosis.diagnosis_desc == d.diagnosis_desc).all():
                dd.manualicd = d.manualicd
                dd.standardicd = d.standardicd
                dd.customicd = d.customicd
                dd.alldesc = d.alldesc
                dd.subtyle = d.subtyle
                # dd.programicd = d.programicd
                dd.manualsure = d.manualsure

    except Exception as e:
        print(e)
    finally:
        close(session)


#  这方法有依赖性，需要icd列表，的id大小是与icd的类排序相应！
#  这样做的目的，是icd直接 是以ID来作为 其分数， 而这个分类是有意义的！
def find_recommend_words(recommend_words, reverse_icds):
    try:
        session = connectDBgetSesion()
        # sql = "SELECT * from custom_icd_desc  where icd LIKE %s   LIMIT 0,10 UNION \
        #     SELECT * from icd_desc  where icd LIKE %s  LIMIT 0,10"
        reverse = session.query(Icd_desc).filter(Icd_desc.icd.in_(reverse_icds)).all()
        reverse_ids = []
        if reverse is None:
            pass
        else:
            for i in reverse:
                reverse_ids.append(i.id)

        recommend_words.sort(key=lambda x: len(x), reverse=True)
        print(reverse_ids, reverse_icds)
        print(recommend_words)
        relist = []
        for word in recommend_words:
            # step1 find a icd by word like
            rows1 = session.query(Icd_desc).filter(Icd_desc.word_desc.like("%" + word + "%")).offset(0).limit(50).all()
            if rows1 is None:
                continue
            if len(rows1) < 1:
                continue
            # step2 find the nearby icd 的id! and compute the relate
            # 找出 距任意已翻译的点 里 最近的一点
            tmpmix = 300000
            tmpicdobj = rows1[0]
            tmpicdobj.word_inside = word

            for icdobj in rows1:
                for id in reverse_ids:
                    if abs(icdobj.id - id) < tmpmix and abs(icdobj.id - id) != 0:
                        # if abs(icdobj.id-id) < tmpmix :
                        tmpmix = abs(icdobj.id - id)
                        tmpicdobj = icdobj
                        tmpicdobj.word_inside = word

            # print(tmpicdobj.id, tmpicdobj.icd, tmpicdobj.word_desc,word,tmpicdobj.word_inside)
            #  已包含icd，则排除   最后生成list 返回 ！

            kv = {"icd": tmpicdobj.icd, "word_desc": tmpicdobj.word_desc, "id": tmpicdobj.id,
                  "word_inside": tmpicdobj.word_inside}
            relist.append(kv)

        results = [obj for obj in relist if obj["id"] not in reverse_ids]

        return results
    except Exception as e:
        print(e)
    finally:
        close(session)

# resetDiagnosis()
#
# setDiagnosissNoRepeatDesc()
# print(countdiagnosis())

# export2excelfromdiagnosis('../temp/xlsx_file2.xlsx')
# statisticit()
# matchlistandupdate()

# newCutWordTOdb('sdfsl','心心')
# searchPerfwordfromDb('心')

# -----
# recommend_words = ['心脏瓣膜病', '老年', '钙化', '性', '主闭', '轻度', '二闭', '三闭', '重度', '性主闭']
# reverse_icds = ['A01.000', 'I38.x01']
# results = find_recommend_words(recommend_words, reverse_icds)
# print(results)

# reverse_icds =  'I38.x01 , A01.000 , '
# reverse_icds = ['A01.000', 'I38.x01']
# print(searchPerfwordfromDb("老年"))
# print(searchPerfwordfromDbNew("老年",reverse_icds))
