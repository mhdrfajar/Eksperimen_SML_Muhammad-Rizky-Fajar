import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from joblib import dump, load # Untuk menyimpan preprocessor dan label encoder

def automate_preprocessing(raw_data_path, preprocessed_X_path, preprocessed_y_path, preprocessor_path, label_encoder_path):
    """
    Melakukan data preprocessing secara otomatis pada dataset Telco Customer Churn.
    Menyimpan data X yang telah diproses, data y yang telah di-encode,
    pipeline preprocessor, dan label encoder.
    """
    print(f"Loading raw data from: {raw_data_path}")
    df = pd.read_csv(raw_data_path)

    # Convert 'No internet service' to 'No' for consistency
    for col in ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']:
        df[col] = df[col].replace({'No internet service': 'No'})
    df['MultipleLines'] = df['MultipleLines'].replace({'No phone service': 'No'})

    # Convert 'TotalCharges' to numeric, handle errors by coercing to NaN
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')

    # Drop customerID
    df = df.drop('customerID', axis=1)

    # Separate features (X) and target (y)
    X = df.drop('Churn', axis=1)
    y = df['Churn']

    # Label Encoding for binary target 'Churn'
    le = LabelEncoder()
    y_encoded = le.fit_transform(y) # No=0, Yes=1
    print(f"Target variable mapping: {list(le.classes_)} -> {le.transform(le.classes_)}")
    dump(le, label_encoder_path) # Save LabelEncoder

    # Identify categorical and numerical columns
    categorical_cols = X.select_dtypes(include='object').columns
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns

    # Create preprocessing pipelines for numerical and categorical features
    # Numerical: Impute missing with mean, then scale
    # Categorical: Impute missing with 'missing', then OneHotEncode
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='mean')),
        ('scaler', MinMaxScaler()) # Using MinMaxScaler as in notebook
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    # Create a preprocessor object using ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ],
        remainder='passthrough' # Keep other columns (if any)
    )

    # Fit and transform the data
    X_processed_array = preprocessor.fit_transform(X)

    # Get feature names after one-hot encoding
    cat_feature_names = preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(categorical_cols)
    all_feature_names = list(numerical_cols) + list(cat_feature_names)

    X_processed = pd.DataFrame(X_processed_array, columns=all_feature_names)

    dump(preprocessor, preprocessor_path) # Save preprocessor pipeline
    print(f"Preprocessor pipeline saved to: {preprocessor_path}")

    # Save preprocessed X and y
    X_processed.to_csv(preprocessed_X_path, index=False)
    pd.DataFrame(y_encoded, columns=['Churn_Encoded']).to_csv(preprocessed_y_path, index=False)
    print(f"Preprocessed X data saved to: {preprocessed_X_path}")
    print(f"Encoded y data saved to: {preprocessed_y_path}")

    return X_processed, y_encoded

if __name__ == "__main__":
    RAW_DATA_PATH = 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
    PREPROCESSED_X_PATH = 'preprocessing/telco_customer_churn_preprocessed_X.csv'
    PREPROCESSED_Y_PATH = 'preprocessing/telco_customer_churn_preprocessed_y.csv'
    PREPROCESSOR_PATH = 'preprocessing/preprocessor_pipeline.joblib'
    LABEL_ENCODER_PATH = 'preprocessing/label_encoder.joblib'

    # Create preprocessing directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(PREPROCESSED_X_PATH), exist_ok=True)

    X_processed, y_encoded = automate_preprocessing(
        RAW_DATA_PATH, PREPROCESSED_X_PATH, PREPROCESSED_Y_PATH, PREPROCESSOR_PATH, LABEL_ENCODER_PATH
    )
    print("\nAutomated preprocessing completed.")
    print("Shape of X_processed:", X_processed.shape)
    print("First 5 rows of X_processed:")
    print(X_processed.head())
