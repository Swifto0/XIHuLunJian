import re
import pandas as pd
import tldextract
from sklearn.preprocessing import LabelEncoder

def processing(data):
    bytesOut = data['bytesOut']
    bytesIn = data['bytesIn']
    pktsOut = data['pktsOut']
    pktsIn = data['pktsIn']
    tlsSubject = data['tlsSubject']
    tlsIssuerDn = data['tlsIssuerDn']
    tlsSni = data['tlsSni']
    tlsVersion = data['tlsVersion']


    outRatio = []  # 出流量/出包数
    inRatio = []  # 入流量/入包数
    orgName = []
    sni = []

    '''
    计算 （出流量/出包数）与（入流量/入包数）
    '''

    for i in range(len(bytesIn)):
        outRatio.append(bytesOut[i] / pktsOut[i])
        inRatio.append(bytesIn[i] / pktsIn[i])
        # print('outRatio: {}, inRatio: {}'.format(bytesOut[i] / pktsOut[i], bytesIn[i] / pktsIn[i]))

    '''
    过滤organization全部放入orgName列表
    '''
    pattern_O = 'O=.*?([,/]+|$)'

    for tmp in tlsSubject:  # 读取TLSSubject内容，将O=字段截出，保存入orgName列表，空值填入NaN字符串
        if pd.isna(tmp):
            orgName.append('NULL')
        else:
            res = re.search(pattern_O, tmp)
            if res:
                res = res.group()
                if res.startswith('O='):
                    res = res[2:]
                if res.endswith(','):
                    res = res[:-1]
                if res.endswith('.'):
                    res = res[:-1]
                if res.endswith('./'):
                    res = res[:-2]
                orgName.append(res)
            else:
                orgName.append('null')  # 区分所有字段的缺失与单字段的缺失

    '''
    过滤Subject中的CN
    '''
    pattern_CN = 'CN=.*?(/|$)'
    commonName = []

    for tmp in tlsSubject:
        if pd.isna(tmp):
            commonName.append('NULL')
        else:
            res = re.search(pattern_CN, tmp)
            if res:
                res = res.group()
                if res.startswith('CN='):
                    res = res[3:]
                if res.endswith('/'):
                    res = res[:-1]
                commonName.append(res)
            else:
                commonName.append('null')

    '''
    过滤tlsIssuerDn中的CN
    '''
    pattern_CN = 'CN=.*?(/|$)'
    dn_commonName = []

    for tmp in tlsIssuerDn:
        if pd.isna(tmp):
            dn_commonName.append('NULL')
        else:
            res = re.search(pattern_CN, tmp)
            if res:
                res = res.group()
                if res.startswith('CN='):
                    res = res[3:]
                if res.endswith('/'):
                    res = res[:-1]
                dn_commonName.append(res)
            else:
                dn_commonName.append('null')

    '''
    从tlsSni取顶级域名
    '''
    for tmp in tlsSni:
        if pd.isna(tmp):
            sni.append('NULL')
        else:
            tld = tldextract.extract(tmp)
            sni.append(tld.domain)

    X = pd.DataFrame({
        'O': orgName,
        'CN': commonName,
        'Dn': dn_commonName,
        'Sni': sni,
        'Version': tlsVersion,
        'OutRatio': outRatio,
        'InRatio': inRatio
    })
    return X

def encoder(data):
    '''
    编码特征数据
    '''

    org_encoder = LabelEncoder().fit(data['O'])  # 将orgName内元素编码为数字
    cmName_encoder = LabelEncoder().fit(data['CN'])  # 将commonName内元素编码为数字
    dncm_encoder = LabelEncoder().fit(data['Dn'])
    sni_encoder = LabelEncoder().fit(data['Sni'])
    version_encoder = LabelEncoder().fit(data['Version'])  # 将证书版本编码
    encoders = [org_encoder, cmName_encoder, dncm_encoder, sni_encoder, version_encoder]

    return encoders