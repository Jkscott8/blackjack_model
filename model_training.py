import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib
import warnings
from sklearn.utils.class_weight import compute_class_weight
from sklearn.tree import plot_tree
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')


df = pd.read_csv('blackjack_hit_outcome_dataset.csv')

feature_columns = ['player_card1','player_card2','player_initial_score','player_is_soft','player_num_aces','dealer_visible_card']
stay = ['stay_outcome']
hit = ['hit_outcome']

x = df[feature_columns]
y_hit = df[hit]
y_stay = df[stay]

x_train, x_test, y_stay_train, y_stay_test, y_hit_train, y_hit_test = (
    train_test_split(x, y_stay, y_hit, test_size=0.2, random_state=42))


model_stay = RandomForestClassifier(n_estimators=200, random_state=42, oob_score=True)
model_stay.fit(x_train, y_stay_train)

model_hit = RandomForestClassifier(n_estimators=200, random_state=42, oob_score=True)
model_hit.fit(x_train, y_hit_train)

y_hit_pred = model_hit.predict(x_test)
y_stay_pred = model_stay.predict(x_test)

joblib.dump(model_stay, 'blackjack_stay_prob_model.joblib')
joblib.dump(model_hit, 'blackjack_hit_prob_model.joblib')

print("=== HIT Model Performance ===")
print("Classification Report:")
print(classification_report(y_hit_test, y_hit_pred))

print("Confusion Matrix:")
cm_hit = confusion_matrix(y_hit_test, y_hit_pred)
print(pd.DataFrame(cm_hit,
                   index=['Actual Lose','Actual Tie','Actual Win'],
                   columns=['Predicted Lose','Predicted Tie','Predicted Win']))

print(f"Accuracy: {accuracy_score(y_hit_test, y_hit_pred):.2f}")


print("\n=== STAY Model Performance ===")
print("Classification Report:")
print(classification_report(y_stay_test, y_stay_pred))

print("Confusion Matrix:")
cm_stay = confusion_matrix(y_stay_test, y_stay_pred)
print(pd.DataFrame(cm_stay,
                   index=['Actual Lose','Actual Tie','Actual Win'],
                   columns=['Predicted Lose','Predicted Tie','Predicted Win']))

print(f"Accuracy: {accuracy_score(y_stay_test, y_stay_pred):.2f}")


importances = model_hit.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importances:")
print(feature_importance_df.to_string(index=False))


importances = model_stay.feature_importances_
feature_importance_df = pd.DataFrame({
    'Feature': feature_columns,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

print("\nFeature Importances:")
print(feature_importance_df.to_string(index=False))
