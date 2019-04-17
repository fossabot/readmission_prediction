import numpy as np
import pandas as pd
import warnings
import xgboost as xgb
import seaborn as sns
import matplotlib.pyplot as plt

from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score

warnings.filterwarnings('ignore')

# file path
DATA_DIR = "./data"
ORI_DATA_PATH = DATA_DIR + "/diabetic_data.csv"
MAP_PATH = DATA_DIR + "/IDs_mapping.csv"
OUTPUT_DATA_PATH = DATA_DIR + "/preprocessed_data.csv"
df = pd.read_csv(OUTPUT_DATA_PATH)
# df.info()
# print('>30 readmmission', df['readmitted'][df['readmitted'] == 2].count())
# print('<30 readmmission', df['readmitted'][df['readmitted'] == 1].count())
# print('Never readmmission', df['readmitted'][df['readmitted'] == 0].count())


feature_set = ['race', 'gender', 'age',
               'admission_type_id', 'discharge_disposition_id', 'admission_source_id',
               'time_in_hospital', 'num_lab_procedures',
               'num_procedures',
               'num_medications', 'number_outpatient', 'number_emergency',
               'number_inpatient', 'diag_1', 'number_diagnoses',
               'max_glu_serum', 'A1Cresult', 'metformin', 'repaglinide', 'nateglinide',
               'chlorpropamide', 'glimepiride', 'acetohexamide', 'glipizide', 'glyburide',
               'tolbutamide',
               'pioglitazone', 'rosiglitazone', 'acarbose', 'miglitol',
               'troglitazone', 'tolazamide', 'insulin', 'glyburide-metformin',
               'glipizide-metformin', 'glimepiride-pioglitazone',
               'metformin-rosiglitazone', 'metformin-pioglitazone', 'change',
               'diabetesMed', 'num_med_changed', 'num_med_taken']

input = df[feature_set]
label = df['readmitted']

# 不均匀采样
smt = SMOTE(random_state=20)
# train_input_new, train_output_new = smt.fit_sample(input, label)
# train_input_new = pd.DataFrame(train_input_new, columns=list(input.columns))

# X_train, X_test, Y_train, Y_test = train_test_split(train_input_new, train_output_new, test_size=0.20, random_state=0)
# print("nums of train/test set: ", len(X_train), len(X_test), len(Y_train), len(Y_test))


X_train_old, X_test, Y_train_old, Y_test = train_test_split(input, label, test_size=0.20, random_state=0)

X_train, Y_train = smt.fit_sample(X_train_old, Y_train_old)
X_train = pd.DataFrame(X_train, columns=list(X_train_old.columns))

print("nums of train/test set: ", len(X_train), len(X_test), len(Y_train), len(Y_test))

#-------- XGboost ---------#
print('--- XGBoost model ---')
xg_reg = xgb.XGBClassifier()

# print("Cross Validation score: ", np.mean(cross_val_score(xg_reg, X_train, Y_train, cv=10)))  # 10-fold 交叉验证
xg_reg.fit(X_train, Y_train)

Y_test_predict = xg_reg.predict(X_test)
acc = accuracy_score(Y_test, Y_test_predict)
mat = confusion_matrix(Y_test, Y_test_predict)
f1 = f1_score(Y_test, Y_test_predict, average='weighted')
print("Accuracy: ", acc)
print("F1 score: ", f1)
print("Confusion matrix: \n", mat)
print('Overall report: \n', classification_report(Y_test, Y_test_predict))

# Save confusion matrix figure
plt.figure(figsize=(4, 4))
sns.set(font_scale=1)
sns.heatmap(mat, square=True, annot=True, cmap='Blues')
plt.xlabel('True Value')
plt.ylabel('Predict Value')
plt.title('Random Forest\n ACC: {0:.2f}%\n F1: {1:.2f}%'.format(acc * 100, f1 * 100))
plt.savefig('./images/XGBoost.png')

feature_names = X_train.columns
feature_imports = xg_reg.feature_importances_
most_imp_features = pd.DataFrame([f for f in zip(feature_names, feature_imports)],
                                 columns=["Feature", "Importance"]).nlargest(10, "Importance")
most_imp_features.sort_values(by="Importance", inplace=True)
plt.figure(figsize=(19, 11))
plt.rc('xtick',labelsize=22)
plt.barh(range(len(most_imp_features)), most_imp_features.Importance, align='center', alpha=0.8)
plt.yticks(range(len(most_imp_features)), most_imp_features.Feature, fontsize=14)
plt.xlabel('Importance', fontsize=25)
plt.title('XGBoost -- Top 10 Important Features', fontsize=25)
plt.savefig('./images/XGBfeatImportance.jpg')
# plt.show()

# ------- RF --------#
print('--- Random-forest model ---')

forest = RandomForestClassifier(n_estimators=100, max_depth=120, criterion="entropy")
# print("Cross Validation Score: ", np.mean(cross_val_score(forest, X_train, Y_train, cv=10)))
forest.fit(X_train, Y_train)

Y_test_predict = forest.predict(X_test)
acc = accuracy_score(Y_test, Y_test_predict)
mat = confusion_matrix(Y_test, Y_test_predict)
f1 = f1_score(Y_test, Y_test_predict, average='weighted')
print("Accuracy: ", acc)
print("F1 score: ", f1)
print("Confusion matrix: \n", mat)
print('Overall report: \n', classification_report(Y_test, Y_test_predict))

# Save confusion matrix figure
plt.figure(figsize=(4, 4))
sns.set(font_scale=1)
sns.heatmap(mat, square=True, annot=True, cmap='Reds')
plt.xlabel('True Value')
plt.ylabel('Predict Value')
plt.title('Random Forest\n ACC: {0:.2f}%\n F1: {1:.2f}%'.format(acc * 100, f1 * 100))
plt.savefig('./images/randomForest.png')

feature_names = X_train.columns
feature_imports = forest.feature_importances_
most_imp_features = pd.DataFrame([f for f in zip(feature_names, feature_imports)],
                                 columns=["Feature", "Importance"]).nlargest(10, "Importance")
most_imp_features.sort_values(by="Importance", inplace=True)
plt.figure(figsize=(19, 11))
plt.rc('xtick',labelsize=22)
plt.barh(range(len(most_imp_features)), most_imp_features.Importance, align='center', alpha=0.8)
plt.yticks(range(len(most_imp_features)), most_imp_features.Feature, fontsize=14)
plt.xlabel('Importance', fontsize=25)
plt.title('Random Forest -- Top 10 Important Features', fontsize=25)
plt.savefig('./images/RFfeatImportance.jpg')
# plt.show()
