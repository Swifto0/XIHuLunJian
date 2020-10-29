# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import dataProcessing as dp
import joblib
import json
from sklearn.preprocessing import MinMaxScaler

def test_func(test_path,save_path):
	# 请填写测试代码
	data = pd.read_csv(test_path)
	# 选手不得改变格式，测试代码跑不通分数以零算

	# #####选手填写测试集处理逻辑,在指定文件夹下生成可提交的csv文件

	# demo#
	# submission = test[['eventId']]
	# submission['label'] = 0
	# submission.to_csv(save_path + '大数据队_eta_submission_1011.csv',index = False,encoding='utf-8')
	X = dp.processing(data)
	encoders = joblib.load('..\\train_code\\encoders.pkl')
	keys = ['O', 'CN', 'Dn', 'Sni', 'Version']
	n = 0
	for key in keys:
		X[key] = X[key].map(lambda x: '<unknown>' if x not in encoders[n].classes_ else x)
		encoders[n].classes_ = np.append(encoders[n].classes_, '<unknown>')
		X[key] = encoders[n].transform(X[key])
		n += 1

	X = MinMaxScaler().fit_transform(X)
	rfc = joblib.load('..\\train_code\\model.pkl')
	results = rfc.predict(X)
	results = pd.DataFrame({
		'id': data['eventId'],
		'label': results
	})
	print(sum(results))
	results.to_csv('..\\result\\友人_eta_submission_1029.csv', index=False)


if __name__ == '__main__':
	test_path = '..\\data\\test_1.csv'
	sava_path = '..\\results\\'
	test_func(test_path,sava_path)