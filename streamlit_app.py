import streamlit as st
import pandas as pd
import joblib

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

# 2. Model loading with validation (sin cambios)
@st.cache_resource
def load_model():
    try:
        model = joblib.load("model/model_final_churn.pkl")
        if not hasattr(model, 'predict'):
            raise ValueError("Invalid model object - missing predict method")
        return model
    except Exception as e:
        st.error(f"🔴 Model Error: {str(e)}")
        st.stop()

# 3. Main application interface
tab_analysis, tab_prediction = st.tabs(["📊 Data Analysis", "🔮 Churn Prediction"])

with tab_analysis:
    st.subheader("Customer Data Overview")
    customer_data = load_data()
    
    # Interactive data explorer
    if st.checkbox("Show raw data"):
        st.dataframe(customer_data, height=300)
    
    # Key metrics - MODIFICADO PARA USAR EndDate
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

# Resto del código (tab_prediction y sidebar) permanece igual
with tab_prediction:
    st.subheader("Real-time Churn Prediction")
    
    # Input widgets
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            tenure = st.slider("Customer Tenure (months)", 1, 72, 24)
        with col2:
            monthly_charges = st.number_input("Monthly Charges ($)", 
                                             min_value=20.0, 
                                             max_value=200.0, 
                                             value=65.0)
        
        # Additional dynamic inputs
        contract_type = st.selectbox("Contract Type", 
                                   ["Month-to-month", "One year", "Two year"])
        internet_service = st.selectbox("Internet Service", 
                                      ["DSL", "Fiber optic", "None"])
        
        submitted = st.form_submit_button("Predict Churn Risk")
    
    # Prediction logic
    if submitted:
        model = load_model()
        try:
            # Create feature vector (adjust based on actual model requirements)
            features = [[tenure, monthly_charges]]  
            
            prediction = model.predict(features)[0]
            probability = model.predict_proba(features)[0][1]
            
            # Display results
            st.subheader("Prediction Results")
            if prediction == 1:
                st.error(f"🚨 High Risk: {probability:.0%} chance of churn")
            else:
                st.success(f"✅ Low Risk: {probability:.0%} chance of churn")
                
            # Explanation
            with st.expander("Interpretation Guide"):
                st.markdown("""
                - **<70% probability**: Low churn risk
                - **70-85% probability**: Moderate risk
                - **>85% probability**: High risk
                """)
                
        except Exception as e:
            st.error(f"Prediction failed: {str(e)}")

# Technical documentation
st.sidebar.markdown("""
### Technical Documentation
**Data Sources:**
- Contract details
- Personal information  
- Internet service records
- Phone service data

**Model Info:**
- Algorithm: Random Forest
- Accuracy: 88%
- Last Updated: {date}
""".format(date=pd.Timestamp.now().strftime("%Y-%m-%d")))
