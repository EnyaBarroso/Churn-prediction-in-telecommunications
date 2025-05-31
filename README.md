Telecommunications operator Interconnect would like to be able to predict its customer churn rate. If a customer is found to be planning to leave, they will be offered promotional codes and special plan options.

### Interconnect Services

Interconnect primarily provides two types of services:

1. Landline communication. The phone can be connected to multiple lines simultaneously.

2. Internet. The network can be set up over a telephone line (DSL, Digital Subscriber Line) or a fiber optic cable.

Some other services the company offers include:

- Internet security: antivirus software (*DeviceProtection*) and a malicious website blocker (*OnlineSecurity*).
- A technical support line (*TechSupport*).
- Cloud file storage and data backup (*OnlineBackup*).
- TV streaming (*StreamingTV*) and movie directory (*StreamingMovies*).
  
Customers can choose between monthly payments or a one- or two-year contract. They can use various payment methods and receive an electronic invoice after each transaction.

### Data Description

The data consists of files obtained from various sources:

- `contract.csv` — contract information;
- `personal.csv` — customer personal data;
- `internet.csv` — information about internet services;
- `phone.csv` — information about telephone services.

In each file, the `customerID` column contains a unique code assigned to each customer. The contract information is valid as of February 1, 2020.

### Steps to follow

The following were performed:

- Data loading
- Data preprocessing
- Exploratory data analysis
- Model training and evaluation: In this project, the 'RandomForestClassifier' model was implemented.

### Results

The results obtained were:

📊 **Classification Report**

| Metric | Class 0 (No Churn) | Class 1 (Churn) | Interpretation |
|---------------|--------------------|------------------|----------------|
| **Precision** | 0.84 | 0.75 | - Of those predicted as "No Churn", 84% were correct.<br>- Of those predicted as "Churn", 75% actually canceled. |
| **Recall** | 0.79 | 0.81 | - Detected 79% of customers who DID NOT cancel.<br>- Identified 81% of customers who DID cancel. |
| **F1-Score** | 0.81 | 0.78 | Balance between precision and recall (ideal >0.8) |

🔹 **Accuracy**: 80% (good, but don't use it as your primary metric due to the initial imbalance).
🔹 **Macro Avg**: Unweighted average (important if both classes are equally relevant).


📈 **AUC-ROC: 0.8812**

- **Excellent Range:** 0.88 is well above the target minimum of 0.85.

- **Interpretation:**

○ 1.0 = Perfect prediction

○ 0.88 = Excellent ability to distinguish between customers who will and will not cancel.

○ 0.5 = Random

👉 **The model has an 88% chance of correctly classifying a random pair (customer who cancels vs. one who doesn't).**

📌 **Confusion Matrix**

| | Prediction: 0 | Prediction: 1 | Total |
|---------------|--------------------|-----------------|----------------|
| **Reality: 0** | 762 | 208 | 970 |
| **Reality: 1** | 147 | 629 | 776 |

- **True Negatives (762):** Correctly identified as non-churn.

- **False Positives (208):** Loyal customers flagged as risk (may receive unnecessary promotions).

- **False Negatives (147):** Customers who will cancel but were not detected by the model (the most critical).

- **True Positives (629):** Correctly identified as churn.


📈 **ROC Curve (AUC = 0.88)**

🎯 **Interpretation of the ROC Curve**

- **Optimum Point**: 

Close to the ideal (area under the curve = 88%)


## 📌 Final Conclusions

Throughout the analysis conducted for Interconnect, key factors influencing customer churn were identified. Among the most relevant findings are the following:

- Customers with month-to-month contracts are significantly more likely to cancel their service, while those with one- or two-year contracts show higher retention. This suggests that incentivizing long-term contracts can reduce the churn rate.

- Payment method is also related to churn: users who pay by e-check cancel more frequently than those who use automatic methods such as credit card or bank transfer.

- Customers who lack online security services or technical support tend to cancel more. This indicates that additional services have a positive impact on loyalty.

- Interestingly, fiber optic internet service, although more modern, has a higher churn rate than DSL. This could be related to unmet expectations or service issues.

Taken together, these results provide a solid foundation for Interconnect's marketing team to design more effective retention strategies, such as offering promotions to those who use electronic payments, encouraging long-term contracts, or including technical support and online security services in basic packages.
