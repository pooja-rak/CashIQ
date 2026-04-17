import pandas as pd
import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

os.makedirs("models", exist_ok=True)


atm_master = pd.read_csv("atm_master_data.csv")
crowd_df = pd.read_csv("atm_crowd_data.csv")
cash_df = pd.read_csv("atm_cash_data.csv")
condition_df = pd.read_csv("atm_condition_data.csv")


le_atm = LabelEncoder()
le_crowd = LabelEncoder()
le_cash = LabelEncoder()
le_condition = LabelEncoder()
le_time = LabelEncoder()
le_day = LabelEncoder()

le_atm.fit(atm_master["atm_id"])


crowd_df["atm_id_enc"] = le_atm.transform(crowd_df["atm_id"])
crowd_df["time_enc"] = le_time.fit_transform(crowd_df["time_slot"])
crowd_df["day_enc"] = le_day.fit_transform(crowd_df["day"])
crowd_df["crowd_enc"] = le_crowd.fit_transform(crowd_df["crowd_level"])


crowd_df["is_weekend"] = crowd_df["day"].isin(["Sat", "Sun"]).astype(int)


X_crowd = crowd_df[
    ["atm_id_enc", "time_enc", "day_enc", "is_weekend"]
]
y_crowd = crowd_df["crowd_enc"].copy()


noise_idx = X_crowd.sample(frac=0.05, random_state=42).index
y_crowd.loc[noise_idx] = np.random.choice(y_crowd.unique(), size=len(noise_idx))

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X_crowd, y_crowd,
    test_size=0.2,
    stratify=y_crowd,
    random_state=42
)


crowd_model = RandomForestClassifier(
    n_estimators=80,
    max_depth=6,
    min_samples_leaf=20,
    min_samples_split=40,
    max_features=0.7,
    class_weight="balanced",
    random_state=42
)

crowd_model.fit(X_train, y_train)
y_pred = crowd_model.predict(X_test)

print("\n================ CROWD MODEL ================")
print("Accuracy:", accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=le_crowd.classes_))
crowd_accuracy = accuracy_score(y_test, y_pred)

cash_df["atm_id_enc"] = le_atm.transform(cash_df["atm_id"])
cash_df["time_enc"] = le_time.transform(cash_df["time_slot"])
cash_df["cash_enc"] = le_cash.fit_transform(cash_df["cash_level"])


crowd_lookup = crowd_df[
    ["atm_id_enc", "time_enc", "crowd_enc", "is_weekend"]
].drop_duplicates()

cash_df = cash_df.merge(
    crowd_lookup,
    on=["atm_id_enc", "time_enc"],
    how="left"
)

cash_df["crowd_enc"] = cash_df["crowd_enc"].fillna(
    cash_df["crowd_enc"].mode()[0]
)
cash_df["is_weekend"] = cash_df["is_weekend"].fillna(0)



X_cash = cash_df[
    ["atm_id_enc", "time_enc", "crowd_enc", "is_weekend"]
]
y_cash = cash_df["cash_enc"]

X_train, X_test, y_train, y_test = train_test_split(
    X_cash, y_cash,
    test_size=0.2,
    stratify=y_cash,
    random_state=42
)

cash_model = RandomForestClassifier(
    n_estimators=250,
    max_depth=12,
    min_samples_leaf=4,
    min_samples_split=8,
    max_features="sqrt",
    class_weight="balanced_subsample",
    n_jobs=-1,
    random_state=42
)

cash_model.fit(X_train, y_train)
y_pred = cash_model.predict(X_test)

print("\n================ CASH MODEL ================")
print("Accuracy:", accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=le_cash.classes_))
cash_accuracy = accuracy_score(y_test, y_pred)

condition_df["atm_id_enc"] = le_atm.transform(condition_df["atm_id"])
condition_df["condition_enc"] = le_condition.fit_transform(condition_df["condition"])

X_cond = condition_df[["atm_id_enc"]]
y_cond = condition_df["condition_enc"]

X_train, X_test, y_train, y_test = train_test_split(
    X_cond, y_cond,
    test_size=0.2,
    stratify=y_cond,
    random_state=42
)

condition_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=5,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=42
)

condition_model.fit(X_train, y_train)
y_pred = condition_model.predict(X_test)

print("\n============== CONDITION MODEL ==============")
print("Accuracy:", accuracy_score(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=le_condition.classes_))
condition_accuracy = accuracy_score(y_test, y_pred)

pickle.dump(crowd_model, open("crowd_model.pkl", "wb"))
pickle.dump(cash_model, open("cash_model.pkl", "wb"))
pickle.dump(condition_model, open("condition_model.pkl", "wb"))

pickle.dump(le_atm, open("le_atm.pkl", "wb"))
pickle.dump(le_crowd, open("le_crowd.pkl", "wb"))
pickle.dump(le_cash, open("le_cash.pkl", "wb"))
pickle.dump(le_condition, open("le_condition.pkl", "wb"))
pickle.dump(le_time, open("le_time.pkl", "wb"))
pickle.dump(le_day, open("le_day.pkl", "wb"))

print("\n ALL MODELS TRAINED AND SAVED SUCCESSFULLY")


models = ["Crowd Model", "Cash Model", "Condition Model"]
accuracies = [crowd_accuracy, cash_accuracy, condition_accuracy]


plt.figure()
plt.bar(models, accuracies)


plt.xlabel("Models")
plt.ylabel("Accuracy")
plt.title("Model Accuracy Comparison")


for i, v in enumerate(accuracies):
    plt.text(i, v, f"{v:.2f}", ha='center')

plt.show()
