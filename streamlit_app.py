import streamlit as st
import pandas as pd
import joblib
import os

# Page configuration
st.set_page_config(page_title="Churn Prediction Dashboard", layout="wide")

# Title and description
st.title("📊 Telecom Churn Prediction Model")
st.markdown("""
Interactive application for predicting customer churn risk.
Data loaded from multiple sources.
""")

# 1. Data loading with enhanced error handling
@st.cache_data
def load_data():
    try:
        # Load individual datasets
        contract = pd.read_csv("data/contract.csv")
        personal = pd.read_csv("data/personal.csv") 
        internet = pd.read_csv("data/internet.csv")
        phone = pd.read_csv("data/phone.csv")
        
        # Validate required columns
        required_cols = ['customerID']
        for df, name in zip([contract, personal, internet, phone],
                          ['contract', 'personal', 'internet', 'phone']):
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing customerID in {name} dataset")
        
        # Merge datasets
        merged_df = contract.merge(personal, on='customerID', how='left', validate='one_to_one')
        merged_df = merged_df.merge(internet, on='customerID', how='left', validate='one_to_one')
        merged_df = merged_df.merge(phone, on='customerID', how='left', validate='one_to_one')
        
        # Data quality check
        if merged_df.isnull().sum().sum() > 0:
            st.warning("Warning: Merged data contains missing values")
            
        # Crear columna Churn basada en EndDate si no existe
        if 'Churn' not in merged_df.columns and 'EndDate' in merged_df.columns:
            merged_df['Churn'] = merged_df['EndDate'].apply(lambda x: 0 if str(x) == "No" else 1)
            
        return merged_df
    
    except FileNotFoundError as e:
        st.error(f"🔴 Critical Error: Missing data file - {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"🔴 System Error: {str(e)}")
        st.stop()

# 2. Model loading with validation
@st.cache_resource
def load_model():
    try:
        model_path = "model/modelo_final_churn.pkl"
        
        if not os.path.exists(model_path):
            st.error(f"🔴 Error: Archivo del modelo no encontrado en {os.path.abspath(model_path)}")
            st.stop()
            
        model = joblib.load(model_path)
        
        if not hasattr(model, 'predict'):
            raise ValueError("Objeto de modelo inválido - falta el método predict")
            
        # Mostrar características esperadas (para debug)
        if hasattr(model, 'feature_names_in_'):
            st.session_state['model_features'] = list(model.feature_names_in_)
            
        return model
        
    except Exception as e:
        st.error(f"🔴 Error al cargar el modelo: {str(e)}")
        st.stop()

# 3. Main application interface
tab_analysis, tab_prediction = st.tabs(["📊 Data Analysis", "🔮 Churn Prediction"])

with tab_analysis:
    st.subheader("Customer Data Overview")
    customer_data = load_data()
    
    if st.checkbox("Show raw data"):
        st.dataframe(customer_data, height=300)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(customer_data))
    with col2:
        if 'EndDate' in customer_data.columns:
            churn_rate = (customer_data['EndDate'] != "No").mean()
            st.metric("Churn Rate", f"{churn_rate:.1%}")
        else:
            st.warning("Churn data not available")
    with col3:
        if 'tenure' in customer_data.columns:
            st.metric("Avg Tenure", f"{customer_data['tenure'].mean():.1f} months")
        else:
            st.warning("Tenure data not available")

with tab_prediction:
    st.subheader("Real-time Churn Prediction")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            tenure = st.slider("Customer Tenure (months)", 1, 72, 24)
        with col2:
            monthly_charges = st.number_input("Monthly Charges ($)", 
                                           min_value=20.0, 
                                           max_value=200.0, 
                                           value=65.0)
        
        # Additional inputs matching the model's expected features
        contract_type = st.selectbox("Contract Type", 
                                   ["Month-to-month", "One year", "Two year"])
        internet_service = st.selectbox("Internet Service", 
                                      ["DSL", "Fiber optic", "None"])
        payment_method = st.selectbox("Payment Method",
                                    ["Electronic check", "Mailed check", "Bank transfer", "Credit card"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        gender = st.selectbox("Gender", ["Male", "Female"])
        senior_citizen = st.selectbox("Senior Citizen", ["No", "Yes"])
        partner = st.selectbox("Partner", ["No", "Yes"])
        dependents = st.selectbox("Dependents", ["No", "Yes"])
        phone_service = st.selectbox("Phone Service", ["No", "Yes"])
        multiple_lines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
        online_security = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
        online_backup = st.selectbox("Online Backup", ["No", "Yes", "No internet service"])
        device_protection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
        tech_support = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])
        streaming_tv = st.selectbox("Streaming TV", ["No", "Yes", "No internet service"])
        streaming_movies = st.selectbox("Streaming Movies", ["No", "Yes", "No internet service"])
        
        submitted = st.form_submit_button("Predict Churn Risk")
    
    if submitted:
        model = load_model()
        try:
            # Create complete feature dictionary
            input_data = {
                'tenure': tenure,
                'MonthlyCharges': monthly_charges,
                'TotalCharges': tenure * monthly_charges,
                
                # Contract type (one-hot)
                'Contract_Month-to-month': 1 if contract_type == "Month-to-month" else 0,
                'Contract_One year': 1 if contract_type == "One year" else 0,
                'Contract_Two year': 1 if contract_type == "Two year" else 0,
                
                # Internet service (one-hot)
                'InternetService_DSL': 1 if internet_service == "DSL" else 0,
                'InternetService_Fiber optic': 1 if internet_service == "Fiber optic" else 0,
                'InternetService_No': 1 if internet_service == "None" else 0,
                
                # Payment method (one-hot)
                'PaymentMethod_Electronic check': 1 if payment_method == "Electronic check" else 0,
                'PaymentMethod_Mailed check': 1 if payment_method == "Mailed check" else 0,
                'PaymentMethod_Bank transfer (automatic)': 1 if payment_method == "Bank transfer" else 0,
                'PaymentMethod_Credit card (automatic)': 1 if payment_method == "Credit card" else 0,
                
                # Other features
                'PaperlessBilling_Yes': 1 if paperless_billing == "Yes" else 0,
                'gender_Male': 1 if gender == "Male" else 0,
                'SeniorCitizen_1': 1 if senior_citizen == "Yes" else 0,
                'Partner_Yes': 1 if partner == "Yes" else 0,
                'Dependents_Yes': 1 if dependents == "Yes" else 0,
                'PhoneService_Yes': 1 if phone_service == "Yes" else 0,
                'MultipleLines_No': 1 if multiple_lines == "No" else 0,
                'MultipleLines_Yes': 1 if multiple_lines == "Yes" else 0,
                'MultipleLines_No phone service': 1 if multiple_lines == "No phone service" else 0,
                'OnlineSecurity_No': 1 if online_security == "No" else 0,
                'OnlineSecurity_Yes': 1 if online_security == "Yes" else 0,
                'OnlineSecurity_No internet service': 1 if online_security == "No internet service" else 0,
                'OnlineBackup_No': 1 if online_backup == "No" else 0,
                'OnlineBackup_Yes': 1 if online_backup == "Yes" else 0,
                'OnlineBackup_No internet service': 1 if online_backup == "No internet service" else 0,
                'DeviceProtection_No': 1 if device_protection == "No" else 0,
                'DeviceProtection_Yes': 1 if device_protection == "Yes" else 0,
                'DeviceProtection_No internet service': 1 if device_protection == "No internet service" else 0,
                'TechSupport_No': 1 if tech_support == "No" else 0,
                'TechSupport_Yes': 1 if tech_support == "Yes" else 0,
                'TechSupport_No internet service': 1 if tech_support == "No internet service" else 0,
                'StreamingTV_No': 1 if streaming_tv == "No" else 0,
                'StreamingTV_Yes': 1 if streaming_tv == "Yes" else 0,
                'StreamingTV_No internet service': 1 if streaming_tv == "No internet service" else 0,
                'StreamingMovies_No': 1 if streaming_movies == "No" else 0,
                'StreamingMovies_Yes': 1 if streaming_movies == "Yes" else 0,
                'StreamingMovies_No internet service': 1 if streaming_movies == "No internet service" else 0
            }
            
            # Convert to DataFrame
            features = pd.DataFrame([input_data])
            
            # Ensure all expected features are present
            if hasattr(model, 'feature_names_in_'):
                missing_features = set(model.feature_names_in_) - set(features.columns)
                for feature in missing_features:
                    features[feature] = 0  # Add missing features with default value
                
                # Reorder columns to match training data
                features = features[model.feature_names_in_]
            
            # Make prediction
            if hasattr(model, 'predict_proba'):
                prediction = model.predict(features)[0]
                probability = model.predict_proba(features)[0][1]
                
                st.subheader("Prediction Results")
                if prediction == 1:
                    st.error(f"🚨 High Risk: {probability:.0%} chance of churn")
                else:
                    st.success(f"✅ Low Risk: {probability:.0%} chance of churn")
            else:
                prediction = model.predict(features)[0]
                st.subheader("Prediction Results")
                if prediction == 1:
                    st.error("🚨 High Risk: Customer likely to churn")
                else:
                    st.success("✅ Low Risk: Customer unlikely to churn")
                
            with st.expander("Interpretation Guide"):
                st.markdown("""
                - **<70% probability**: Low churn risk
                - **70-85% probability**: Moderate risk
                - **>85% probability**: High risk
                """)
                
            # Debug: Show features used (opcional)
            with st.expander("Debug: Features Used"):
                st.write(features.T)
                
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")
            if hasattr(model, 'feature_names_in_'):
                st.warning(f"Model expects these features: {list(model.feature_names_in_)}")

# =============================================
# NUEVA DOCUMENTACIÓN EN SIDEBAR (REEMPLAZA LO ANTERIOR)
# =============================================

st.sidebar.markdown("## 📋 Project Documentation")

# Pestañas principales
tab_docs, tab_links = st.sidebar.tabs(["Project Info", "External Links"])

with tab_docs:
    with st.expander("📌 Assignment Overview", expanded=True):
        st.markdown("""
        **Telecom operator Interconnect** needs to predict customer churn to offer retention promotions.

        ### Core Services:
        - Landline & Internet (DSL/Fiber)
        - Value-added services:
          - Security: DeviceProtection, OnlineSecurity
          - TechSupport, OnlineBackup
          - StreamingTV/Movies
        """)
    
    with st.expander("📊 Data Structure"):
        st.table(pd.DataFrame({
            "File": ["contract.csv", "personal.csv", "internet.csv", "phone.csv"],
            "Records": [7043, 7043, 5517, 6361],
            "Key Fields": ["ContractType, PaymentMethod", "Gender, SeniorCitizen", 
                          "InternetService, OnlineSecurity", "PhoneService, MultipleLines"]
        }))
    
    with st.expander("🤖 Model Details"):
        st.markdown("""
        - **Algorithm**: Random Forest
        - **Accuracy**: 88%
        - **Precision**: 85%
        - **Recall**: 82%
        - **Last Updated**: 2025-07-15
        """)
        st.progress(0.88)

with tab_links:
    st.markdown("### 🔗 Project Resources")
    st.markdown("""
    <a href="https://github.com/EnyaBarroso/Churn-prediction-in-telecommunications" target="_blank">
        <img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" style="width:200px;">
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <a href="https://enyabarroso.github.io/Churn-prediction-in-telecommunications/" target="_blank">
        <img src="https://img.shields.io/badge/GitHub_Pages-Documentation-green?logo=github" style="width:200px;">
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📬 Contact
    - [Email me](mailto:enyabarroso1998@gmail.com)
    - [LinkedIn Profile](https://www.linkedin.com/in/enya-alvarez-barroso/)
    - [GitHub Profile](https://github.com/EnyaBarroso)
    """)

# =============================================
# FIN DEL CÓDIGO
# =============================================
